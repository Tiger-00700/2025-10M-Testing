#!/usr/bin/env python3
"""
Normalize/validate headings and emit a report for the cleaned book.

Checks:
 - Level jumps > 1 (e.g., H2 -> H4)
 - Trailing spaces in heading titles
 - Duplicate adjacent headings (same level and title)
 - Headings that are placeholders
 - Titles with suspicious punctuation spacing

Input:  book/1022.2025.newbook.cleaned.md
Report: tools/reports/heading-normalization-<ts>.md
Exit 0 always (report-only).
"""
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import re

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / 'book' / '1022.2025.newbook.cleaned.md'
REPORTS = ROOT / 'tools' / 'reports'

HEAD_RE = re.compile(r'^(#{1,6})\s+(.*\S)\s*$')
PLACEHOLDER_KEY = 'Placeholder: migrated from book reference, please fill content.'

def analyze(lines: list[str]):
    # Provide an explicit type for issues to satisfy var-annotated checks
    issues: dict[str, list] = {
        'level_jumps': [],
        'trailing_spaces': [],
        'duplicate_adjacent': [],
        'placeholder_headings': [],
        'punctuation_spacing': [],
    }
    prev_level = None
    prev_title = None
    for i, line in enumerate(lines, start=1):
        m = HEAD_RE.match(line)
        if not m:
            continue
        level = len(m.group(1))
        title = m.group(2)
        # level jump
        if prev_level is not None and (level - prev_level) > 1:
            issues['level_jumps'].append((i, prev_level, level, title))
        # trailing spaces (already stripped by regex end), re-check raw
        if line.rstrip('\n').endswith(' '):
            issues['trailing_spaces'].append((i, title))
        # duplicate adjacent
        if prev_level == level and prev_title == title:
            issues['duplicate_adjacent'].append((i, level, title))
        # placeholder heading
        if title == PLACEHOLDER_KEY:
            issues['placeholder_headings'].append((i, level))
        # punctuation spacing: simple heuristic - spaces before Chinese colon
        if ' :' in title or ' ：' in title:
            issues['punctuation_spacing'].append((i, title))

    prev_level, prev_title = level, title
    return issues

def main():
    if not BOOK.exists():
        raise SystemExit(f'Book not found: {BOOK}')
    raw = BOOK.read_text(encoding='utf-8')
    lines = raw.splitlines()
    issues = analyze(lines)
    ts = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    REPORTS.mkdir(parents=True, exist_ok=True)
    rep = REPORTS / f'heading-normalization-{ts}.md'
    out = [f'# Heading normalization report ({ts})','']
    def emit(title, arr, fmt):
        out.append(f'## {title} ({len(arr)})')
        if not arr:
            out.append('- None')
            out.append('')
            return
        for item in arr[:200]:
            out.append(fmt(item))
        if len(arr) > 200:
            out.append(f'- ... ({len(arr)-200} more)')
        out.append('')

    emit('Level jumps > 1', issues['level_jumps'], lambda x: f'- line {x[0]}: prev={x[1]} -> now={x[2]} | {x[3]}')
    emit('Trailing spaces in headings', issues['trailing_spaces'], lambda x: f'- line {x[0]}: {x[1]}')
    emit('Duplicate adjacent headings', issues['duplicate_adjacent'], lambda x: f'- line {x[0]}: H{x[1]} {x[2]}')
    emit('Placeholder headings', issues['placeholder_headings'], lambda x: f'- line {x[0]}: H{x[1]}')
    emit('Suspicious punctuation spacing', issues['punctuation_spacing'], lambda x: f'- line {x[0]}: {x[1]}')

    rep.write_text('\n'.join(out)+'\n', encoding='utf-8')
    print(f'Heading normalization report written: {rep.name}')

if __name__ == '__main__':
    main()
