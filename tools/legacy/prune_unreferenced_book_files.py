#!/usr/bin/env python3
"""Prune /book/*.md files not referenced by the frozen canonical book.

Canonical source: book/1022.2025.newbook.augmented.frozen.md

Keeps always:
  - 1022.2025.newbook.augmented.frozen.md (canonical)
  - 1022.2025.newbook.merged.md (audit)
  - 1022.2025.newbook.cleaned.md (current release)
  - 1030.2025.book.md (twin)
  - Any file starting with '附录-' (appendix assets)
  - Directories (not touched)

Reference heuristic (STRICT):
    A book file X is considered referenced ONLY if it is the target of a Markdown link
    in the frozen book (e.g., [text](book/1030.2025.book.md) or [text](../book/1030.2025.book.md)
    or [text](1030.2025.book.md)). We compare by filename (last path segment) equality.

Outputs report: tools/reports/prune-unreferenced-book-<ts>.md listing kept, deleted, and reasons.
"""
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import re

ROOT = Path(__file__).resolve().parents[1]
BOOK_DIR = ROOT / 'book'
FROZEN = BOOK_DIR / '1022.2025.newbook.augmented.frozen.md'
KEEP_ALWAYS = {
    '1022.2025.newbook.augmented.frozen.md',
    '1022.2025.newbook.merged.md',
    '1022.2025.newbook.cleaned.md',
    '1030.2025.book.md',
}

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")

def load_frozen() -> str:
    return FROZEN.read_text(encoding='utf-8') if FROZEN.exists() else ''

def extract_link_book_filenames(text: str) -> set[str]:
    names: set[str] = set()
    for m in LINK_RE.finditer(text or ''):
        target = m.group(1).strip()
        # Strip anchors/query
        target = target.split('#', 1)[0].split('?', 1)[0]
        # Skip URLs and mailto
        if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', target):
            continue
        t = target.replace('\\', '/').strip()
        parts = [p for p in t.split('/') if p]
        if 'book' not in parts:
            continue
        # Get last path segment as filename
        from pathlib import Path as _P
        name = _P(t).name
        if name:
            names.add(name)
    return names

def referenced(link_names: set[str], name: str) -> bool:
    # Strict rule: filename must appear as the link target's last segment
    return name in link_names

def main() -> int:
    if not FROZEN.exists():
        print('Frozen book missing; abort.')
        return 2
    frozen_text = load_frozen()
    link_names = extract_link_book_filenames(frozen_text)
    ts = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    reports = ROOT / 'tools' / 'reports'
    reports.mkdir(parents=True, exist_ok=True)
    report = reports / f'prune-unreferenced-book-{ts}.md'
    lines = [f'# Prune Unreferenced Book Files Report ({ts})', '']
    lines.append('## Always-kept baseline files')
    for k in sorted(KEEP_ALWAYS):
        lines.append(f'- {k}')
    lines.append('')
    deleted = []
    kept = []
    for p in sorted(BOOK_DIR.glob('*.md')):
        name = p.name
        if name in KEEP_ALWAYS or name.startswith('附录-'):
            kept.append((name, 'baseline/appendix'))
            continue
        # Decide by reference heuristic
        if referenced(link_names, name):
            kept.append((name, 'referenced'))
        else:
            p.unlink()
            deleted.append(name)
    if deleted:
        lines.append('## Deleted (unreferenced)')
        for d in deleted:
            lines.append(f'- {d}')
        lines.append('')
    lines.append('## Kept (reason)')
    for name, reason in kept:
        lines.append(f'- {name} ({reason})')
    lines.append('')
    lines.append(f'Total deleted: {len(deleted)}')
    lines.append(f'Total kept: {len(kept)}')
    report.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'Report written: {report}')
    print(f'Deleted={len(deleted)} Kept={len(kept)}')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
