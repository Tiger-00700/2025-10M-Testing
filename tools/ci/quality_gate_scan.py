"""Quality gate scanner (Chapter 14 exercise).

Usage:
  python tools/ci/quality_gate_scan.py --p95-latency 4.2 --accuracy 99.7 --latency-threshold 5 --accuracy-threshold 99.5 --out tools/reports/quality_gate_scan.md

Notes:
  - Demo thresholds: latency (seconds) and accuracy (%).
  - Extend to ingest real metrics from monitoring or job outputs.
"""
from __future__ import annotations

import argparse
import pathlib
import datetime as dt


def evaluate(p95_latency: float, accuracy: float, lat_thr: float, acc_thr: float) -> str:
    checks = []
    checks.append(("P95 latency", p95_latency <= lat_thr, f"{p95_latency}s <= {lat_thr}s"))
    checks.append(("Accuracy", accuracy >= acc_thr, f"{accuracy}% >= {acc_thr}%"))
    all_pass = all(ok for _, ok, _ in checks)
    verdict = "PASS" if all_pass else "FAIL"
    lines = [f"- {name}: {'OK' if ok else 'NOT OK'} ({desc})" for name, ok, desc in checks]
    return verdict, "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Quality gate scan demo")
    ap.add_argument("--p95-latency", type=float, default=4.2)
    ap.add_argument("--accuracy", type=float, default=99.7)
    ap.add_argument("--latency-threshold", type=float, default=5.0)
    ap.add_argument("--accuracy-threshold", type=float, default=99.5)
    ap.add_argument("--out", default="tools/reports/quality_gate_scan.md")
    args = ap.parse_args()

    verdict, details = evaluate(args.p95_latency, args.accuracy, args.latency_threshold, args.accuracy_threshold)
    now = dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    report = [
      "# Quality Gate Report",
      f"Generated: {now}",
      f"Verdict: {verdict}",
      "",
      "## Checks",
      details,
      "",
      "## Recommendations",
      "(no recommendations)" if verdict == "PASS" else "Tune thresholds or investigate performance/accuracy",
    ]
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(report), encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
