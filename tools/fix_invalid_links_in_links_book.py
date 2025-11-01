#!/usr/bin/env python3
"""
Remove invalid Windows-style relative appendix links from the links-only book.
Example to remove (convert to plain text):
  [脚本：2-4__block9.py](..\appendix\2-4__block9.py)

Strategy:
- Find markdown links whose URL matches (..\\|../)+appendix/...
- Replace the whole [text](url) with just 'text' (preserve visible content).

Idempotent and safe: only affects links starting with up-level '..' into appendix.
"""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOK_LINKS = ROOT / 'book' / '1022.2025.newbook.links.md'

LINK_PATTERN1 = re.compile(r"\[([^\]]+)\]\(((?:\.\.[\\]+)+appendix[\\][^\)]+)\)")
LINK_PATTERN2 = re.compile(r"\[([^\]]+)\]\(((?:\.\./+)+appendix/[^\)]+)\)")


def main() -> int:
    if not BOOK_LINKS.exists():
        print(f"No links-only book found: {BOOK_LINKS}")
        return 0
    text = BOOK_LINKS.read_text(encoding='utf-8')
    new_text, n1 = LINK_PATTERN1.subn(r"\1", text)
    new_text, n2 = LINK_PATTERN2.subn(r"\1", new_text)
    n = n1 + n2
    if n:
        BOOK_LINKS.write_text(new_text, encoding='utf-8')
        print(f"Removed {n} invalid appendix links from {BOOK_LINKS.relative_to(ROOT)} (backslash:{n1}, slash:{n2})")
    else:
        print("No invalid appendix links found.")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
