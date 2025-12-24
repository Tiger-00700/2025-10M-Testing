import os
import re
import shutil

def reorganize_chapters():
    """重新组织章节文件，消除重复和排序问题"""

    # 定义正确的篇章结构
    correct_structure = {
        1: list(range(1, 6)),      # 第1篇：第1-5章
        2: list(range(6, 12)),     # 第2篇：第6-11章
        3: list(range(12, 14)),    # 第3篇：第12-13章
        4: list(range(14, 19)),    # 第4篇：第14-18章
        5: list(range(19, 21)),    # 第5篇：第19-20章
        6: list(range(21, 25)),    # 第6篇：第21-24章
        7: list(range(25, 29)),    # 第7篇：第25-28章
        8: list(range(29, 36)),    # 第8篇：第29-35章
    }

    chapter_new_dir = 'chapter-new'
    backup_dir = 'chapter-new-backup'

    # 创建备份
    if os.path.exists(backup_dir):
        shutil.rmtree(backup_dir)
    shutil.copytree(chapter_new_dir, backup_dir)
    print(f"✅ 已创建备份: {backup_dir}")

    # 清空 chapter-new 目录
    for filename in os.listdir(chapter_new_dir):
        if filename.endswith('.md'):
            os.remove(os.path.join(chapter_new_dir, filename))
    print("✅ 已清空 chapter-new 目录")

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
                # 确定文件名
                filename = f"第{part_num}篇-第{chapter_num}章.md"
                filepath = os.path.join(chapter_new_dir, filename)

                # 获取章节内容
                _, start_line, end_line = chapter_to_range[chapter_num]
                chapter_content = lines[start_line:end_line + 1]

                # 创建文件内容
                header = "<!-- 自动生成：已按 /framework/ 目录顺序插入 第{}篇～第8篇 的完整内容（2025-12-22）。来源：/framework/*.md -->\n\n".format(part_num)
                part_title = "<!-- BEGIN 第{}篇 -->\n## 第{}篇\n\n".format(part_num, part_num)

                new_content = header + part_title + '\n'.join(chapter_content)

                # 写入文件
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)

                created_files += 1
                print(f"✅ 创建: {filename} ({len(new_content)} 字符)")
            else:
                print(f"⚠️  章节 {chapter_num} 在主书籍中不存在")

    print(f"\n📊 重组完成:")
    print(f"  创建文件数: {created_files}")
    print(f"  预期文件数: {sum(len(chapters) for chapters in correct_structure.values())}")
    print(f"  备份位置: {backup_dir}")

    # 验证结果
    final_files = [f for f in os.listdir(chapter_new_dir) if f.endswith('.md')]
    print(f"  最终文件数: {len(final_files)}")

    # 检查是否还有重复
    chapter_count = {}
    for filename in final_files:
        match = re.match(r'第(\d+)篇-第(\d+)章\.md', filename)
        if match:
            chapter_num = int(match.group(2))
            chapter_count[chapter_num] = chapter_count.get(chapter_num, 0) + 1

    duplicates = [ch for ch, count in chapter_count.items() if count > 1]
    if duplicates:
        print(f"⚠️  仍有重复章节: {duplicates}")
    else:
        print("✅ 无重复章节")

if __name__ == "__main__":
    print("🔄 开始重新组织章节文件...")
    reorganize_chapters()
    print("🎉 重组完成！")