#!/usr/bin/env python3
"""Minimal environment health check stub.
- Checks required directories exist.
- Prints a simple summary for CI/automation hooks.
"""
from __future__ import annotations
import argparse
import pathlib
import sys

CHECKS = [
    ("logs", pathlib.Path("/var/log")),
    ("tmp", pathlib.Path("/tmp")),
]


def run_checks() -> bool:
    ok = True
    for name, path in CHECKS:
        exists = path.exists()
        print(f"[check] {name}: {'ok' if exists else 'missing'} ({path})")
        ok = ok and exists
    return ok


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Environment health check (stub)")
    parser.add_argument("--require", action="append", default=[], help="Extra paths to assert exist")
    args = parser.parse_args(argv)

    extra_ok = True
    for raw in args.require:
        p = pathlib.Path(raw)
        exists = p.exists()
        print(f"[check] extra:{p}: {'ok' if exists else 'missing'}")
        extra_ok = extra_ok and exists

    base_ok = run_checks()
    return 0 if (base_ok and extra_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
