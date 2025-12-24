#!/usr/bin/env python3
"""Log health check stub: reports size and mtime for given files."""
from __future__ import annotations
import argparse
import os
from pathlib import Path
from datetime import datetime


def inspect(path: Path) -> None:
    if not path.exists():
        print(f"missing: {path}")
        return
    stat = path.stat()
    mtime = datetime.fromtimestamp(stat.st_mtime).isoformat()
    print(f"ok: {path} size={stat.st_size} mtime={mtime}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Log health check")
    p.add_argument("paths", nargs="+", type=Path)
    args = p.parse_args(argv)
    for path in args.paths:
        inspect(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
