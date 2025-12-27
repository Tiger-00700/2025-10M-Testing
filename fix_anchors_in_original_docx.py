from docx import Document
from docx.oxml import parse_xml
import re

def fix_and_format_anchors_in_docx(input_path, output_path):
    """直接修复原始DOCX文件中的锚点格式问题并应用视觉格式"""

    doc = Document(input_path)
    fixed_count = 0
    formatted_count = 0

    # 遍历所有段落，修复锚点格式
    i = 0
    while i < len(doc.paragraphs):
        para = doc.paragraphs[i]
        text = para.text.strip()

        # 检查是否是锚点块的开始
        if text.startswith('> [') and ('锚点' in text or '第' in text):
            # 解析锚点ID和标题
            title_match = re.search(r'> \*\*\[([^\]]+)\]\*\* (.+)', text)
            if title_match:
                anchor_id = title_match.group(1)
                title = title_match.group(2)

                # 收集所有锚点字段
                fields = {}
                field_count = 0
                j = i + 1

                while j < len(doc.paragraphs) and field_count < 10:  # 最多检查10个段落
                    next_para = doc.paragraphs[j]
                    next_text = next_para.text.strip()

                    if next_text.startswith('> **') and ':' in next_text:
                        if '锚点类型:' in next_text:
                            fields['type'] = next_text.replace('> **锚点类型**:', '').strip()
                        elif '锚点方法:' in next_text:
                            fields['method'] = next_text.replace('> **锚点方法**:', '').strip()
                        elif '引用附件:' in next_text:
                            fields['reference'] = next_text.replace('> **引用附件**:', '').strip()
                        elif '完成情况:' in next_text:
                            fields['status'] = next_text.replace('> **完成情况**:', '').strip()
                        elif '状态:' in next_text:
                            fields['status'] = next_text.replace('> **状态**:', '').strip()
                        elif '补充建议:' in next_text:
                            fields['suggestion'] = next_text.replace('> **补充建议**:', '').strip()
                        elif '更新时间:' in next_text:
                            fields['timestamp'] = next_text.replace('> **更新时间**:', '').strip()
                        elif '时间戳:' in next_text:
                            fields['timestamp'] = next_text.replace('> **时间戳**:', '').strip()
                        field_count += 1
                        j += 1
                    else:
                        break

                # 检查是否需要修复
                needs_fix = (
                    'type' not in fields or
                    'method' not in fields or
                    'status' not in fields or
                    'timestamp' not in fields
                )

                if needs_fix:
                    # 重建锚点块
                    fixed_lines = [
                        f'> **[{anchor_id}]** {title}',
                        f'> **锚点类型**: {fields.get("type", "建议")}',
                        f'> **锚点方法**: {fields.get("method", "配置示例")}',
                        f'> **引用附件**: {fields.get("reference", "")}',
                        f'> **完成情况**: {fields.get("status", "已完成")}',
                        f'> **补充建议**: {fields.get("suggestion", "")}',
                        f'> **更新时间**: {fields.get("timestamp", "2025-12-26")}'
                    ]

                    # 更新段落内容
                    for k, line in enumerate(fixed_lines):
                        if i + k < len(doc.paragraphs):
                            doc.paragraphs[i + k].text = line

                    fixed_count += 1
                    i += len(fixed_lines)  # 跳过已处理的段落
                    continue

        i += 1

    # 应用视觉格式到所有锚点段落
    for para in doc.paragraphs:
        text = para.text.strip()
        if ('锚点类型:' in text and '锚点方法:' in text) or ('更新时间:' in text) or text.startswith('> ['):
            # 应用浅蓝色背景
            p_element = para._element
            pPr = p_element.get_or_add_pPr()
            shading_xml = '''<w:shd xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:val="clear" w:color="auto" w:fill="E6F3FF"/>'''
            shading = parse_xml(shading_xml)
            pPr.append(shading)
            formatted_count += 1

    doc.save(output_path)
    print(f"Fixed {fixed_count} incomplete anchor blocks")
    print(f"Applied visual formatting to {formatted_count} anchor paragraphs")
    print(f"Saved to: {output_path}")

if __name__ == '__main__':
    fix_and_format_anchors_in_docx('1225全书定稿.docx', '1225全书定稿_final_complete_fixed.docx')