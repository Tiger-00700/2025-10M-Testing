from docx import Document
from docx.oxml import parse_xml
import re

def fix_anchor_issues(input_path, output_path):
    '''修复锚点相关问题'''

    doc = Document(input_path)
    fixes_applied = {
        'empty_lines_removed': 0,
        'timestamps_updated': 0,
        'anchors_standardized': 0,
        'duplicate_fields_removed': 0
    }

    print('Fixing anchor issues...')

    # Define XML string
    shading_xml = '<w:shd xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:val="clear" w:color="auto" w:fill="E6F3FF"/>'

    # Process all anchor paragraphs
    for para in doc.paragraphs:
        text = para.text.strip()

        # Check if this is an anchor paragraph
        is_anchor = False
        if ('锚点类型:' in text and '锚点方法:' in text) or ('**锚点类型**:' in text):
            is_anchor = True
        elif re.match(r'^\[锚点\d+-\d+\]', text) or re.match(r'^\[第\d+篇-\d+\]', text):
            is_anchor = True
        elif text.startswith('>锚点名称:') and ('锚点类型:' in text or '**锚点类型**:' in text):
            is_anchor = True

        if is_anchor:
            print(f'Processing anchor: {text[:50]}...')

            # Split into lines and clean up
            lines = text.split('\n')
            cleaned_lines = []

            # Remove empty lines and > only lines
            for line in lines:
                line = line.strip()
                if line and line != '>' and not line.startswith('**') and not line.endswith('**'):
                    cleaned_lines.append(line)

            # Remove markdown bold markers from lines
            processed_lines = []
            for line in cleaned_lines:
                # Remove ** markers
                line = re.sub(r'^\*\*|\*\*$', '', line)
                processed_lines.append(line)

            # Update timestamp and remove duplicates
            final_lines = []
            seen_fields = set()

            for line in processed_lines:
                if line.startswith('>更新时间:'):
                    final_lines.append('>更新时间: 2025-12-27')
                    fixes_applied['timestamps_updated'] += 1
                elif line.startswith('更新时间:'):
                    final_lines.append('>更新时间: 2025-12-27')
                    fixes_applied['timestamps_updated'] += 1
                elif ':' in line and not line.startswith('>'):
                    # Add > prefix if missing
                    if not line.startswith('>'):
                        line = '>' + line
                    final_lines.append(line)
                elif line.startswith('>') and ':' in line:
                    # Check for duplicates
                    field_name = line.split(':', 1)[0].lstrip('>')
                    if field_name not in seen_fields:
                        final_lines.append(line)
                        seen_fields.add(field_name)
                    else:
                        fixes_applied['duplicate_fields_removed'] += 1
                        print(f'  Removed duplicate field: {field_name}')
                else:
                    final_lines.append(line)

            # Remove any remaining empty > lines
            final_cleaned = []
            for line in final_lines:
                if line.strip() not in ['', '>']:
                    final_cleaned.append(line)

            if final_cleaned != processed_lines:
                fixes_applied['empty_lines_removed'] += 1

            para.text = '\n'.join(final_cleaned)

            # Apply visual formatting
            p_element = para._element
            pPr = p_element.get_or_add_pPr()
            shading = parse_xml(shading_xml)
            pPr.append(shading)

            fixes_applied['anchors_standardized'] += 1

    doc.save(output_path)

    print(f'\nAnchor fixes applied:')
    for fix_type, count in fixes_applied.items():
        print(f'  {fix_type}: {count}')

    print(f'\nSaved to: {output_path}')
    return fixes_applied

# Run the fix
fixes = fix_anchor_issues('1225全书定稿_markdown_fixed.docx', '1225全书定稿_anchors_cleaned.docx')