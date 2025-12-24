import os
import re

def verify_split_completion():
    """验证书籍拆分是否完成"""
    chapter_new_dir = 'chapter-new'

    # 获取所有文件
    files = [f for f in os.listdir(chapter_new_dir) if f.endswith('.md')]
    files.sort()

    print(f"Total files in chapter-new: {len(files)}")

    # 检查每个文件是否包含章节内容
    total_chapters_found = 0
    empty_files = []

    for filename in files:
        filepath = os.path.join(chapter_new_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查是否包含章节标题
        chapter_matches = re.findall(r'### 第(\d+)章', content)
        if chapter_matches:
            total_chapters_found += len(chapter_matches)
            print(f"✓ {filename}: {len(chapter_matches)} chapter(s) - {len(content)} chars")
        else:
            empty_files.append(filename)
            print(f"✗ {filename}: NO chapters found")

    print(f"\nSummary:")
    print(f"  Total files: {len(files)}")
    print(f"  Files with chapters: {len(files) - len(empty_files)}")
    print(f"  Total chapters found: {total_chapters_found}")
    if empty_files:
        print(f"  Empty files: {len(empty_files)} - {empty_files}")

    # 验证主书籍中的章节数
    with open('book/1208.2025.newbook.update.md', 'r', encoding='utf-8') as f:
        book_content = f.read()

    book_chapters = re.findall(r'### 第\d+章', book_content)
    print(f"  Chapters in main book: {len(book_chapters)}")

    if total_chapters_found == len(book_chapters):
        print("✅ SUCCESS: All chapters have been successfully split!")
    else:
        print(f"⚠️  WARNING: Chapter count mismatch! Expected {len(book_chapters)}, found {total_chapters_found}")

if __name__ == "__main__":
    verify_split_completion()