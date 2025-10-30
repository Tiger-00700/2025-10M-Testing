#!/usr/bin/env python3
from pathlib import Path
import re
from glob import glob

TARGETS = ["book/**/*.md", "chapter/**/*.md", "PR_DESCRIPTION.md"]
OUT_LOG = 'tools/md012-autofix.log'

pattern = re.compile(r"\n{3,}")

changed_files = []
notes = []

for g in TARGETS:
    for p in sorted(set(glob(g, recursive=True))):
        if p.startswith('tools/'):
            continue
        path = Path(p)
        if not path.is_file():
            continue
        text = path.read_text(encoding='utf-8')
        new = pattern.sub('\n\n', text)
        if new != text:
            path.write_text(new, encoding='utf-8')
            changed_files.append(p)
            notes.append(f'Collapsed blank lines in {p}')

if notes:
    Path(OUT_LOG).write_text('\n'.join(notes) + '\n', encoding='utf-8')

print('FILES_CHANGED:', len(changed_files))
for f in changed_files:
    print(f)
