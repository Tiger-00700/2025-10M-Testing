"""
Extract fenced code blocks from book markdown into files under
examples/extracted/.

Produces a manifest JSON at tools/reports/extracted_codeblocks_manifest-<timestamp>.json

Usage:
    python tools/extract_codeblocks_from_book.py \
        --book book/1022.2025.newbook.cleaned.md \
        --out examples/extracted \
        --manifest tools/reports

This script DOES NOT modify the book file. It writes extracted files and a
manifest mapping.
"""
import os
import re
import json
import argparse
from datetime import datetime

LANG_EXT = {
    'python': 'py',
    'py': 'py',
    'bash': 'sh',
    'sh': 'sh',
    'shell': 'sh',
    'yml': 'yml',
    'yaml': 'yml',
    'json': 'json',
    'xml': 'xml',
    'html': 'html',
    'java': 'java',
    'sql': 'sql',
    'scala': 'scala',
    'go': 'go',
    'js': 'js',
    'javascript': 'js',
    'text': 'txt',
}

FENCE_RE = re.compile(r'^\s*```\s*([a-zA-Z0-9_+-]*)\s*$')
FENCE_CLOSE_RE = re.compile(r'^\s*```\s*$')


def ensure_dir(p):
    os.makedirs(p, exist_ok=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--book', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--manifest', required=True)
    args = parser.parse_args()

    book = args.book
    out_dir = args.out
    manifest_dir = args.manifest
    ensure_dir(out_dir)
    ensure_dir(manifest_dir)

    with open(book, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    in_fence = False
    fence_lang = ''
    fence_start = 0
    buffer = []
    blocks = []

    for i, raw in enumerate(lines, start=1):
        line = raw.rstrip('\n')
        if not in_fence:
            m = FENCE_RE.match(line)
            if m:
                in_fence = True
                fence_lang = m.group(1).strip().lower() if m.group(1) else ''
                fence_start = i
                buffer = []
        else:
            if FENCE_CLOSE_RE.match(line):
                # end fence
                fence_end = i
                content = '\n'.join(buffer)
                # ensure trailing newline
                if content and not content.endswith('\n'):
                    content += '\n'
                blocks.append({
                    'start': fence_start,
                    'end': fence_end,
                    'lang': fence_lang,
                    'content': content,
                })
                in_fence = False
                fence_lang = ''
                buffer = []
            else:
                buffer.append(raw.rstrip('\n'))

    ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    manifest = {
        'book': book,
        'generated_at': ts,
        'blocks': []
    }

    for idx, blk in enumerate(blocks, start=1):
        lang = blk['lang'] or 'text'
        ext = LANG_EXT.get(lang, 'txt')
        # create filename: chapter-block-<idx>.<ext>
        filename = f'book__block{idx:04d}.{ext}'
        filepath = os.path.join(out_dir, filename)
        # avoid overwriting existing file by adding suffix if exists
        base, extn = os.path.splitext(filepath)
        n = 1
        while os.path.exists(filepath):
            filepath = f"{base}_{n}{extn}"
            n += 1
        with open(filepath, 'w', encoding='utf-8', newline='\n') as wf:
            wf.write(blk['content'])
        manifest['blocks'].append({
            'index': idx,
            'start_line': blk['start'],
            'end_line': blk['end'],
            'lang': lang,
            'out_relpath': os.path.relpath(filepath).replace('\\', '/'),
            'out_abspath': os.path.abspath(filepath)
        })

    manifest_path = os.path.join(
        manifest_dir,
        f"extracted_codeblocks_manifest-{ts}.json",
    )
    with open(manifest_path, 'w', encoding='utf-8') as mf:
        json.dump(manifest, mf, ensure_ascii=False, indent=2)

    msg = (
        f"Wrote {len(manifest['blocks'])} blocks to {out_dir}. "
        f"Manifest: {manifest_path}"
    )
    print(msg)


if __name__ == '__main__':
    main()
