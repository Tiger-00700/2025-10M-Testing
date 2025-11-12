import json
import os

IN = 'tools/duplicate-headings.json'
OUT = 'tools/duplicate-headings-proposals.md'

with open(IN, 'r', encoding='utf-8') as f:
    data = json.load(f)

dups = data.get('duplicates', {})

lines = []
lines.append('# Duplicate heading rename proposals\n')
lines.append('This file proposes concrete, reversible heading-renames for duplicate headings detected across the project.\n')
lines.append('Proposal strategy: keep the first occurrence as canonical (wherever it appears), and for other occurrences append a short disambiguator derived from the source filename in parentheses. This is conservative and reversible.\n')

for idx, (heading, occurrences) in enumerate(dups.items(), start=1):
    if len(occurrences) < 2:
        continue
    lines.append('---\n')
    lines.append(f'## {idx}. "{heading}"\n')
    lines.append('\n')
    lines.append('Occurrences (canonical choice = first listed):\n')
    for i, occ in enumerate(occurrences):
        file = occ.get('file')
        line_no = occ.get('line')
        basename = os.path.splitext(os.path.basename(file))[0]
        # create a short ascii-friendly disambiguator by replacing spaces with hyphens
        disamb = ''.join(ch if ord(ch) < 128 else '-' for ch in basename).replace(' ', '-')
        suggested = heading
        # For non-canonical occurrences, propose appending a short disambiguator
        if i != 0:
            suggested = f"{heading} （来自：{basename}）"
        lines.append(f'- {file}:{line_no}  \n  - suggested heading: **{suggested}**\n')
    lines.append('\n')

with open(OUT, 'w', encoding='utf-8') as f:
    f.writelines([l + '\n' if not l.endswith('\n') else l for l in lines])

print(f'Wrote {OUT}')
