#!/usr/bin/env python3
import re
from pathlib import Path
from glob import glob
import tempfile
import subprocess

RAW = 'tools/markdownlint-project-raw.txt'
OUT_PATCH = 'tools/markdown-md013-suggestions.patch'

# Collect files that have MD013 from the linter raw output
md013_files = set()
if Path(RAW).exists():
    for line in Path(RAW).read_text(encoding='utf-8').splitlines():
        m = re.match(r'^(?P<file>[^:]+):(?P<line>\d+)\s+MD013', line)
        if m:
            md013_files.add(m.group('file'))

# Fallback: if no raw file, scan all markdown files
if not md013_files:
    md013_files = set(glob('book/**/*.md', recursive=True) + glob('chapter/**/*.md', recursive=True) + ['PR_DESCRIPTION.md'])
    md013_files = {f for f in md013_files if Path(f).is_file()}

# Wrapping logic: only wrap plain paragraph lines (not headings, lists, blockquotes, tables, code fences)
MAX = 80

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

changed = []
with tempfile.TemporaryDirectory() as td:
    tdpath = Path(td)
    for f in sorted(md013_files):
        # skip tools/ and non-md
        if f.startswith('tools/'):
            continue
        p = Path(f)
        if not p.exists():
            continue
        text = p.read_text(encoding='utf-8')
        lines = text.splitlines()
        out_lines = []
        in_fence = False
        fence_marker = None
        modified = False
        for i, line in enumerate(lines):
            stripped = line.lstrip()
            # detect fence start/end
            if stripped.startswith('```'):
                if not in_fence:
                    in_fence = True
                    fence_marker = stripped
                else:
                    in_fence = False
                    fence_marker = None
                out_lines.append(line)
                continue
            if in_fence:
                out_lines.append(line)
                continue
            # skip headings, lists, blockquotes, tables, indented code
            if re.match(r'^#{1,6}\s', line) or re.match(r'^[>\s]*([-+*]|\d+\.)\s+', line) or line.startswith('>') or line.startswith('|') or line.startswith('    ') or line.strip()=='' or line.strip().startswith('<!--'):
                out_lines.append(line)
                continue
            # also skip lines containing URLs (bare URLs) to avoid breaking them
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
            changed.append(f)
            newp = tdpath / f
            newp.parent.mkdir(parents=True, exist_ok=True)
            newp.write_text('\n'.join(out_lines) + '\n', encoding='utf-8')

    # build unified diff using git --no-index between original and temp modified files
    if changed:
        parts = []
        for f in changed:
            orig = Path(f).absolute()
            mod = Path(td) / f
            # ensure parent exists
            parts.extend(['--no-index', str(orig), str(mod)])
        # Instead of batching, produce a single diff by running git diff --no-index for all file pairs
        # We'll run git diff --no-index <orig> <mod> for each and append
        with open(OUT_PATCH, 'w', encoding='utf-8') as outf:
            for f in changed:
                orig = Path(f).absolute()
                mod = Path(td) / f
                try:
                    res = subprocess.run(['git','diff','--no-index','--','-U3', str(orig), str(mod)], capture_output=True, text=True)
                    outf.write(res.stdout)
                except Exception as e:
                    outf.write(f'# Failed to diff {f}: {e}\n')
    else:
        Path(OUT_PATCH).write_text('# No MD013 modifications generated\n', encoding='utf-8')

print('WROTE PATCH:', OUT_PATCH)
print('FILES_PROPOSED:', len(changed))
for f in changed:
    print(f)
