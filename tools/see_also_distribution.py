"""Generate a chapter-level distribution report of See Also blocks.

Definition:
  - Chapter is any H2 heading (## ...). All subsequent content until next H2 belongs to that chapter.
  - Counts number of lines starting with '> 【See Also】' within that chapter span.

Usage:
  python tools/see_also_distribution.py --top 20

Outputs a markdown report under tools/reports/ named see-also-distribution-<timestamp>.md
"""
from __future__ import annotations
import re, argparse
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / 'book' / '1022.2025.newbook.cleaned.md'
REPORTS = ROOT / 'tools' / 'reports'

H2_RE = re.compile(r'^##\s+(.*\S)\s*$')
SEE_ALSO_RE = re.compile(r'^>\s*【See Also】')

def load_lines(p: Path) -> list[str]:
    return p.read_text(encoding='utf-8').replace('\r\n','\n').replace('\r','\n').split('\n')

def collect(lines: list[str]):
    chapters = []
    current = None
    for i, ln in enumerate(lines):
        m = H2_RE.match(ln)
        if m:
            if current:
                current['end'] = i
                chapters.append(current)
            current = {'title': m.group(1).strip(), 'start': i, 'end': len(lines), 'count': 0}
        else:
            if current and SEE_ALSO_RE.match(ln.strip()):
                current['count'] += 1
    if current:
        chapters.append(current)
    return chapters

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--top', type=int, default=20, help='Top N chapters to display')
    args = ap.parse_args()
    if not BOOK.exists():
        raise SystemExit(f'Book not found: {BOOK}')
    lines = load_lines(BOOK)
    chapters = collect(lines)
    total_blocks = sum(c['count'] for c in chapters)
    chapters_sorted = sorted(chapters, key=lambda c: c['count'], reverse=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    rep = REPORTS / f'see-also-distribution-{ts}.md'
    out = [f'# See Also Distribution ({ts})','',f'Total chapters: {len(chapters)}',f'Total See Also blocks: {total_blocks}','']
    out.append(f'## Top {args.top} chapters by See Also blocks')
    out.append('')
    for c in chapters_sorted[:args.top]:
        out.append(f'- {c["title"]}: {c["count"]}')
    out.append('')
    # Basic stats
    if chapters:
        mean = total_blocks/len(chapters)
        max_c = chapters_sorted[0]['count'] if chapters_sorted else 0
        out.append(f'## Stats')
        out.append('')
        out.append(f'- Mean blocks per chapter: {mean:.2f}')
        out.append(f'- Max blocks in a chapter: {max_c}')
    rep.write_text('\n'.join(out)+'\n', encoding='utf-8')
    print(f'Report written: {rep.name} chapters={len(chapters)} total_blocks={total_blocks}')

if __name__ == '__main__':
    main()
