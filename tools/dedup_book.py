#!/usr/bin/env python3
"""Deduplicate exact repeated paragraphs in a markdown file.
Usage: python tools/dedup_book.py <file>
"""
import sys
from pathlib import Path

def dedup_file(path: Path):
    text = path.read_text(encoding='utf-8')
    # Split into paragraphs by two or more newlines
    parts = []
    buf = []
    for line in text.splitlines():
        # Keep line endings normalized
        buf.append(line)
        if line.strip() == '':
            parts.append('\n'.join(buf).rstrip())
            buf = []
    if buf:
        parts.append('\n'.join(buf).rstrip())
    seen = set()
    out_parts = []
    for p in parts:
        if p in seen:
            continue
        seen.add(p)
        out_parts.append(p)
    new_text = '\n\n'.join(out_parts).strip() + '\n'
    backup = path.with_suffix(path.suffix + '.bak')
    path.replace(backup)
    path.write_text(new_text, encoding='utf-8')
    print(f"Deduplicated {path}, backup at {backup}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: dedup_book.py <file>')
        sys.exit(2)
    dedup_file(Path(sys.argv[1]))
