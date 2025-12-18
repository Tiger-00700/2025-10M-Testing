import pandas as pd
import re

md_path = 'appendix/建议明细表.md'
excel_path = 'appendix/建议明细表.xlsx'

with open(md_path, encoding='utf-8') as f:
    lines = [line.strip() for line in f if line.strip() and line.startswith('|')]

header = [h.strip() for h in lines[0].strip('|').split('|')]
rows = [[cell.strip() for cell in line.strip('|').split('|')] for line in lines[1:]]

# 过滤掉与表头长度不一致的行（如多余分隔线）
rows = [row for row in rows if len(row) == len(header)]

df = pd.DataFrame(rows, columns=header)
df.to_excel(excel_path, index=False)

print(f'已导出 {len(rows)} 行到 {excel_path}')
