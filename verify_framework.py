import os
import re

def verify_framework_files():
    """验证framework目录下所有文件的格式和内容"""
    framework_dir = 'framework'

    # 预期的文件名格式
    expected_files = [
        "第1篇-入门篇-大数据测试基础.md",
        "第2篇-进阶篇-大数据测试方法与技术.md",
        "第3篇-进阶篇-环境与数据治理.md",
        "第4篇-进阶篇-数据质量安全.md",
        "第5篇-进阶篇-自动化、工具与可观测性.md",
        "第6篇-专家篇-案例与性能.md",
        "第7篇-专家篇-项目与治理.md",
        "第8篇-专家篇-趋势与平台化.md",
    ]

    print("🔍 验证 /framework/ 目录文件格式...\n")

    # 检查文件是否存在
    existing_files = [f for f in os.listdir(framework_dir) if f.endswith('.md')]
    existing_files.sort()

    print(f"现有文件 ({len(existing_files)} 个):")
    for filename in existing_files:
        print(f"  ✓ {filename}")

    print(f"\n预期文件 ({len(expected_files)} 个):")
    for filename in expected_files:
        status = "✓" if filename in existing_files else "✗"
        print(f"  {status} {filename}")

    # 检查文件名格式
    print(f"\n📋 格式验证:")
    format_pattern = r'^第\d+篇-(入门篇|进阶篇|专家篇)-.+\.md$'

    all_correct = True
    for filename in existing_files:
        if re.match(format_pattern, filename):
            print(f"  ✓ {filename} - 格式正确")
        else:
            print(f"  ✗ {filename} - 格式不正确")
            all_correct = False

    # 检查文件内容结构
    print(f"\n📖 内容结构检查:")
    for filename in existing_files:
        filepath = os.path.join(framework_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            lines = content.split('\n')
            if lines and lines[0].startswith('## 第'):
                print(f"  ✓ {filename} - 内容结构正确")
            else:
                print(f"  ⚠️ {filename} - 内容结构可能需要检查")
        except Exception as e:
            print(f"  ✗ {filename} - 读取失败: {e}")
            all_correct = False

    print(f"\n🎯 总结:")
    if all_correct and len(existing_files) == len(expected_files):
        print("✅ 所有文件都符合要求！")
    else:
        print("⚠️ 发现一些问题需要处理")

    return all_correct

if __name__ == "__main__":
    verify_framework_files()