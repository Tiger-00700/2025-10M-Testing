import re

def fix_section_numbers_v2():
    """Fix section numbering issues in all framework files - version 2"""

    framework_files = [
        'framework/第1篇-入门篇-大数据测试基础.md',
        'framework/第2篇-进阶篇-大数据测试方法与技术.md',
        'framework/第3篇-进阶篇-环境与数据治理.md',
        'framework/第4篇-进阶篇-数据质量安全.md',
        'framework/第5篇-进阶篇-自动化、工具与可观测性.md',
        'framework/第6篇-专家篇-案例与性能.md',
        'framework/第7篇-专家篇-项目与治理.md',
        'framework/第8篇-专家篇-趋势与平台化.md'
    ]

    for file_path in framework_files:
        print(f'Processing {file_path}...')

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        lines = content.split('\n')
        new_lines = []
        current_chapter = None
        section_counter = 0
        subsection_counters = {}  # Track subsections for each section

        for line in lines:
            # Check for chapter headers
            chapter_match = re.match(r'^### 第(\d+)章', line)
            if chapter_match:
                current_chapter = int(chapter_match.group(1))
                section_counter = 0  # Reset section counter for new chapter
                subsection_counters = {}  # Reset subsection counters
                new_lines.append(line)
                continue

            # Check for main section headers (#### X.X)
            section_match = re.match(r'^#### (\d+(?:\.\d+)*)', line)
            if section_match and current_chapter:
                old_section = section_match.group(1)
                section_counter += 1
                new_section = f"{current_chapter}.{section_counter}"
                new_line = line.replace(old_section, new_section, 1)
                new_lines.append(new_line)

                # Initialize subsection counter for this section
                subsection_counters[section_counter] = 0
                continue

            # Check for subsection headers (##### X.X.X)
            subsection_match = re.match(r'^##### (\d+(?:\.\d+)+)', line)
            if subsection_match and current_chapter and section_counter > 0:
                old_subsection = subsection_match.group(1)
                parts = old_subsection.split('.')

                # If it has 3 parts and the first two match current chapter.section
                if len(parts) >= 3:
                    try:
                        major = int(parts[0])
                        minor = int(parts[1])
                        sub = int(parts[2])

                        # If the major.minor matches current chapter.section, update the sub number
                        if major == current_chapter and minor == section_counter:
                            subsection_counters[section_counter] += 1
                            new_subsection = f"{current_chapter}.{section_counter}.{subsection_counters[section_counter]}"
                            new_line = line.replace(old_subsection, new_subsection, 1)
                            new_lines.append(new_line)
                            continue
                        # If it doesn't match, it might be from a different section, keep as is
                        else:
                            new_lines.append(line)
                            continue
                    except ValueError:
                        pass

                # Keep line as is if we can't parse it
                new_lines.append(line)
                continue

            # Keep line as is
            new_lines.append(line)

        # Write back the fixed content
        new_content = '\n'.join(new_lines)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f'Fixed {file_path}')

    print('All framework files processed. Rebuilding book...')

if __name__ == '__main__':
    fix_section_numbers_v2()