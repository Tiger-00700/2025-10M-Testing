#!/usr/bin/env python3
"""
Strip merge scaffolding from the cleaned book:
 - Remove sections titled 'A 专有段落（供筛选）' or 'B 专有段落（供筛选）' with their content
 - Compress MERGED markers: replace 'MERGED-BEGIN ...' with a single '<!-- merged: ... -->'
   and remove the closing 'MERGED-END' lines

Input:  book/1022.2025.newbook.cleaned.md (in-place)
Report: tools/reports/strip-merge-scaffolding-<ts>.md
"""
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import re

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / 'book' / '1022.2025.newbook.cleaned.md'
REPORTS = ROOT / 'tools' / 'reports'

HEAD_RE = re.compile(r'^(#{1,6})\s+(.*\S)\s*$')
MERGED_BEGIN_RE = re.compile(r'^<!--\s*MERGED-BEGIN\s+(.*)-->\s*$')
MERGED_END_RE = re.compile(r'^<!--\s*MERGED-END\s*-->\s*$')

def strip_scaffolding(lines: list[str]):
    out = []
    removed_blocks = 0
    removed_end = 0
    replaced_begin = 0

    # First pass: remove A/B 专有段落 blocks
    i = 0
    while i < len(lines):
        line = lines[i]
        m = HEAD_RE.match(line)
        if m and m.group(2).strip() in ('A 专有段落（供筛选）','B 专有段落（供筛选）'):
            # remove until next heading of same or higher level
            lvl = len(m.group(1))
            j = i + 1
            while j < len(lines):
                mm = HEAD_RE.match(lines[j])
                if mm and len(mm.group(1)) <= lvl:
                    break
                j += 1
            removed_blocks += 1
            i = j
            continue
        out.append(line)
        i += 1

    # Second pass: compress MERGED markers
    final = []
    for ln in out:
        mb = MERGED_BEGIN_RE.match(ln)
        if mb:
            final.append(f'<!-- merged: {mb.group(1)} -->')
            replaced_begin += 1
            continue
        if MERGED_END_RE.match(ln):
            removed_end += 1
            continue
        final.append(ln)

    return final, removed_blocks, replaced_begin, removed_end

def main():
    if not BOOK.exists():
        raise SystemExit(f'Book not found: {BOOK}')
    raw = BOOK.read_text(encoding='utf-8')
    lines = raw.splitlines()
    new_lines, rm_blocks, rep_begin, rm_end = strip_scaffolding(lines)
    BOOK.write_text('\n'.join(new_lines) + '\n', encoding='utf-8')
    ts = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    REPORTS.mkdir(parents=True, exist_ok=True)
    rep = REPORTS / f'strip-merge-scaffolding-{ts}.md'
    rep.write_text('\n'.join([
        f'# Strip merge scaffolding ({ts})',
        '',
        f'- Removed A/B 专有段落 blocks: {rm_blocks}',
        f'- Replaced MERGED-BEGIN -> merged: {rep_begin}',
        f'- Removed MERGED-END: {rm_end}',
        ''
    ]), encoding='utf-8')
    print(f'Stripped scaffolding. blocks={rm_blocks} begin->merged={rep_begin} end-removed={rm_end} | Report: {rep.name}')

if __name__ == '__main__':
    main()
