#!/usr/bin/env python3
from pathlib import Path
import re
import sys

CHN_NUM = {
    '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6,
    '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
}
NUM_TO_CHN = {v: k for k, v in CHN_NUM.items()}

BASE_BOOK = Path('book/1022.2025.newbook.cleaned.md')
OUT_BOOK = Path('book/1022.2025.newbook.cleaned.new.md')
FIXED_FILES = {
    1: Path('examples/第1篇/from_book_1.candidate.fixed.md'),
    2: Path('examples/第2篇/from_book_2.candidate.fixed.md'),
    3: Path('examples/第3篇/from_book_3.candidate.fixed.md'),
    4: Path('examples/第4篇/from_book_4.candidate.fixed.md'),
    5: Path('examples/第5篇/from_book_5.candidate.fixed.md'),
    6: Path('examples/第6篇/from_book_6.candidate.fixed.md'),
}

PART_HEAD_RE = re.compile(r'^\s*##\s*第([一二三四五六1-6])篇')
HEAD_RE = re.compile(r'^(#{1,6})(\s+)(.+)$')


def adjust_heading_levels(text: str, target_min_level: int = 2) -> str:
    lines = text.splitlines()
    in_code = False
    in_html = False
    min_level = None
    # Detect minimal heading level outside code/html comments
    for L in lines:
        S = L.strip()
        if S.startswith('```'):
            in_code = not in_code
            continue
        if in_code:
            continue
        if not in_html and '<!--' in L:
            start = L.find('<!--'); end = L.find('-->')
            if end == -1 or end < start:
                in_html = True
        elif in_html and '-->' in L:
            in_html = False
        if in_html:
            continue
        m = HEAD_RE.match(L)
        if m:
            lvl = len(m.group(1))
            min_level = lvl if min_level is None else min(min_level, lvl)
    if min_level is None:
        return text
    offset = max(0, target_min_level - min_level)
    if offset == 0:
        return text
    out = []
    in_code = False
    in_html = False
    for L in lines:
        S = L.strip()
        if S.startswith('```'):
            in_code = not in_code
            out.append(L)
            continue
        if in_code:
            out.append(L)
            continue
        if not in_html and '<!--' in L:
            start = L.find('<!--'); end = L.find('-->')
            if end == -1 or end < start:
                in_html = True
        elif in_html and '-->' in L:
            in_html = False
        if in_html:
            out.append(L)
            continue
        m = HEAD_RE.match(L)
        if m:
            hashes, space, rest = m.groups()
            new_level = min(6, len(hashes) + offset)
            out.append('#' * new_level + space + rest)
        else:
            out.append(L)
    return '\n'.join(out) + ('\n' if text.endswith('\n') else '')


def load_fixed_parts():
    fixed = {}
    for n, p in FIXED_FILES.items():
        if p.exists():
            fixed_text = p.read_text(encoding='utf8')
            fixed[n] = adjust_heading_levels(fixed_text, target_min_level=2)
    return fixed


def merge_book(base_text: str, fixed_parts: dict[int, str]) -> str:
    lines = base_text.splitlines()
    out = []
    i = 0
    N = len(lines)
    while i < N:
        L = lines[i]
        m = PART_HEAD_RE.match(L)
        if not m:
            out.append(L)
            i += 1
            continue
        chn = m.group(1)
        part_num = CHN_NUM.get(chn)
        # Find end of this part: next part heading or EOF
        j = i + 1
        while j < N and not PART_HEAD_RE.match(lines[j]):
            j += 1
        # Replace block [i, j) if fixed exists; else keep original
        if part_num in fixed_parts:
            # Insert fixed part content directly (already adjusted heading levels)
            fixed_block = fixed_parts[part_num]
            original_heading = lines[i]
            fixed_lines = fixed_block.splitlines()
            has_part_heading = False
            # Check first few lines for a part-level heading like "## 第N篇"
            for k in range(min(10, len(fixed_lines))):
                if PART_HEAD_RE.match(fixed_lines[k]):
                    has_part_heading = True
                    break
            # Ensure separation
            if out and out[-1].strip() != '':
                out.append('')
            if has_part_heading:
                out.append(fixed_block.rstrip('\n'))
            else:
                out.append(original_heading.rstrip('\n'))
                out.append('')
                out.append(fixed_block.rstrip('\n'))
            if j < N and (out and out[-1].strip() != ''):
                out.append('')
        else:
            out.extend(lines[i:j])
        i = j
    new_text = '\n'.join(out)
    if base_text.endswith('\n') and not new_text.endswith('\n'):
        new_text += '\n'
    return new_text


def main():
    if not BASE_BOOK.exists():
        print(f'Base book not found: {BASE_BOOK}', file=sys.stderr)
        raise SystemExit(2)
    base_text = BASE_BOOK.read_text(encoding='utf8')
    fixed_parts = load_fixed_parts()
    merged = merge_book(base_text, fixed_parts)
    OUT_BOOK.parent.mkdir(parents=True, exist_ok=True)
    OUT_BOOK.write_text(merged, encoding='utf8')
    print(f'Wrote merged book: {OUT_BOOK} (parts merged: {sorted(fixed_parts.keys())})')


if __name__ == '__main__':
    main()
