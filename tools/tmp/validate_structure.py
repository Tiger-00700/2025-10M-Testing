# 验证书籍结构
import re

def validate_book_structure():
    book_file = r'e:\DONT_TOUCH\10M-2025-Testing\book\1208.2025.newbook.update.md'

    with open(book_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查篇章结构
    parts = re.findall(r'^## 第(\d+)篇', content, re.MULTILINE)
    print(f"Found parts: {parts}")

    # 检查章节结构
    chapters = re.findall(r'^### 第(\d+)章', content, re.MULTILINE)
    print(f"Found chapters: {sorted(set(chapters), key=int)}")

    # 检查第18章的小节
    chapter_18_sections = re.findall(r'^#### 18\.(\d+)', content, re.MULTILINE)
    print(f"Chapter 18 sections: {sorted(set(chapter_18_sections), key=int)}")

    # 检查是否有重复的18.12
    duplicate_18_12 = re.findall(r'^#### 18\.12', content, re.MULTILINE)
    print(f"Duplicate 18.12 sections: {len(duplicate_18_12)}")

    # 验证连续性
    expected_parts = list(range(1, 9))  # 1-8篇
    expected_chapters = list(range(1, 40))  # 1-39章

    actual_parts = sorted(set(int(p) for p in parts))
    actual_chapters = sorted(set(int(c) for c in chapters))

    print(f"Parts continuity: {actual_parts == expected_parts}")
    print(f"Chapters continuity: {actual_chapters == expected_chapters}")

    # 检查第18章是否正好有8个小节
    expected_18_sections = list(range(1, 9))
    actual_18_sections = sorted(set(int(s) for s in chapter_18_sections))
    print(f"Chapter 18 sections continuity: {actual_18_sections == expected_18_sections}")

if __name__ == '__main__':
    validate_book_structure()