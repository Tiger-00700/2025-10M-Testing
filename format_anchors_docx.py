from docx import Document
from docx.oxml import parse_xml

def format_anchor_blocks(docx_path, output_path):
    doc = Document(docx_path)
    
    formatted_count = 0
    
    for para in doc.paragraphs:
        text = para.text.strip()
        # Check if this paragraph contains anchor information
        if ('锚点类型:' in text and '锚点方法:' in text) or ('更新时间:' in text and '版本:' in text):
            # This is an anchor block paragraph
            p_element = para._element
            pPr = p_element.get_or_add_pPr()
            shading_xml = '''<w:shd xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:val="clear" w:color="auto" w:fill="E6F3FF"/>'''
            shading = parse_xml(shading_xml)
            pPr.append(shading)
            formatted_count += 1
        elif text.startswith('> [锚点') or text.startswith('> [第'):
            # Anchor block with > prefix
            p_element = para._element
            pPr = p_element.get_or_add_pPr()
            shading_xml = '''<w:shd xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:val="clear" w:color="auto" w:fill="E6F3FF"/>'''
            shading = parse_xml(shading_xml)
            pPr.append(shading)
            formatted_count += 1
    
    doc.save(output_path)
    print(f'Formatted {formatted_count} anchor block paragraphs with light blue background')

if __name__ == '__main__':
    format_anchor_blocks('1225全书定稿.docx', '1225全书定稿_anchors_formatted.docx')