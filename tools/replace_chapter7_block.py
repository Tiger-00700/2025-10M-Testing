#!/usr/bin/env python3
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
BOOK = ROOT / 'book' / '1208.2025.newbook.update.md'
FRAME = ROOT / 'framework' / '第7篇-专家篇-趋势与平台化.md'
book_text = BOOK.read_text(encoding='utf-8')
frame_text = FRAME.read_text(encoding='utf-8')
begin = '<!-- BEGIN 第7篇 -->'
end = '<!-- END 第7篇 -->'
if begin not in book_text or end not in book_text:
    print('Markers not found in book')
    raise SystemExit(1)
start = book_text.index(begin)
# find the end marker after start
end_idx = book_text.index(end, start)
new_book = book_text[:start+len(begin)] + '\n' + frame_text + '\n' + book_text[end_idx:]
# backup
bk = BOOK.with_suffix(BOOK.suffix + '.bak7')
BOOK.write_text(new_book, encoding='utf-8')
print('Replaced chapter 7 block with framework text and wrote backup at', bk)
BOOK.write_text(new_book, encoding='utf-8')
BOOK.with_suffix(BOOK.suffix + '.bak').write_text(book_text, encoding='utf-8')
print('Backup of original file saved as', BOOK.with_suffix(BOOK.suffix + '.bak'))
print('Done')