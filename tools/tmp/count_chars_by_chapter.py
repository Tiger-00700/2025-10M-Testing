from pathlib import Path
import re
import csv
import datetime

book_path = Path('E:/DONT_TOUCH/10M-2025-Testing/book/1208.2025.newbook.md')
text = book_path.read_text(encoding='utf-8')
lines = text.splitlines()

# Identify parts and chapters based on headings
chapters = []
current = None
part_no = 0
for line in lines:
    if line.startswith('## 第') and '篇' in line:
        part_no += 1
    m = re.match(r"### 第(\d+)章\s+(.+)", line)
    if m:
        # flush previous
        if current:
            chapters.append(current)
        title_full = m.group(2).strip()
        title_clean = re.sub(r"【.*?】", "", title_full).strip()
        current = {
            'part': part_no,
            'chapter': int(m.group(1)),
            'title': title_clean,
            'content': ''
        }
    else:
        if current is not None:
            current['content'] += line + '\n'

if current:
    chapters.append(current)

# Compute counts
rows = []
for ch in chapters:
    s = ch['content']
    total_chars = len(s)
    chars_no_ws = len(re.sub(r"\s+", "", s))
    words_like = len(re.findall(r"\w+", s))
    rows.append({
        'part': ch['part'],
        'chapter': ch['chapter'],
        'title': ch['title'],
        'total_chars': total_chars,
        'chars_excluding_whitespace': chars_no_ws,
        'word_tokens_ascii': words_like,
    })

# Write CSV and summary
ts = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
report_dir = Path('E:/DONT_TOUCH/10M-2025-Testing/tools/reports')
report_dir.mkdir(parents=True, exist_ok=True)
csv_path = report_dir / f'book_1208_charcounts_by_chapter_{ts}.csv'
with csv_path.open('w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['part','chapter','title','total_chars','chars_excluding_whitespace','word_tokens_ascii'])
    w.writeheader()
    for r in rows:
        w.writerow(r)

summary_path = report_dir / f'book_1208_charcounts_by_chapter_{ts}.txt'
with summary_path.open('w', encoding='utf-8') as f:
    total_all = sum(r['total_chars'] for r in rows)
    total_no_ws = sum(r['chars_excluding_whitespace'] for r in rows)
    f.write(f'file: {book_path}\n')
    f.write(f'total_chars_sum: {total_all}\n')
    f.write(f'chars_excluding_whitespace_sum: {total_no_ws}\n')
    for r in rows:
        f.write(f"第{r['part']}篇-第{r['chapter']}章-{r['title']}: total={r['total_chars']}, no_ws={r['chars_excluding_whitespace']}\n")

print(f'csv: {csv_path}')
print(f'summary: {summary_path}')
