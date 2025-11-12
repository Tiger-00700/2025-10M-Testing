#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path


def replace_in_file(path: Path, old: str, new: str) -> int:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        text = path.read_text(errors="ignore")
    if old not in text:
        return 0
    text2 = text.replace(old, new)
    if text2 != text:
        path.write_text(text2, encoding="utf-8")
        return 1
    return 0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default="book", help="Root folder to scan")
    ap.add_argument("--old", required=True)
    ap.add_argument("--new", required=True)
    args = ap.parse_args()

    root = Path(args.root)
    changed = 0
    for p in root.rglob("*.md"):
        changed += replace_in_file(p, args.old, args.new)
    print(f"Files changed: {changed}")


if __name__ == "__main__":
    main()
