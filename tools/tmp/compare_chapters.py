from pathlib import Path
import re

repo = Path('E:/DONT_TOUCH/10M-2025-Testing')
book = repo / 'book/1208.2025.newbook.md'
chapter_dir = repo / 'chapter'

lines = book.read_text(encoding='utf-8').splitlines()
part = 0
book_order = []
for line in lines:
    if line.startswith('## 第') and '篇' in line:
        part += 1
    m = re.match(r"### 第(\d+)章\s+(.+)", line)
    if m:
        title = re.sub(r"【.*?】", "", m.group(2)).strip()
        book_order.append((part, int(m.group(1)), title))

file_entries = []
for p in chapter_dir.glob('*.md'):
    pm = re.search(r'^第(\d+)篇', p.name)
    cm = re.search(r'第(\d+)章', p.name)
    if not (pm and cm):
        continue
    file_entries.append((int(pm.group(1)), int(cm.group(1)), p.name))

file_order = sorted(file_entries, key=lambda x: (x[0], x[1]))

print(f"book chapters: {len(book_order)}")
print(f"files: {len(file_order)}\n")

print('Book order:')
for part_no, chap_no, title in book_order:
    print(f"第{part_no}篇-第{chap_no}章-{title}")

print('\nFile order:')
for part_no, chap_no, fname in file_order:
    print(fname)

# quick mismatch check
mismatch = []
for i, ((bp, bc, bt), (fp, fc, fn)) in enumerate(zip(book_order, file_order)):
    if (bp, bc) != (fp, fc):
        mismatch.append((i+1, (bp, bc), (fp, fc), fn, bt))

if mismatch:
    print('\nMISMATCHES:')
    for idx, book_idx, file_idx, fname, btitle in mismatch:
        print(f"pos {idx}: book 第{book_idx[0]}篇-第{book_idx[1]}章 vs file 第{file_idx[0]}篇-第{file_idx[1]}章 ({fname})")
else:
    print('\nOrder matches by part/chapter numbering')
