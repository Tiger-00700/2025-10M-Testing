#!/usr/bin/env python3
"""
Inventory references in the canonical book to examples/ and appendix/ assets.
- Default canonical: book/1208.2025.newbook.md (fallback to older variants if missing)
- Scans the chosen book for any references to paths containing
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
import os
from pathlib import Path
from datetime import datetime
from typing import Iterable, Set, List

import argparse

ROOT = Path(__file__).resolve().parents[1]
# Prefer the latest canonical book; allow older snapshots as fallback for compatibility
BOOK_PRIMARY = ROOT / 'book' / '1208.2025.newbook.md'
BOOK_LEGACY = ROOT / 'book' / '1022.2025.newbook.md'
BOOK_LEGACY_AUG = ROOT / 'book' / '1022.2025.newbook.augmented.md'
BOOK_LEGACY_CLEAN = ROOT / 'book' / '1022.2025.newbook.cleaned.md'
BOOK_LEGACY_FILLED = ROOT / 'book' / '1022.2025.newbook.filled.md'
BOOK_LEGACY_LINKS = ROOT / 'book' / '1022.2025.newbook.links.md'

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


def list_existing_assets(target_dirs: List[str]) -> Set[str]:
    existing: Set[str] = set()
    for base in target_dirs:
        base_path = ROOT / base
        if not base_path.exists():
            continue
        for p in base_path.rglob('*'):
            rel = p.relative_to(ROOT).as_posix()
            existing.add(rel)
        # Do not add the base directory itself; it is a container and not meaningful as an asset
    return existing


def expand_directories(refs: Iterable[str]) -> Set[str]:
    """If a referenced path is a directory, cover all children under it; otherwise cover the file.
    """
    expanded: Set[str] = set()
    for r in refs:
        rp = ROOT / r
        if rp.is_dir():
            # include dir and all descendants (files and directories)
            expanded.add(r)
            for p in rp.rglob('*'):
                expanded.add(p.relative_to(ROOT).as_posix())
        else:
            expanded.add(r)
    return expanded

def include_ancestor_dirs(paths: Iterable[str], target_dirs: List[str]) -> Set[str]:
    """For each covered path, also include its ancestor directories under targets to avoid
    falsely reporting container folders as 'unused'.
    """
    covered: Set[str] = set()
    for rel in paths:
        covered.add(rel)
        p = ROOT / rel
        # walk up until repo root or outside targets
        try:
            while True:
                p = p.parent
                if p == ROOT:
                    break
                relp = p.relative_to(ROOT).as_posix()
                # only include ancestors within target roots
                if relp.split('/', 1)[0] in target_dirs:
                    covered.add(relp)
                else:
                    break
        except Exception:
            # best-effort; ignore oddities
            pass
    return covered


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description='Inventory references in books to examples/ and appendix/.')
    ap.add_argument('--book', type=str, help='Override book file (path relative to repo root or absolute). Default: book/1208.2025.newbook.md')
    ap.add_argument('--only-canonical', action='store_true', help='Only consider canonical book (ignore links-only variant)')
    ap.add_argument('--targets', default='examples,appendix', help='Comma-separated list of top-level target dirs to include (default: examples,appendix)')
    args = ap.parse_args(argv)
    sources: List[Path] = []
    # Build candidate list in preferred order
    if args.book:
        user_path = Path(args.book)
        if not user_path.is_absolute():
            user_path = ROOT / user_path
        candidates = [user_path]
        links_candidate = None
    else:
        candidates = [BOOK_PRIMARY, BOOK_LEGACY, BOOK_LEGACY_AUG, BOOK_LEGACY_CLEAN, BOOK_LEGACY_FILLED]
        links_candidate = BOOK_LEGACY_LINKS
    # If only_canonical is requested, only consider the first candidate
    if args.only_canonical:
        candidates = candidates[:1]
        links_candidate = None
    # Pick first existing candidate(s)
    for c in candidates:
        if c.exists():
            sources.append(c)
            break
    # Still allow links-only variant to be included (as supplemental) unless only-canonical
    if not args.only_canonical and links_candidate and links_candidate.exists():
        if not sources or sources[0] != links_candidate:
            sources.append(links_candidate)
    if not sources:
        missing_list = [p.relative_to(ROOT).as_posix() for p in candidates]
        if links_candidate:
            missing_list.append(links_candidate.relative_to(ROOT).as_posix())
        print(f"ERROR: book file not found (tried): {missing_list}", file=sys.stderr)
        return 2

    refs: Set[str] = set()
    for src in sources:
        text = src.read_text(encoding='utf-8')
        refs.update(extract_references(text))

    target_dirs = [t.strip() for t in args.targets.split(',') if t.strip()]
    existing = list_existing_assets(target_dirs)

    # Compute present/missing and unused
    referenced_present = sorted([r for r in refs if (ROOT / r).exists()])
    referenced_missing = sorted([r for r in refs if not (ROOT / r).exists()])

    # Unused: everything existing under targets but not covered by any referenced item.
    # If a directory is referenced, treat all its children as covered.
    # Mark covered items: referenced dirs (recursively), referenced files, and ancestor dirs
    covered_raw = expand_directories(referenced_present)
    covered = include_ancestor_dirs(covered_raw, target_dirs)
    unused_existing = sorted([e for e in existing if e.split('/', 1)[0] in target_dirs and e not in covered])

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
    lines.append(f"Targets: {', '.join([t + '/' for t in target_dirs])}")
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
    # Fail CI if any referenced assets are missing (configurable via env INVENTORY_FAIL_ON_MISSING)
    fail_on_missing = True
    try:
        env_val = (os.environ.get('INVENTORY_FAIL_ON_MISSING') or '').strip()
        if env_val == '0' or env_val.lower() in ('false','no'):
            fail_on_missing = False
    except Exception:
        # best-effort; default to True
        pass

    if len(referenced_missing) > 0:
        msg = "ERROR: Referenced assets missing. See report above."
        if fail_on_missing:
            print(msg, file=sys.stderr)
            return 2
        else:
            print("WARNING: Referenced assets missing but INVENTORY_FAIL_ON_MISSING=0, continuing.")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
