#!/usr/bin/env python3
"""Compare two CSV files on a key column and report mismatches (minimal stub)."""
from __future__ import annotations
import argparse
import csv
from pathlib import Path


def load_index(path: Path, key: str) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {row[key]: row for row in reader}


def reconcile(src: Path, tgt: Path, key: str) -> None:
    src_rows = load_index(src, key)
    tgt_rows = load_index(tgt, key)

    missing = set(src_rows) - set(tgt_rows)
    extra = set(tgt_rows) - set(src_rows)
    print(f"missing_in_target: {len(missing)}")
    print(f"extra_in_target: {len(extra)}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Minimal batch reconciliation")
    p.add_argument("src", type=Path)
    p.add_argument("tgt", type=Path)
    p.add_argument("--key", default="id")
    args = p.parse_args(argv)
    reconcile(args.src, args.tgt, args.key)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
