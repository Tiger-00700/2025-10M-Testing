import re
import os

def split_book_complete():
    """修正版：按照第x篇-第x章.md格式完整拆分35章书籍到chapter目录"""

    # 修正的篇章结构 - 包含所有35章
    correct_structure = {
        1: list(range(1, 6)),      # 第1篇：第1-5章
        2: list(range(6, 12)),     # 第2篇：第6-11章
        3: list(range(12, 14)),    # 第3篇：第12-13章
        4: list(range(14, 19)),    # 第4篇：第14-18章
        5: list(range(19, 21)),    # 第5篇：第19-20章
        6: list(range(21, 26)),    # 第6篇：第21-25章
        7: list(range(26, 29)),    # 第7篇：第26-28章
        8: list(range(29, 36)),    # 第8篇：第29-35章 (新增)
    }

    chapter_dir = 'chapter'

    # 读取主书籍内容
    with open('book/1208.2025.newbook.update.md', 'r', encoding='utf-8') as f:
        book_content = f.read()

    lines = book_content.split('\n')

    # 找到所有章节的起始行
    chapter_starts = []
    current_part = None

    for i, line in enumerate(lines):
        # 检测篇标题
        part_match = re.match(r'^## 第(\d+)篇', line)
        if part_match:
            current_part = int(part_match.group(1))

        # 检测章节标题
        chapter_match = re.match(r'^### 第(\d+)章', line)
        if chapter_match:
            chapter_num = int(chapter_match.group(1))
            chapter_starts.append((chapter_num, current_part, i))

    # 为每个章节确定结束行
    chapter_ranges = []
    for i, (chapter_num, part_num, start_line) in enumerate(chapter_starts):
        if i < len(chapter_starts) - 1:
            end_line = chapter_starts[i + 1][2] - 1
        else:
            end_line = len(lines) - 1
        chapter_ranges.append((chapter_num, part_num, start_line, end_line))

    # 创建章节到范围的映射
    chapter_to_range = {chapter_num: (part_num, start_line, end_line)
                       for chapter_num, part_num, start_line, end_line in chapter_ranges}

    # 统计现有文件
    existing_files = [f for f in os.listdir(chapter_dir) if f.endswith('.md')]
    print(f"现有文件数: {len(existing_files)}")

    # 创建缺失的文件
    created_files = 0
    for part_num, chapter_nums in correct_structure.items():
        for chapter_num in chapter_nums:
            # 确定文件名：第x篇-第x章.md (第2篇特殊处理前导零)
            if part_num == 2 and chapter_num < 10:
                filename = f"第{part_num}篇-第0{chapter_num}章.md"
            else:
                filename = f"第{part_num}篇-第{chapter_num}章.md"

            filepath = os.path.join(chapter_dir, filename)

            # 检查文件是否已存在
            if os.path.exists(filepath):
                print(f"⏭️  跳过: {filename} (已存在)")
                continue

            if chapter_num in chapter_to_range:
                # 获取章节内容
                _, start_line, end_line = chapter_to_range[chapter_num]
                chapter_content = lines[start_line:end_line + 1]

                # 创建文件内容
                new_content = '\n'.join(chapter_content)

                # 写入文件
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)

                created_files += 1
                print(f"✅ 创建: {filename} ({len(new_content)} 字符)")
            else:
                print(f"⚠️  章节 {chapter_num} 在主书籍中不存在")

    print(f"\n📊 补充完成:")
    print(f"  新增文件数: {created_files}")
    print(f"  预期总文件数: {sum(len(chapters) for chapters in correct_structure.values())}")

    # 验证最终结果
    final_files = sorted([f for f in os.listdir(chapter_dir) if f.endswith('.md')])
    print(f"  最终文件数: {len(final_files)}")

    # 检查缺失的章节
    all_expected_chapters = set()
    for chapters in correct_structure.values():
        all_expected_chapters.update(chapters)

    missing_chapters = []
    for chapter_num in all_expected_chapters:
        filename_pattern = f"第*篇-第{chapter_num}章.md" if chapter_num >= 10 else f"第*篇-第0{chapter_num}章.md"
        found = False
        for filename in final_files:
            if f"第{chapter_num}章" in filename:
                found = True
                break
        if not found:
            missing_chapters.append(chapter_num)

    if missing_chapters:
        print(f"⚠️  仍缺失章节: {missing_chapters}")
    else:
        print("✅ 所有章节文件都已创建")

if __name__ == "__main__":
    print("🔄 补充缺失的第29-35章...")
    split_book_complete()
    print("🎉 补充完成！")