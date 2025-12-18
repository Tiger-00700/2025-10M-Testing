#!/usr/bin/env python3
"""Compare framework/第N篇 files to the corresponding blocks in book/1208.2025.newbook.update.md
Outputs a per-篇 report: identical / differs, line counts, placeholder flags, and `12.16建议` counts.
"""
import difflib
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
BOOK = ROOT / 'book' / '1208.2025.newbook.update.md'
FRAMEWORK = ROOT / 'framework'

def read(p: Path):
    return p.read_text(encoding='utf-8')

def find_block(book_text, i):
    # Match markers like <!-- BEGIN 第1篇 --> with optional spaces
    import re
    bm = re.compile(r"<!--\s*BEGIN\s*第" + str(i) + r"篇\s*-->")
    em = re.compile(r"<!--\s*END\s*第" + str(i) + r"篇\s*-->")
    mb = bm.search(book_text)
    me = em.search(book_text)
    if not mb or not me:
        return None
    return book_text[mb.end():me.start()]

def normalize(text):
    # Normalize line endings and strip trailing spaces
    lines = [ln.rstrip() for ln in text.replace('\r\n','\n').split('\n')]
    # drop leading/trailing blank lines
    while lines and lines[0].strip()=='' : lines.pop(0)
    while lines and lines[-1].strip()=='' : lines.pop()
    return '\n'.join(lines)

report = []
book_text = read(BOOK)
for i in range(1,8):
    fr_file = FRAMEWORK / f'第{i}篇-{'入门篇' if i==1 else '进阶篇' if i in [2,3,4] else '专家篇'}-'.encode() if False else FRAMEWORK.glob(f'第{i}篇*.md')

# Slightly different approach: find the framework file by matching '第{i}篇' prefix
from glob import glob
for i in range(1,8):
    matches = list(FRAMEWORK.glob(f'第{i}篇*.md'))
    if not matches:
        report.append((i, 'missing_framework_file', None))
        continue
    fr_path = matches[0]
    fr_text = read(fr_path)
    block = find_block(book_text, i)
    n_fr = len(fr_text.splitlines())
    norm_fr = normalize(fr_text)
    norm_book = normalize(book_text)
    if block is not None:
        n_block = len(block.splitlines())
        norm_block = normalize(block)
        identical = norm_fr == norm_block
        diff = list(difflib.unified_diff(norm_fr.splitlines(), norm_block.splitlines(), lineterm=''))
        markers_found = True
    else:
        # fallback: check if framework content is included somewhere in the book
        included = norm_fr in norm_book
        identical = included
        n_block = len(norm_book.splitlines())
        diff = []
        markers_found = False
    # placeholders (use empty string if block is None)
    placeholders = []
    block_for_checks = block or ''
    if re.search(r'\btruncated\b', block_for_checks, re.I) or 'content truncated' in block_for_checks:
        placeholders.append('truncated')
    if '<THE FULL CONTENT' in block_for_checks or '（已完整插入' in block_for_checks or '（已完整插入' in block_for_checks:
        placeholders.append('completion-note')
    if '（余下' in block_for_checks or '余下內容省略' in block_for_checks or '（余下内容省略）' in block_for_checks:
        placeholders.append('ellipsis')
    if 'content truncated' in block_for_checks:
        placeholders.append('content-truncated')
    # count suggestions
    suggest_count_fr = len(re.findall(r'12\.16建议', fr_text))
    # If block is None but the framework text is included somewhere, extract that region from the book for checks
    if block is None and (norm_fr in norm_book):
        start = norm_book.find(norm_fr)
        end = start + len(norm_fr)
        book_region = norm_book[start:end]
    else:
        book_region = block_for_checks
    suggest_count_block = len(re.findall(r'12\.16建议', book_region))
    # also check placeholders in the matched book region
    if 'truncated' in book_region.lower() or 'content truncated' in book_region.lower():
        if 'truncated' not in placeholders:
            placeholders.append('truncated')
    if '（已完整插入' in book_region or '<THE FULL CONTENT' in book_region:
        if 'completion-note' not in placeholders:
            placeholders.append('completion-note')
    normalized_contains = (norm_fr in norm_book)
    if identical:
        status = 'identical'
    elif not markers_found and normalized_contains:
        status = 'included_without_markers'
    else:
        status = 'differs'
    report.append((i, status, fr_path.name, n_fr, n_block, placeholders, suggest_count_fr, suggest_count_block, diff[:20], markers_found))

# Print report
for r in report:
    if r[1] in ('missing_framework_file','missing_block_in_book'):
        if r[1]=='missing_framework_file':
            print(f'第{r[0]}篇: framework file not found')
        else:
            print(f'第{r[0]}篇: BEGIN/END block not found in book (expected file {r[2]})')
        continue
    idx, status, fname, n_fr, n_block, placeholders, sc_fr, sc_block, diffs, markers_found = r
    print(f'第{idx}篇 ({fname}): {status}')
    print(f'  framework lines: {n_fr}, book block lines or book total lines used for comparison: {n_block}')
    print(f'  markers present: {markers_found}')
    if placeholders:
        print(f'  placeholders found in book block: {placeholders}')
    print(f'  12.16建议 counts - framework: {sc_fr}, book: {sc_block}')
    if status != 'identical' and diffs:
        print('  Diff snippet (up to 20 lines):')
        for d in diffs:
            print('   ', d)
    print()

# Exit code

