import re
text = open('book/1208.2025.newbook.update.md','r',encoding='utf-8').read()
for i in range(1,8):
    pat = re.compile(r"<!--\s*BEGIN\s*第"+str(i)+r"篇\s*-->", re.M)
    m = pat.search(text)
    print(i, 'BEGIN found' if m else 'BEGIN not found')
    if m:
        print('  ->', repr(text[m.start():m.end()]))
    pat2 = re.compile(r"<!--\s*END\s*第"+str(i)+r"篇\s*-->", re.M)
    m2 = pat2.search(text)
    print(i, 'END found' if m2 else 'END not found')
    if m2:
        print('  ->', repr(text[m2.start():m2.end()]))
