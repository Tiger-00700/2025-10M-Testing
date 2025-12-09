#!/usr/bin/env python3
"""Masking policy demo: masks email/userid fields in CSV."""
from __future__ import annotations
import argparse
import csv
from pathlib import Path


def mask_email(val: str) -> str:
    if "@" not in val:
        return "***"
    user, domain = val.split("@", 1)
    return f"{user[:1]}***@{domain}"


def process(inp: Path, out: Path) -> None:
    with inp.open(encoding="utf-8") as fi, out.open("w", newline="", encoding="utf-8") as fo:
        reader = csv.DictReader(fi)
        writer = csv.DictWriter(fo, fieldnames=reader.fieldnames)
        writer.writeheader()
        for row in reader:
            if "email" in row:
                row["email"] = mask_email(row["email"] or "")
            if "user_id" in row:
                row["user_id"] = f"user-{hash(row['user_id']) % 1000}"
            writer.writerow(row)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Mask PII fields in CSV")
    p.add_argument("--in", dest="inp", type=Path, required=True)
    p.add_argument("--out", dest="out", type=Path, default=Path("masked.csv"))
    args = p.parse_args(argv)
    process(args.inp, args.out)
    print(f"written: {args.out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
