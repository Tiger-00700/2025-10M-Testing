#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Clean exported Python code blocks under examples/99_book_exports.

Removes non-code prose lines introduced during markdown export (for example,
lines starting with '>' or containing full-width brackets like '【...】').
Writes changes in-place and prints a short summary.
"""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPORTS = ROOT/"examples"/"99_book_exports"

PATTERNS = [
    re.compile(r"^\s*>"),             # blockquote prose
    re.compile(r"^\s*#>"),            # commented prose markers
    re.compile(r"^\s*【.*?】"),       # full-width bracketed notes
    re.compile(r"^\s*//"),            # stray java/js comments in py
    re.compile(r"^\s*\|"),            # table residue
    re.compile(r"^\s*[-*•—–·]\s+"),    # markdown bullet lines (Chinese/ASCII bullets)
    re.compile(r"^\s*\d+\.\s+"),       # numbered list like '1. '
    re.compile(r"^\s*(本节要点|要点|提示|注意|说明)\s*[:：]"),  # common Chinese lead-ins
]

def is_prose(line: str) -> bool:
    s = line.rstrip("\n")
    if not s:
        return False
    for p in PATTERNS:
        if p.match(s):
            return True
    # Extra heuristics for stray prose markers inside code fences.
    # Treat lines that look like section dividers as prose too.
    if re.match(r"^\s*[-=*]{3,}\s*$", s):
        return True
    return False

def sanitize_py(text: str) -> str:
    lines = text.splitlines()
    kept: list[str] = []
    for ln in lines:
        if is_prose(ln):
            continue
        kept.append(ln)
    body = "\n".join(kept).strip()
    if not body:
        body = "if __name__ == '__main__':\n    pass\n"
    end = "\n" if not body.endswith("\n") else ""
    return body + end


def main() -> None:
    if not EXPORTS.exists():
        print(f"Exports folder not found: {EXPORTS}")
        return
    py_files = list(EXPORTS.rglob("*.py"))
    changed = 0
    for f in py_files:
        try:
            original = f.read_text(encoding="utf-8", errors="ignore")
            cleaned = sanitize_py(original)
            if cleaned != original:
                f.write_text(cleaned, encoding="utf-8")
                changed += 1
        except Exception as e:
            print(f"WARN: Failed to clean {f}: {e}")
    print(f"Cleaned {changed} Python export(s) out of {len(py_files)}")


if __name__ == "__main__":
    main()
