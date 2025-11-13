#!/usr/bin/env python3
"""CI check for book reference topology.

Checks:
    - Cycles in book reference graph (links that include 'book/' and target .md)
    - Unreferenced book files (no incoming links), excluding a keep allowlist

Exit codes:
    0 = OK (or only warnings)
    2 = ERROR (when --fail-on-* threshold is triggered)

Writes a concise markdown report under tools/reports/check-book-topology-<ts>.md
and prints a one-line summary. UTF-8 safe printing.
"""
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import argparse
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
BOOK_DIR = ROOT / 'book'
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")

DEFAULT_KEEP = {
    '1022.2025.newbook.augmented.frozen.md',
    '1022.2025.newbook.merged.md',
    '1022.2025.newbook.cleaned.md',
    '1030.2025.book.md',
}

def extract_book_links(text: str) -> set[str]:
    targets: set[str] = set()
    for m in LINK_RE.finditer(text):
        raw = m.group(1).strip()
        raw = raw.split('#',1)[0].split('?',1)[0]
        if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', raw):
            continue
        t = raw.replace('\\','/')
        parts = [p for p in t.split('/') if p]
        if 'book' not in parts:
            continue
        if not t.lower().endswith('.md'):
            continue
        from pathlib import Path as _P
        targets.add(_P(t).name)
    return targets

def build_graph() -> tuple[
    dict[str, set[str]],
    dict[str, set[str]],
    list[str],
]:
    files = sorted([p.name for p in BOOK_DIR.glob('*.md') if p.is_file()])
    adj: dict[str,set[str]] = {f:set() for f in files}
    for fname in files:
        text = (BOOK_DIR / fname).read_text(encoding='utf-8')
        tgts = extract_book_links(text)
        adj[fname] = set(t for t in tgts if t in adj and t != fname)
    rev: dict[str,set[str]] = {f:set() for f in files}
    for s, tgts in adj.items():
        for t in tgts:
            rev[t].add(s)
    return adj, rev, files

def find_cycles(graph: dict[str,set[str]]) -> list[list[str]]:
    cycles: list[list[str]] = []
    path: list[str] = []
    visited: set[str] = set()
    in_path: set[str] = set()
    def dfs(node: str):
        visited.add(node)
        path.append(node)
        in_path.add(node)
        for nxt in graph.get(node, set()):
            if nxt not in visited:
                dfs(nxt)
            elif nxt in in_path:
                try:
                    idx = path.index(nxt)
                    cyc = path[idx:] + [nxt]
                    min_idx = min(range(len(cyc)-1), key=lambda i: cyc[i])
                    norm = cyc[min_idx:-1] + cyc[:min_idx] + [cyc[min_idx]]
                    if norm not in cycles:
                        cycles.append(norm)
                except ValueError:
                    pass
        in_path.remove(node)
        path.pop()
    for n in graph.keys():
        if n not in visited:
            dfs(n)
    return cycles

def uprint(s: str):
    try:
        sys.stdout.buffer.write((s+'\n').encode('utf-8'))
    except Exception:
        print(s)

def main(argv: list[str] | None = None) -> int:
    desc = 'CI checks for book topology (cycles, unreferenced).'
    ap = argparse.ArgumentParser(description=desc)
    help_cycles = 'Exit non-zero when cycles detected'
    ap.add_argument('--fail-on-cycles', action='store_true', help=help_cycles)
    help_unref = 'Exit non-zero when unreferenced book files found'
    ap.add_argument('--fail-on-unreferenced', action='store_true', help=help_unref)
    default_keep_str = ','.join(sorted(DEFAULT_KEEP))
    ap.add_argument(
        '--keep',
        default=default_keep_str,
        help='Comma-separated filenames to always keep from unreferenced warnings',
    )
    args = ap.parse_args(argv)

    keep = {x.strip() for x in args.keep.split(',') if x.strip()}
    adj, rev, files = build_graph()
    in_deg = {f: len(rev.get(f, set())) for f in files}
    unref = []
    for f in files:
        if in_deg.get(f, 0) != 0:
            continue
        if f.startswith('附录-'):
            continue
        if f in keep:
            continue
        unref.append(f)
    unref = sorted(unref)
    cycles = find_cycles(adj)

    ts = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    reports = ROOT / 'tools' / 'reports'
    reports.mkdir(parents=True, exist_ok=True)
    out = reports / f'check-book-topology-{ts}.md'
    lines = [f'# Book Topology CI Check ({ts})','']
    if cycles:
        lines.append('## Cycles (ERROR/WARN)')
        for cyc in cycles:
            lines.append('- ' + ' -> '.join(cyc))
        lines.append('\nTotal cycles: ' + str(len(cycles)))
        lines.append('')
    else:
        lines.append('## Cycles')
        lines.append('- None')
        lines.append('')
    if unref:
        lines.append('## Unreferenced book files (WARN unless configured to fail)')
        for f in unref:
            lines.append(f'- {f}')
        lines.append('\nTotal unreferenced: ' + str(len(unref)))
        lines.append('')
    else:
        lines.append('## Unreferenced book files')
        lines.append('- None')
        lines.append('')
    out.write_text('\n'.join(lines)+'\n', encoding='utf-8')

    status = 'OK'
    exit_code = 0
    if cycles and getattr(args, 'fail_on_cycles'):
        status = 'ERROR'
        exit_code = 2
    elif unref and getattr(args, 'fail_on_unreferenced') and exit_code == 0:
        status = 'ERROR'
        exit_code = 2
    elif cycles or unref:
        status = 'WARN'
    msg = (
        'Status: ' + status +
        ' | cycles=' + str(len(cycles)) +
        ' unreferenced=' + str(len(unref)) +
        ' | Report: ' + out.name
    )
    uprint(msg)
    return exit_code

if __name__ == '__main__':
    raise SystemExit(main())
