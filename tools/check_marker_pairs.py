#!/usr/bin/env python3
"""Check BEGIN/END markers like <!-- BEGIN 第1篇 --> / <!-- END 第1篇 -->
and report unpaired, orphan, duplicate, or overlapping markers with context.
"""
import re
from pathlib import Path

P = Path(__file__).resolve().parent.parent / 'book' / '1208.2025.newbook.update.md'
text = P.read_text(encoding='utf-8')
lines = text.splitlines()

pattern = re.compile(r"<!--\s*(BEGIN|END)\s*第(\d+)篇\s*-->")
markers = []  # list of (type, num, line_no, col, raw)
for i, line in enumerate(lines, start=1):
    for m in pattern.finditer(line):
        typ = m.group(1)
        num = int(m.group(2))
        col = m.start()+1
        markers.append({'type':typ, 'num':num, 'line':i, 'col':col, 'raw':m.group(0)})

# Report structure
issues = []
stack = []  # stack of (num, line)
for mk in markers:
    if mk['type'] == 'BEGIN':
        # check duplicates: if same num already on stack, it's nested BEGIN for same num
        if any(s[0]==mk['num'] for s in stack):
            issues.append({'kind':'nested_begin_same_num','marker':mk, 'stack':stack.copy()})
        stack.append((mk['num'], mk['line']))
    else:  # END
        if not stack:
            issues.append({'kind':'orphan_end','marker':mk, 'stack':stack.copy()})
        else:
            top_num, top_line = stack[-1]
            if top_num == mk['num']:
                stack.pop()
            else:
                # overlapping: top doesn't match this end
                issues.append({'kind':'overlap','marker':mk, 'expected':top_num, 'top':(top_num, top_line), 'stack':stack.copy()})
                # attempt to recover: try to find matching BEGIN in stack
                found = False
                for idx in range(len(stack)-1,-1,-1):
                    if stack[idx][0] == mk['num']:
                        # pop until that
                        for _ in range(len(stack)-1, idx-1, -1):
                            stack.pop()
                        found = True
                        break
                if not found:
                    # orphan end
                    issues.append({'kind':'orphan_end_no_begin','marker':mk, 'stack':stack.copy()})

# any unclosed begins left in stack are orphan begins
for rem in stack:
    issues.append({'kind':'unclosed_begin','num':rem[0], 'line':rem[1]})

# Also check count mismatches per num
from collections import Counter
beg_counts = Counter(m['num'] for m in markers if m['type']=='BEGIN')
end_counts = Counter(m['num'] for m in markers if m['type']=='END')
counts_issues = []
all_nums = sorted(set(list(beg_counts.keys())+list(end_counts.keys())))
for n in all_nums:
    if beg_counts[n] != end_counts[n]:
        counts_issues.append({'num':n, 'beg':beg_counts[n], 'end':end_counts[n]})

# Output
print('Marker pairing check results for', P)
print('Total markers found:', len(markers))
print('BEGIN counts per num:', dict(beg_counts))
print('END counts per num:  ', dict(end_counts))
print('Count mismatches:', counts_issues)
print('\nDetected issues (detailed):')
if not issues:
    print('  None — all markers paired and properly nested (stack empty).')
else:
    for it in issues:
        kind = it['kind']
        if kind == 'nested_begin_same_num':
            mk=it['marker']
            print(f"- Nested BEGIN for same num: {mk['raw']} at line {mk['line']} (stack top: {it['stack']})")
            # print context
        elif kind == 'orphan_end':
            mk=it['marker']
            print(f"- Orphan END (no open BEGIN): {mk['raw']} at line {mk['line']}")
        elif kind == 'orphan_end_no_begin':
            mk=it['marker']
            print(f"- Orphan END (no matching BEGIN in stack): {mk['raw']} at line {mk['line']}")
        elif kind == 'overlap':
            mk=it['marker']
            print(f"- Overlapping END: {mk['raw']} at line {mk['line']}; expected END for 第{it['expected']}篇 (stack top {it['top']})")
        elif kind == 'unclosed_begin':
            print(f"- Unclosed BEGIN (missing END): BEGIN 第{it['num']}篇 at line {it['line']}")

# Also list exact marker sequence with context for human review
print('\nFull marker sequence (line: marker):')
for mk in markers:
    i=mk['line']
    context = '\n'.join(lines[max(0,i-3):min(len(lines), i+2)])
    print(f"Line {i}: {mk['raw']}")
    print('  Context:')
    for ctx_line in context.splitlines():
        print('   ', ctx_line)
    print('')

# Exit code
if issues or counts_issues:
    raise SystemExit(2)
else:
    raise SystemExit(0)
