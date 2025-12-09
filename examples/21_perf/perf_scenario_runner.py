#!/usr/bin/env python3
"""Performance scenario runner stub: simulates load steps."""
from __future__ import annotations
import argparse
import time


def run(steps: int, sleep: float) -> None:
    for i in range(1, steps + 1):
        print(f"step {i}/{steps}: simulated load")
        time.sleep(sleep)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Performance scenario runner (stub)")
    p.add_argument("--steps", type=int, default=3)
    p.add_argument("--sleep", type=float, default=0.1)
    args = p.parse_args(argv)
    run(args.steps, args.sleep)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
