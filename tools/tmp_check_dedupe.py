from pathlib import Path
p=Path(r'E:\DONT TOUCH\10M-2025-Testing\tools\dedupe_book.py')
s=p.read_text(encoding='utf-8')
lines=s.splitlines()
errs=[]
for i,l in enumerate(lines,1):
    if len(l)>88:
        errs.append(f"{p}: {i}: E501 line too long ({len(l)} > 88)")
# check W391: blank line at end of file
if s.endswith('\n') and lines and lines[-1].strip()=='' :
    errs.append(f"{p}: {len(lines)}: W391 blank line at end of file")
if errs:
    print('\n'.join(errs))
else:
    print('No E501/W391 found for', p)
