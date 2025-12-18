#!/usr/bin/env python3
"""Replace the content between <!-- BEGIN 第N篇 --> and <!-- END 第N篇 --> with the exact framework file content for that 第N篇."""
import sys
from pathlib import Path
if len(sys.argv)<2:
    print('Usage: replace_chapter_block.py <chapter_number>')
    raise SystemExit(2)
try:
    num=int(sys.argv[1])
except:
    print('Chapter number must be integer')
    raise SystemExit(2)
ROOT=Path(__file__).resolve().parent.parent
BOOK=ROOT / 'book' / '1208.2025.newbook.update.md'
FRAME_GLOB = ROOT / 'framework'
matches=list(FRAME_GLOB.glob(f'第{num}篇*.md'))
if not matches:
    print('Framework file for chapter',num,'not found')
    raise SystemExit(1)
FRAME=matches[0]
book_text=BOOK.read_text(encoding='utf-8')
frame_text=FRAME.read_text(encoding='utf-8')
begin=f'<!-- BEGIN 第{num}篇 -->'
end=f'<!-- END 第{num}篇 -->'
if begin not in book_text or end not in book_text:
    print('Markers not found in book for chapter',num)
    raise SystemExit(1)
start=book_text.index(begin)
end_idx=book_text.index(end,start)
new_book=book_text[:start+len(begin)] + '\n' + frame_text + '\n' + book_text[end_idx:]
# backup
BOOK.with_suffix(BOOK.suffix + f'.bak_ch{num}').write_text(book_text,encoding='utf-8')
BOOK.write_text(new_book,encoding='utf-8')
print(f'Replaced chapter {num} block with framework text. Backup saved as {BOOK.with_suffix(BOOK.suffix + f".bak_ch{num}")}')
