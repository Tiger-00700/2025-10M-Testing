"""Replace fenced code blocks in the book markdown with links to extracted files based on manifest.
Creates a backup of the original markdown as .bak before editing.

Usage:
  python tools/replace_codeblocks_with_links.py --book book/1022.2025.newbook.cleaned.md --manifest tools/reports/extracted_codeblocks_manifest-YYYYMMDDT....json
"""
import argparse
import json
import shutil


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--book', required=True)
    parser.add_argument('--manifest', required=True)
    args = parser.parse_args()

    book = args.book
    manifest_path = args.manifest

    with open(manifest_path, 'r', encoding='utf-8') as mf:
        manifest = json.load(mf)

    # sort blocks by start_line descending to replace from bottom up
    blocks = sorted(manifest.get('blocks', []), key=lambda b: b['start_line'], reverse=True)

    with open(book, 'r', encoding='utf-8') as bf:
        lines = bf.readlines()

    # backup
    shutil.copyfile(book, book + '.bak')
    print(f'Backup written to {book}.bak')

    for blk in blocks:
        s = blk['start_line'] - 1
        e = blk['end_line']  # inclusive index, e is 1-based
        out_rel = blk['out_relpath']
        # Use relative path from book to examples as '../' prefix if not already
        link_target = '../' + out_rel if not out_rel.startswith('..') else out_rel
        replacement = f"[示例附件: {out_rel}]({link_target})\n"
        # Replace lines s..e-1 (since e is line number of closing fence)
        # lines list is 0-based
        print(f"Replacing lines {s+1}-{e} with link to {out_rel}")
        lines[s:e] = [replacement]

    with open(book, 'w', encoding='utf-8', newline='\n') as bf:
        bf.writelines(lines)

    print('Done. Please review the modified markdown and commit changes as appropriate.')


if __name__ == '__main__':
    main()
