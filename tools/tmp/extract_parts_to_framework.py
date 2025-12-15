from pathlib import Path
import re

repo = Path('E:/DONT_TOUCH/10M-2025-Testing')
book = repo / 'book/1208.2025.newbook.md'
out_dir = repo / 'Framework'
out_dir.mkdir(parents=True, exist_ok=True)

text = book.read_text(encoding='utf-8')
lines = text.splitlines()

parts = []
current = None

def infer_level(title: str) -> str:
    m = re.search(r'（(入门|进阶|专家)）', title)
    if m:
        return m.group(1) + '篇'
    # fallback by keywords
    if '入门' in title:
        return '入门篇'
    if '进阶' in title:
        return '进阶篇'
    if '专家' in title:
        return '专家篇'
    return '篇'

for line in lines:
    if line.startswith('## '):
        m = re.match(r'## 第([一二三四五六七八九十]+)篇\s+(.+)', line)
        if m:
            # flush previous
            if current:
                parts.append(current)
            part_cn = m.group(1)
            # convert Chinese numerals to Arabic
            numerals = {
                '一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10
            }
            # handle up to 七
            total = 0
            if len(part_cn) == 1:
                total = numerals.get(part_cn, 0)
            elif len(part_cn) == 2 and part_cn[0] == '十':
                total = 10 + numerals.get(part_cn[1],0)
            else:
                # simple mapping by known parts
                mapping = {
                    '第一':1,'第二':2,'第三':3,'第四':4,'第五':5,'第六':6,'第七':7
                }
                total = mapping.get('第'+part_cn, 0)
            title = m.group(2).strip()
            level = infer_level(title)
            current = {
                'num': total,
                'title': title,
                'level': level,
                'content': line + '\n'
            }
        else:
            if current is not None:
                current['content'] += line + '\n'
    else:
        if current is not None:
            current['content'] += line + '\n'

if current:
    parts.append(current)

# Write files
for p in parts:
    # Clean title to remove brackets
    clean_title = re.sub(r'（.*?）','', p['title']).strip()
    fname = f"第{p['num']}篇-{p['level']}-{clean_title}.md"
    (out_dir / fname).write_text(p['content'], encoding='utf-8')
    print('wrote', fname)

print(f"wrote {len(parts)} parts to {out_dir}")
