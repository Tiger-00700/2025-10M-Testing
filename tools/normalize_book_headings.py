#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Normalize headings in book/1022.2025.book.md to follow the Part→Chapter→Section→Subsection
structure defined in book/篇章结构.md.

Rules applied (conservative, low-risk):
- Keep single H1 (book title) unchanged.
- Ensure '第一篇/第二篇/… 第N篇 …' are H2 (##).
- Ensure '第 N 章 …' are H3 (###).
- Ensure 'N.M …' or '第 N 节 …' are H4 (####).
- For H4 sections, any nested subpoints become H5+ (left as-is if already >= H5).
- Split accidental multiple headings merged on one line into separate lines.
- Do not change non-heading content.

A dry summary of changes is printed. The file is updated in-place only if changes are made.
"""
from __future__ import annotations
import io
import os
import re
import sys
from typing import List, Tuple

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_PATH = os.path.join(ROOT, 'book', '1022.2025.book.md')

# Chinese numerals and digits for 篇 detection
CN_NUM = '零一二三四五六七八九十百千〇两'

# Compiled regexes
RE_HEADING = re.compile(r'^(?P<hashes>#{1,6})\s+(?P<text>.*)$')
RE_PART = re.compile(r'^第\s*([%s0-9]+)\s*篇\b' % CN_NUM)
RE_CHAPTER = re.compile(r'^第\s*([0-9]+)\s*章\b')
RE_SECTION_NUMERIC = re.compile(r'^(\d+(?:\.\d+)+)\b')
RE_SECTION_WORD = re.compile(r'^第\s*([0-9]+)\s*节\b')
RE_APPENDIX = re.compile(r'^附录\s*$')
RE_APPENDIX_ITEM = re.compile(r'^附录\s+[A-Z](?:\b|\s)')

# Detect additional heading tokens later in the same line (merged headings)
RE_INLINE_HEADING_TOKEN = re.compile(r'(\s)(#{2,6})\s+(?=\S)')


def split_merged_headings(line: str) -> List[str]:
    """Split a line that mistakenly contains multiple headings into separate lines.
    Keeps the first heading as-is; subsequent heading tokens become new lines.
    """
    m = RE_HEADING.match(line)
    if not m:
        return [line]
    # Only operate on the tail after the first heading marker+space
    first = f"{m.group('hashes')} "
    tail = m.group('text')
    # If tail itself starts with a heading token, prefer the inner heading (drop the outer one)
    if tail.lstrip().startswith('#'):
        return [tail.strip()]
    # Replace inline tokens in tail with newline + token
    # Apply from longest to shortest to avoid partial replacements
    patterns = ['######', '#####', '####', '###', '##']
    for p in patterns:
        tail = tail.replace(f' {p} ', f"\n{p} ")
    parts = [p for p in tail.split('\n') if p.strip()]
    if not parts:
        return [line]
    pieces: List[str] = []
    # First piece keeps the original heading marker
    pieces.append(first + parts[0].strip())
    # Subsequent parts are already proper headings (e.g., ### 19.2.1 ...)
    for p in parts[1:]:
        pieces.append(p.strip())
    return pieces


def normalize_heading_line(line: str) -> str:
    """Normalize a single heading line according to the rules."""
    m = RE_HEADING.match(line)
    if not m:
        return line
    hashes = m.group('hashes')
    text = m.group('text').strip()

    # H1 left intact
    if len(hashes) == 1:
        return f"{hashes} {text}".rstrip()

    # Normalize levels by patterns
    # 篇 → H2
    if RE_PART.match(text):
        return f"## {text}".rstrip()

    # 章 → H3
    if RE_CHAPTER.match(text):
        return f"### {text}".rstrip()

    # 附录总标题 → H2；附录项（附录 A/B/…）→ H3
    if RE_APPENDIX.match(text):
        return f"## {text}".rstrip()
    if RE_APPENDIX_ITEM.match(text):
        return f"### {text}".rstrip()

    # 节（文字）或 数字节：
    # - Numeric N.M → H4
    # - Numeric N.M.K (>=3 segments) → H5
    mnum = RE_SECTION_NUMERIC.match(text)
    if RE_SECTION_WORD.match(text) or mnum:
        if mnum:
            segs = mnum.group(1).split('.')
            if len(segs) >= 3:
                return f"##### {text}".rstrip()
        return f"#### {text}".rstrip()

    # Otherwise, keep as-is (could be subpoints under H4, e.g., H5/H6)
    return f"{hashes} {text}".rstrip()


def normalize_content(lines: List[str]) -> Tuple[List[str], int, int]:
    """Return normalized lines, with counts of (lines_changed, splits_made)."""
    out: List[str] = []
    changed = 0
    splits = 0
    for line in lines:
        # First, split merged headings if any
        if RE_INLINE_HEADING_TOKEN.search(line) and line.lstrip().startswith('#'):
            pieces = split_merged_headings(line)
            if len(pieces) > 1:
                splits += len(pieces) - 1
            for p in pieces:
                norm = normalize_heading_line(p)
                if norm != p.rstrip('\n'):
                    changed += 1
                out.append(norm + '\n')
            continue

        # Then normalize heading level if applicable
        norm = normalize_heading_line(line.rstrip('\n'))
        if norm + ('\n' if line.endswith('\n') else '') != line:
            changed += 1
        out.append(norm + ('\n' if line.endswith('\n') else ''))
    return out, changed, splits


def summarize_headings(lines: List[str]) -> str:
    """Produce a small summary of heading counts by level and first 5 examples."""
    levels = {i: [] for i in range(1, 7)}
    for i, line in enumerate(lines, start=1):
        m = RE_HEADING.match(line)
        if m:
            lvl = len(m.group('hashes'))
            if len(levels[lvl]) < 5:
                levels[lvl].append(f"L{i}: {m.group('hashes')} {m.group('text')[:60]}")
    parts = []
    for lvl in range(1, 7):
        samples = '\n    '.join(levels[lvl]) if levels[lvl] else '—'
        parts.append(f"H{lvl}: samples\n    {samples}")
    return "\n\n".join(parts)


def main(path: str) -> int:
    if not os.path.isfile(path):
        print(f"ERROR: File not found: {path}", file=sys.stderr)
        return 2
    with io.open(path, 'r', encoding='utf-8') as f:
        original_lines = f.readlines()

    normalized_lines, changed, splits = normalize_content(original_lines)

    if changed == 0 and splits == 0:
        print("No heading changes needed.")
        print(summarize_headings(original_lines))
        return 0

    with io.open(path, 'w', encoding='utf-8', newline='') as f:
        f.writelines(normalized_lines)

    print(f"Applied heading normalization: changed_lines={changed}, split_merged_headings={splits}")
    print("After normalization, samples:")
    print(summarize_headings(normalized_lines))
    return 0


if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PATH
    sys.exit(main(target))
