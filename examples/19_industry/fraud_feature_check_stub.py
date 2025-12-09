#!/usr/bin/env python3
"""Fraud feature check stub: flags records over a threshold."""
from __future__ import annotations
import argparse
import csv
from pathlib import Path


def run(path: Path, field: str, threshold: float) -> int:
    flagged = 0
    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                val = float(row.get(field, 0))
                if val > threshold:
                    flagged += 1
            except Exception:
                flagged += 1
    print(f"flagged: {flagged}")
    return 0 if flagged == 0 else 2


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Fraud feature check stub")
    p.add_argument("csv", type=Path)
    p.add_argument("--field", default="score")
    p.add_argument("--threshold", type=float, default=0.8)
    args = p.parse_args(argv)
    return run(args.csv, args.field, args.threshold)


if __name__ == "__main__":
    raise SystemExit(main())
