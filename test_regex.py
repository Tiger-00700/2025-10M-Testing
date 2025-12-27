import re

# 测试文本
test_text = "> [锚点015] 大数据系统分层架构图\n> 锚点类型: 建议\n> 锚点方法: 分层架构图\n> 补充建议: 梳理分层架构，标注关键组件、接口、质量关注点，补充 YAML/JSON 示例，参考脚本 examples/01_intro/tools/qa_summary.py\n> 完成情况: 已标准化\n> 版本: v1.0\n> 更新时间: 2025-12-23"

print("Original text:")
print(test_text)
print()

# 测试ID提取
id_match = re.search(r'> \[([^\]]+)\]', test_text)
if id_match:
    anchor_id = id_match.group(1)
    print(f"Anchor ID: {anchor_id}")
else:
    print("ID not found")

# 测试标题提取
title_match = re.search(r'> \[[^\]]+\] ([^>\n]+?)>', test_text)
if title_match:
    title = title_match.group(1).strip()
    print(f"Title: '{title}'")
else:
    print("Title not found")

# 测试字段提取
fields = {}
type_match = re.search(r'> 锚点类型:\s*([^>\n]+)', test_text)
if type_match:
    fields['type'] = type_match.group(1).strip()

method_match = re.search(r'> 锚点方法:\s*([^>\n]+)', test_text)
if method_match:
    fields['method'] = method_match.group(1).strip()

print(f"Fields found: {fields}")

# 生成标准化文本
standardized_text = '\n'.join([
    f'> **[{anchor_id}]** {title}',
    f'> **锚点类型**: {fields.get("type", "建议")}',
    f'> **锚点方法**: {fields.get("method", "配置示例")}',
    f'> **引用附件**: {fields.get("reference", "")}',
    f'> **完成情况**: {fields.get("status", "已完成")}',
    f'> **补充建议**: {fields.get("suggestion", "")}',
    f'> **更新时间**: {fields.get("timestamp", "2025-12-26")}'
])

print("\nStandardized text:")
print(standardized_text)