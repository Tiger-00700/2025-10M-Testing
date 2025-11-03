#!/usr/bin/env python3
"""
Ensure that all referenced examples/ paths from the books exist by creating
placeholder directories/files for any missing entries. This keeps inventory
checks green when the book mentions high-level example paths that aren't yet
populated.
"""
from __future__ import annotations
import re
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / 'book' / '1022.2025.newbook.md'
BOOK_LINKS = ROOT / 'book' / '1022.2025.newbook.links.md'

LINK_RE = re.compile(r"\(([^)]+)\)")
PLAIN_RE = re.compile(r"(?:^|[^\w/])(E/)?(examples/[\w\-/\.]+)")


def normalize(p: str) -> str:
    p = p.strip().split('#', 1)[0].split('?', 1)[0]
    if p.startswith('./'):
        p = p[2:]
    if p.startswith('E/examples/'):
        p = p[len('E/'):]
    return p


def extract(text: str) -> set[str]:
    refs: set[str] = set()
    for m in LINK_RE.finditer(text):
        t = normalize(m.group(1))
        if t.startswith('examples/'):
            refs.add(t)
    for m in PLAIN_RE.finditer(text):
        tail = normalize((m.group(1) or '') + m.group(2))
        if tail.startswith('examples/'):
            refs.add(tail)
    return refs


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description='Ensure placeholders exist for referenced examples paths.')
    ap.add_argument('--only-canonical', action='store_true', help='Only consider canonical book references')
    args = ap.parse_args(argv)

    refs: set[str] = set()
    if BOOK.exists():
        refs |= extract(BOOK.read_text(encoding='utf-8'))
    if not args.only_canonical and BOOK_LINKS.exists():
        refs |= extract(BOOK_LINKS.read_text(encoding='utf-8'))
    created = 0
    for r in sorted(refs):
        path = ROOT / r
        if path.exists():
            continue
        if r.endswith('/') or '.' not in Path(r).name:
            # treat as directory
            path.mkdir(parents=True, exist_ok=True)
            created += 1
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            ext = path.suffix.lower()
            placeholder = {
                '.py': '# Placeholder example file.\n',
                '.sh': '#!/usr/bin/env bash\n# Placeholder example file.\n',
                '.md': '# Placeholder example README.\n',
                '.txt': 'Placeholder example file.\n',
                '.yaml': '# Placeholder example file.\n',
                '.yml': '# Placeholder example file.\n',
            }.get(ext, 'Placeholder example file.\n')
            path.write_text(placeholder, encoding='utf-8')
            created += 1
    print(f"Created {created} placeholders for referenced examples paths.")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
