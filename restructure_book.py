import re

def restructure_book():
    # Read the book
    with open('book/1208.2025.newbook.update.md', 'r', encoding='utf-8') as f:
        content = f.read()

    # Process each chapter
    chapters = re.split(r'(?=### 第\d+章)', content)

    restructured_chapters = []

    for chapter in chapters:
        if not chapter.strip():
            continue

        # Find chapter number
        chapter_match = re.search(r'### 第(\d+)章', chapter)
        if not chapter_match:
            restructured_chapters.append(chapter)
            continue

        chapter_num = int(chapter_match.group(1))
        print(f"Processing chapter {chapter_num}")

        # Find all main sections (#### X.Y) and convert them to subsections (##### X.Y.1)
        # Pattern: #### X.Y Title -> ##### X.Y.1 Title
        def replace_main_section(match):
            level = match.group(1)
            section_num = match.group(2)
            title = match.group(3)

            # Convert X.Y to X.Y.1
            parts = section_num.split('.')
            if len(parts) == 2:
                new_section_num = f"{parts[0]}.{parts[1]}.1"
                return f"##### {new_section_num} {title}"
            return match.group(0)

        # Replace all main sections
        restructured_chapter = re.sub(
            r'(####) (\d+\.\d+)([^\n]*)',
            replace_main_section,
            chapter
        )

        restructured_chapters.append(restructured_chapter)

    # Join all chapters back
    result = ''.join(restructured_chapters)

    # Write back
    with open('book/1208.2025.newbook.update.md', 'w', encoding='utf-8') as f:
        f.write(result)

    print("Book restructuring completed - converted all main sections to subsections")

if __name__ == "__main__":
    restructure_book()