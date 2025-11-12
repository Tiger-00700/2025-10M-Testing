#!/usr/bin/env python3
"""
Scan chapter/*.md to verify archive pattern compliance:
- Check presence of archived-content block markers
- Check presence of markdownlint-disable MD025 near the top (first 12 lines)
Outputs a markdown report under tools/reports/archive-status-YYYYMMDD-HHMMSS.md
"""
from __future__ import annotations
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
CHAPTER = ROOT / 'chapter'


def check_file(p: Path):
    text = p.read_text(encoding='utf-8', errors='ignore')
    lines = text.splitlines()
    # Check MD025 suppression within first 12 lines (allow HTML or bare form)
    head = '\n'.join(lines[:12])
    has_md025 = ('markdownlint-disable MD025' in head)
    has_archive = ('archived-content:start' in text and 'archived-content:end' in text)
    return has_md025, has_archive


def main() -> int:
    md_files = sorted(CHAPTER.glob('*.md'))
    missing_md025 = []
    missing_archive = []
    ok = []

    for p in md_files:
        has_md025, has_archive = check_file(p)
        if has_md025 and has_archive:
            ok.append(p)
        else:
            if not has_md025:
                missing_md025.append(p)
            if not has_archive:
                missing_archive.append(p)

    ts = datetime.now().strftime('%Y%m%d-%H%M%S')
    reports = ROOT / 'tools' / 'reports'
    reports.mkdir(parents=True, exist_ok=True)
    out = reports / f'archive-status-{ts}.md'

    def rel(p: Path) -> str:
        return p.relative_to(ROOT).as_posix()

    lines = []
    lines.append(f'# Chapter Archive Compliance Report ({ts})')
    lines.append('')
    lines.append(f'- Total chapter files: {len(md_files)}')
    lines.append(f'- Fully compliant (MD025 at top + archive block): {len(ok)}')
    lines.append(f'- Missing MD025 suppression (top): {len(missing_md025)}')
    lines.append(f'- Missing archived-content block: {len(missing_archive)}')
    lines.append('')

    if missing_md025:
        lines.append('## ❗ Missing MD025 suppression (top 12 lines)')
        for p in missing_md025:
            lines.append(f'- {rel(p)}')
        lines.append('')
    if missing_archive:
        lines.append('## ❗ Missing archived-content block')
        for p in missing_archive:
            lines.append(f'- {rel(p)}')
        lines.append('')
    if ok:
        lines.append('## ✅ Fully compliant files (excerpt)')
        for p in ok[:30]:
            lines.append(f'- {rel(p)}')
        if len(ok) > 30:
            lines.append(f'- ... and {len(ok)-30} more')
        lines.append('')

    out.write_text('\n'.join(lines), encoding='utf-8')
    print(f'Report written: {out}')
    print(f'Total={len(md_files)} OK={len(ok)} missing_md025={len(missing_md025)} missing_archive={len(missing_archive)}')
    # Fail CI if any chapter is non-compliant
    if missing_md025 or missing_archive:
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
