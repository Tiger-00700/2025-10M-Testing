#!/usr/bin/env python3
"""Minimal ETL diff checker for two JSONL files (by key)."""
from __future__ import annotations
import argparse
import json
from pathlib import Path


def load_jsonl(path: Path, key: str) -> dict[str, dict]:
    data: dict[str, dict] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        obj = json.loads(line)
        data[str(obj[key])] = obj
    return data


def diff(a: dict[str, dict], b: dict[str, dict]) -> None:
    missing = set(a) - set(b)
    extra = set(b) - set(a)
    print(f"missing_in_b: {len(missing)} | extra_in_b: {len(extra)}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Batch ETL diff (JSONL, keyed)")
    p.add_argument("source", type=Path)
    p.add_argument("target", type=Path)
    p.add_argument("--key", default="id")
    args = p.parse_args(argv)

    a = load_jsonl(args.source, args.key)
    b = load_jsonl(args.target, args.key)
    diff(a, b)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
