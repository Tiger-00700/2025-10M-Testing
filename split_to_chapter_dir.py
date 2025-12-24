import re
import os

def split_book_to_chapter_directory():
    """按照第x篇-第x章.md格式拆分书籍到chapter目录"""

    # 定义正确的篇章结构
    correct_structure = {
        1: list(range(1, 6)),      # 第1篇：第1-5章
        2: list(range(6, 12)),     # 第2篇：第6-11章
        3: list(range(12, 14)),    # 第3篇：第12-13章
        4: list(range(14, 19)),    # 第4篇：第14-18章
        5: list(range(19, 21)),    # 第5篇：第19-20章
        6: list(range(21, 26)),    # 第6篇：第21-25章
        7: list(range(26, 29)),    # 第7篇：第26-28章
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

    # 按照正确结构创建文件
    created_files = 0
    for part_num, chapter_nums in correct_structure.items():
        for chapter_num in chapter_nums:
            if chapter_num in chapter_to_range:
                # 确定文件名：第x篇-第x章.md
                filename = f"第{part_num}篇-第{chapter_num}章.md"
                filepath = os.path.join(chapter_dir, filename)

                # 获取章节内容
                _, start_line, end_line = chapter_to_range[chapter_num]
                chapter_content = lines[start_line:end_line + 1]

                # 创建文件内容（简化格式，不需要篇标题头）
                new_content = '\n'.join(chapter_content)

                # 写入文件
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)

                created_files += 1
                print(f"✅ 创建: {filename} ({len(new_content)} 字符)")
            else:
                print(f"⚠️  章节 {chapter_num} 在主书籍中不存在")

    print(f"\n📊 拆分完成:")
    print(f"  创建文件数: {created_files}")
    print(f"  预期文件数: {sum(len(chapters) for chapters in correct_structure.values())}")

    # 验证结果
    final_files = sorted([f for f in os.listdir(chapter_dir) if f.endswith('.md')])
    print(f"  最终文件数: {len(final_files)}")

    # 显示文件顺序
    print(f"\n📋 文件顺序:")
    for filename in final_files:
        print(f"  {filename}")

if __name__ == "__main__":
    print("🔄 开始按照第x篇-第x章.md格式拆分书籍...")
    split_book_to_chapter_directory()
    print("🎉 拆分完成！")