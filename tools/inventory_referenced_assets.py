#!/usr/bin/env python3
"""
Inventory references in the canonical book to examples/ and appendix/ assets.
- Scans book/1022.2025.newbook.md for any references to paths containing
  'examples/' or 'appendix/' (also supports 'E/examples/' prefix in text)
- Normalizes to repo-root-relative paths (E/examples -> examples)
- Lists actual filesystem contents under examples/ and appendix/
- Produces a markdown report with:
  - Referenced present
  - Referenced missing
  - Existing but unreferenced (files/dirs)
Outputs to: tools/reports/inventory-assets-YYYYMMDD-HHMMSS.md
"""
from __future__ import annotations
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Iterable, Set

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / 'book' / '1022.2025.newbook.md'
BOOK_LINKS = ROOT / 'book' / '1022.2025.newbook.links.md'
TARGET_DIRS = ['examples', 'appendix']

# Match markdown links/images and plain-text path mentions
# Examples:
# - [link](examples/03_environment/foo.md)
# - ![](appendix/2-7__block1.py)
# - 最小实操路径：附录 E/examples/03_environment
# We capture paths that start with (E/)?examples/ or appendix/
PATH_CHARS = r"[\w\-/\.]+"
LINK_RE = re.compile(r"\(([^)]+)\)")
PLAIN_RE = re.compile(rf"(?:^|[^\w/])(E/)?(examples/{PATH_CHARS}|appendix/{PATH_CHARS})")


def normalize_path(p: str) -> str:
    p = p.strip()
    # strip anchors and queries
    p = p.split('#', 1)[0].split('?', 1)[0]
    # remove leading ./ or / if present (treat as repo-root relative when starting with examples/ or appendix/)
    if p.startswith('./'):
        p = p[2:]
    if p.startswith('E/examples/'):
        p = p[len('E/'):]  # -> examples/
    return p


def extract_references(text: str) -> Set[str]:
    refs: Set[str] = set()
    # 1) from markdown links/images (...) content
    for m in LINK_RE.finditer(text):
        target = m.group(1).strip()
        if 'examples/' in target or 'appendix/' in target or 'E/examples/' in target:
            p = normalize_path(target)
            # Only keep if path starts with desired prefixes after normalization
            if p.startswith('examples/') or p.startswith('appendix/'):
                refs.add(p)
    # 2) from plain text occurrences
    for m in PLAIN_RE.finditer(text):
        _e_prefix = m.group(1) or ''
        tail = m.group(2)
        p = normalize_path(_e_prefix + tail)
        if p.startswith('examples/99_book_exports'):
            # Skip plain-text matches for nested exports (only trust markdown links)
            continue
        if p.startswith('examples/') or p.startswith('appendix/'):
            refs.add(p)
    return refs


def list_existing_assets() -> Set[str]:
    existing: Set[str] = set()
    for base in TARGET_DIRS:
        base_path = ROOT / base
        if not base_path.exists():
            continue
        for p in base_path.rglob('*'):
            rel = p.relative_to(ROOT).as_posix()
            existing.add(rel)
        # also add the base directory itself
        existing.add(base_path.relative_to(ROOT).as_posix())
    return existing


def expand_directories(refs: Iterable[str]) -> Set[str]:
    # If a referenced path is a directory, cover all children under it
    expanded: Set[str] = set()
    for r in refs:
        rp = ROOT / r
        if rp.is_dir():
            # include dir and all descendants
            expanded.add(r)
            for p in rp.rglob('*'):
                expanded.add(p.relative_to(ROOT).as_posix())
        else:
            expanded.add(r)
    return expanded


def main() -> int:
    sources = []
    if BOOK.exists():
        sources.append(BOOK)
    else:
        print(f"ERROR: book file not found: {BOOK}", file=sys.stderr)
        return 2
    # If links-only variant exists, include it as well
    if BOOK_LINKS.exists():
        sources.append(BOOK_LINKS)

    refs: Set[str] = set()
    for src in sources:
        text = src.read_text(encoding='utf-8')
        refs.update(extract_references(text))

    existing = list_existing_assets()

    # Compute present/missing and unused
    referenced_present = sorted([r for r in refs if (ROOT / r).exists()])
    referenced_missing = sorted([r for r in refs if not (ROOT / r).exists()])

    # Unused: everything existing under targets but not covered by any referenced item.
    # If a directory is referenced, treat all its children as covered.
    covered = expand_directories(referenced_present)
    unused_existing = sorted([e for e in existing if e.split('/', 1)[0] in TARGET_DIRS and e not in covered])

    # Write report
    reports_dir = ROOT / 'tools' / 'reports'
    reports_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d-%H%M%S')
    out = reports_dir / f'inventory-assets-{ts}.md'

    lines = []
    lines.append(f"# Referenced Assets Inventory ({ts})")
    lines.append("")
    if len(sources) == 1:
        lines.append(f"Source: {sources[0].relative_to(ROOT).as_posix()}")
    else:
        lines.append("Sources:")
        for s in sources:
            lines.append(f"- {s.relative_to(ROOT).as_posix()}")
    lines.append(f"Targets: examples/, appendix/")
    lines.append("")
    lines.append(f"- Total references found: {len(refs)}")
    lines.append(f"- Present: {len(referenced_present)}")
    lines.append(f"- Missing: {len(referenced_missing)}")
    lines.append(f"- Existing but unreferenced: {len(unused_existing)}")
    lines.append("")

    if referenced_present:
        lines.append("## ✅ Referenced & Present")
        for p in referenced_present:
            lines.append(f"- {p}")
        lines.append("")
    if referenced_missing:
        lines.append("## ❌ Referenced but Missing")
        for p in referenced_missing:
            lines.append(f"- {p}")
        lines.append("")
    # Note: to避免噪音，默认不展开未引用清单（依然计数并保留在摘要里）

    out.write_text('\n'.join(lines), encoding='utf-8')
    print(f"Report written: {out}")
    print(f"References: {len(refs)}, Present: {len(referenced_present)}, Missing: {len(referenced_missing)}, Unused: {len(unused_existing)}")
    # Fail CI if any referenced assets are missing
    if len(referenced_missing) > 0:
        print("ERROR: Referenced assets missing. See report above.", file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
