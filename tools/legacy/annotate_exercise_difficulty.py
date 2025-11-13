"""Annotate exercise questions with difficulty gradient (入门/进阶/专家) in cleaned book.

Heuristics:
    - Detect blocks starting with "> 【课后思考/练习题】".
    - For each numbered or bulleted question line inside the block, if no
        difficulty tag is present, assign one based on position:
        first third → 入门, middle third → 进阶, last third → 专家.
    - Very small sets map as follows:
            1 → 入门
            2 → 入门, 进阶
            3 → 入门, 进阶, 专家
        For 4–5 questions use a 1/2 → 入门, middle → 进阶, last → 专家 allocation.

Idempotent: skips lines already containing any of the tags at the start (after
bullet/number). Writes updated book in-place and a short markdown report.
"""
from __future__ import annotations
import re
from pathlib import Path
from datetime import datetime, timezone
import argparse

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / 'book' / '1022.2025.newbook.cleaned.md'
REPORTS = ROOT / 'tools' / 'reports'

BLOCK_RE = re.compile(r"^>\s*【课后思考/练习题】")
Q_RE = re.compile(
    (
        r"^(?P<prefix>(?:\d+\.\s+|[-*]\s+))"
        r"(?!【(?:入门|进阶|专家)】)"
        r"(?P<body>.+)"
    )
)
HAS_TAG_RE = re.compile(
    r"^(?:\d+\.\s+|[-*]\s+)【(?:入门|进阶|专家)】"
)

def load(p: Path) -> list[str]:
    text = p.read_text(encoding='utf-8')
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    return text.split('\n')

def save(p: Path, lines: list[str]):
    p.write_text('\n'.join(lines) + '\n', encoding='utf-8')

def assign_tags(count: int) -> list[str]:
    if count <= 0:
        return []
    if count == 1:
        return ['入门']
    if count == 2:
        return ['入门','进阶']
    if count == 3:
        return ['入门','进阶','专家']
    tags = []
    # thirds boundaries
    for i in range(count):
        frac = (i+1)/count
        if frac <= 0.4:
            tags.append('入门')
        elif frac <= 0.7:
            tags.append('进阶')
        else:
            tags.append('专家')
    return tags

def process(lines: list[str]):
    updated = 0
    blocks = 0
    i = 0
    while i < len(lines):
        ln = lines[i]
        if BLOCK_RE.match(ln.strip()):
            blocks += 1
            # collect question indices
            q_idx = []
            j = i + 1
            while j < len(lines):
                s = lines[j].strip()
                if s == '':
                    if j + 1 < len(lines) and lines[j+1].strip() == '':
                        break
                    j += 1
                    continue
                if BLOCK_RE.match(s):
                    break
                if s.startswith('#'):
                    break
                if HAS_TAG_RE.match(lines[j]):
                    j += 1
                    continue
                qm = Q_RE.match(lines[j])
                if qm:
                    q_idx.append(j)
                    j += 1
                    continue
                j += 1
            if q_idx:
                tags = assign_tags(len(q_idx))
                for pos, line_idx in enumerate(q_idx):
                    if pos < len(tags):
                        prefix_match = Q_RE.match(lines[line_idx])
                        if prefix_match:
                            prefix = prefix_match.group('prefix')
                            body = prefix_match.group('body').strip()
                            label = f"【{tags[pos]}】 "
                            new_line = prefix + label + body
                            lines[line_idx] = new_line
                            updated += 1
            i = j
            continue
        i += 1
    return lines, updated, blocks

def main():
    ap = argparse.ArgumentParser()
    dry_help = 'Only report, do not modify book.'
    ap.add_argument('--dry-run', action='store_true', help=dry_help)
    args = ap.parse_args()
    if not BOOK.exists():
        raise SystemExit(f'Cleaned book not found: {BOOK}')
    lines = load(BOOK)
    new_lines, updated, blocks = process(lines.copy())
    REPORTS.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    rep = REPORTS / f'exercise-difficulty-{ts}.md'
    mode_str = "dry-run" if args.dry_run else "in-place"
    md_lines = [
        f'# Exercise Difficulty Annotation Report ({ts})',
        '',
        f'Blocks scanned: {blocks}',
        f'Questions annotated: {updated}',
        f'Mode: {mode_str}',
        ''
    ]
    rep.write_text('\n'.join(md_lines), encoding='utf-8')
    if not args.dry_run and updated > 0:
        save(BOOK, new_lines)
    msg = (
        f'Blocks={blocks} annotated={updated} '
        f'dry_run={args.dry_run} report={rep.name}'
    )
    print(msg)

if __name__ == '__main__':
    main()
