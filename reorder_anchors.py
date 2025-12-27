import re

def reorder_anchor_fields(anchor_text):
    """Reorder anchor fields to the specified order"""
    lines = anchor_text.strip().split('\n')
    fields = {}
    
    # Parse existing fields
    for line in lines:
        line = line.strip()
        if line.startswith('> **[锚点') or line.startswith('> **[第'):
            fields['title'] = line
        elif line.startswith('> **锚点类型**:'):
            fields['type'] = line
        elif line.startswith('> **锚点方法**:'):
            fields['method'] = line
        elif line.startswith('> **引用附件**:'):
            fields['reference'] = line
        elif line.startswith('> **完成情况**:'):
            fields['status'] = line
        elif line.startswith('> **补充建议**:'):
            fields['suggestion'] = line
        elif line.startswith('> **版本**:'):
            fields['version'] = line
        elif line.startswith('> **更新时间**:') or line.startswith('> **时间戳**:'):
            fields['timestamp'] = line
    
    # Reorder according to: 编号/名称/类型/方法/引用附件/完成情况/补充建议/更新时间
    ordered_lines = []
    if 'title' in fields:
        ordered_lines.append(fields['title'])
    if 'type' in fields:
        ordered_lines.append(fields['type'])
    if 'method' in fields:
        ordered_lines.append(fields['method'])
    if 'reference' in fields:
        ordered_lines.append(fields['reference'])
    if 'status' in fields:
        ordered_lines.append(fields['status'])
    if 'suggestion' in fields:
        ordered_lines.append(fields['suggestion'])
    if 'timestamp' in fields:
        ordered_lines.append(fields['timestamp'])
    
    return '\n'.join(ordered_lines)

def process_md_file(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match anchor blocks
    anchor_pattern = r'(> \*\*\[.*?\]\*\* .*?(?:\n> \*\*.*?\*\*.*?)+\n)'
    
    def replace_anchor(match):
        anchor_text = match.group(1)
        reordered = reorder_anchor_fields(anchor_text)
        return reordered + '\n'
    
    new_content = re.sub(anchor_pattern, replace_anchor, content, flags=re.MULTILINE)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("MD file processed and anchor fields reordered")

if __name__ == '__main__':
    process_md_file('book/1225.2025.newbook.md', 'book/1225.2025.newbook_reordered.md')