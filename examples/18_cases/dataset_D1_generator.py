#!/usr/bin/env python3
"""Generate a toy dataset D1 (stub)."""
from __future__ import annotations
import argparse
import csv
from pathlib import Path

def generate(out: Path, n: int) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "value", "label"])
        for i in range(n):
            w.writerow([i, i % 5, "ok" if i % 2 == 0 else "warn"])


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Dataset D1 generator")
    p.add_argument("--out", type=Path, default=Path("./dataset_D1.csv"))
    p.add_argument("--rows", type=int, default=20)
    args = p.parse_args(argv)
    generate(args.out, args.rows)
    print(f"written: {args.out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
