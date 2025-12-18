#!/usr/bin/env python3
from pathlib import Path
import re

P = Path('book/1208.2025.newbook.update.md')
bak = P.with_suffix('.markers_restore.bak')
text = P.read_text(encoding='utf-8')
bak.write_text(text, encoding='utf-8')
lines = text.splitlines()

# find indices of top-level headers like "## 第X篇" where X may be Chinese numeral or Arabic
# map Chinese numerals to numbers for 1..7
cn_map = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7}
header_pat = re.compile(r"^##\s*第([0-9]+|[一二三四五六七])篇\b")
headers = []  # list of (num, line_idx)
for i, ln in enumerate(lines):
    m = header_pat.match(ln)
    if m:
        headers.append((int(m.group(1)), i))

# We'll iterate headers and insert BEGIN before header line, and END before next header (or at EOF)
out_lines = []
pos = 0
for idx, (num, line_idx) in enumerate(headers):
    # copy from pos to line_idx
    out_lines.extend(lines[pos:line_idx])
    # insert BEGIN marker
    out_lines.append(f"<!-- BEGIN 第{num}篇 -->")
    # now find where this 篇 ends: start of next header or EOF
    if idx+1 < len(headers):
        next_line_idx = headers[idx+1][1]
        # copy the 篇 content
        out_lines.extend(lines[line_idx:next_line_idx])
        # insert END marker before next header
        out_lines.append(f"<!-- END 第{num}篇 -->")
        pos = next_line_idx
    else:
        # last 篇: copy to EOF
        out_lines.extend(lines[line_idx:])
        out_lines.append(f"<!-- END 第{num}篇 -->")
        pos = len(lines)

new_text = '\n'.join(out_lines) + '\n'
P.write_text(new_text, encoding='utf-8')
print(f"Markers inserted; backup created at {bak}")

# Exit

