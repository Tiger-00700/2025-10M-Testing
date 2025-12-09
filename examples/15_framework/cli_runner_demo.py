#!/usr/bin/env python3
"""CLI runner demo with subcommands (stub)."""
from __future__ import annotations
import argparse


def cmd_echo(args: argparse.Namespace) -> int:
    print(args.message)
    return 0


def cmd_sum(args: argparse.Namespace) -> int:
    print(sum(args.numbers))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CLI runner demo")
    sub = parser.add_subparsers(dest="command", required=True)

    p_echo = sub.add_parser("echo", help="Echo a message")
    p_echo.add_argument("message")
    p_echo.set_defaults(func=cmd_echo)

    p_sum = sub.add_parser("sum", help="Sum numbers")
    p_sum.add_argument("numbers", nargs="+", type=float)
    p_sum.set_defaults(func=cmd_sum)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
