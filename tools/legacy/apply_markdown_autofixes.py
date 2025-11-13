#!/usr/bin/env python3
import re
from pathlib import Path

TARGET_GLOBS = ["book/**/*.md", "chapter/**/*.md", "PR_DESCRIPTION.md"]
OUT_LOG = 'tools/markdown-autofix.log'

list_item_re = re.compile(r"^\s*(?:[-+*]|\d+\.)\s+")
fence_open_re = re.compile(r"^(```+)(\s*\w+)?\s*$")

# simple heuristics for fence language detection
def detect_language(block_lines):
    sample = "\n".join(block_lines[:20])
    code_pattern = (
        r"^\s*import\s+|def\s+\w+\(|class\s+\w+|print\(|from\s+\w+"
    )
    if re.search(code_pattern, sample, re.M):
        return 'python'
    if re.search(r"\bSELECT\b|\bFROM\b|\bINSERT\b|\bUPDATE\b|\bWHERE\b", sample, re.I):
        return 'sql'
    if re.search(r"public\s+class|System\.out|package\s+", sample):
        return 'java'
    if re.search(r"^\s*#\!/.+sh|bash\b|echo\s+|#!/bin/bash", sample):
        return 'bash'
    if re.search(r"<\/?html|<div|<script", sample):
        return 'html'
    return None


def process_file(path: Path):
    changed = False
    lines = path.read_text(encoding='utf-8').splitlines()
    out: list[str] = []
    i = 0
    n = len(lines)
    log = []

    while i < n:
        line = lines[i]
        # handle fenced code blocks
        m = fence_open_re.match(line)
        if m:
            fence = m.group(1)
            lang = m.group(2).strip() if m.group(2) else ''
            # ensure previous line is blank (unless start of file)
            if len(out) > 0 and out[-1].strip() != '':
                out.append('')
                changed = True
                log.append(f'Inserted blank line before fence at {i+1}')
            # possibly add language
            block = []
            j = i + 1
            while j < n:
                if lines[j].startswith(fence):
                    break
                block.append(lines[j])
                j += 1
            if not lang:
                detected = detect_language(block)
                if detected:
                    out.append(f'{fence} {detected}')
                    changed = True
                    log.append(f'Added fence language "{detected}" at {i+1}')
                else:
                    out.append(line)
                i += 1
            else:
                out.append(line)
                i += 1
            # copy block
            while i < n:
                out.append(lines[i])
                if lines[i].startswith(fence):
                    # ensure blank line after closing fence
                    if i+1 < n and lines[i+1].strip() != '':
                        out.append('')
                        changed = True
                        log.append(f'Inserted blank line after fence at {i+1}')
                    i += 1
                    break
                i += 1
            continue

        # handle list items: ensure blank line before a list
        # that follows a non-blank non-list line
        if list_item_re.match(line):
                prev_is_nonblank_nonlist = (
                    len(out) > 0 and out[-1].strip() != '' and not list_item_re.match(out[-1])
                )
                if prev_is_nonblank_nonlist:
                    out.append('')
                    changed = True
                    log.append(f'Inserted blank line before list at {i+1}')
            out.append(line)
            # ensure after list ends, there's a blank line
            j = i + 1
            while j < n and (list_item_re.match(lines[j]) or lines[j].strip() == ''):
                out.append(lines[j])
                j += 1
            if j < n and lines[j].strip() != '':
                out.append('')
                changed = True
                log.append(f'Inserted blank line after list ending at {j}')
            i = j
            continue

        out.append(line)
        i += 1

    if changed:
        path.write_text('\n'.join(out) + '\n', encoding='utf-8')
    return changed, log


def main():
    from glob import glob
    targets = []
    for g in TARGET_GLOBS:
        targets.extend(glob(g, recursive=True))
    # de-dup and filter
    targets = sorted(set(targets))
    # filter out tools and .git
    targets = [t for t in targets if not t.startswith('tools/')]
    changed_files = []
    all_logs = []
    for t in targets:
        p = Path(t)
        if not p.exists() or not p.is_file():
            continue
        ch, log = process_file(p)
        if ch:
            changed_files.append(t)
            all_logs.extend([f'{t}: {l}' for l in log])
    if all_logs:
        Path(OUT_LOG).write_text('\n'.join(all_logs)+"\n", encoding='utf-8')
    print('FILES_CHANGED:', len(changed_files))
    for f in changed_files:
        print(f)

if __name__ == '__main__':
    main()
