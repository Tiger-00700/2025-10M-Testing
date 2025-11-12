import json
import os
from collections import defaultdict

IN_JSON = 'tools/duplicate-headings.json'
OUT_LOG = 'tools/duplicate-headings-applied.log'

with open(IN_JSON,'r',encoding='utf-8') as f:
    data = json.load(f)

dups = data.get('duplicates', {})
# collect replacements per file: list of (line_no, old, new)
replacements = defaultdict(list)

for heading, occs in dups.items():
    if len(occs) < 2:
        continue
    for i, occ in enumerate(occs):
        if i == 0:
            continue
        file = occ['file']
        line_no = occ['line']
        basename = os.path.splitext(os.path.basename(file))[0]
        disamb = basename
        new_heading = f"{heading} （来自：{disamb}）"
        replacements[file].append((line_no, heading, new_heading))

changed_files = []
notes = []

for file, reps in replacements.items():
    path = os.path.join(os.getcwd(), file)
    if not os.path.exists(path):
        notes.append(f"SKIP (missing): {file}")
        continue
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    # sort reps descending by line to avoid shifting
    reps_sorted = sorted(reps, key=lambda x: x[0], reverse=True)
    modified = False
    for line_no, old, new in reps_sorted:
        idx = line_no - 1
        if idx < 0 or idx >= len(lines):
            notes.append(f"LINE OOB {file}:{line_no}")
            continue
        orig_line = lines[idx].rstrip('\n')
        if old in orig_line:
            new_line = orig_line.replace(old, new)
            if new_line != orig_line:
                lines[idx] = new_line + '\n'
                modified = True
                notes.append(f"REPLACED {file}:{line_no} -- '{old[:40]}...' -> '{new[:40]}...'")
        else:
            # try a looser match: strip punctuation and compare
            if orig_line.strip() == old.strip():
                lines[idx] = new + '\n'
                modified = True
                notes.append(f"REPLACED exact {file}:{line_no}")
            else:
                notes.append(f"NO MATCH {file}:{line_no} -- line does not contain expected heading")
    if modified:
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        changed_files.append(file)

with open(OUT_LOG, 'w', encoding='utf-8') as f:
    f.write('\n'.join(notes))

print('WROTE LOG:', OUT_LOG)
print('FILES_CHANGED:', len(changed_files))
for cf in changed_files:
    print(cf)
