#!/usr/bin/env python3
"""Produce per-chapter unified diffs between framework files and book blocks.
Prints up to a configurable number of diff lines per chapter.
"""
from pathlib import Path
import difflib
import re

ROOT = Path(__file__).resolve().parent.parent
BOOK = ROOT / 'book' / '1208.2025.newbook.update.md'
FRAMEWORK = ROOT / 'framework'
MAX_LINES = 200

text = BOOK.read_text(encoding='utf-8')

# helper to extract block between markers
def extract_block(text, i):
    bm = re.compile(r"<!--\s*BEGIN\s*第" + str(i) + r"篇\s*-->")
    em = re.compile(r"<!--\s*END\s*第" + str(i) + r"篇\s*-->")
    mb = bm.search(text)
    me = em.search(text)
    if not mb or not me:
        return None
    return text[mb.end():me.start()]

# normalize: strip trailing spaces, normalize line endings, strip leading/trailing blank lines
def normalize(s):
    lines = [ln.rstrip() for ln in s.replace('\r\n','\n').split('\n')]
    while lines and lines[0].strip()=='' : lines.pop(0)
    while lines and lines[-1].strip()=='' : lines.pop()
    return '\n'.join(lines) + '\n'

summary = []
for i in range(1,8):
    matches = list(FRAMEWORK.glob(f'第{i}篇*.md'))
    if not matches:
        print(f'第{i}篇: Framework file not found')
        summary.append((i, 'missing_framework'))
        continue
    fr_path = matches[0]
    fr_text = fr_path.read_text(encoding='utf-8')
    block = extract_block(text, i)
    if block is None:
        print(f'第{i}篇: BEGIN/END block not found in book')
        summary.append((i, 'missing_block'))
        continue
    norm_fr = normalize(fr_text)
    norm_block = normalize(block)
    if norm_fr == norm_block:
        print(f'第{i}篇: IDENTICAL (no differences)')
        summary.append((i, 'identical'))
        continue
    diff = list(difflib.unified_diff(norm_fr.splitlines(), norm_block.splitlines(), lineterm=''))
    print(f'--- 第{i}篇 差异（unified diff） - framework: {fr_path.name} ---')
    print(f'Framework lines: {len(norm_fr.splitlines())}, Book block lines: {len(norm_block.splitlines())}')
    print(f'Diff total lines: {len(diff)}')
    to_show = diff[:MAX_LINES]
    for line in to_show:
        print(line)
    if len(diff) > MAX_LINES:
        print(f'...（已截断，省略 {len(diff)-MAX_LINES} 行）')
    print('\n')
    summary.append((i, 'diff', len(diff)))

# summary
print('Summary:')
for r in summary:
    print(r)

# exit

