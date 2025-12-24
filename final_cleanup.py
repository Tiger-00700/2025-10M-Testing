import re

def final_cleanup():
    # Read the book
    with open('book/1208.2025.newbook.update.md', 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix the introduction section - convert ## to regular text
    content = re.sub(r'^## 适合谁阅读这本书\s*$', '**适合谁阅读这本书**\n', content, flags=re.MULTILINE)

    # Clean up extra spaces in subsection titles
    content = re.sub(r'^(##### \d+\.\d+)\s+', r'\1 ', content, flags=re.MULTILINE)

    # Also clean up extra spaces in section titles
    content = re.sub(r'^(#### \d+\.\d+)\s+', r'\1 ', content, flags=re.MULTILINE)

    # Write back
    with open('book/1208.2025.newbook.update.md', 'w', encoding='utf-8') as f:
        f.write(content)

    print("Final cleanup completed")

def final_verification():
    # Read the book
    with open('book/1208.2025.newbook.update.md', 'r', encoding='utf-8') as f:
        content = f.read()

    # Check hierarchy
    header_pattern = r'^(#{1,5}) (.+)$'
    headers = re.findall(header_pattern, content, re.MULTILINE)

    print("Final hierarchy verification:")
    print("Expected structure:")
    print("  # 书名")
    print("  ## 篇名 (第X篇)")
    print("  ### 章名 (第X章)")
    print("  #### 节名 (X.Y)")
    print("  ##### 子节名 (X.Y.Z)")

    print("\nActual structure (first 15 headers):")
    for level, title in headers[:15]:
        print(f"  {'#' * len(level)} {title[:50]}...")

    # Count by level
    levels = {}
    for level, title in headers:
        level_num = len(level)
        levels[level_num] = levels.get(level_num, 0) + 1

    print("\nHeader count by level:")
    for level in sorted(levels.keys()):
        print(f"  Level {level} ({'#' * level}): {levels[level]} headers")

    # Check for issues
    issues = []
    for level, title in headers:
        level_num = len(level)
        if level_num == 1:
            if not title.startswith('大数据全栈测试'):
                issues.append(f"Book title issue: {title}")
        elif level_num == 2:
            if not re.match(r'第\d+篇', title) and not title.startswith('**适合谁阅读这本书**'):
                issues.append(f"Part title issue: {title}")
        elif level_num == 3:
            if not re.match(r'第\d+章', title):
                issues.append(f"Chapter title issue: {title}")
        elif level_num == 4:
            if not re.match(r'\d+\.\d+', title.split()[0]):
                issues.append(f"Section title issue: {title}")
        elif level_num == 5:
            if not re.match(r'\d+\.\d+\.\d+', title.split()[0]):
                issues.append(f"Subsection title issue: {title}")

    if issues:
        print("\nIssues found:")
        for issue in issues[:5]:  # Show first 5 issues
            print(f"  - {issue}")
    else:
        print("\n✓ All headers follow the correct hierarchy pattern!")

if __name__ == "__main__":
    final_cleanup()
    final_verification()