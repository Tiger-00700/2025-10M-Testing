with open('book/1208.2025.newbook.update.md','rb') as f:
    b = f.read(200)
print(repr(b))
print('\nDecoded:\n')
print(b.decode('utf-8'))
for i,ch in enumerate(b[:80]):
    print(i, hex(ch), end='\n')
