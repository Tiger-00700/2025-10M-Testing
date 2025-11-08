#!/usr/bin/env python3
"""Prune intermediate book markdown files, keeping only designated artifacts.

Keeps:
  - 1022.2025.newbook.augmented.frozen.md
  - 1022.2025.newbook.merged.md
  - 1022.2025.newbook.cleaned.md
  - 1030.2025.book.md
Also preserves any appendix files (prefix '附录-') and non-book template/support files.

Deletes other top-level book/*.md that match 1022.2025.* or 1030.2025.* and are not in keep set.
Writes a report in tools/reports/prune-books-<ts>.md listing deleted/skipped files.
"""
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
BOOK_DIR = ROOT / 'book'
KEEP = {
    '1022.2025.newbook.augmented.frozen.md',
    '1022.2025.newbook.merged.md',
    '1022.2025.newbook.cleaned.md',
    '1030.2025.book.md',
}

def is_appendix(name: str) -> bool:
    return name.startswith('附录-')

def is_candidate(p: Path) -> bool:
    if p.is_dir():
        return False
    if p.name in KEEP:
        return False
    if is_appendix(p.name):
        return False
    # Only prune top-level numbered book variants
    return (p.name.startswith('1022.2025') or p.name.startswith('1030.2025')) and p.suffix == '.md'

def main() -> int:
    ts = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    reports = ROOT / 'tools' / 'reports'
    reports.mkdir(parents=True, exist_ok=True)
    report = reports / f'prune-books-{ts}.md'
    lines = [f'# Prune Book Files Report ({ts})', '', '## Keep Set', '']
    for k in sorted(KEEP):
        lines.append(f'- {k}')
    lines.append('')
    deleted = 0
    skipped = 0
    for p in sorted(BOOK_DIR.glob('*.md')):
        if is_candidate(p):
            p.unlink()
            deleted += 1
            lines.append(f'Deleted: {p.name}')
        else:
            skipped += 1
    lines.append('')
    lines.append(f'Total deleted: {deleted}')
    lines.append(f'Total preserved/skipped: {skipped}')
    report.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'Prune report written: {report}')
    print(f'Deleted={deleted} Preserved={skipped}')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
