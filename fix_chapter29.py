import re

# Read the file
with open('book/1208.2025.newbook.update.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Find chapter 29 boundaries
chapter_29_start = content.find('### 第29章')
if chapter_29_start != -1:
    next_chapter_match = re.search(r'### 第\d+章', content[chapter_29_start + 1:])
    if next_chapter_match:
        chapter_29_end = chapter_29_start + next_chapter_match.start()
        chapter_29_content = content[chapter_29_start:chapter_29_end]
    else:
        chapter_29_content = content[chapter_29_start:]

    # Fix malformed headers
    fixed_content = chapter_29_content

    # Replace all 29. with sequential numbers
    counter = 1
    while '29.\x01' in fixed_content:
        fixed_content = fixed_content.replace('29.\x01', f'29.{counter}', 1)
        counter += 1

    # Replace the chapter content
    content = content.replace(chapter_29_content, fixed_content)

# Write back
with open('book/1208.2025.newbook.update.md', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed malformed headers in chapter 29')