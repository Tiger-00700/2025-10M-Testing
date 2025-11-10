"""Inject alias anchors for the last few broken internal link targets in cleaned book.

Reads latest internal-anchors-cleaned-* report, extracts broken anchor IDs, and
adds a grouped alias block near the top of the cleaned book if those anchors
don't already exist.
"""
from __future__ import annotations
import re, argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / 'book' / '1022.2025.newbook.cleaned.md'
REPORTS = ROOT / 'tools' / 'reports'
REPORT_PATTERN = 'internal-anchors-cleaned-'  # prefix
ANCHOR_RE = re.compile(r'^\s*<a\s+id="([^"/]+)"\s*></a>\s*$', re.IGNORECASE)

def latest_report():
    files = sorted(REPORTS.glob(REPORT_PATTERN + '*.md'))
    return files[-1] if files else None

def parse_broken(report_path: Path):
    lines = report_path.read_text(encoding='utf-8').splitlines()
    broken = []
    table = False
    for ln in lines:
        if ln.strip().startswith('| Line | Anchor |'):
            table = True
            continue
        if table:
            if ln.strip().startswith('|---'):
                continue
            if not ln.strip().startswith('|'):
                break
            parts = [p.strip() for p in ln.strip().strip('|').split('|')]
            if len(parts) >= 2:
                anchor = parts[1]
                if anchor and anchor not in broken:
                    broken.append(anchor)
    return broken

def collect_existing(lines: list[str]):
    existing = set()
    for ln in lines:
        m = ANCHOR_RE.match(ln.strip())
        if m:
            existing.add(m.group(1))
    return existing

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--all', action='store_true', help='Inject alias anchors for ALL broken fragments in latest report.')
    args = ap.parse_args()
    rep = latest_report()
    if not rep or not BOOK.exists():
        raise SystemExit('Missing cleaned book or internal anchors report.')
    targets = parse_broken(rep)
    if not targets:
        print('No broken anchors found in latest report.')
        return
    # If not --all, keep only a small allowlist (e.g. previous residual 5)
    if not args.all and len(targets) > 10:
        # heuristics: keep those with digits or long mixed segments (previous residual style)
        selected = [t for t in targets if re.search(r'\d', t) or len(t) > 10][:10]
    else:
        selected = targets
    lines = BOOK.read_text(encoding='utf-8').splitlines()
    existing = collect_existing(lines)
    new_alias = [t for t in selected if t not in existing]
    if not new_alias:
        print('All selected broken anchors already present; nothing to inject.')
        return
    insert_at = 0
    while insert_at < len(lines) and (lines[insert_at].strip() == '' or lines[insert_at].startswith('<!--')):
        insert_at += 1
    block = ['','<!-- alias-anchors: auto-injected -->'] + [f'<a id="{aid}"></a>' for aid in new_alias] + ['<!-- /alias-anchors -->','']
    lines[insert_at:insert_at] = block
    BOOK.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'Injected {len(new_alias)} alias anchors (mode={"all" if args.all else "filtered"}): {", ".join(new_alias)}')

if __name__ == '__main__':
    main()
