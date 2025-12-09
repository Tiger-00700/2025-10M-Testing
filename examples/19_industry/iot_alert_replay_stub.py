#!/usr/bin/env python3
"""IoT alert replay stub."""
from __future__ import annotations
import argparse
from pathlib import Path


def replay(path: Path) -> None:
    for line in path.read_text(encoding="utf-8").splitlines():
        print(f"replay:{line}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="IoT alert replay stub")
    p.add_argument("input", type=Path)
    args = p.parse_args(argv)
    replay(args.input)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
