#!/usr/bin/env python3
"""Generate a tiny CSV dataset for testing.
Outputs columns: id,value,tag
"""
from __future__ import annotations
import argparse
import csv
from pathlib import Path

def generate(out: Path, rows: int) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "value", "tag"])
        for i in range(rows):
            writer.writerow([i, i * 10, "sample"])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Minimal test data generator")
    parser.add_argument("--out", type=Path, default=Path("./sample_data.csv"))
    parser.add_argument("--rows", type=int, default=10)
    args = parser.parse_args(argv)
    generate(args.out, args.rows)
    print(f"written: {args.out} ({args.rows} rows)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
