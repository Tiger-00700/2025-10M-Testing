import re

# Read the file
with open('framework/第7篇-专家篇-项目与治理.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix by identifying each chapter by its title and assigning correct numbers

corrections = [
    ('大数据测试项目实施与实战经验【项目管理与团队协作】', '29'),
    ('技术与方法演进', '30'),
    ('流批一体基础架构与设计', '31'),
    ('流批一体端到端案例与实战', '32'),
    ('跨云/混合云迁移与演练案例【迁移与韧性】', '33'),
    ('大规模数据处理性能与容量测试实践【性能与容量篇】', '34'),
    ('CI/CD、GitOps 与运维治理中的测试角色【自动化与治理篇】', '35')
]

for title, correct_num in corrections:
    # Replace chapter header - look for any 3x chapter number
    content = re.sub(r'### 第3\d章 ' + re.escape(title), f'### 第{correct_num}章 {title}', content)

    # Replace anchor
    content = re.sub(r'<a id="第3\d章-' + re.escape(title.split('【')[0]), f'<a id="第{correct_num}章-{title.split("【")[0]}', content)

    # Replace section numbers
    content = re.sub(r'#### 3\d\.([0-9]+)', f'#### {correct_num}.\1', content)

# Write back
with open('framework/第7篇-专家篇-项目与治理.md', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed chapter numbers in 第7篇')