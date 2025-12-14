"""Aggregate automation reports into a single summary.

Reads individual Markdown reports (test runner, data factory, security patrol,
quality gates, contract checks, drift diffs) and composes a consolidated
automation summary for audit.

Usage:
  python tools/ci/automation_summary.py --out tools/reports/automation_summary.md
"""
from __future__ import annotations

import argparse
import pathlib
import datetime as dt
from typing import List, Tuple


DEFAULT_REPORTS = [
    pathlib.Path("tools/reports/test_runner.md"),
    pathlib.Path("tools/reports/data_factory_sample.md"),
    pathlib.Path("tools/reports/security_patrol.md"),
    pathlib.Path("tools/reports/quality_gate_scan.md"),
    pathlib.Path("tools/reports/contract_check.md"),
    pathlib.Path("tools/reports/drift_diff.md"),
]


def read_report(p: pathlib.Path) -> str:
    if not p.exists():
        return f"(missing: {p})"
    try:
        return p.read_text(encoding="utf-8").strip() or "(empty)"
    except Exception as exc:
        return f"(error reading {p}: {exc})"


def extract_verdict(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("Verdict:"):
            return line.split("Verdict:", 1)[1].strip()
    if "(missing:" in text or text.strip() == "(empty)":
        return "MISSING"
    return "UNKNOWN"


def extract_recommendations(text: str) -> str:
    capture = False
    lines = []
    for line in text.splitlines():
        if line.strip().startswith("## Recommendations"):
            capture = True
            continue
        if capture:
            if line.strip().startswith("## "):
                break
            lines.append(line)
    return "\n".join(lines).strip() or ""


def main() -> int:
    ap = argparse.ArgumentParser(description="Aggregate automation reports")
    ap.add_argument("--out", default="tools/reports/automation_summary.md")
    ap.add_argument(
        "--inputs",
        nargs="*",
        default=[str(p) for p in DEFAULT_REPORTS],
        help="List of report paths to include",
    )
    args = ap.parse_args()

    now = dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    sections: List[str] = ["# Automation Summary", f"Generated: {now}", ""]
    verdicts: List[Tuple[str, str]] = []
    recs_all: List[str] = []
    for path_str in args.inputs:
        p = pathlib.Path(path_str)
        content = read_report(p)
        sections.append(f"## {p.name}")
        sections.append(content)
        sections.append("")
        verdicts.append((p.name, extract_verdict(content)))
        rec = extract_recommendations(content)
        if rec:
            recs_all.append(f"### {p.name}\n{rec}")

    # Summary of verdicts
    counts = {}
    for _, v in verdicts:
        counts[v] = counts.get(v, 0) + 1
    sections.append("## Summary")
    summary_lines = [f"- {v}: {n}" for v, n in sorted(counts.items())]
    sections.append("\n".join(summary_lines) or "(no reports)")
    # List non-PASS items
    non_pass = [name for name, v in verdicts if v not in ("PASS", "INFO")]
    sections.append("")
    sections.append("## Non-PASS Items")
    sections.append("\n".join([f"- {n}" for n in non_pass]) or "(all PASS/INFO)")
    sections.append("")
    sections.append("## Aggregated Recommendations")
    sections.append("\n\n".join(recs_all) or "(no recommendations)")
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(sections), encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
