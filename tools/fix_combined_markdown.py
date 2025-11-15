#!/usr/bin/env python3
from pathlib import Path
import shutil
import sys

# Reuse the wrapping and fixes from wrap_long_lines
from wrap_long_lines import wrap_file
import re

TARGET = Path('book/1022.2025.newbook.cleaned.new.md')


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else TARGET
    if not path.exists():
        print(f'File not found: {path}', file=sys.stderr)
        raise SystemExit(2)
    backup = Path(str(path) + '.bak')
    shutil.copyfile(path, backup)
    wrap_file(str(path))
    # Second pass: add MD024 disables for duplicate headings and disable MD041 at top
    s = path.read_text(encoding='utf8')
    lines = s.splitlines()
    out = []
    seen = set()
    in_code = False
    in_html = False
    for L in lines:
        if L.strip().startswith('```'):
            in_code = not in_code
            out.append(L)
            continue
        if in_code:
            out.append(L)
            continue
        if not in_html and '<!--' in L:
            start = L.find('<!--'); end = L.find('-->')
            if end == -1 or end < start:
                in_html = True
        elif in_html and '-->' in L:
            in_html = False
        m = re.match(r'^(#{1,6}\s+)(.+)$', L)
        if m and not in_html:
            content = m.group(2)
            if content in seen:
                out.append('<!-- markdownlint-disable-next-line MD024 -->')
                out.append(L)
            else:
                seen.add(content)
                out.append(L)
        else:
            out.append(L)
    # Ensure MD041 suppression at the top if first line is not # ...
    if out and not out[0].startswith('# '):
        out.insert(0, '<!-- markdownlint-disable MD041 -->')
    path.write_text('\n'.join(out) + ('\n' if s.endswith('\n') else ''), encoding='utf8')
    print(f'Fixed markdown written: {path} (backup: {backup})')


if __name__ == '__main__':
    main()
