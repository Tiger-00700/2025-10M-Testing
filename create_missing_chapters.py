import re
import os

def create_missing_chapter_files():
    """创建缺失的章节文件"""
    chapter_new_dir = 'chapter-new'

    # 需要创建的文件列表（从脚本输出中提取）
    missing_files = [
        ("第3篇-第14章.md", 3, 14),
        ("第3篇-第15章.md", 3, 15),
        ("第3篇-第16章.md", 3, 16),
        ("第4篇-第19章.md", 4, 19),
        ("第4篇-第20章.md", 4, 20),
        ("第5篇-第21章.md", 5, 21),
        ("第5篇-第22章.md", 5, 22),
        ("第5篇-第23章.md", 5, 23),
        ("第6篇-第25章.md", 6, 25),
        ("第6篇-第26章.md", 6, 26),
        ("第6篇-第27章.md", 6, 27),
        ("第6篇-第28章.md", 6, 28),
        ("第7篇-第29章.md", 7, 29),
        ("第7篇-第30章.md", 7, 30),
        ("第7篇-第31章.md", 7, 31),
        ("第7篇-第32章.md", 7, 32),
        ("第7篇-第33章.md", 7, 33),
        ("第8篇-第34章.md", 8, 34),
        ("第8篇-第35章.md", 8, 35),
    ]

    # 读取主书籍文件
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

    # 创建缺失的文件
    for filename, expected_part, expected_chapter in missing_files:
        if expected_chapter in chapter_to_range:
            part_num, start_line, end_line = chapter_to_range[expected_chapter]

            # 提取章节内容
            chapter_content = lines[start_line:end_line + 1]

            # 创建新的文件内容
            header = "<!-- 自动生成：已按 /framework/ 目录顺序插入 第{}篇～第7篇 的完整内容（2025-12-22）。来源：/framework/*.md -->\n\n".format(expected_part)
            part_title = "<!-- BEGIN 第{}篇 -->\n## 第{}篇\n\n".format(expected_part, expected_part)

            # 组合内容
            new_content = header + part_title + '\n'.join(chapter_content)

            # 写入文件
            target_path = os.path.join(chapter_new_dir, filename)
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            print(f"Created {filename} with {len(new_content)} characters")
        else:
            print(f"Warning: Chapter {expected_chapter} not found in book")

if __name__ == "__main__":
    create_missing_chapter_files()