"""
Cleanup historical 'See Also' blocks and optionally regenerate with current settings.

Usage examples:
    python tools/cleanup_related_links.py --dry-run
    python tools/cleanup_related_links.py --apply
    python tools/cleanup_related_links.py --apply --regen

Behavior summary:
    - Detect lines starting with "> 【See Also】" and remove the whole block
        (including an adjacent single blank line where present).
    - Idempotent. Writes a timestamped report under tools/reports/.
"""
from __future__ import annotations
import argparse
import re
from pathlib import Path
from datetime import datetime, timezone
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / 'book' / '1022.2025.newbook.cleaned.md'
REPORTS = ROOT / 'tools' / 'reports'

SEE_ALSO_RE = re.compile(r'^>\s*【See Also】')


def load_lines(p: Path) -> list[str]:
    txt = p.read_text(encoding='utf-8')
    txt = txt.replace('\r\n', '\n')
    txt = txt.replace('\r', '\n')
    return txt.split('\n')


def save_lines(p: Path, lines: list[str]):
    p.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def cleanup(lines: list[str]):
    idx = 0
    removed_spans = []
    n = len(lines)
    while idx < n:
        if SEE_ALSO_RE.match(lines[idx].strip()):
            start = idx
            end = idx
            # Include trailing blank line immediately after block if present
            if end + 1 < n and lines[end + 1].strip() == '':
                end += 1
            # Include leading blank line immediately before block if present
            # (and not at BOF)
            if start - 1 >= 0 and lines[start - 1].strip() == '':
                start -= 1
            removed_spans.append((start, end))
            idx = end + 1
        else:
            idx += 1
    # Apply removals from bottom to top
    new_lines = lines[:]
    total_removed = 0
    for s, e in reversed(removed_spans):
        total_removed += (e - s + 1)
        del new_lines[s:e+1]
    return new_lines, removed_spans, total_removed


def write_report(name: str, content: list[str]):
    REPORTS.mkdir(parents=True, exist_ok=True)
    path = REPORTS / name
    path.write_text('\n'.join(content) + '\n', encoding='utf-8')
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        '--dry-run',
        action='store_true',
        help='Only report, do not write book file',
    )
    ap.add_argument(
        '--apply',
        action='store_true',
        help='Apply cleanup to book file',
    )
    ap.add_argument(
        '--regen',
        action='store_true',
        help=(
            'After apply, regenerate See Also using current generator'
        ),
    )
    args = ap.parse_args()

    if not BOOK.exists():
        raise SystemExit(f'Book not found: {BOOK}')
    lines = load_lines(BOOK)
    new_lines, spans, total = cleanup(lines)
    ts = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    report_lines = [
        f'# See Also Cleanup Report ({ts})',
        '',
        f'File: {BOOK.name}',
        f'Blocks removed: {len(spans)}',
        f'Lines removed: {total}',
        ''
    ]
    # include up to first 10 spans preview
    for i, (s, e) in enumerate(spans[:10]):
        snippet = ' '.join(l.strip() for l in lines[s:e+1])[:200]
        report_lines.append('- span[{}]: lines {}-{}: {}...'.format(i, s, e, snippet))
    rep = write_report(f'see-also-cleanup-{ts}.md', report_lines)

    if args.apply:
        save_lines(BOOK, new_lines)
        # optionally regenerate
        if args.regen:
                try:
                    cmd = ['python', str(ROOT / 'tools' / 'generate_related_links.py')]
                    subprocess.run(cmd, check=True)
            except Exception as e:
                print('Regeneration failed: {}'.format(e))
        else:
            print('DRY RUN. No changes written. To apply, run with --apply [--regen].')
        print('Report: {} Blocks={} Lines={}'.format(rep.name, len(spans), total))


if __name__ == '__main__':
    main()
