#!/usr/bin/env python3
"""
Inventory and clean placeholders in the cleaned book.

Classifies placeholders into:
  A) Heading placeholders: markdown headings whose title is the placeholder key
  B) Inline placeholders: plain lines containing the placeholder key (needs authoring)
  C) Migrated notices or comment-only placeholders that can be removed safely

Performs removal of Type C in-place on cleaned book and writes a markdown report.

Inputs:
  book/1022.2025.newbook.cleaned.md
Outputs:
  - Updated cleaned book (Type C removed)
  - tools/reports/placeholder-inventory-<ts>.md
"""
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import re

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / 'book' / '1022.2025.newbook.cleaned.md'
REPORTS = ROOT / 'tools' / 'reports'

PLACEHOLDER_KEY = 'Placeholder: migrated from book reference, please fill content.'
MIGRATED_NOTICE = 'Placeholder: migrated to part dir.'

HEAD_RE = re.compile(r'^(#{1,6})\s+(.*\S)\s*$')

def classify_and_clean(lines: list[str]):
    A = []  # heading placeholders (line index)
    B = []  # inline placeholders (line index)
    C = []  # removable notices or comment placeholders (line index)

    # Identify types
    for i, line in enumerate(lines):
        m = HEAD_RE.match(line.rstrip('\n'))
        if m:
            title = m.group(2).strip()
            if title == PLACEHOLDER_KEY:
                A.append(i)
                continue
        s = line.strip()
        if s == MIGRATED_NOTICE:
            C.append(i)
            continue
        # comment-only placeholders (non-heading), safe to drop
        if (s.startswith('//') or s.startswith('--')) and PLACEHOLDER_KEY in s:
            C.append(i)
            continue
        # inline placeholder occurrences (non-heading)
        if PLACEHOLDER_KEY in s:
            B.append(i)

    # Remove type C lines
    to_remove = set(C)
    new_lines = [ln for idx, ln in enumerate(lines) if idx not in to_remove]
    return A, B, C, new_lines

def main():
    if not BOOK.exists():
        raise SystemExit(f'Book not found: {BOOK}')
    raw = BOOK.read_text(encoding='utf-8')
    lines = raw.splitlines()
    A, B, C, cleaned = classify_and_clean(lines)

    # Write back
    BOOK.write_text('\n'.join(cleaned) + '\n', encoding='utf-8')

    ts = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    REPORTS.mkdir(parents=True, exist_ok=True)
    rep = REPORTS / f'placeholder-inventory-{ts}.md'
    rep.write_text('\n'.join([
        f'# Placeholder Inventory ({ts})',
        '',
        f'- Type A (heading placeholders): {len(A)}',
        f'- Type B (inline placeholders): {len(B)}',
        f'- Type C (removed notices/comments): {len(C)}',
        '',
        '## Type A samples (up to 20)',
        *[f'- line {i+1}' for i in A[:20]],
        '',
        '## Type B samples (up to 20)',
        *[f'- line {i+1}' for i in B[:20]],
        '',
        '## Type C removed lines (up to 20)',
        *[f'- line {i+1}' for i in C[:20]],
        ''
    ]), encoding='utf-8')
    print(f'Inventory done. A={len(A)} B={len(B)} C-removed={len(C)} | Report: {rep.name}')

if __name__ == '__main__':
    main()
