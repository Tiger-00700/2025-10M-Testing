import re

# Read the file
with open('framework/第7篇-专家篇-项目与治理.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the messed up chapter numbers by replacing them in reverse order
# First replace the highest numbers to avoid conflicts

# Replace 第32章 with appropriate numbers based on context
# We need to identify each chapter by its title and assign correct numbers

# Find all chapter positions and titles
chapters = []
lines = content.split('\n')
for i, line in enumerate(lines):
    if line.startswith('### 第') and '章' in line:
        chapter_match = re.search(r'### 第(\d+)章 (.+)', line)
        if chapter_match:
            chapters.append((i, chapter_match.group(1), chapter_match.group(2)))

print("Found chapters:")
for pos, num, title in chapters:
    print(f"Line {pos}: 第{num}章 {title}")

# Now assign correct numbers:
# 第25章 -> 第25章 (correct)
# 第26章 -> 第26章 (correct, newly added)
# 第32章 流批一体基础架构与设计 -> 第27章
# 第32章 流批一体端到端案例与实战 -> 第28章
# 第32章 跨云/混合云迁移与演练案例 -> 第29章
# 第32章 大规模数据处理性能与容量测试实践 -> 第30章
# 第32章 CI/CD、GitOps 与运维治理中的测试角色 -> 第31章

corrections = [
    ('流批一体基础架构与设计', '27'),
    ('流批一体端到端案例与实战', '28'),
    ('跨云/混合云迁移与演练案例', '29'),
    ('大规模数据处理性能与容量测试实践', '30'),
    ('CI/CD、GitOps 与运维治理中的测试角色', '31')
]

for title, correct_num in corrections:
    # Replace chapter header
    old_header = f'### 第32章 {title}'
    new_header = f'### 第{correct_num}章 {title}'
    content = content.replace(old_header, new_header)

    # Replace anchor if it exists
    old_anchor = f'<a id="第32章-{title}'
    new_anchor = f'<a id="第{correct_num}章-{title}'
    content = content.replace(old_anchor, new_anchor)

    # Replace section numbers
    content = re.sub(rf'#### 32\.([0-9]+)', rf'#### {correct_num}.\1', content)

# Write back
with open('framework/第7篇-专家篇-项目与治理.md', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed chapter numbers in 第7篇')