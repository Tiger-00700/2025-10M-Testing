from docx import Document
import re

def fix_remaining_issues(input_path, output_path):
    '''修复剩余的文档问题'''

    doc = Document(input_path)
    fixes_applied = {
        'anchors_standardized': 0,
        'markdown_headers_converted': 0,
        'prefixes_added': 0
    }

    print('Fixing remaining issues...')

    for para in doc.paragraphs:
        text = para.text.strip()
        original_text = text

        # Fix unstandardized anchors - add > prefix to anchor fields
        if ('锚点类型:' in text or '锚点方法:' in text or '锚点名称:' in text) and not text.startswith('>'):
            lines = text.split('\n')
            fixed_lines = []
            for line in lines:
                line = line.strip()
                if any(keyword in line for keyword in ['锚点名称:', '锚点类型:', '锚点方法:', '更新时间:', '补充建议:', '引用附件:']):
                    if not line.startswith('>'):
                        line = '>' + line
                        fixes_applied['prefixes_added'] += 1
                fixed_lines.append(line)
            text = '\n'.join(fixed_lines)
            fixes_applied['anchors_standardized'] += 1

        # Convert markdown headers to proper format
        if re.match(r'^#{1,6}\s', text):
            # Convert # headers to proper heading format
            # For now, just remove the # and keep the text
            text = re.sub(r'^#{1,6}\s+', '', text)
            fixes_applied['markdown_headers_converted'] += 1

        if text != original_text:
            para.text = text

    doc.save(output_path)

    print(f'\nRemaining fixes applied:')
    for fix_type, count in fixes_applied.items():
        print(f'  {fix_type}: {count}')

    print(f'\nSaved to: {output_path}')
    return fixes_applied

# Run the fix
fixes = fix_remaining_issues('1225全书定稿_anchors_cleaned.docx', '1225全书定稿_final_fixed.docx')