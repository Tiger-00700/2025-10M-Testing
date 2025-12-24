import os
import re

def extract_chapter_name(filename):
    # filename like 第7篇-第28章.md -> 第7篇-第28章
    return filename[:-3]

def process_file(filepath, chapter_name):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all anchor blocks
    anchor_pattern = r'(\[锚点编号: \d+\]\n(?:.*?\n)*?)(?=\[锚点编号: \d+\]|\Z)'
    anchors = re.findall(anchor_pattern, content, re.MULTILINE | re.DOTALL)
    
    modified = False
    new_content = content
    
    for anchor in anchors:
        lines = anchor.strip().split('\n')
        has_location = any('所在行区间:' in line for line in lines)
        has_update_time = any('更新时间:' in line for line in lines)
        
        if not has_location or not has_update_time:
            modified = True
            # Find positions
            name_index = next(i for i, line in enumerate(lines) if line.startswith('锚点名称:'))
            suggestion_index = next((i for i, line in enumerate(lines) if line.startswith('补充建议:')), len(lines))
            
            new_lines = lines[:]
            if not has_location:
                # Insert after name
                new_lines.insert(name_index + 1, f'所在行区间: {chapter_name}')
            if not has_update_time:
                # Insert after suggestion
                new_lines.insert(suggestion_index + 1, '更新时间: 2025-12-23')
            
            new_anchor = '\n'.join(new_lines) + '\n'
            new_content = new_content.replace(anchor, new_anchor)
    
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def main():
    chapter_dir = r'e:\DONT_TOUCH\10M-2025-Testing\chapter'
    fixed_files = []
    
    for filename in os.listdir(chapter_dir):
        if filename.endswith('.md'):
            filepath = os.path.join(chapter_dir, filename)
            chapter_name = extract_chapter_name(filename)
            if process_file(filepath, chapter_name):
                fixed_files.append(filename)
    
    print('Fixed files:', fixed_files)

if __name__ == '__main__':
    main()</content>
<parameter name="filePath">e:\DONT_TOUCH\10M-2025-Testing\fix_anchors.py