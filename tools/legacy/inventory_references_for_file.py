#!/usr/bin/env python3
"""Inventory references in a given markdown file to examples/ and appendix/ assets.

Usage:
  python tools/inventory_references_for_file.py --source book/1022.2025.newbook.augmented.frozen.md

Outputs: tools/reports/inventory-assets-<name>-<ts>.md
Prints a one-line summary: References / Present / Missing / Unused
"""
from __future__ import annotations
import argparse
import re
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]

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


def extract_references(text: str) -> set[str]:
    refs: set[str] = set()
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


def list_existing_assets(target_dirs: list[str]) -> set[str]:
    existing: set[str] = set()
    for base in target_dirs:
        base_path = ROOT / base
        if not base_path.exists():
            continue
        for p in base_path.rglob('*'):
            existing.add(p.relative_to(ROOT).as_posix())
    return existing


def expand_directories(refs: set[str]) -> set[str]:
    expanded: set[str] = set()
    for r in refs:
        rp = ROOT / r
        if rp.is_dir():
            expanded.add(r)
            for p in rp.rglob('*'):
                expanded.add(p.relative_to(ROOT).as_posix())
        else:
            expanded.add(r)
    return expanded


def include_ancestors(paths: set[str], target_dirs: list[str]) -> set[str]:
    covered: set[str] = set()
    for rel in paths:
        covered.add(rel)
        p = ROOT / rel
        try:
            while True:
                p = p.parent
                if p == ROOT:
                    break
                relp = p.relative_to(ROOT).as_posix()
                if relp.split('/', 1)[0] in target_dirs:
                    covered.add(relp)
                else:
                    break
        except Exception:
            pass
    return covered


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', required=True, help='Path to markdown file relative to repo root')
    ap.add_argument('--targets', default='examples,appendix')
    args = ap.parse_args(argv)

    src = ROOT / args.source
    if not src.exists():
        print(f"ERROR: source not found: {src}")
        return 2
    text = src.read_text(encoding='utf-8')
    refs = extract_references(text)
    target_dirs = [t.strip() for t in args.targets.split(',') if t.strip()]
    existing = list_existing_assets(target_dirs)
    present = sorted([r for r in refs if (ROOT / r).exists()])
    missing = sorted([r for r in refs if not (ROOT / r).exists()])
    covered = include_ancestors(expand_directories(set(present)), target_dirs)
    unused = sorted([e for e in existing if e.split('/', 1)[0] in target_dirs and e not in covered])

    reports = ROOT / 'tools' / 'reports'
    reports.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d-%H%M%S')
    out = reports / f"inventory-assets-{src.stem}-{ts}.md"
    lines = []
    lines.append(f"# Referenced Assets Inventory for {src.as_posix()} ({ts})")
    lines.append("")
    lines.append(f"- Total references found: {len(refs)}")
    lines.append(f"- Present: {len(present)}")
    lines.append(f"- Missing: {len(missing)}")
    lines.append(f"- Existing but unreferenced: {len(unused)}")
    lines.append("")
    if missing:
        lines.append("## ❌ Missing")
        for m in missing:
            lines.append(f"- {m}")
        lines.append("")
    out.write_text('\n'.join(lines), encoding='utf-8')
    print(f"Report written: {out}")
    print(f"References: {len(refs)}, Present: {len(present)}, Missing: {len(missing)}, Unused: {len(unused)}")
    return 0 if not missing else 2


if __name__ == '__main__':
    raise SystemExit(main())
