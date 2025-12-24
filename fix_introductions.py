import re

def fix_chapter_introductions():
    # Read the book
    with open('book/1208.2025.newbook.update.md', 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix "本章你将学到什么" - convert from #### to regular text
    content = re.sub(r'^#### 本章你将学到什么\s*$', '**本章你将学到什么**\n', content, flags=re.MULTILINE)

    # Fix other non-standard section headers that start with #### but don't have proper numbering
    # These should be converted to regular text or lower level headers

    # Convert "增补：" sections to regular text
    content = re.sub(r'^#### 增补：(.+)$', r'**增补：\1**', content, flags=re.MULTILINE)

    # Convert "行业" sections to regular text
    content = re.sub(r'^#### 行业(.+)$', r'**行业\1**', content, flags=re.MULTILINE)

    # Fix sections that have incorrect numbering like "29. " instead of proper X.Y format
    # These need to be analyzed case by case, but for now let's convert them to regular text
    content = re.sub(r'^#### 29\.\s+(.+)$', r'**29. \1**', content, flags=re.MULTILINE)

    # Write back
    with open('book/1208.2025.newbook.update.md', 'w', encoding='utf-8') as f:
        f.write(content)

    print("Fixed chapter introductions and non-standard headers")

def verify_hierarchy():
    # Read the book
    with open('book/1208.2025.newbook.update.md', 'r', encoding='utf-8') as f:
        content = f.read()

    # Check hierarchy
    header_pattern = r'^(#{1,5}) (.+)$'
    headers = re.findall(header_pattern, content, re.MULTILINE)

    print("Current hierarchy structure:")
    for level, title in headers[:20]:  # Show first 20 headers
        print(f"  {'#' * len(level)} {title[:50]}...")

    # Count headers by level
    levels = {}
    for level, title in headers:
        level_num = len(level)
        levels[level_num] = levels.get(level_num, 0) + 1

    print("\nHeader count by level:")
    for level in sorted(levels.keys()):
        print(f"  Level {level} ({'#' * level}): {levels[level]} headers")

if __name__ == "__main__":
    fix_chapter_introductions()
    verify_hierarchy()