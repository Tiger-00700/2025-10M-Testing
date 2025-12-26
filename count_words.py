import re

def count_chinese(text):
    return len(re.findall(r'[\u4e00-\u9fff]', text))

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    counts = {'total': 0, 'parts': {}, 'chapters': {}}
    current_part = None
    current_chapter = None
    in_code = False
    in_mermaid = False
    in_table = False
    mermaid_counted = False
    table_counted = False
    
    for line in lines:
        line = line.rstrip('\n')
        
        # Check for part anchor
        part_anchor_match = re.search(r'\*\*\[第(\d+)篇-', line)
        if part_anchor_match:
            current_part = int(part_anchor_match.group(1))
            current_chapter = None
            continue
        
        # Check for chapter header
        chapter_match = re.match(r'^## 第(\d+)章', line)
        if chapter_match:
            current_chapter = int(chapter_match.group(1))
            chapter_key = f"{current_part}-{current_chapter}"
            if chapter_key not in counts['chapters']:
                counts['chapters'][chapter_key] = 0
            continue
        
        # Check for code block start/end
        if line.strip().startswith('```'):
            if in_code:
                in_code = False
                if in_mermaid and not mermaid_counted:
                    counts['total'] += 1
                    if current_part:
                        counts['parts'].setdefault(current_part, 0)
                        counts['parts'][current_part] += 1
                    if current_chapter:
                        counts['chapters'][f"{current_part}-{current_chapter}"] += 1
                    mermaid_counted = True
                in_mermaid = False
                mermaid_counted = False
            else:
                in_code = True
                if 'mermaid' in line.lower():
                    in_mermaid = True
                    mermaid_counted = False
            continue
        
        if in_code:
            continue
        
        # Check for table
        if line.strip().startswith('|'):
            if not in_table:
                in_table = True
                table_counted = False
            if not table_counted:
                counts['total'] += 1
                if current_part:
                    counts['parts'].setdefault(current_part, 0)
                    counts['parts'][current_part] += 1
                if current_chapter:
                    counts['chapters'][f"{current_part}-{current_chapter}"] += 1
                table_counted = True
        else:
            if in_table:
                in_table = False
                table_counted = False
        
        # Count Chinese characters in pure text
        chinese_count = count_chinese(line)
        if chinese_count > 0:
            counts['total'] += chinese_count
            if current_part:
                counts['parts'].setdefault(current_part, 0)
                counts['parts'][current_part] += chinese_count
            if current_chapter:
                counts['chapters'][f"{current_part}-{current_chapter}"] += chinese_count
    
    # Build output
    output_parts = [str(counts['total'])]
    for part_num in sorted(counts['parts'].keys()):
        output_parts.append(str(counts['parts'][part_num]))
        chapter_counts = [str(counts['chapters'].get(f"{part_num}-{chap}", 0)) for chap in sorted([int(k.split('-')[1]) for k in counts['chapters'] if k.startswith(f"{part_num}-")])]
        if chapter_counts:
            output_parts.append(', '.join(chapter_counts))
    
    return ' / '.join(output_parts)

if __name__ == "__main__":
    filepath = r"e:\DONT_TOUCH\10M-2025-Testing\book\1225.2025.newbook.md"
    result = process_file(filepath)
    print(result)
    with open('result.txt', 'w', encoding='utf-8') as f:
        f.write(result)