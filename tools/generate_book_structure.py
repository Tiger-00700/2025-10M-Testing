#!/usr/bin/env python3
import re, json, os
book='book/1022.2025.book.md'
out_json='tools/book-structure.json'
out_txt='tools/book-structure.txt'
text=open(book,encoding='utf-8').read().splitlines()
entries=[]
pat=re.compile(r"^(?:#{1,6}\s*)?(.*?第\s*(\d+)\s*章\s*(.*))$")
for i,line in enumerate(text, start=1):
    m=pat.search(line)
    if m:
        full=m.group(1).strip()
        num=m.group(2)
        title=m.group(3).strip()
        entries.append({'index':len(entries)+1,'line':i,'chapter_number':int(num),'title':title,'full_line':full})

# fallback: also match lines starting with "第 X 章" without surrounding
pat2=re.compile(r"^\s*第\s*(\d+)\s*章\s*(.+)$")
for i,line in enumerate(text, start=1):
    if any(e['line']==i for e in entries):
        continue
    m=pat2.search(line)
    if m:
        num=m.group(1); title=m.group(2).strip()
        entries.append({'index':len(entries)+1,'line':i,'chapter_number':int(num),'title':title,'full_line':line.strip()})

# normalize fnames and search
chap_dir='chapter'
all_files=[]
if os.path.isdir(chap_dir):
    all_files=[os.path.join(chap_dir,f) for f in os.listdir(chap_dir) if os.path.isfile(os.path.join(chap_dir,f))]
else:
    print('Missing chapter directory:', chap_dir)

for e in entries:
    num=e['chapter_number']
    title=e['title']
    key1=f'第{num}章'
    token=re.sub(r"[\s\-–—:\[\]（）(){}<>]+","",title)
    matches=[]
    for f in all_files:
        fn=os.path.basename(f)
        if key1 in fn or (token and token in fn):
            matches.append(f)
    e['matches']=matches
    e['exists']=len(matches)>0

report={'summary':{'total_chapters_found':len(entries),'found_files':sum(1 for e in entries if e['exists'])},'chapters':entries}
open(out_json,'w',encoding='utf-8').write(json.dumps(report,ensure_ascii=False,indent=2))
with open(out_txt,'w',encoding='utf-8') as fh:
    fh.write(f"Book structure parsed from {book}\n")
    fh.write(f"Chapters found: {len(entries)}; with matching files: {report['summary']['found_files']}\n\n")
    for e in entries:
        fh.write(f"{e['index']:02d}. 第{e['chapter_number']}章 {e['title']} (line {e['line']})\n")
        if e['exists']:
            for m in e['matches']:
                fh.write(f"    - MATCH: {m}\n")
        else:
            fh.write(f"    - MISSING: no chapter file matched\n")

print('Wrote', out_json, 'and', out_txt)
