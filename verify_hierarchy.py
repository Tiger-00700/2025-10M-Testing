import re

def add_book_title_and_verify_hierarchy():
    # Read the book
    with open('book/1208.2025.newbook.update.md', 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if book title already exists
    if not content.startswith('# 大数据全栈测试：从理论到实战'):
        # Add book title at the beginning, after the auto-generated comment
        lines = content.split('\n')
        insert_index = 0

        # Find where to insert the title (after the first comment block)
        for i, line in enumerate(lines):
            if line.startswith('<!-- BEGIN 第1篇 -->'):
                insert_index = i
                break
            elif not line.startswith('<!--') and line.strip():
                # If we hit non-comment content, insert before it
                insert_index = i
                break

        # Insert the book title
        lines.insert(insert_index, '# 大数据全栈测试：从理论到实战\n')
        content = '\n'.join(lines)

    # Now verify the hierarchy structure
    # Expected pattern:
    # # Book Title
    # ## Part Title (第X篇)
    # ### Chapter Title (第X章)
    # #### Section Title (X.Y)
    # ##### Subsection Title (X.Y.Z)

    # Check for any incorrect hierarchy patterns
    issues = []

    # Find all headers
    header_pattern = r'^(#{1,5}) (.+)$'
    headers = re.findall(header_pattern, content, re.MULTILINE)

    current_part = None
    current_chapter = None
    current_section = None

    for level, title in headers:
        level_num = len(level)

        if level_num == 1:
            # Book title
            if not title.startswith('大数据全栈测试'):
                issues.append(f"Unexpected book title: {title}")
        elif level_num == 2:
            # Part title (第X篇)
            if not re.match(r'第\d+篇', title):
                issues.append(f"Part title doesn't match expected pattern: {title}")
            current_part = title
            current_chapter = None
            current_section = None
        elif level_num == 3:
            # Chapter title (第X章)
            if not re.match(r'第\d+章', title):
                issues.append(f"Chapter title doesn't match expected pattern: {title}")
            current_chapter = title
            current_section = None
        elif level_num == 4:
            # Section title (X.Y)
            if not re.match(r'\d+\.\d+', title.split()[0] if title.split() else ''):
                issues.append(f"Section title doesn't match expected pattern: {title}")
            current_section = title
        elif level_num == 5:
            # Subsection title (X.Y.Z)
            if not re.match(r'\d+\.\d+\.\d+', title.split()[0] if title.split() else ''):
                issues.append(f"Subsection title doesn't match expected pattern: {title}")

    # Write back the content
    with open('book/1208.2025.newbook.update.md', 'w', encoding='utf-8') as f:
        f.write(content)

    if issues:
        print("Hierarchy issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("Book hierarchy is correct:")
        print("  # 书名")
        print("  ## 篇名")
        print("  ### 章名")
        print("  #### 节名")
        print("  ##### 子节名")

if __name__ == "__main__":
    add_book_title_and_verify_hierarchy()