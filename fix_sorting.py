import os
import re

def fix_part2_sorting():
    """修复第2篇的章节排序问题"""
    chapter_new_dir = 'chapter-new'

    # 第2篇的文件映射：当前文件名 -> 正确文件名
    # 当前：第2篇-第10章.md, 第2篇-第11章.md, 第2篇-第6章.md, 第2篇-第7章.md, 第2篇-第8章.md, 第2篇-第9章.md
    # 正确顺序应该是：第6,7,8,9,10,11章

    rename_map = {
        "第2篇-第10章.md": "第2篇-第10章_temp.md",
        "第2篇-第11章.md": "第2篇-第11章_temp.md",
        "第2篇-第6章.md": "第2篇-第6章_temp.md",
        "第2篇-第7章.md": "第2篇-第7章_temp.md",
        "第2篇-第8章.md": "第2篇-第8章_temp.md",
        "第2篇-第9章.md": "第2篇-第9章_temp.md",
    }

    # 临时重命名
    for old_name, temp_name in rename_map.items():
        old_path = os.path.join(chapter_new_dir, old_name)
        temp_path = os.path.join(chapter_new_dir, temp_name)
        if os.path.exists(old_path):
            os.rename(old_path, temp_path)
            print(f"临时重命名: {old_name} -> {temp_name}")

    # 重新命名回正确顺序
    correct_order = ["第6章", "第7章", "第8章", "第9章", "第10章", "第11章"]
    for i, chapter in enumerate(correct_order, 6):
        temp_name = f"第2篇-{chapter}_temp.md"
        correct_name = f"第2篇-第{i}章.md"

        temp_path = os.path.join(chapter_new_dir, temp_name)
        correct_path = os.path.join(chapter_new_dir, correct_name)

        if os.path.exists(temp_path):
            os.rename(temp_path, correct_path)
            print(f"正确重命名: {temp_name} -> {correct_name}")
        else:
            print(f"警告: 临时文件不存在 {temp_name}")

    print("第2篇排序修复完成！")

def verify_final_structure():
    """验证最终的文件结构"""
    chapter_new_dir = 'chapter-new'
    files = sorted([f for f in os.listdir(chapter_new_dir) if f.endswith('.md')])

    print("\n最终文件结构:")
    current_part = None
    part_chapters = []

    for filename in files:
        match = re.match(r'第(\d+)篇-第(\d+)章\.md', filename)
        if match:
            part_num = int(match.group(1))
            chapter_num = int(match.group(2))

            if part_num != current_part:
                if current_part is not None:
                    print(f"  第{current_part}篇: {sorted(part_chapters)}章")
                current_part = part_num
                part_chapters = []

            part_chapters.append(chapter_num)

    if part_chapters:
        print(f"  第{current_part}篇: {sorted(part_chapters)}章")

    # 检查是否有排序问题
    print("\n排序检查:")
    issues = []
    for filename in files:
        match = re.match(r'第(\d+)篇-第(\d+)章\.md', filename)
        if match:
            part_num = int(match.group(1))
            chapter_num = int(match.group(2))

            # 对于第2篇，检查顺序
            if part_num == 2:
                expected_order = [6, 7, 8, 9, 10, 11]
                if chapter_num not in expected_order:
                    issues.append(f"第2篇-第{chapter_num}章 不在预期顺序中")

    if issues:
        print("⚠️  发现问题:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("✅ 所有文件排序正确")

if __name__ == "__main__":
    print("🔧 修复第2篇排序问题...")
    fix_part2_sorting()
    verify_final_structure()