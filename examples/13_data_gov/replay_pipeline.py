#!/usr/bin/env python3
"""Minimal replay pipeline stub: reads input events and echoes them with stage markers."""
from __future__ import annotations
import argparse
from pathlib import Path


def replay(path: Path) -> None:
    for line in path.read_text(encoding="utf-8").splitlines():
        print(f"[ingest]{line}")
        print(f"[validate]{line}")
        print(f"[publish]{line}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Replay pipeline stub")
    p.add_argument("input", type=Path)
    args = p.parse_args(argv)
    replay(args.input)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
