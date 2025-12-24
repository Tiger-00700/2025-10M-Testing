import re
import os

def analyze_chapter_mapping():
    """分析章节到文件的映射关系"""
    # 读取主书籍文件
    with open('book/1208.2025.newbook.update.md', 'r', encoding='utf-8') as f:
        book_content = f.read()

    # 找到所有章节标题
    chapter_pattern = r'^### 第(\d+)章 (.+)$'
    chapters = re.findall(chapter_pattern, book_content, re.MULTILINE)

    print(f"Found {len(chapters)} chapters in main book:")
    for chapter_num, title in chapters:
        print(f"  Chapter {chapter_num}: {title}")

    # 分析 chapter-new 目录中的文件
    chapter_new_files = {}
    chapter_new_dir = 'chapter-new'

    for filename in os.listdir(chapter_new_dir):
        if filename.endswith('.md'):
            filepath = os.path.join(chapter_new_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # 找到这个文件包含的章节
            file_chapters = re.findall(r'### 第(\d+)章', content)
            if file_chapters:
                chapter_new_files[filename] = file_chapters
                print(f"  {filename}: contains chapters {file_chapters}")

    return chapters, chapter_new_files

def split_book_by_chapters():
    """按照章节拆分书籍内容"""
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
            print(f"Found part {current_part} at line {i}")

        # 检测章节标题
        chapter_match = re.match(r'^### 第(\d+)章', line)
        if chapter_match:
            chapter_num = int(chapter_match.group(1))
            chapter_starts.append((chapter_num, current_part, i))
            print(f"Found chapter {chapter_num} (part {current_part}) at line {i}")

    # 为每个章节确定结束行
    chapter_ranges = []
    for i, (chapter_num, part_num, start_line) in enumerate(chapter_starts):
        if i < len(chapter_starts) - 1:
            end_line = chapter_starts[i + 1][2] - 1
        else:
            end_line = len(lines) - 1
        chapter_ranges.append((chapter_num, part_num, start_line, end_line))

    print(f"\nChapter ranges:")
    for chapter_num, part_num, start, end in chapter_ranges:
        print(f"  Chapter {chapter_num} (Part {part_num}): lines {start}-{end}")

    # 现在按照映射关系写入文件
    chapter_new_dir = 'chapter-new'

    for chapter_num, part_num, start_line, end_line in chapter_ranges:
        # 确定目标文件名
        target_filename = f"第{part_num}篇-第{chapter_num}章.md"
        target_path = os.path.join(chapter_new_dir, target_filename)

        if os.path.exists(target_path):
            print(f"Processing {target_filename}...")

            # 提取章节内容
            chapter_content = lines[start_line:end_line + 1]

            # 创建新的文件内容
            header = f"<!-- 自动生成：已按 /framework/ 目录顺序插入 第{part_num}篇～第7篇 的完整内容（2025-12-22）。来源：/framework/*.md -->\n\n"
            part_title = f"<!-- BEGIN 第{part_num}篇 -->\n## 第{part_num}篇\n\n"

            # 组合内容
            new_content = header + part_title + '\n'.join(chapter_content)

            # 写入文件（清空原有内容）
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            print(f"  Written {len(new_content)} characters to {target_filename}")
        else:
            print(f"Warning: Target file {target_filename} does not exist")

if __name__ == "__main__":
    print("Analyzing chapter mapping...")
    chapters, chapter_files = analyze_chapter_mapping()

    print("\nSplitting book content...")
    split_book_by_chapters()

    print("Done!")