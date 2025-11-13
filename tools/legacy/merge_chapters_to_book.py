#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Merge all chapter/*.md into book/1022.2025.newbook.md in logical order:
- Sort by Part number (第N篇), within each Part put the Part overview (no 章) before Chapters (第M章)
- Append Appendix (e.g., 附录.md) at the end
- Preserve content as-is; insert two blank lines between files
"""
from __future__ import annotations
import io
import os
import re
from typing import List, Tuple

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAPTER_DIR = os.path.join(ROOT, 'chapter')
BOOK_PATH = os.path.join(ROOT, 'book', '1022.2025.newbook.md')

RE_PART = re.compile(r'^第(\d+)篇')
RE_CHAPTER = re.compile(r'^第(\d+)篇-第(\d+)章')


def sort_key(filename: str) -> Tuple[int, int, int, str]:
    name = os.path.basename(filename)
    base, ext = os.path.splitext(name)
    if base == '附录':
        return (10_000, 10_000, 10_000, name)
    m_ch = RE_CHAPTER.match(base)
    if m_ch:
        part = int(m_ch.group(1))
        chap = int(m_ch.group(2))
        return (part, 1, chap, name)
    m_part = RE_PART.match(base)
    if m_part:
        part = int(m_part.group(1))
        return (part, 0, 0, name)
    # Fallback: put unknown patterns before appendix but after known parts
    return (9_999, 9_999, 9_999, name)


def main() -> int:
    md_files: List[str] = []
    for fn in os.listdir(CHAPTER_DIR):
        path = os.path.join(CHAPTER_DIR, fn)
        if os.path.isfile(path) and fn.lower().endswith('.md'):
            md_files.append(path)

    if not md_files:
        print('No Markdown files found in chapter/. Nothing to merge.')
        return 0

    md_files.sort(key=sort_key)

    parts: List[str] = []
    print('Merging files in order:')
    for p in md_files:
        rel = os.path.relpath(p, ROOT)
        print(f' - {rel}')
        with io.open(p, 'r', encoding='utf-8') as f:
            txt = f.read().rstrip('\n')
        parts.append(txt)

    merged = ('\n\n'.join(parts) + '\n')

    os.makedirs(os.path.dirname(BOOK_PATH), exist_ok=True)
    with io.open(BOOK_PATH, 'w', encoding='utf-8', newline='') as f:
        f.write(merged)

    print(f'Wrote merged book to: {os.path.relpath(BOOK_PATH, ROOT)}')
    print(f'Included {len(md_files)} files.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
