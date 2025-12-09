#!/usr/bin/env python3
"""Run simple data quality rules against CSV rows.
Rules: non-empty columns and numeric range check.
"""
from __future__ import annotations
import argparse
import csv
from pathlib import Path


def run_rules(path: Path, required: list[str], min_value: float | None, max_value: float | None) -> int:
    failures = 0
    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for col in required:
                if not row.get(col):
                    failures += 1
            if min_value is not None or max_value is not None:
                try:
                    val = float(row.get(required[0], 0))
                    if min_value is not None and val < min_value:
                        failures += 1
                    if max_value is not None and val > max_value:
                        failures += 1
                except Exception:
                    failures += 1
    return failures


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Simple CSV rule runner")
    p.add_argument("csv_file", type=Path)
    p.add_argument("--required", nargs="+", default=["id"], help="Columns that must be non-empty")
    p.add_argument("--min", type=float)
    p.add_argument("--max", type=float)
    args = p.parse_args(argv)

    failures = run_rules(args.csv_file, args.required, args.min, args.max)
    print(f"failures: {failures}")
    return 0 if failures == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
