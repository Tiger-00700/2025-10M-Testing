"""Minimal contract checker (Chapter 14 exercise).

Usage:
  python tools/ci/contract_check.py --schema examples/06_ingest/batch_reconciliation.py --policy backward --out tools/reports/contract_check.md

Notes:
  - This is a demo: it inspects file presence and simulates a compatible change.
  - Replace with real schema registry or JSON schema diff in production.
"""
from __future__ import annotations

import argparse
import pathlib
import datetime as dt


def run(schema_path: pathlib.Path, policy: str) -> str:
    exists = schema_path.exists()
    verdict = "PASS" if exists else "FAIL"
    details = [
        f"Policy: {policy}",
        f"Schema artifact: {schema_path}",
        f"Artifact exists: {exists}",
        "Compat result: simulated-backward-compatible-change",
    ]
    return verdict, "\n".join(details)


def main() -> int:
    ap = argparse.ArgumentParser(description="Contract check demo")
    ap.add_argument("--schema", default="examples/06_ingest/batch_reconciliation.py")
    ap.add_argument("--policy", default="backward", choices=["backward", "forward", "full"])
    ap.add_argument("--out", default="tools/reports/contract_check.md")
    args = ap.parse_args()

    schema_path = pathlib.Path(args.schema)
    verdict, info = run(schema_path, args.policy)
    now = dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    report = [
        "# Contract Check Report",
        f"Generated: {now}",
        f"Verdict: {verdict}",
        "",
        "## Details",
        info,
        "",
        "## Recommendations",
        "(no recommendations)" if verdict == "PASS" else "Fix missing or incompatible schema artifacts",
    ]
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(report), encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
