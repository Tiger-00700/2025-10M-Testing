# 重新编号所有章节以确保连续性
import os
import re

def renumber_chapters():
    framework_dir = r'e:\DONT_TOUCH\10M-2025-Testing\framework'

    # 按照文件名排序处理framework文件
    framework_files = sorted([f for f in os.listdir(framework_dir) if f.endswith('.md')])

    chapter_counter = 1

    for file_name in framework_files:
        file_path = os.path.join(framework_dir, file_name)
        print(f'Processing {file_name}')

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 找到所有章节标题
        chapter_pattern = r'^### 第(\d+)章(.*)$'
        chapters = re.findall(chapter_pattern, content, re.MULTILINE)

        if not chapters:
            continue

        # 重新编号章节
        new_content = content
        for old_num, title_suffix in chapters:
            old_header = f'### 第{old_num}章{title_suffix}'
            new_header = f'### 第{chapter_counter}章{title_suffix}'
            new_content = new_content.replace(old_header, new_header)

            # 同时更新对应的子节编号
            old_section_pattern = f'#### {old_num}\.'
            new_section_pattern = f'#### {chapter_counter}.'
            new_content = re.sub(old_section_pattern, new_section_pattern, new_content)

            # 更新子节的引用
            old_subsection_pattern = f'##### {old_num}\.'
            new_subsection_pattern = f'##### {chapter_counter}.'
            new_content = re.sub(old_subsection_pattern, new_subsection_pattern, new_content)

            chapter_counter += 1

        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

    print(f'Renumbered chapters from 1 to {chapter_counter-1}')

if __name__ == '__main__':
    renumber_chapters()