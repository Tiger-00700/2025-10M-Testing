#!/usr/bin/env python3
"""Stub for HDFS consistency check.
Simulates a path listing comparison between two snapshots.
"""
from __future__ import annotations
import argparse
from pathlib import Path


def compare_lists(baseline: list[str], current: list[str]) -> None:
    missing = set(baseline) - set(current)
    extra = set(current) - set(baseline)
    print(f"missing: {len(missing)} | extra: {len(extra)}")
    if missing:
        print("missing items:")
        for item in sorted(missing):
            print(f"  - {item}")
    if extra:
        print("extra items:")
        for item in sorted(extra):
            print(f"  - {item}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="HDFS consistency check (stub)")
    parser.add_argument("baseline", type=Path, help="Baseline file list (one path per line)")
    parser.add_argument("current", type=Path, help="Current file list (one path per line)")
    args = parser.parse_args(argv)

    base_list = args.baseline.read_text(encoding="utf-8").splitlines()
    curr_list = args.current.read_text(encoding="utf-8").splitlines()
    compare_lists(base_list, curr_list)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
