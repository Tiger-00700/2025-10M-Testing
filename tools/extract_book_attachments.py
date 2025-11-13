#!/usr/bin/env python3
"""Extract augment code blocks from the cleaned book into example files and replace them with links.

Behavior:
- Finds patterns like:
    > Source: path\to\file

  <!-- augment:code -->
  ```lang
  ...code...
  ```

- Writes the code to the target path under the repo root (converting backslashes to posix).
  If the file already exists, it will not overwrite unless --overwrite is provided.
- Replaces the whole augment/code fence block in the book with a link to the example file:
    [示例附件: examples/...](../examples/...)

Usage: run from repo root.
"""
from __future__ import annotations
import re
from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / 'book' / '1022.2025.newbook.cleaned.md'
EXAMPLES = ROOT / 'examples'

AUGMENT_RE = re.compile(
    r"^>\s*Source:\s*(?P<source>.+?)\s*$"  # Source line starting with >
    r"\s*\n\s*<!--\s*augment:code\s*-->\s*\n"  # augment marker
    r"```(?P<lang>[^\n]*)\n(?P<code>.*?)\n```\s*\n?",
    re.MULTILINE | re.DOTALL,
)


def ensure_parent(path: Path):
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)


def normalize_src(s: str) -> str:
    # Convert backslashes to posix and strip
    return s.strip().replace('\\', '/').lstrip('./\\')


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--overwrite', action='store_true', help='Overwrite existing example files')
    args = ap.parse_args(argv)

    text = BOOK.read_text(encoding='utf-8')
    matches = list(AUGMENT_RE.finditer(text))
    if not matches:
        print('No augment code blocks with Source: found in book.')
        return 0

    new_text = []
    last_end = 0
    created = []

    for m in matches:
        start, end = m.span()
        new_text.append(text[last_end:start])
    src_raw = m.group('source')
    _lang = m.group('lang').strip()
        code = m.group('code')
        src_norm = normalize_src(src_raw)
        target = ROOT / src_norm
        # If the source path is not under examples/, and is a relative path, default to examples/
        if not src_norm.startswith('examples/'):
            # allow some appendix or other paths; place under examples/book_extracted/ for safety
            target = EXAMPLES / 'book_extracted' / src_norm
        ensure_parent(target)
        if target.exists() and not args.overwrite:
            print(f'Skipping existing {target}')
        else:
            target.write_text(code, encoding='utf-8')
            created.append(str(target.relative_to(ROOT)))
            print(f'Wrote {target}')
        # Build replacement link relative to book file: book/ -> examples/ is ../examples/...
        rel_link = Path('..') / Path(src_norm)
        # If we wrote into examples/book_extracted, adjust link accordingly
        if not src_norm.startswith('examples/'):
            rel_link = Path('..') / Path('examples') / 'book_extracted' / Path(src_norm)
        link_md = f"[示例附件: {src_norm}]({rel_link.as_posix()})\n"
        new_text.append(link_md)
        last_end = end

    new_text.append(text[last_end:])
    out = ''.join(new_text)
    backup = BOOK.with_suffix('.cleaned.extracted.bak')
    BOOK.rename(backup)
    BOOK.write_text(out, encoding='utf-8')
    print(f'Book updated, backup saved to: {backup}')
    if created:
        print('Created files:')
        for c in created:
            print(' -', c)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
