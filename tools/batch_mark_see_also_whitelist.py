"""Batch mark whitelist sections/chapters for See Also generation.

Usage:
  # Mark chapters whose H2 title contains any of the given substrings
  python tools/batch_mark_see_also_whitelist.py --contains 概述 原理 案例 --apply

  # Or provide an explicit titles file (one pattern per line)
  python tools/batch_mark_see_also_whitelist.py --titles-file tools/whitelist_titles.txt --apply

Effect:
  Inserts a metadata marker right after matching H2 lines:
    <!-- see-also: whitelist -->
  Which relaxes thresholds in generate_related_links.py (slightly lower min_sim, +1 to top_n).
"""
from __future__ import annotations
import argparse, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / 'book' / '1022.2025.newbook.cleaned.md'
H2_RE = re.compile(r'^##\s+(.*\S)\s*$')
META_RE = re.compile(r'<!--\s*see-also:')

def load_lines(p: Path) -> list[str]:
    return p.read_text(encoding='utf-8').replace('\r\n','\n').replace('\r','\n').split('\n')

def save_lines(p: Path, lines: list[str]):
    p.write_text('\n'.join(lines)+'\n', encoding='utf-8')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--contains', nargs='*', default=[], help='Mark H2 chapters whose titles contain any of these substrings')
    ap.add_argument('--titles-file', type=str, help='File with one pattern per line')
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()

    patterns = set(args.contains or [])
    if args.titles_file:
        p = Path(args.titles_file)
        if p.exists():
            for line in p.read_text(encoding='utf-8').splitlines():
                line = line.strip()
                if line and not line.startswith('#'):
                    patterns.add(line)
    if not patterns:
        print('No patterns provided. Nothing to do.')
        return

    if not BOOK.exists():
        raise SystemExit(f'Book not found: {BOOK}')
    lines = load_lines(BOOK)
    inserted = []
    for i, ln in enumerate(lines):
        m = H2_RE.match(ln)
        if not m:
            continue
        title = m.group(1).strip()
        if any(pat in title for pat in patterns):
            # check if already has a meta marker in next few lines
            already = False
            for look in lines[i+1:i+6]:
                if META_RE.search(look):
                    already = True
                    break
            if already:
                continue
            lines.insert(i+1, '<!-- see-also: whitelist -->')
            inserted.append(title)
    if args.apply and inserted:
        save_lines(BOOK, lines)
        print(f'Applied whitelist markers: {len(inserted)}')
    else:
        print(f'Dry run. Would insert: {len(inserted)} markers')
    if inserted:
        print('Examples:')
        for t in inserted[:10]:
            print(' -', t)

if __name__ == '__main__':
    main()
