import re

def extract_parts_from_book():
    """从1208书籍中提取每个篇的内容"""
    with open('book/1208.2025.newbook.update.md', 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')

    # 找到所有篇标题的位置
    part_positions = []
    for i, line in enumerate(lines):
        match = re.match(r'^## 第(\d+)篇', line)
        if match:
            part_num = int(match.group(1))
            part_positions.append((part_num, i))

    print(f"找到 {len(part_positions)} 个篇:")
    for part_num, line_num in part_positions:
        print(f"  第{part_num}篇: 第{line_num}行")

    # 提取每个篇的内容
    parts_content = {}
    for i, (part_num, start_line) in enumerate(part_positions):
        if i < len(part_positions) - 1:
            end_line = part_positions[i + 1][1] - 1
        else:
            end_line = len(lines) - 1

        part_content = '\n'.join(lines[start_line:end_line + 1])
        parts_content[part_num] = part_content

        print(f"  第{part_num}篇: {start_line}-{end_line}行 ({len(part_content)} 字符)")

    return parts_content

def update_framework_files():
    """更新framework目录下的文件内容"""
    # 提取书籍中的篇内容
    parts_content = extract_parts_from_book()

    # framework文件名映射
    framework_files = {
        1: "第1篇-入门篇-大数据测试基础.md",
        2: "第2篇-进阶篇-大数据测试方法与技术.md",
        3: "第3篇-进阶篇-环境与数据治理.md",
        4: "第4篇-进阶篇-数据质量安全.md",
        5: "第5篇-进阶篇-自动化、工具与可观测性.md",
        6: "第6篇-专家篇-案例与性能.md",
        7: "第7篇-专家篇-项目与治理.md",
        8: "第8篇-专家篇-趋势与平台化.md",
    }

    print(f"\n📝 开始更新 framework 文件...")

    for part_num, filename in framework_files.items():
        if part_num in parts_content:
            filepath = f"framework/{filename}"

            # 写入新内容
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(parts_content[part_num])

            print(f"✅ 更新: {filename} ({len(parts_content[part_num])} 字符)")
        else:
            print(f"⚠️  警告: 第{part_num}篇的内容不存在")

if __name__ == "__main__":
    update_framework_files()