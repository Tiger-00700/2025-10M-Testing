"""Generate baseline report for environment UCs (UC1/UC3/UC4).

UC mapping (from tools/checklists/env_testing_use_cases.md):
- UC1: Environment bootstrap via IaC -> health/contract/quality gate -> baseline report.
- UC3: Permission baseline (least privilege matrix + audit log check).
- UC4: Config drift scan -> detect unauthorized changes -> rollback or ticket.

This script is CI-friendly: pass file paths or commands that produce artifacts,
and it will stitch a markdown report under tools/reports/.

Usage example (PowerShell / CI step):
  python tools/ci/run_env_uc_checks.py \
    --uc1-log artifacts/uc1_health.txt \
    --uc3-log artifacts/uc3_perms.txt \
    --uc4-log artifacts/uc4_drift.txt \
    --report tools/reports/env_uc_baseline_report.md

If a log is missing, the report will mark the section as TODO.
"""
from __future__ import annotations

import argparse
import datetime as dt
import pathlib
from typing import Optional

DEFAULT_REPORT = pathlib.Path("tools/reports/env_uc_baseline_report.md")
DEFAULT_LOG_DIR = pathlib.Path("tools/reports")
DEFAULT_UC1 = DEFAULT_LOG_DIR / "uc1_bootstrap.log"
DEFAULT_UC3 = DEFAULT_LOG_DIR / "uc3_permissions.log"
DEFAULT_UC4 = DEFAULT_LOG_DIR / "uc4_drift_scan.log"


def read_optional(path: Optional[str]) -> str:
    if not path:
        return "(missing)"
    p = pathlib.Path(path)
    if not p.exists():
        return f"(missing: {p})"
    try:
        return p.read_text(encoding="utf-8").strip() or "(empty log)"
    except Exception as exc:  # pragma: no cover - defensive
        return f"(error reading {p}: {exc})"


def autodiscover(path: Optional[str], fallback: pathlib.Path) -> str:
    """Return content for path if provided, else try fallback file.

    If neither exists, return a helpful missing message that indicates both
    attempted locations.
    """
    if path:
        return read_optional(path)
    # No explicit path provided; try fallback
    if fallback.exists():
        return read_optional(str(fallback))
    return f"(missing: {fallback} — provide via --{fallback.stem.replace('_', '-')} or place log here)"


def build_report(uc1: str, uc3: str, uc4: str) -> str:
    now = dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    lines = [
        "# Environment Baseline Report (UC1/UC3/UC4)",
        f"Generated: {now}",
        "", "## UC1 - Bootstrap & Quality Gates", uc1,
        "", "## UC3 - Permission Baseline & Audit", uc3,
        "", "## UC4 - Config Drift Scan", uc4,
        "", "## Notes", "- Replace '(missing)' sections with actual outputs from CI steps.",
        "- Keep this report in version control or artifacts for auditability.",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compose env UC baseline report")
    parser.add_argument("--uc1-log", help="Path to UC1 log (health/contract/gates)")
    parser.add_argument("--uc3-log", help="Path to UC3 log (permission matrix + audit)")
    parser.add_argument("--uc4-log", help="Path to UC4 log (drift scan)")
    parser.add_argument(
        "--report", default=str(DEFAULT_REPORT), help="Output report path (default: tools/reports/env_uc_baseline_report.md)",
    )
    args = parser.parse_args()

    # Auto-discover default logs under tools/reports/ if args not provided
    uc1 = autodiscover(args.uc1_log, DEFAULT_UC1)
    uc3 = autodiscover(args.uc3_log, DEFAULT_UC3)
    uc4 = autodiscover(args.uc4_log, DEFAULT_UC4)

    report = build_report(uc1, uc3, uc4)
    out_path = pathlib.Path(args.report)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")
    print(f"Wrote report to {out_path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
