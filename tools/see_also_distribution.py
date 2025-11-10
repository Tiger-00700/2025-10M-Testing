"""Generate a chapter-level distribution report of See Also blocks.

Definition:
  - Chapter is any H2 heading (## ...). All subsequent content until next H2 belongs to that chapter.
  - Counts number of lines starting with '> 【See Also】' within that chapter span.

Usage:
  python tools/see_also_distribution.py --top 20

Outputs a markdown report under tools/reports/ named see-also-distribution-<timestamp>.md
"""
from __future__ import annotations
import re, argparse, math
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
    counts = [c['count'] for c in chapters]
    total_blocks = sum(counts)
    chapters_sorted = sorted(chapters, key=lambda c: c['count'], reverse=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    rep = REPORTS / f'see-also-distribution-{ts}.md'
    # stats helpers
    def median(vals):
        if not vals: return 0.0
        s = sorted(vals)
        n = len(s)
        m = n//2
        return float(s[m]) if n%2==1 else (s[m-1]+s[m])/2.0
    def percentile(vals, p):
        if not vals: return 0.0
        s = sorted(vals)
        k = (len(s)-1)*p
        f = math.floor(k); c = math.ceil(k)
        if f==c: return float(s[int(k)])
        d0 = s[f]*(c-k)
        d1 = s[c]*(k-f)
        return float(d0+d1)
    def stdev(vals):
        if not vals: return 0.0
        mu = sum(vals)/len(vals)
        var = sum((x-mu)*(x-mu) for x in vals)/len(vals)
        return math.sqrt(var)
    def gini(vals):
        n = len(vals)
        if n==0: return 0.0
        s = sorted(vals)
        total = sum(s)
        if total == 0: return 0.0
        # G = (sum_{i=1..n} (2i-n-1)*x_i) / (n * sum x)
        num = 0
        for i, x in enumerate(s, start=1):
            num += (2*i - n - 1) * x
        return float(num)/(n*total)
    mean = (total_blocks/len(chapters)) if chapters else 0.0
    med = median(counts)
    p90 = percentile(counts, 0.90)
    sd = stdev(counts)
    gi = gini(counts)
    out = [
        f'# See Also Distribution ({ts})','',
        f'Total chapters: {len(chapters)}',
        f'Total See Also blocks: {total_blocks}',
        '',
        '## Stats',
        '',
        f'- Mean blocks per chapter: {mean:.2f}',
        f'- Median: {med:.2f}',
        f'- P90: {p90:.2f}',
        f'- Std dev: {sd:.2f}',
        f'- Gini: {gi:.3f}',
        '',
    ]
    out.append(f'## Top {args.top} chapters by See Also blocks')
    out.append('')
    for c in chapters_sorted[:args.top]:
        out.append(f'- {c["title"]}: {c["count"]}')
    out.append('')
    if chapters_sorted:
        out.append(f'- Max blocks in a chapter: {chapters_sorted[0]["count"]}')
    rep.write_text('\n'.join(out)+'\n', encoding='utf-8')
    print(f'Report written: {rep.name} chapters={len(chapters)} total_blocks={total_blocks}')

if __name__ == '__main__':
    main()
