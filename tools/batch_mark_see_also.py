"""Batch annotate top-N chapters with per-section See Also metadata to reduce density.

Strategy:
  - Identify H2 chapters with highest See Also block counts (requires prior run of see_also_distribution.py or fresh scan).
  - For top K chapters, insert a metadata marker after the H2 heading to globally reduce recommendations:
        <!-- see-also: min_sim=0.35; top_n=1 -->
    or disable entirely if count exceeds a hard threshold:
        <!-- see-also: off -->

Usage:
  python tools/batch_mark_see_also.py --limit 10 --disable-threshold 120 --reduce-threshold 60 --apply

Heuristics:
  - If chapter count >= disable_threshold -> off
  - Else if chapter count >= reduce_threshold -> min_sim/top_n override
  - Else untouched.

Dry run prints a summary; --apply writes modifications.
"""
from __future__ import annotations
import argparse, re
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / 'book' / '1022.2025.newbook.cleaned.md'
REPORTS = ROOT / 'tools' / 'reports'

H2_RE = re.compile(r'^##\s+(.*\S)\s*$')
SEE_ALSO_RE = re.compile(r'^>\s*【See Also】')
META_RE = re.compile(r'<!--\s*see-also:')

def load_lines(p: Path) -> list[str]:
    return p.read_text(encoding='utf-8').replace('\r\n','\n').replace('\r','\n').split('\n')

def save_lines(p: Path, lines: list[str]):
    p.write_text('\n'.join(lines)+'\n', encoding='utf-8')

def chapter_counts(lines: list[str]):
    chapters = []
    current = None
    for i, ln in enumerate(lines):
        m = H2_RE.match(ln)
        if m:
            if current:
                chapters.append(current)
            current = {'title': m.group(1).strip(), 'start': i, 'end': len(lines), 'count': 0}
        else:
            if current and SEE_ALSO_RE.match(ln.strip()):
                current['count'] += 1
    if current:
        chapters.append(current)
    # determine end indices
    for idx in range(len(chapters)-1):
        chapters[idx]['end'] = chapters[idx+1]['start']
    return chapters

def apply_marks(lines: list[str], chapters, limit, disable_threshold, reduce_threshold, min_sim, top_n):
    # Sort chapters by count descending
    sorted_ch = sorted(chapters, key=lambda c: c['count'], reverse=True)[:limit]
    inserted = []
    for ch in sorted_ch:
        # check existing metadata in first few lines after start
        already = False
        for ln in lines[ch['start']+1: min(ch['start']+6, len(lines))]:
            if META_RE.search(ln):
                already = True
                break
        if already:
            continue
        if ch['count'] >= disable_threshold:
            marker = '<!-- see-also: off -->'
            lines.insert(ch['start']+1, marker)
            inserted.append((ch['title'], ch['count'], 'off'))
        elif ch['count'] >= reduce_threshold:
            marker = f'<!-- see-also: min_sim={min_sim}; top_n={top_n} -->'
            lines.insert(ch['start']+1, marker)
            inserted.append((ch['title'], ch['count'], f'min_sim={min_sim};top_n={top_n}'))
    return lines, inserted, sorted_ch

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int, default=15, help='Number of top chapters to annotate')
    ap.add_argument('--disable-threshold', type=int, default=150, help='Count above which See Also is disabled')
    ap.add_argument('--reduce-threshold', type=int, default=70, help='Count above which overrides are applied')
    ap.add_argument('--min-sim', type=float, default=0.35, help='Per-chapter min_sim override when reducing')
    ap.add_argument('--top-n', type=int, default=1, help='Per-chapter top_n override when reducing')
    ap.add_argument('--apply', action='store_true', help='Write changes to book')
    args = ap.parse_args()

    if not BOOK.exists():
        raise SystemExit(f'Book not found: {BOOK}')
    lines = load_lines(BOOK)
    chapters = chapter_counts(lines)
    new_lines, inserted, considered = apply_marks(lines, chapters, args.limit, args.disable_threshold, args.reduce_threshold, args.min_sim, args.top_n)
    REPORTS.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    rep = REPORTS / f'batch-see-also-marks-{ts}.md'
    rep_lines = [f'# Batch See Also Marks ({ts})','',f'Top considered chapters: {len(considered)}', f'Inserted markers: {len(inserted)}','']
    for title, cnt, mode in inserted:
        rep_lines.append(f'- {title} | count={cnt} | mode={mode}')
    rep.write_text('\n'.join(rep_lines)+'\n', encoding='utf-8')
    if args.apply and inserted:
        save_lines(BOOK, new_lines)
        print(f'Applied {len(inserted)} metadata markers to book.')
    else:
        print('Dry run (no changes written).' if not args.apply else 'No markers inserted.')
    print(f'Report: {rep.name} chapters_scanned={len(chapters)}')

if __name__ == '__main__':
    main()
