"""Observability drill report generator (Chapter 18).

Simulates a drill result and writes a markdown report. Replace the simulated
values with real metrics from your observability platform.

Usage:
  python tools/ci/observability_drill.py --scenario latency --mttd 2.5 --mttr 8 --signals logs,metrics,traces,alerts --out tools/reports/observability_drill.md
"""
from __future__ import annotations

import argparse
import pathlib
import datetime as dt


def main() -> int:
    ap = argparse.ArgumentParser(description="Observability drill report generator")
    ap.add_argument("--scenario", default="latency_spike")
    ap.add_argument("--mttd", type=float, default=2.5, help="minutes to detect")
    ap.add_argument("--mttr", type=float, default=8.0, help="minutes to recover")
    ap.add_argument("--signals", default="logs,metrics,traces,alerts")
    ap.add_argument("--gaps", default="sampling_low;missing_fields")
    ap.add_argument("--actions", default="raise_sampling;add_trace_tags;fix_alert_routing")
    ap.add_argument("--out", default="tools/reports/observability_drill.md")
    args = ap.parse_args()

    now = dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    verdict = "PASS" if args.mttd <= 5 and args.mttr <= 15 else "WARN"
    report = [
        "# Observability Drill Report",
        f"Generated: {now}",
        f"Verdict: {verdict}",
        "",
        "## Scenario",
        f"- Name: {args.scenario}",
        f"- Signals: {args.signals}",
        "",
        "## Outcomes",
        f"- MTTD: {args.mttd} min",
        f"- MTTR: {args.mttr} min",
        "",
        "## Gaps",
        "- " + "\n- ".join(args.gaps.split(";")),
        "",
        "## Recommended Actions",
        "- " + "\n- ".join(args.actions.split(";")),
    ]
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(report), encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
