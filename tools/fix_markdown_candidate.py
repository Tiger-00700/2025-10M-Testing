#!/usr/bin/env python3
"""
Simple Markdown candidate fixer.

Usage:
  python tools/fix_markdown_candidate.py --glob "chapter/第1篇*" --title "第1篇 大数据测试基础" \
    --candidate examples/第1篇/from_book_1.candidate.md \
    --fixed examples/第1篇/from_book_1.candidate.fixed.md

This script concatenates matching source files, writes the candidate, applies simple
text fixes and writes the fixed output.

Fixes applied:
- Remove empty anchor tags like <a id="..."></a>
- Convert simple inline links: <a href="URL">text</a> -> [text](URL)
- Collapse 3+ consecutive newlines to 2 newlines (single blank line between paragraphs)
- Ensure first non-empty heading is H1 (promote if necessary)
- Adjust heading increments: if a heading level jumps by more than 1, reduce it to last+1

This is conservative and intended for human-in-the-loop review.
"""
import argparse
import glob
import re
from pathlib import Path


def read_sources(glob_pattern):
    files = sorted(glob.glob(glob_pattern))
    contents = []
    for p in files:
        with open(p, 'r', encoding='utf8') as f:
            contents.append(f.read())
    return files, "\n\n".join(contents)


def fix_text(s: str, title: str = None) -> str:
    # remove empty anchor tags
    s = re.sub(r"<a[^>]*>\s*</a>", "", s)
    # convert simple anchors with href to markdown links
    s = re.sub(r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>([^<]+)</a>', r'[\2](\1)', s)
    # normalize Windows line endings
    s = s.replace('\r\n', '\n')
    # collapse 3+ newlines into 2 (single blank line)
    s = re.sub(r'\n{3,}', '\n\n', s)

    lines = s.split('\n')
    # Ensure first non-empty line is H1; if not, promote first heading or insert title
    for i, L in enumerate(lines):
        if L.strip() == '':
            continue
        if re.match(r'^#{1,6}\s', L):
            # found a heading
            if not L.startswith('# '):
                # make it H1
                lines[i] = '# ' + re.sub(r'^#{1,6}\s*', '', L)
            break
        else:
            # no heading found yet, insert title as H1 if provided
            if title:
                lines.insert(i, f'# {title}')
            else:
                lines.insert(i, '#')
            break

    # Adjust heading increments to not jump more than +1, and remove duplicate headings
    last_level = 0
    seen_headings = set()
    out_lines = []
    in_code_block = False
    import textwrap
    for L in lines:
        if L.strip().startswith('```'):
            in_code_block = not in_code_block
            out_lines.append(L)
            continue
        if in_code_block:
            out_lines.append(L)
            continue
        m = re.match(r'^(#{1,6})\s+(.*)$', L)
        if m:
            lvl = len(m.group(1))
            text = m.group(2).strip()
            # deduplicate exact heading text
            if text in seen_headings:
                # skip this heading line (keep content below)
                continue
            seen_headings.add(text)
            if last_level == 0:
                last_level = lvl
            else:
                if lvl > last_level + 1:
                    new_lvl = last_level + 1
                    L = ('#' * new_lvl) + ' ' + text
                    lvl = new_lvl
            last_level = lvl
            out_lines.append(L)
        else:
            # wrap long paragraph lines (naive): if it's a normal paragraph, wrap to 80
            if L.strip() != '' and not L.strip().startswith('>') and not re.match(r'^\s*[-*+]\s', L):
                wrapped = '\n'.join(textwrap.fill(L, width=80, replace_whitespace=False).split('\n'))
                out_lines.append(wrapped)
            else:
                out_lines.append(L)

    lines = out_lines

    # collapse multiple blank lines to a single blank line
    collapsed = []
    blank_count = 0
    for L in lines:
        if L.strip() == '':
            blank_count += 1
            if blank_count == 1:
                collapsed.append('')
            else:
                # skip extra blank lines
                continue
        else:
            blank_count = 0
            collapsed.append(L)

    # second pass: wrap any remaining long lines (naive), skipping code blocks and tables
    final_lines = []
    in_code = False
    import textwrap
    for L in collapsed:
        if L.strip().startswith('```'):
            in_code = not in_code
            final_lines.append(L)
            continue
        if in_code or L.strip().startswith('|'):
            final_lines.append(L)
            continue
        if len(L) > 80 and L.strip() != '' and not L.lstrip().startswith(('-', '*', '+')) and not L.lstrip().startswith('>'):
            indent = len(L) - len(L.lstrip(' '))
            wrapped = textwrap.fill(L.strip(), width=80)
            wrapped = '\n'.join((' ' * indent) + l for l in wrapped.split('\n'))
            final_lines.append(wrapped)
        else:
            final_lines.append(L)

    out = '\n'.join(final_lines)
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--glob', required=True)
    p.add_argument('--title', required=False)
    p.add_argument('--candidate', required=True)
    p.add_argument('--fixed', required=True)
    args = p.parse_args()

    files, content = read_sources(args.glob)
    if not files:
        print(f'No files matched {args.glob}', flush=True)
        raise SystemExit(2)

    cand_path = Path(args.candidate)
    cand_path.parent.mkdir(parents=True, exist_ok=True)
    cand_path.write_text(content, encoding='utf8')
    print(f'Wrote candidate: {cand_path} (from {len(files)} files)', flush=True)

    fixed = fix_text(content, title=args.title)
    fixed_path = Path(args.fixed)
    fixed_path.parent.mkdir(parents=True, exist_ok=True)
    fixed_path.write_text(fixed, encoding='utf8')
    print(f'Wrote fixed: {fixed_path}', flush=True)


if __name__ == '__main__':
    main()
