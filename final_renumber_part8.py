import re

# Read the file
with open('framework/第8篇-专家篇-趋势与平台化.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Update chapter numbers: 31->33, 32->34
content = re.sub(r'### 第31章', '### 第33章', content)
content = re.sub(r'### 第32章', '### 第34章', content)

# Update anchor IDs
content = re.sub(r'<a id="第31章', '<a id="第33章', content)
content = re.sub(r'<a id="第32章', '<a id="第34章', content)

# Update section numbers
content = re.sub(r'#### 31\.([0-9]+)', r'#### 33.\1', content)
content = re.sub(r'#### 32\.([0-9]+)', r'#### 34.\1', content)

# Write back
with open('framework/第8篇-专家篇-趋势与平台化.md', 'w', encoding='utf-8') as f:
    f.write(content)

print('Updated chapter numbers in 第8篇 to 33-34')