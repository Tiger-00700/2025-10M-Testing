#!/usr/bin/env python3
from pathlib import Path
import re
import sys

BOOK = Path('book/1022.2025.newbook.cleaned.new.md')
PART_RE = re.compile(r'^##\s*第([一二三四五六1-6])篇')
MAP = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'1':1,'2':2,'3':3,'4':4,'5':5,'6':6}

def main():
    if not BOOK.exists():
        print(f'File not found: {BOOK}', file=sys.stderr)
        raise SystemExit(2)
    lines = BOOK.read_text(encoding='utf8').splitlines()
    positions = []
    for i,L in enumerate(lines):
        m = PART_RE.match(L)
        if m:
            n = MAP[m.group(1)]
            positions.append((i,n))
    if not positions:
        print('No part headings found', file=sys.stderr)
        raise SystemExit(1)
    positions.sort(key=lambda x: x[0])
    # compute lengths
    parts = {}
    for idx,(start, num) in enumerate(positions):
        end = positions[idx+1][0] if idx+1 < len(positions) else len(lines)
        parts[num] = end - start
    missing = [n for n in range(1,7) if n not in parts]
    if missing:
        print(f'Missing parts: {missing}', file=sys.stderr)
        raise SystemExit(1)
    for n in range(1,7):
        length = parts[n]
        status = 'OK' if length > 50 else 'SHORT'
        print(f'Part {n}: {length} lines [{status}]')
    if any(parts[n] <= 50 for n in range(1,7)):
        raise SystemExit(1)

if __name__ == '__main__':
    main()
