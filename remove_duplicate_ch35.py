import re

# Read the file
with open('framework/第8篇-专家篇-趋势与平台化.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the duplicate 第35章 by finding and removing it
lines = content.split('\n')
new_lines = []
skip_until_next_chapter = False

for line in lines:
    if '### 第35章' in line:
        skip_until_next_chapter = True
        continue
    elif skip_until_next_chapter and line.startswith('### 第'):
        skip_until_next_chapter = False
        new_lines.append(line)
    elif not skip_until_next_chapter:
        new_lines.append(line)

# Write back
with open('framework/第8篇-专家篇-趋势与平台化.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(new_lines))

print('Removed duplicate 第35章 from 第8篇')