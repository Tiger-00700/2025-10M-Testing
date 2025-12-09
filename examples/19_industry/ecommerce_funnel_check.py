#!/usr/bin/env python3
"""E-commerce funnel check stub."""
from __future__ import annotations
import argparse


def check(view: int, cart: int, pay: int) -> None:
    conv_view_cart = (cart / view) * 100 if view else 0
    conv_cart_pay = (pay / cart) * 100 if cart else 0
    print(f"view->{cart}: {conv_view_cart:.2f}% | cart->{pay}: {conv_cart_pay:.2f}%")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="E-commerce funnel check")
    p.add_argument("views", type=int)
    p.add_argument("carts", type=int)
    p.add_argument("payments", type=int)
    args = p.parse_args(argv)
    check(args.views, args.carts, args.payments)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
