#!/usr/bin/env python3
"""Minimal file replay entry stub.
Reads an input file and echoes lines with sequence numbers to stdout.
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

def replay(path: Path) -> None:
    for idx, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        print(f"{idx}\t{line}")

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Replay a text file with sequence numbers")
    parser.add_argument("file", type=Path, help="Input file to replay")
    args = parser.parse_args(argv)
    if not args.file.exists():
        print(f"ERROR: file not found: {args.file}", file=sys.stderr)
        return 1
    replay(args.file)
    return 0

if __name__ == "__main__":
    sys.exit(main())
