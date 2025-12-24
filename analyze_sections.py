import re

def analyze_section_numbers():
    # Read the generated book
    with open('book/1208.2025.newbook.update.md', 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract all chapter headers
    chapters = re.findall(r'^### 第(\d+)章', content, re.MULTILINE)
    print(f'Found {len(chapters)} chapters: {chapters}')

    # Extract all section headers (#### X.X or #### X.X.X)
    section_pattern = r'^#### (\d+(?:\.\d+)+)'
    sections = re.findall(section_pattern, content, re.MULTILINE)
    print(f'Found {len(sections)} sections: {sections[:20]}...')  # Show first 20

    # Group sections by chapter
    chapter_sections = {}
    current_chapter = None

    lines = content.split('\n')
    for i, line in enumerate(lines):
        # Find chapter headers
        chapter_match = re.match(r'^### 第(\d+)章', line)
        if chapter_match:
            current_chapter = int(chapter_match.group(1))
            chapter_sections[current_chapter] = []
            continue

        # Find section headers within current chapter
        section_match = re.match(r'^#### (\d+(?:\.\d+)+)', line)
        if section_match and current_chapter:
            section_num = section_match.group(1)
            chapter_sections[current_chapter].append(section_num)

    print(f'\nChapter sections mapping:')
    for chap, secs in chapter_sections.items():
        print(f'Chapter {chap}: {secs}')

    # Analyze each chapter's sections
    issues = []
    all_sections = set()

    for chapter_num, section_nums in chapter_sections.items():
        if not section_nums:
            issues.append(f'Chapter {chapter_num}: No sections found')
            continue

        # Check for duplicates within chapter
        if len(section_nums) != len(set(section_nums)):
            duplicates = [x for x in section_nums if section_nums.count(x) > 1]
            issues.append(f'Chapter {chapter_num}: Duplicate sections within chapter: {list(set(duplicates))}')

        # Check for duplicates across entire book
        for sec in section_nums:
            if sec in all_sections:
                issues.append(f'Chapter {chapter_num}: Section {sec} duplicates across book')
            all_sections.add(sec)

        # Parse section numbers and check continuity
        parsed_sections = []
        for sec in section_nums:
            parts = sec.split('.')
            if len(parts) >= 2:
                try:
                    major = int(parts[0])
                    minor = int(parts[1]) if len(parts) > 1 else 0
                    sub = int(parts[2]) if len(parts) > 2 else 0
                    parsed_sections.append((major, minor, sub))
                except ValueError:
                    issues.append(f'Chapter {chapter_num}: Invalid section format: {sec}')

        # Sort sections for continuity check
        parsed_sections.sort()

        # Check if sections start from X.1 where X is chapter number
        expected_major = chapter_num
        if parsed_sections and parsed_sections[0][0] != expected_major:
            issues.append(f'Chapter {chapter_num}: First section should start with {expected_major}.1, found {parsed_sections[0][0]}.{parsed_sections[0][1]}')

        # Check continuity (basic check - sections should be sequential)
        expected_minor = 1
        for major, minor, sub in parsed_sections:
            if major != expected_major:
                issues.append(f'Chapter {chapter_num}: Section {major}.{minor} has wrong major number (expected {expected_major})')
            elif minor != expected_minor:
                issues.append(f'Chapter {chapter_num}: Missing section {expected_major}.{expected_minor} before {major}.{minor}')
                expected_minor = minor + 1
            else:
                expected_minor += 1

    # Check for missing chapters
    expected_chapters = set(range(1, 36))  # 1-35
    found_chapters = set(int(c) for c in chapters)
    missing_chapters = expected_chapters - found_chapters
    if missing_chapters:
        issues.append(f'Missing chapters: {sorted(missing_chapters)}')

    # Summary
    print(f'\n=== ANALYSIS SUMMARY ===')
    print(f'Total chapters: {len(chapters)} (expected: 35)')
    print(f'Total sections: {len(sections)}')
    print(f'Total unique sections: {len(all_sections)}')

    if issues:
        print(f'\n❌ FOUND {len(issues)} ISSUES:')
        for issue in issues:
            print(f'   • {issue}')
    else:
        print(f'\n✅ NO ISSUES FOUND - Section numbering is correct!')

    return issues

if __name__ == '__main__':
    analyze_section_numbers()