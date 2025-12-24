import re

# Read the file
with open('framework/第7篇-专家篇-项目与治理.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Update chapter numbers: 27->28, 28->29, 29->30, 30->31, 31->32
content = re.sub(r'### 第27章', '### 第28章', content)
content = re.sub(r'### 第28章', '### 第29章', content)
content = re.sub(r'### 第29章', '### 第30章', content)
content = re.sub(r'### 第30章', '### 第31章', content)
content = re.sub(r'### 第31章', '### 第32章', content)

# Update anchor IDs accordingly
content = re.sub(r'<a id="第27章', '<a id="第28章', content)
content = re.sub(r'<a id="第28章', '<a id="第29章', content)
content = re.sub(r'<a id="第29章', '<a id="第30章', content)
content = re.sub(r'<a id="第30章', '<a id="第31章', content)
content = re.sub(r'<a id="第31章', '<a id="第32章', content)

# Update section numbers within chapters
content = re.sub(r'#### 27\.([0-9]+)', r'#### 28.\1', content)
content = re.sub(r'#### 28\.([0-9]+)', r'#### 29.\1', content)
content = re.sub(r'#### 29\.([0-9]+)', r'#### 30.\1', content)
content = re.sub(r'#### 30\.([0-9]+)', r'#### 31.\1', content)
content = re.sub(r'#### 31\.([0-9]+)', r'#### 32.\1', content)

# Write back
with open('framework/第7篇-专家篇-项目与治理.md', 'w', encoding='utf-8') as f:
    f.write(content)

print('Updated chapter numbers in 第7篇')