import argparse
import csv
import json
import os
from datetime import datetime
from typing import Dict, Tuple, List


def _maybe_import(name: str):
    try:
        return __import__(name)
    except Exception:
        return None


def load_metrics(path: str) -> Dict[str, float]:
    ext = os.path.splitext(path)[1].lower()
    data: Dict[str, float] = {}
    # Optional Parquet support via pandas if file ends with .parquet
    if ext == ".parquet":
        pd = _maybe_import("pandas")
        if pd is None:
            raise RuntimeError("Parquet input requires pandas installed (with pyarrow/fastparquet).")
        df = pd.read_parquet(path)
        if {"metric", "value"}.issubset(df.columns):
            for _, row in df.iterrows():
                try:
                    data[str(row["metric"])] = float(row["value"])
                except (TypeError, ValueError):
                    continue
            return data
        if len(df) == 1:
            row = df.iloc[0]
            for col in df.columns:
                try:
                    data[str(col)] = float(row[col])
                except (TypeError, ValueError):
                    continue
            return data
        if len(df.columns) >= 2:
            mcol, vcol = df.columns[:2]
            for _, row in df.iterrows():
                try:
                    data[str(row[mcol])] = float(row[vcol])
                except (TypeError, ValueError):
                    continue
            return data
    if ext in {".json"}:
        with open(path, "r", encoding="utf-8") as f:
            obj = json.load(f)
        # Expect {metric: value}
        for k, v in obj.items():
            try:
                data[str(k)] = float(v)
            except (TypeError, ValueError):
                pass
    elif ext in {".csv"}:
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            # Expect columns: metric,value
            for row in reader:
                k = row.get("metric")
                v = row.get("value")
                if k is None or v is None:
                    continue
                try:
                    data[str(k)] = float(v)
                except (TypeError, ValueError):
                    continue
    else:
        # Simple line format: metric=value
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                try:
                    data[k.strip()] = float(v.strip())
                except (TypeError, ValueError):
                    continue
    return data


def diff_metrics(a: Dict[str, float], b: Dict[str, float], tolerance_pct: float) -> Tuple[List[Tuple[str, float, float, float]], List[str]]:
    rows: List[Tuple[str, float, float, float]] = []
    failures: List[str] = []
    all_keys = sorted(set(a.keys()) | set(b.keys()))
    for k in all_keys:
        va = a.get(k)
        vb = b.get(k)
        if va is None or vb is None:
            failures.append(f"Missing metric '{k}' in {'A' if va is None else 'B'}")
            rows.append((k, va if va is not None else float('nan'), vb if vb is not None else float('nan'), float('nan')))
            continue
        diff = vb - va
        # percent relative to A
        pct = (diff / va * 100.0) if va != 0 else (float('inf') if diff != 0 else 0.0)
        rows.append((k, va, vb, pct))
        if abs(pct) > tolerance_pct:
            failures.append(f"Metric '{k}' diff {pct:.3f}% exceeds tolerance {tolerance_pct:.3f}%")
    return rows, failures


def write_report(rows: List[Tuple[str, float, float, float]], failures: List[str], out_dir: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(out_dir, f"report_diff_{stamp}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("# Report Metric Diff\n\n")
        f.write("| Metric | Source A | Source B | Diff % |\n")
        f.write("|---|---:|---:|---:|\n")
        for k, va, vb, pct in rows:
            va_str = "NaN" if (va != va) else f"{va:.6f}"  # check NaN
            vb_str = "NaN" if (vb != vb) else f"{vb:.6f}"
            pct_str = "NaN" if (pct != pct) else f"{pct:.3f}%"
            f.write(f"| {k} | {va_str} | {vb_str} | {pct_str} |\n")
        f.write("\n## Failures\n\n")
        if failures:
            for msg in failures:
                f.write(f"- {msg}\n")
        else:
            f.write("- None\n")
        # Append minimal compliance sections for completeness
        f.write("\n## 摘要\n\n")
        f.write("本报告用于源/目标度量对账与容忍度校验，作为发布门禁证据。\n")
        f.write("\n## 证据\n\n")
        f.write("- 对账表与失败列表见上文。\n")
        f.write("\n## 结论\n\n")
        f.write("结论：" + ("通过" if not failures else "不通过") + "。\n")
        f.write("\n## 签署\n\n")
        f.write("- 责任人：\n- 复核人：\n- 日期：" + stamp + "\n")
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Compare metric aggregates and write diff report")
    parser.add_argument("--source-a", required=True, help="Path to source A metrics (json/csv/kv/parquet) or sql://conn?query=...")
    parser.add_argument("--source-b", required=True, help="Path to source B metrics (json/csv/kv/parquet) or sql://conn?query=...")
    parser.add_argument("--tolerance-pct", type=float, default=1.0, help="Max allowed percent change (relative to A)")
    parser.add_argument("--out-dir", default=os.path.join("tools", "reports"), help="Directory to write report")
    args = parser.parse_args()

    def load_any(spec: str) -> Dict[str, float]:
        if spec.startswith("sql://"):
            part = spec[len("sql://"):]
            conn, _, query_part = part.partition("?query=")
            if not conn or not query_part:
                raise RuntimeError("SQL spec must be sql://<conn>?query=<SQL>")
            pd = _maybe_import("pandas")
            sa = _maybe_import("sqlalchemy")
            if pd is None or sa is None:
                raise RuntimeError("SQL input requires pandas and sqlalchemy installed.")
            engine = sa.create_engine(conn)
            df = pd.read_sql_query(query_part, engine)
            data: Dict[str, float] = {}
            if {"metric", "value"}.issubset(df.columns):
                for _, row in df.iterrows():
                    try:
                        data[str(row["metric"])] = float(row["value"])
                    except (TypeError, ValueError):
                        continue
                return data
            if len(df) == 1:
                row = df.iloc[0]
                for col in df.columns:
                    try:
                        data[str(col)] = float(row[col])
                    except (TypeError, ValueError):
                        continue
                return data
            if len(df.columns) >= 2:
                mcol, vcol = df.columns[:2]
                for _, row in df.iterrows():
                    try:
                        data[str(row[mcol])] = float(row[vcol])
                    except (TypeError, ValueError):
                        continue
                return data
            return data
        return load_metrics(spec)

    a = load_any(args.source_a)
    b = load_any(args.source_b)
    rows, failures = diff_metrics(a, b, args.tolerance_pct)
    report_path = write_report(rows, failures, args.out_dir)
    print(f"Report written: {report_path}")

    if failures:
        # Non-zero exit to gate CI when differences exceed tolerance
        raise SystemExit(2)


if __name__ == "__main__":
    main()
