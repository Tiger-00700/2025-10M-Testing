import re

# Read the file
with open('framework/第6篇-专家篇-案例与性能.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Update chapter numbers: 20->24, 21->25, 22->26, 23->27, 24->28
content = re.sub(r'### 第20章', '### 第24章', content)
content = re.sub(r'### 第21章', '### 第25章', content)
content = re.sub(r'### 第22章', '### 第26章', content)
content = re.sub(r'### 第23章', '### 第27章', content)
content = re.sub(r'### 第24章', '### 第28章', content)

# Update anchor IDs accordingly
content = re.sub(r'<a id="第20章', '<a id="第24章', content)
content = re.sub(r'<a id="第21章', '<a id="第25章', content)
content = re.sub(r'<a id="第22章', '<a id="第26章', content)
content = re.sub(r'<a id="第23章', '<a id="第27章', content)
content = re.sub(r'<a id="第24章', '<a id="第28章', content)

# Update section numbers within chapters
content = re.sub(r'#### 20\.([0-9]+)', r'#### 24.\1', content)
content = re.sub(r'#### 21\.([0-9]+)', r'#### 25.\1', content)
content = re.sub(r'#### 22\.([0-9]+)', r'#### 26.\1', content)
content = re.sub(r'#### 23\.([0-9]+)', r'#### 27.\1', content)
content = re.sub(r'#### 24\.([0-9]+)', r'#### 28.\1', content)

# Write back
with open('framework/第6篇-专家篇-案例与性能.md', 'w', encoding='utf-8') as f:
    f.write(content)

print('Updated chapter numbers in 第6篇')