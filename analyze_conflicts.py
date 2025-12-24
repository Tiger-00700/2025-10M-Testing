import os
import re
from collections import defaultdict

def analyze_chapter_conflicts():
    """分析章节冲突和排序问题"""
    chapter_new_dir = 'chapter-new'

    # 收集所有文件信息
    files = [f for f in os.listdir(chapter_new_dir) if f.endswith('.md')]

    # 按篇和章分组
    chapters_by_part = defaultdict(list)
    chapters_by_number = defaultdict(list)

    for filename in files:
        # 解析文件名：第X篇-第Y章.md
        match = re.match(r'第(\d+)篇-第(\d+)章\.md', filename)
        if match:
            part_num = int(match.group(1))
            chapter_num = int(match.group(2))

            chapters_by_part[part_num].append((chapter_num, filename))
            chapters_by_number[chapter_num].append((part_num, filename))

    print("=== 章节冲突分析 ===\n")

    # 检查重复章节
    print("🔴 重复章节号（同一个章节出现在多个篇中）：")
    duplicate_chapters = []
    for chapter_num, parts in chapters_by_number.items():
        if len(parts) > 1:
            duplicate_chapters.append(chapter_num)
            print(f"  第{chapter_num}章 出现在 {len(parts)} 个篇中：")
            for part_num, filename in parts:
                print(f"    - {filename}")
            print()

    # 检查篇内排序
    print("🟡 篇内排序问题：")
    for part_num in sorted(chapters_by_part.keys()):
        chapters_in_part = chapters_by_part[part_num]
        chapter_nums = [ch[0] for ch in chapters_in_part]

        # 检查是否连续
        if chapter_nums:
            min_ch = min(chapter_nums)
            max_ch = max(chapter_nums)
            expected_range = set(range(min_ch, max_ch + 1))
            actual_set = set(chapter_nums)

            missing = expected_range - actual_set
            extra = actual_set - expected_range

            if missing or extra or chapter_nums != sorted(chapter_nums):
                print(f"  第{part_num}篇 ({len(chapters_in_part)} 个章节): {sorted(chapter_nums)}")
                if missing:
                    print(f"    缺失章节: {sorted(missing)}")
                if extra:
                    print(f"    额外章节: {sorted(extra)}")
                if chapter_nums != sorted(chapter_nums):
                    print("    排序不正确")
                print()

    # 检查整体章节覆盖
    print("🟢 整体章节覆盖情况：")
    all_chapter_nums = sorted(chapters_by_number.keys())
    print(f"  总共 {len(all_chapter_nums)} 个唯一章节号: {all_chapter_nums}")

    # 检查连续性
    if all_chapter_nums:
        min_ch = min(all_chapter_nums)
        max_ch = max(all_chapter_nums)
        expected_all = set(range(min_ch, max_ch + 1))
        actual_all = set(all_chapter_nums)

        missing_all = expected_all - actual_all
        if missing_all:
            print(f"  缺失的章节号: {sorted(missing_all)}")

    print(f"\n📊 统计信息：")
    print(f"  总文件数: {len(files)}")
    print(f"  篇数: {len(chapters_by_part)}")
    print(f"  唯一章节数: {len(chapters_by_number)}")
    print(f"  重复章节数: {len(duplicate_chapters)}")

    # 建议解决方案
    print(f"\n💡 建议解决方案：")
    print("1. 消除重复章节：每个章节只能属于一个篇")
    print("2. 重新组织篇章结构：")
    print("   - 第1篇：第1-5章 (入门基础)")
    print("   - 第2篇：第6-11章 (核心技术)")
    print("   - 第3篇：第12-13章 (环境与数据)")
    print("   - 第4篇：第14-18章 (自动化与工具)")
    print("   - 第5篇：第19-20章 (案例分析)")
    print("   - 第6篇：第21-24章 (项目实施)")
    print("   - 第7篇：第25-28章 (趋势与平台)")
    print("3. 确保每个篇内的章节连续编号")

    return duplicate_chapters, chapters_by_part, chapters_by_number

if __name__ == "__main__":
    analyze_chapter_conflicts()