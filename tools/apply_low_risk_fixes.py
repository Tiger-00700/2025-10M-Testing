#!/usr/bin/env python3
"""
Scan `book/` and `chapter/` Markdown files and produce a patch of low-risk formatting fixes.

Fixes performed (non-destructive — script writes a patch file and DOES NOT modify files):
- Strip trailing whitespace from lines
- Ensure a single trailing newline at EOF
- Ensure blank line before and after ATX headings (lines beginning with #)
- Ensure fenced code blocks (``` ) are surrounded by blank lines

Output:
- tools/low-risk-format-fixes.patch  (unified diff)

Run locally: `python tools/apply_low_risk_fixes.py` (it will create the patch file)
"""
from pathlib import Path
import re
import difflib

ROOT = Path('.')
TARGET_DIRS = ['book', 'chapter']
PATCH_OUT = Path('tools/low-risk-format-fixes.patch')

heading_re = re.compile(r'^(\s{0,3}#{1,6}\s+).*')
fence_re = re.compile(r'^\s{0,3}```')

def list_md_files():
    files = []
    for d in TARGET_DIRS:
        p = ROOT / d
        if not p.exists():
            continue
        for f in p.rglob('*.md'):
            files.append(f)
    return sorted(files)

def fix_text(orig_text: str) -> str:
    lines = orig_text.splitlines()
    new_lines = []
    i = 0
    in_fence = False
    while i < len(lines):
        line = lines[i].rstrip(' \t')  # remove trailing spaces/tabs

        # detect fence start/end
        if fence_re.match(lines[i]):
            # ensure blank line before fence
            if new_lines and new_lines[-1] != '':
                new_lines.append('')
            new_lines.append(line)
            i += 1
            # copy fence content until closing fence
            while i < len(lines):
                l = lines[i].rstrip(' \t')
                new_lines.append(l)
                if fence_re.match(lines[i]):
                    i += 1
                    break
                i += 1
            # ensure blank line after fence
            if i < len(lines) and (i < len(lines) and lines[i].strip() != ''):
                new_lines.append('')
            continue

        # headings: ensure blank line before and after
        if heading_re.match(lines[i]):
            if new_lines and new_lines[-1] != '':
                new_lines.append('')
            new_lines.append(line)
            # ensure next is blank (if exists and not blank)
            if i+1 < len(lines) and lines[i+1].strip() != '':
                new_lines.append('')
            i += 1
            continue

        # default: copy
        new_lines.append(line)
        i += 1

    # Ensure single trailing newline
    text = '\n'.join(new_lines) + '\n'
    return text

def main():
    files = list_md_files()
    diffs = []
    for f in files:
        try:
            orig = f.read_text(encoding='utf-8')
        except Exception:
            continue
        fixed = fix_text(orig)
        if orig.replace('\r\n','\n') != fixed:
            diff = difflib.unified_diff(
                orig.splitlines(keepends=True),
                fixed.splitlines(keepends=True),
                fromfile=str(f),
                tofile=str(f) + '.fixed',
            )
            diffs.extend(diff)

    if not diffs:
        print('No low-risk fixes needed.')
        if PATCH_OUT.exists():
            PATCH_OUT.unlink()
        return

    PATCH_OUT.parent.mkdir(parents=True, exist_ok=True)
    PATCH_OUT.write_text(''.join(diffs), encoding='utf-8')
    print(f'Wrote patch to {PATCH_OUT} (review before applying)')

if __name__ == '__main__':
    main()
