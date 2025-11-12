#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path('.')
TARGET_DIRS = ['book', 'chapter']

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
    while i < len(lines):
        line = lines[i].rstrip(' \t')

        # fenced code block handling
        if fence_re.match(lines[i]):
            if new_lines and new_lines[-1] != '':
                new_lines.append('')
            new_lines.append(line)
            i += 1
            while i < len(lines):
                l = lines[i].rstrip(' \t')
                new_lines.append(l)
                if fence_re.match(lines[i]):
                    i += 1
                    break
                i += 1
            if i < len(lines) and lines[i].strip() != '':
                new_lines.append('')
            continue

        # heading handling
        if heading_re.match(lines[i]):
            if new_lines and new_lines[-1] != '':
                new_lines.append('')
            new_lines.append(line)
            if i+1 < len(lines) and lines[i+1].strip() != '':
                new_lines.append('')
            i += 1
            continue

        new_lines.append(line)
        i += 1

    return '\n'.join(new_lines) + '\n'

def main():
    files = list_md_files()
    changed = []
    for f in files:
        try:
            orig = f.read_text(encoding='utf-8')
        except Exception:
            continue
        fixed = fix_text(orig.replace('\r\n','\n'))
        if orig.replace('\r\n','\n') != fixed:
            f.write_text(fixed, encoding='utf-8')
            changed.append(f)

    if not changed:
        print('No files changed')
    else:
        print('Updated', len(changed), 'files:')
        for p in changed:
            print(' -', p)

if __name__ == '__main__':
    main()
