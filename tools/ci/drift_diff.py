"""Config drift diff generator (Chapter 14 exercise).

Usage:
  python tools/ci/drift_diff.py --baseline commit:abc123 --current commit:def456 --items 2 --out tools/reports/drift_diff.md

Notes:
  - Demo computes a simple summary; extend for real config diffs.
"""
from __future__ import annotations

import argparse
import pathlib
import datetime as dt


def summarize(baseline: str, current: str, items: int) -> str:
    changes = [
        "- tag 差异",
        "- 参数不一致",
    ]
    changes = changes[:max(0, items)]
    return "\n".join(changes) or "(no changes)"


def main() -> int:
    ap = argparse.ArgumentParser(description="Drift diff demo")
    ap.add_argument("--baseline", default="commit:abc123")
    ap.add_argument("--current", default="commit:def456")
    ap.add_argument("--items", type=int, default=2)
    ap.add_argument("--out", default="tools/reports/drift_diff.md")
    args = ap.parse_args()

    now = dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    details = summarize(args.baseline, args.current, args.items)
    verdict = "PASS" if details == "(no changes)" else "WARN"
    report = [
        "# Drift Diff Report",
        f"Generated: {now}",
        f"Verdict: {verdict}",
        f"Baseline: {args.baseline}",
        f"Current: {args.current}",
        "",
        "## Changes",
        details,
        "",
        "## Recommendations",
        "Review and remediate drift items" if verdict != "PASS" else "(no recommendations)",
    ]
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(report), encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
