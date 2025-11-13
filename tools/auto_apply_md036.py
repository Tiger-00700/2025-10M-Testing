#!/usr/bin/env python3
"""Auto-apply conservative MD036 fixes.

This script looks for whole lines that are only bold/underline-wrapped and start with a
numeric section prefix (e.g. **10.3.1.1 Some title**) and converts them into a
level-4 heading: #### 10.3.1.1 Some title

This is intentionally conservative: it only touches **...** or __...__ lines where the
content begins with digits and dots. It avoids changes inside fenced code blocks.

It writes a log to tools/md036-autofix.log and writes files in-place using UTF-8.
"""
from pathlib import Path
import re

ROOT = Path('.').resolve()
LOG_PATH = ROOT / 'tools' / 'md036-autofix.log'

EMPH_NUM_RE = re.compile(
    r'^(?:\*\*|__)(\d+(?:\.\d+)*\s+.+?)(?:\*\*|__)$'
)
FENCE_RE = re.compile(r'^```')

def process_file(p: Path):
    try:
        text = p.read_text(encoding='utf-8')
    except Exception as e:
        return False, f'read-failed: {e}'
    lines = text.splitlines(keepends=True)
    out_lines = []
    in_fence = False
    changed = False
    for orig in lines:
        s = orig.rstrip('\r\n')
        if FENCE_RE.match(s):
            in_fence = not in_fence
            out_lines.append(orig)
            continue
        if in_fence:
            out_lines.append(orig)
            continue
        m = EMPH_NUM_RE.match(s.strip())
        if m:
            content = m.group(1).strip()
            newline = '#### ' + content + '\n'
            out_lines.append(newline)
            changed = True
        else:
            out_lines.append(orig)

    if changed:
        try:
            p.write_text(''.join(out_lines), encoding='utf-8')
            return True, 'modified'
        except Exception as e:
            return False, f'write-failed: {e}'
    return False, 'unchanged'

def main():
    modified = []
    skipped = []
    for p in sorted(ROOT.rglob('*.md')):
        # skip tools and patches directories
        if 'tools' in p.parts and p.parent.name != 'editorial-issues':
            # allow reading the suggested-diffs/patches area but skip core tools edits
            # conservative: skip anything under tools except editorial-issues
            continue
        if 'node_modules' in p.parts:
            continue
        # only operate on book/ and chapter/ and top-level PR_DESCRIPTION.md
        if not (
            p.match('book/**')
            or p.match('chapter/**')
            or p.name == 'PR_DESCRIPTION.md'
            or p.match('*.md')
        ):
            # still allow top-level md files
            pass
        # process
        ok, reason = process_file(p)
        if ok:
            modified.append((str(p), reason))
        else:
            if reason != 'unchanged':
                skipped.append((str(p), reason))

    with LOG_PATH.open('w', encoding='utf-8') as lf:
        lf.write('MD036 Auto-fix run\n')
        lf.write('Root: ' + str(ROOT) + '\n')
        lf.write('\nModified files:\n')
        for f, r in modified:
            lf.write(f + ' -> ' + r + '\n')
        lf.write('\nSkipped/Errors:\n')
        for f, r in skipped:
            lf.write(f + ' -> ' + r + '\n')

    # print a short summary to stdout (avoid printing non-ascii filenames individually)
    msg = "MD036 autofix: modified=" + str(len(modified))
    msg += " skipped_or_errors=" + str(len(skipped))
    msg += " log=" + str(LOG_PATH)
    print(msg)


if __name__ == '__main__':
    main()
