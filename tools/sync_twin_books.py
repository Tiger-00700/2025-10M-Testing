#!/usr/bin/env python3
"""
Keep two book files in sync bidirectionally.

Default behavior: compare last modified times; copy newer file content to the older file if contents differ.

Usage:
  python tools/sync_twin_books.py [--force A|B]

Where:
  A = book/1022.2025.newbook.cleaned.md
  B = book/1030.2025.book.md

Writes a short report under tools/reports/.
"""
from __future__ import annotations
import argparse
import hashlib
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / 'book/1022.2025.newbook.cleaned.md'
B = ROOT / 'book/1030.2025.book.md'
REPORTS = ROOT / 'tools/reports'

def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--force', choices=['A','B'], help='Force copy direction: A->B or B->A')
    args = ap.parse_args(argv)

    REPORTS.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    out = REPORTS / f'sync-books-{ts}.md'

    lines = []
    lines.append(f'# Twin Books Sync Report ({ts})')
    lines.append('')
    lines.append(f'- A: {A.as_posix()}')
    lines.append(f'- B: {B.as_posix()}')
    lines.append('')

    if not A.exists() or not B.exists():
        lines.append('ERROR: One or both files are missing.')
        out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
        print(f'Report written: {out}')
        return 2

    ha, hb = sha256(A), sha256(B)
    if ha == hb:
        lines.append('- Status: Already in sync (identical content).')
        out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
        print(f'Report written: {out}')
        return 0

    if args.force == 'A':
        src, dst, dir_label = A, B, 'A->B'
    elif args.force == 'B':
        src, dst, dir_label = B, A, 'B->A'
    else:
        # Auto: newer mtime wins
        ma = A.stat().st_mtime
        mb = B.stat().st_mtime
        if ma >= mb:
            src, dst, dir_label = A, B, 'A->B (mtime)'
        else:
            src, dst, dir_label = B, A, 'B->A (mtime)'

    dst.write_text(src.read_text(encoding='utf-8'), encoding='utf-8')
    lines.append(f'- Action: Copied {dir_label}')
    lines.append(f'  - src_sha: {sha256(src)}')
    lines.append(f'  - dst_sha: {sha256(dst)}')
    out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'Report written: {out}')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
