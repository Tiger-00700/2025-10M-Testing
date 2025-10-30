#!/usr/bin/env python3
"""
Apply low-risk markdown fixes across book/ and chapter/:
- Remove trailing spaces (MD009)
- Ensure blank lines around top-level list items (heuristic for MD032)
- Add code-fence languages for obvious fences (MD040) when detectable

This script edits files in-place. It is conservative and logs changes.
"""
import re
from pathlib import Path

ROOT = Path('.')
TARGET_GLOBS = ['book/**/*.md', 'chapter/**/*.md']

def detect_fence_language(lines, idx):
    # lines[idx] is opening fence line with ```
    # inspect the next non-empty line for hints
    n = len(lines)
    for j in range(idx+1, min(idx+6, n)):
        s = lines[j].strip()
        if not s:
            continue
        ls = s.lower()
        # quick heuristics
        if ls.startswith('#!') or ls.startswith('http'):
            return None
        if ls.startswith('$') or ls.startswith('./') or ls.startswith('sudo'):
            return 'bash'
        if ls.startswith('select ') or 'select ' in ls or 'from ' in ls and ';' in ls:
            return 'sql'
        if ls.startswith('import ') or ls.startswith('def ') or ls.startswith('class ') or ls.startswith('print('):
            return 'python'
        if 'public class' in ls or 'System.out' in ls or ls.startswith('package '):
            return 'java'
        if ls.startswith('{') or ls.startswith('['):
            return 'json'
        if ls.startswith('---') or ':' in ls and not ls.startswith('- '):
            return 'yaml'
        if ls.startswith('<') and ls.endswith('>'):
            return 'xml'
        # detect shell scripts by shebang
        if ls.startswith('#!/bin/bash') or ls.startswith('#!/usr/bin/env bash'):
            return 'bash'
        # heuristics for powershell
        if ls.startswith('param(') or ls.startswith('function '):
            return 'powershell'
        # fallback: none
        break
    return None

def fix_file(p: Path):
    text = p.read_text(encoding='utf-8')
    lines = text.splitlines()
    changed = False
    out = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        orig_line = line
        # remove trailing spaces
        if line.rstrip('\r\n') != line.rstrip():
            line = line.rstrip()
            changed = True

        # blank line before list item (simple heuristic)
        if re.match(r'^(\s*[-+*]|\s*\d+\.)\s+', line):
            if out and out[-1].strip() != '':
                # insert a blank line before this list start to satisfy MD032
                out.append('')
                changed = True

        # code fence language addition
        if line.strip() == '```':
            lang = detect_fence_language(lines, i)
            if lang:
                line = '```' + lang
                changed = True

        out.append(line)
        # if current is a list item, ensure blank line after list end (peek next)
        if re.match(r'^(\s*[-+*]|\s*\d+\.)\s+', line):
            # look ahead: if next line exists and is not a list item and not blank, insert blank
            if i+1 < n:
                nxt = lines[i+1]
                if not re.match(r'^(\s*[-+*]|\s*\d+\.)\s+', nxt) and nxt.strip() != '':
                    out.append('')
                    changed = True
        i += 1

    if changed:
        p.write_text('\n'.join(out) + '\n', encoding='utf-8')
    return changed

def main():
    files = []
    for g in TARGET_GLOBS:
        files += list(ROOT.glob(g))
    files = [f for f in files if f.is_file()]
    modified = []
    for f in files:
        try:
            if fix_file(f):
                modified.append(str(f))
        except Exception as e:
            print(f"ERROR processing {f}: {e}")
    print(f"Modified {len(modified)} files")
    for m in modified:
        print(m)

if __name__ == '__main__':
    main()
