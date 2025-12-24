import re

def add_missing_subsections():
    # Read the book
    with open('book/1208.2025.newbook.update.md', 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract all sections
    sections = re.findall(r'^(?:#{4}|#{5}) (\d+(?:\.\d+)+)', content, re.MULTILINE)

    chapters = {}
    for sec in sections:
        parts = sec.split('.')
        chapter = int(parts[0])
        section = int(parts[1])
        subsection = int(parts[2])

        if chapter not in chapters:
            chapters[chapter] = {}
        if section not in chapters[chapter]:
            chapters[chapter][section] = []
        chapters[chapter][section].append(subsection)

    # Find missing subsections
    missing_subs = []
    for chapter in sorted(chapters.keys()):
        for section in sorted(chapters[chapter].keys()):
            subsections = sorted(chapters[chapter][section])
            expected = list(range(1, max(subsections) + 1))
            for expected_sub in expected:
                if expected_sub not in subsections:
                    missing_subs.append(f'{chapter}.{section}.{expected_sub}')

    print(f'Found {len(missing_subs)} missing subsections: {missing_subs}')

    # Add missing subsections with placeholder content
    for missing_sub in missing_subs:
        # Find where to insert - after the last subsection of the same section
        parts = missing_sub.split('.')
        chapter_num = int(parts[0])
        section_num = int(parts[1])
        sub_num = int(parts[2])

        # Find the pattern for the last subsection of this section
        last_sub_pattern = f'##### {chapter_num}.{section_num}.{sub_num - 1}'
        insert_content = f'\n##### {missing_sub} [待补充内容]\n\n[此小节内容待补充]\n\n---\n'

        # Find the position after the previous subsection
        if sub_num > 1:
            prev_sub_pattern = f'##### {chapter_num}.{section_num}.{sub_num - 1}'
            # Find the end of the previous subsection (next section or ---)
            pos = content.find(prev_sub_pattern)
            if pos != -1:
                # Find the next section or chapter
                next_section_start = pos + len(prev_sub_pattern)
                # Look for next ##### or ### or ---
                next_patterns = [
                    re.search(r'#{3,5} \d+', content[next_section_start:]),
                    re.search(r'---', content[next_section_start:])
                ]

                insert_pos = next_section_start
                for pattern in next_patterns:
                    if pattern:
                        pattern_pos = next_section_start + pattern.start()
                        if insert_pos == next_section_start or pattern_pos < insert_pos:
                            insert_pos = pattern_pos

                if insert_pos > next_section_start:
                    content = content[:insert_pos] + insert_content + content[insert_pos:]
                else:
                    # Append at the end of the section
                    content = content.replace(prev_sub_pattern, prev_sub_pattern + insert_content, 1)

    # Write back
    with open('book/1208.2025.newbook.update.md', 'w', encoding='utf-8') as f:
        f.write(content)

    print(f'Added {len(missing_subs)} missing subsections with placeholder content')

if __name__ == "__main__":
    add_missing_subsections()