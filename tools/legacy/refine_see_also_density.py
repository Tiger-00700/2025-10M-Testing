"""Iteratively refine See Also density using chapter-level markers until targets met.

Process (one pass):
  1. Compute chapter distribution and stats.
  2. If mean > target_mean or gini > max_gini:
       - Mark top chapters with batch_mark_see_also.py using adaptive thresholds.
       - Cleanup + regenerate.
  3. Recompute stats; repeat up to --max-iterations.

Dry-run mode prints planned actions without modifying book.

Usage:
  python tools/refine_see_also_density.py --target-mean 20 --max-gini 0.30 --max-iterations 4 --dry-run
  python tools/refine_see_also_density.py --target-mean 20 --max-gini 0.30 --max-iterations 4 --apply
"""
from __future__ import annotations
import argparse, subprocess, math, re
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / 'book' / '1022.2025.newbook.cleaned.md'
REPORTS = ROOT / 'tools' / 'reports'
H2_RE = re.compile(r'^##\s+(.*\S)\s*$')
SEE_ALSO_RE = re.compile(r'^>\s*【See Also】')

def load_lines(p: Path) -> list[str]:
    return p.read_text(encoding='utf-8').replace('\r\n','\n').replace('\r','\n').split('\n')

def chapter_counts(lines: list[str]):
    chapters = []
    current = None
    for i, ln in enumerate(lines):
        m = H2_RE.match(ln)
        if m:
            if current:
                chapters.append(current)
            # ensure count is always an int
            current = {'title': m.group(1).strip(), 'start': i, 'count': 0}
        else:
            if current and SEE_ALSO_RE.match(ln.strip()):
                # guard against accidental non-int values
                current['count'] = int(current.get('count', 0)) + 1
    if current:
        chapters.append(current)
    return chapters

def stats(counts):
    if not counts:
        return dict(mean=0, gini=0, p90=0)
    mean = sum(counts)/len(counts)
    s = sorted(counts)
    def percentile(s, p):
        k = (len(s)-1)*p
        f = math.floor(k); c = math.ceil(k)
        if f==c: return float(s[int(k)])
        return s[f]*(c-k)+s[c]*(k-f)
    p90 = percentile(s,0.90)
    total = sum(s)
    if total == 0:
        gini = 0.0
    else:
        num = 0
        n = len(s)
        for i,x in enumerate(s, start=1):
            num += (2*i - n - 1) * x
        gini = num/(n*total)
    return dict(mean=mean, gini=gini, p90=p90)

def adaptive_parameters(chapters: list[dict], iter_idx: int) -> dict:
    # progressively tighten thresholds
    disable_threshold = max(30, 120 - iter_idx*15)
    reduce_threshold = max(15, 60 - iter_idx*10)
    min_sim = min(0.5, 0.36 + iter_idx*0.02)
    top_n = 1
    limit = 15
    return dict(disable=disable_threshold, reduce=reduce_threshold, min_sim=min_sim, top_n=top_n, limit=limit)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--target-mean', type=float, default=25.0, help='Target mean blocks per chapter')
    ap.add_argument('--max-gini', type=float, default=0.32, help='Max allowed Gini coefficient')
    ap.add_argument('--max-iterations', type=int, default=5, help='Maximum refinement passes')
    ap.add_argument('--apply', action='store_true', help='Apply changes (else dry-run)')
    ap.add_argument('--dry-run', action='store_true', help='Force dry-run even if --apply given')
    args = ap.parse_args()

    if not BOOK.exists():
        raise SystemExit(f'Book not found: {BOOK}')

    REPORTS.mkdir(parents=True, exist_ok=True)
    actions = []
    for iteration in range(args.max_iterations):
        lines = load_lines(BOOK)
        chapters = chapter_counts(lines)
        counts = [c['count'] for c in chapters]
        st = stats(counts)
        actions.append(f'Iteration {iteration}: mean={st["mean"]:.2f} gini={st["gini"]:.3f} p90={st["p90"]:.2f}')
        if st['mean'] <= args.target_mean and st['gini'] <= args.max_gini:
            actions.append('Targets met. Stop.')
            break
        params = adaptive_parameters(chapters, iteration)
        actions.append(f'  Adaptive params: disable>={params["disable"]} reduce>={params["reduce"]} min_sim={params["min_sim"]:.2f} top_n={params["top_n"]}')
        mark_cmd = ['python', str(ROOT/'tools'/'batch_mark_see_also.py'), '--limit', str(params['limit']), '--disable-threshold', str(params['disable']), '--reduce-threshold', str(params['reduce']), '--min-sim', str(params['min_sim']), '--top-n', str(params['top_n'])]
        if args.apply and not args.dry_run:
            mark_cmd.append('--apply')
        actions.append('  Run: ' + ' '.join(mark_cmd))
        if args.apply and not args.dry_run:
            subprocess.run(mark_cmd, check=True)
            subprocess.run(['python', str(ROOT/'tools'/'cleanup_related_links.py'), '--apply', '--regen'], check=True)
        else:
            # dry-run: do not modify
            pass
    ts = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    rep = REPORTS / f'see-also-refine-{ts}.md'
    rep.write_text('\n'.join(['# See Also Refinement Plan/Log', ''] + actions) + '\n', encoding='utf-8')
    print(f'Refinement log written: {rep.name}')
    if not (args.apply and not args.dry_run):
        print('Dry-run mode (no changes applied).')

if __name__ == '__main__':
    main()
