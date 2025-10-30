import json
j=json.load(open('tools/content-lint-triage.json',encoding='utf-8'))
files=j['files']
summary=[]
for f,items in files.items():
    total=sum(it['count'] for it in items)
    summary.append((total,f,items))
summary.sort(reverse=True)
for i,(tot,f,items) in enumerate(summary[:10],start=1):
    print(f"{i}. {f} — total_issues={tot} — rules={[ (it['rule'],it['count']) for it in items ]}")
