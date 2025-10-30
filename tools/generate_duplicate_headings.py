#!/usr/bin/env python3
"""
Scan `book/` and `chapter/` for Markdown headings and report duplicates.

Outputs:
- tools/duplicate-headings.json
- tools/duplicate-headings.txt

The report lists heading text (normalized), total occurrences and file/line locations.
"""
import re
import json
import os
from collections import defaultdict

OUT_JSON = "tools/duplicate-headings.json"
OUT_TXT = "tools/duplicate-headings.txt"

def find_markdown_files(root_dirs=("book", "chapter")):
    files = []
    for rd in root_dirs:
        if not os.path.isdir(rd):
            continue
        for dirpath, _, filenames in os.walk(rd):
            for fn in filenames:
                if fn.lower().endswith('.md'):
                    files.append(os.path.join(dirpath, fn))
    return files

def normalize_heading(text):
    text = text.strip()
    # collapse whitespace
    text = re.sub(r"\s+", " ", text)
    # remove trailing punctuation often used in headings
    return text

def main():
    files = find_markdown_files()
    headings = defaultdict(list)  # heading -> list of (file, line)
    h_re = re.compile(r"^\s{0,3}(#{1,6})\s+(.*)$")

    for f in files:
        try:
            with open(f, encoding='utf-8') as fh:
                for i, line in enumerate(fh, start=1):
                    m = h_re.match(line)
                    if m:
                        text = normalize_heading(m.group(2))
                        headings[text].append({'file': f, 'line': i})
        except Exception:
            # ignore unreadable files
            continue

    duplicates = {h: locs for h, locs in headings.items() if len(locs) > 1}

    out = {'total_headings': len(headings), 'duplicate_count': len(duplicates), 'duplicates': duplicates}

    with open(OUT_JSON, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)

    with open(OUT_TXT, 'w', encoding='utf-8') as fh:
        fh.write(f"Duplicate headings report\nFound {len(duplicates)} headings that appear multiple times across files.\n\n")
        for h, locs in sorted(duplicates.items(), key=lambda kv: -len(kv[1])):
            fh.write(f"Heading: {h} (occurrences: {len(locs)})\n")
            for loc in locs:
                fh.write(f"  - {loc['file']}: line {loc['line']}\n")
            fh.write('\n')

    print(f"Wrote {OUT_JSON} and {OUT_TXT}")

if __name__ == '__main__':
    main()
