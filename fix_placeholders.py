import re

def fix_placeholder_numbers():
    # Read the book
    with open('book/1208.2025.newbook.update.md', 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix the placeholder character  in section headers
    # Pattern: #### 29. Title -> #### 29.X Title where X increments
    # Pattern: ##### 29..Y Title -> ##### 29.X.Y Title

    # First, let's identify all the sections that need fixing
    # Find all #### 29. patterns
    main_sections = re.findall(r'#### 29\. ([^\n]+)', content)

    print(f"Found {len(main_sections)} main sections to fix:")
    for i, title in enumerate(main_sections, 1):
        print(f"  29.{i}: {title}")

    # Replace main sections: #### 29. Title -> #### 29.X Title
    for i, title in enumerate(main_sections, 1):
        old_pattern = f"#### 29. {title}"
        new_pattern = f"#### 29.{i} {title}"
        content = content.replace(old_pattern, new_pattern)

    # Now fix subsections: ##### 29..Y Title -> ##### 29.X.Y Title
    # We need to track which main section we're in
    lines = content.split('\n')
    current_main_section = 0

    for i, line in enumerate(lines):
        if line.startswith('#### 29.') and not '' in line:
            # Extract the main section number
            match = re.match(r'#### 29\.(\d+)', line)
            if match:
                current_main_section = int(match.group(1))

        elif line.startswith('##### 29..'):
            # Fix subsection numbering
            match = re.match(r'##### 29\.\.(\d+) (.+)', line)
            if match:
                subsection_num = match.group(1)
                title = match.group(2)
                new_line = f"##### 29.{current_main_section}.{subsection_num} {title}"
                lines[i] = new_line

    content = '\n'.join(lines)

    # Write back
    with open('book/1208.2025.newbook.update.md', 'w', encoding='utf-8') as f:
        f.write(content)

    print("Fixed placeholder numbers in section headers")

def verify_final_hierarchy():
    # Read the book
    with open('book/1208.2025.newbook.update.md', 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for any remaining placeholder characters
    placeholders = re.findall(r'', content)
    if placeholders:
        print(f"Warning: {len(placeholders)} placeholder characters still remain")
    else:
        print("No placeholder characters found")

    # Count headers by level
    header_pattern = r'^(#{1,5}) (.+)$'
    headers = re.findall(header_pattern, content, re.MULTILINE)

    levels = {}
    for level, title in headers:
        level_num = len(level)
        levels[level_num] = levels.get(level_num, 0) + 1

    print("\nFinal header count by level:")
    for level in sorted(levels.keys()):
        print(f"  Level {level} ({'#' * level}): {levels[level]} headers")

if __name__ == "__main__":
    fix_placeholder_numbers()
    verify_final_hierarchy()