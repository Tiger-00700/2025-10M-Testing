import re

def standardize_anchor_format(md_file_path, output_file_path):
    """Standardize anchor format in MD file"""

    with open(md_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern to find anchor blocks
    anchor_pattern = r'(> \*\*\[([^\]]+)\]\*\* [^\n]*\n(?:> \*\*[^*]*\*\*:[^\n]*\n)*)'

    def fix_anchor_block(match):
        anchor_block = match.group(1)
        anchor_id = match.group(2)

        # Parse existing fields
        lines = anchor_block.strip().split('\n')
        fields = {}

        for line in lines:
            line = line.strip()
            if line.startswith('> **[锚点类型]**:'):
                fields['type'] = line.replace('> **[锚点类型]**:', '').strip()
            elif line.startswith('> **锚点方法]**:'):
                fields['method'] = line.replace('> **[锚点方法]**:', '').strip()
            elif line.startswith('> **锚点名称]**:'):
                fields['name'] = line.replace('> **[锚点名称]**:', '').strip()
            elif line.startswith('> **引用附件]**:'):
                fields['reference'] = line.replace('> **[引用附件]**:', '').strip()
            elif line.startswith('> **补充建议]**:'):
                fields['suggestion'] = line.replace('> **[补充建议]**:', '').strip()
            elif line.startswith('> **完成情况]**:'):
                fields['status'] = line.replace('> **[完成情况]**:', '').strip()
            elif line.startswith('> **状态]**:'):
                fields['status'] = line.replace('> **[状态]**:', '').strip()
            elif line.startswith('> **版本]**:'):
                fields['version'] = line.replace('> **[版本]**:', '').strip()
            elif line.startswith('> **更新时间]**:'):
                fields['timestamp'] = line.replace('> **[更新时间]**:', '').strip()
            elif line.startswith('> **时间戳]**:'):
                fields['timestamp'] = line.replace('> **[时间戳]**:', '').strip()

        # Extract title from first line
        title_match = re.search(r'> \*\*\[[^\]]+\]\*\* (.+)', lines[0])
        title = title_match.group(1) if title_match else ""

        # Build standardized anchor block
        standardized_lines = [
            f'> **[{anchor_id}]** {title}',
            f'> **锚点类型**: {fields.get("type", "建议")}',
            f'> **锚点方法**: {fields.get("method", "配置示例")}',
            f'> **引用附件**: {fields.get("reference", "")}',
            f'> **完成情况**: {fields.get("status", "已完成")}',
            f'> **补充建议**: {fields.get("suggestion", "")}',
            f'> **更新时间**: {fields.get("timestamp", "2025-12-24")}'
        ]

        return '\n'.join(standardized_lines) + '\n'

    # Apply fixes
    updated_content = re.sub(anchor_pattern, fix_anchor_block, content, flags=re.MULTILINE)

    # Write to output file
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)

    print(f"Standardized anchor formats saved to: {output_file_path}")

if __name__ == '__main__':
    standardize_anchor_format('book/1225.2025.newbook.md', 'book/1225.2025.newbook_standardized.md')