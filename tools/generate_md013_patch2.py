#!/usr/bin/env python3
import re
from pathlib import Path
from glob import glob
import difflib

RAW = 'tools/markdownlint-project-raw.txt'
OUT_PATCH = 'tools/markdown-md013-suggestions.patch'
OUT_DIR = Path('tools/_md013_suggest')
MAX = 80

# Collect files with MD013
md013_files = []
if Path(RAW).exists():
    for line in Path(RAW).read_text(encoding='utf-8').splitlines():
        m = re.match(r'^(?P<file>[^:]+):(?P<line>\d+)\s+MD013', line)
        if m:
            md013_files.append(m.group('file'))

if not md013_files:
    md013_files = glob('book/**/*.md', recursive=True) + glob('chapter/**/*.md', recursive=True) + ['PR_DESCRIPTION.md']
    md013_files = [f for f in md013_files if Path(f).is_file()]

md013_files = sorted(set(md013_files))

def wrap_line(line, maxcol=MAX):
    if len(line) <= maxcol:
        return [line]
    words = line.split(' ')
    out = []
    cur = ''
    for w in words:
        if cur == '':
            cur = w
        elif len(cur) + 1 + len(w) <= maxcol:
            cur = cur + ' ' + w
        else:
            out.append(cur)
            cur = w
    if cur:
        out.append(cur)
    return out

OUT_DIR.mkdir(exist_ok=True)
changes = []
patch_lines = []
for f in md013_files:
    if f.startswith('tools/'):
        continue
    p = Path(f)
    if not p.exists():
        continue
    text = p.read_text(encoding='utf-8')
    lines = text.splitlines()
    out_lines = []
    in_fence = False
    modified = False
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        if stripped.startswith('```'):
            in_fence = not in_fence
            out_lines.append(line)
            continue
        if in_fence:
            out_lines.append(line)
            continue
        # skip headings, lists, blockquotes, tables, indented code, html comments
        if re.match(r'^#{1,6}\s', line) or re.match(r'^\s*(?:[-+*]|\d+\.)\s+', line) or line.startswith('>') or line.startswith('|') or line.startswith('    ') or line.strip()=='' or line.strip().startswith('<!--'):
            out_lines.append(line)
            continue
        if 'http://' in line or 'https://' in line or re.search(r'\S+@\S+\.\S+', line):
            out_lines.append(line)
            continue
        if len(line) > MAX:
            wrapped = wrap_line(line, MAX)
            if len(wrapped) > 1:
                out_lines.extend(wrapped)
                modified = True
                continue
        out_lines.append(line)
    if modified:
        changes.append(f)
        new_path = OUT_DIR / f
        new_path.parent.mkdir(parents=True, exist_ok=True)
        new_text = '\n'.join(out_lines) + '\n'
        new_path.write_text(new_text, encoding='utf-8')
        # produce unified diff
        diff = difflib.unified_diff(
            lines,
            out_lines + [''],
            fromfile=str(p),
            tofile=str(p) + '.md013.suggest',
            lineterm='\n'
        )
        patch_lines.extend(list(diff))

if not patch_lines:
    Path(OUT_PATCH).write_text('# No MD013 suggestions generated\n', encoding='utf-8')
else:
    Path(OUT_PATCH).write_text(''.join(patch_lines), encoding='utf-8')

print('WROTE PATCH:', OUT_PATCH)
print('FILES_PROPOSED:', len(changes))
for f in changes:
    print(f)
