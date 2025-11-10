#!/usr/bin/env python3
"""
Merge learning blocks from filled book into cleaned book by replacing cleaned with filled
when they share the same base structure. Prefer safety with a simple heuristic check
and produce a report.

Inputs:
  - book/1022.2025.newbook.cleaned.md
  - book/1022.2025.newbook.filled.md

Output:
  - Overwrites cleaned.md with filled.md content (after passing checks)
  - tools/reports/merge-filled-into-cleaned-<ts>.md
"""
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import re

ROOT = Path(__file__).resolve().parents[1]
CLEANED = ROOT / 'book' / '1022.2025.newbook.cleaned.md'
FILLED = ROOT / 'book' / '1022.2025.newbook.filled.md'
REPORTS = ROOT / 'tools' / 'reports'

HEAD_RE = re.compile(r'^(#{1,6})\s+(.*\S)\s*$')

def headings_signature(text: str) -> list[str]:
    sig = []
    for line in text.splitlines():
        m = HEAD_RE.match(line)
        if m:
            title = m.group(2).strip()
            # skip learning-block subheads to stabilize signature
            if title in ('学习目标','小结','练习'):
                continue
            sig.append(f'{len(m.group(1))}:{title}')
    return sig

def count_learning_blocks(text: str) -> tuple[int,int,int]:
    s = b = e = 0
    for line in text.splitlines():
        if line.strip().startswith('##### '):
            t = line.strip()[6:].strip()
            if t == '学习目标': s += 1
            elif t == '小结': b += 1
            elif t == '练习': e += 1
    return s,b,e

def main():
    if not CLEANED.exists() or not FILLED.exists():
        raise SystemExit('Missing cleaned or filled book.')
    tc = CLEANED.read_text(encoding='utf-8')
    tf = FILLED.read_text(encoding='utf-8')

    sig_c = headings_signature(tc)
    sig_f = headings_signature(tf)
    compatible = (sig_c == sig_f) and len(sig_c) > 0

    sc,sb,se = count_learning_blocks(tc)
    fc,fb,fe = count_learning_blocks(tf)

    ts = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    REPORTS.mkdir(parents=True, exist_ok=True)
    rep = REPORTS / f'merge-filled-into-cleaned-{ts}.md'

    if not compatible:
        mismatch_lines = [f'- C: {c}\n  F: {f}' for c, f in list(zip(sig_c, sig_f))[:10]]
        rep.write_text('\n'.join([
            f'# Merge filled -> cleaned report ({ts})',
            '',
            'Compatibility check: FAILED',
            f'- cleaned headings: {len(sig_c)}',
            f'- filled  headings: {len(sig_f)}',
            'First 10 mismatches:',
            *mismatch_lines,
            ''
        ]), encoding='utf-8')
        print(f'Merge skipped (signature mismatch). Report: {rep.name}')
        return

    # Overwrite cleaned with filled
    CLEANED.write_text(tf, encoding='utf-8')
    rep.write_text('\n'.join([
        f'# Merge filled -> cleaned report ({ts})',
        '',
        'Compatibility check: OK',
        f'- Headings: {len(sig_c)}',
        f'- Learning blocks in cleaned (before): 学习目标={sc} 小结={sb} 练习={se}',
        f'- Learning blocks in filled:           学习目标={fc} 小结={fb} 练习={fe}',
        'Action: cleaned overwritten by filled content.',
        ''
    ]), encoding='utf-8')
    print(f'Merged filled into cleaned. Report: {rep.name}')

if __name__ == '__main__':
    main()
