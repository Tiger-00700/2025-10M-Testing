#!/usr/bin/env python3
"""
Prune unused assets under examples/ and appendix/ based on book references.

- Recomputes referenced assets using the same rules as inventory_referenced_assets.py
- Determines the set of existing-but-unreferenced assets (files only by default)
- Supports dry-run, moving to a trash folder, or permanent delete
 - Optional filters by extension and by path substring

Usage examples:
  python tools/prune_unused_assets.py --dry-run
  python tools/prune_unused_assets.py --ext .png,.jpg --move
  python tools/prune_unused_assets.py --delete --confirm "examples/preview"

Output:
  Prints counts and groups by extension; when moving, places files under tools/trash/<timestamp>/...
"""
from __future__ import annotations
import argparse
from pathlib import Path
from datetime import datetime
import re
import shutil
from typing import Iterable, Set, List, Dict

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / 'book' / '1022.2025.newbook.md'
BOOK_LINKS = ROOT / 'book' / '1022.2025.newbook.links.md'

PATH_CHARS = r"[\w\-/\.]+"
LINK_RE = re.compile(r"\(([^)]+)\)")
PLAIN_RE = re.compile(rf"(?:^|[^\w/])(E/)?(examples/{PATH_CHARS}|appendix/{PATH_CHARS})")


def normalize_path(p: str) -> str:
    p = p.strip()
    p = p.split('#', 1)[0].split('?', 1)[0]
    if p.startswith('./'):
        p = p[2:]
    if p.startswith('E/examples/'):
        p = p[len('E/'):]
    return p


def extract_references(text: str) -> Set[str]:
    refs: Set[str] = set()
    for m in LINK_RE.finditer(text):
        target = m.group(1).strip()
        if 'examples/' in target or 'appendix/' in target or 'E/examples/' in target:
            p = normalize_path(target)
            if p.startswith('examples/') or p.startswith('appendix/'):
                refs.add(p)
    for m in PLAIN_RE.finditer(text):
        _e_prefix = m.group(1) or ''
        tail = m.group(2)
        p = normalize_path(_e_prefix + tail)
        if p.startswith('examples/99_book_exports'):
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
            existing.add(p.relative_to(ROOT).as_posix())
        existing.add(base_path.relative_to(ROOT).as_posix())
    return existing


def expand_directories(refs: Iterable[str]) -> Set[str]:
    expanded: Set[str] = set()
    for r in refs:
        rp = ROOT / r
        if rp.is_dir():
            expanded.add(r)
            for p in rp.rglob('*'):
                expanded.add(p.relative_to(ROOT).as_posix())
        else:
            expanded.add(r)
    return expanded


def group_by_ext(paths: Iterable[str]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for p in paths:
        ext = Path(p).suffix.lower()
        counts[ext] = counts.get(ext, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description='Prune unused assets under examples/ and appendix/.')
    ap.add_argument('--targets', default='examples,appendix', help='Comma-separated target dirs (default: examples,appendix)')
    ap.add_argument('--only-canonical', action='store_true', help='Only consider canonical book (ignore links-only variant)')
    ap.add_argument('--ext', default='', help='Comma-separated extension whitelist (e.g., .png,.jpg,.gif); empty means all')
    ap.add_argument('--path-contains', default='', help='Only prune paths containing this substring (optional)')
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument('--dry-run', action='store_true', help='Dry-run only (default)')
    mode.add_argument('--move', action='store_true', help='Move files to tools/trash/<timestamp>')
    mode.add_argument('--delete', action='store_true', help='Permanently delete files (CAUTION)')
    ap.add_argument('--confirm', default='', help='Safety confirmation substring required when --delete is used')
    args = ap.parse_args(argv)

    target_dirs = [t.strip() for t in args.targets.split(',') if t.strip()]
    sources = []
    if BOOK.exists():
        sources.append(BOOK)
    if not args.only_canonical and BOOK_LINKS.exists():
        sources.append(BOOK_LINKS)

    refs: Set[str] = set()
    for src in sources:
        text = src.read_text(encoding='utf-8')
        refs.update(extract_references(text))

    existing = list_existing_assets(target_dirs)
    covered = expand_directories([r for r in refs if (ROOT / r).exists()])

    # File candidates only
    candidates = []
    for e in existing:
        p = ROOT / e
        if not p.exists() or p.is_dir():
            continue
        if e in covered:
            continue
        if e.split('/', 1)[0] not in target_dirs:
            continue
        candidates.append(e)

    # Apply filters
    if args.ext:
        allow = {x.strip().lower() for x in args.ext.split(',') if x.strip()}
        candidates = [e for e in candidates if Path(e).suffix.lower() in allow]
    if args.path_contains:
        candidates = [e for e in candidates if args.path_contains in e]

    counts = group_by_ext(candidates)
    total = len(candidates)
    print(f"Unused file candidates: {total}")
    if counts:
        print("By extension:")
        for ext, c in counts.items():
            print(f"  {ext or '<noext>'}: {c}")

    if args.dry_run or (not args.move and not args.delete):
        print("DRY-RUN: No changes made.")
        return 0

    # Move or delete
    moved = 0
    deleted = 0
    if args.move:
        trash_root = ROOT / 'tools' / 'trash' / datetime.now().strftime('%Y%m%d-%H%M%S')
        trash_root.mkdir(parents=True, exist_ok=True)
        for rel in candidates:
            src = ROOT / rel
            dst = trash_root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            moved += 1
        # Clean up empty dirs under targets
        for t in target_dirs:
            base = ROOT / t
            for d in sorted([p for p in base.rglob('*') if p.is_dir()], reverse=True):
                try:
                    d.rmdir()
                except OSError:
                    pass
        print(f"Moved {moved} files to {trash_root}")
    elif args.delete:
        if not args.confirm or args.confirm not in ','.join(target_dirs):
            print("--delete requires --confirm matching one of the target dirs; aborting.")
            return 2
        for rel in candidates:
            p = ROOT / rel
            try:
                p.unlink()
                deleted += 1
            except OSError:
                pass
        for t in target_dirs:
            base = ROOT / t
            for d in sorted([p for p in base.rglob('*') if p.is_dir()], reverse=True):
                try:
                    d.rmdir()
                except OSError:
                    pass
        print(f"Deleted {deleted} files.")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
