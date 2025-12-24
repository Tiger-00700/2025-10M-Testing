import re

# Read the file
with open('framework/第6篇-专家篇-案例与性能.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the specific problematic chapter
content = re.sub(r'### 第28章 通用大数据测试案例设计【方法与模板篇】', '### 第24章 通用大数据测试案例设计【方法与模板篇】', content)
content = re.sub(r'<a id="第28章-通用大数据测试案例设计', '<a id="第24章-通用大数据测试案例设计', content)

# Fix section numbers for chapter 24
content = re.sub(r'#### 28\.([0-9]+)', r'#### 24.\1', content)

# Write back
with open('framework/第6篇-专家篇-案例与性能.md', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed 第6篇 chapter 24')