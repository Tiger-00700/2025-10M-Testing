from docx import Document
from docx.shared import Pt
from docx.oxml.ns import nsdecls, qn
from docx.oxml import parse_xml

def format_yaml_blocks(docx_path, output_path):
    doc = Document(docx_path)
    
    formatted_count = 0
    for paragraph in doc.paragraphs:
        # Check if it's a code block containing YAML
        is_yaml = False
        if paragraph.style.name in ['Source Code', 'Code', 'Preformatted']:
            is_yaml = True
        elif 'yaml' in paragraph.text.lower() or 'yml' in paragraph.text.lower():
            is_yaml = True
        elif paragraph.text.strip().startswith('#') and ('examples/' in paragraph.text or 'config' in paragraph.text.lower()):
            is_yaml = True
        
        if is_yaml:
            # Format YAML blocks
            for run in paragraph.runs:
                run.font.size = Pt(8)  # Smaller font
                run.font.name = 'Consolas'  # Monospace font
            
            # Add border
            p = paragraph._element
            pPr = p.get_or_add_pPr()
            borders_xml = '''<w:pBdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
                <w:top w:val="single" w:sz="4" w:space="0" w:color="000000"/>
                <w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/>
                <w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/>
                <w:right w:val="single" w:sz="4" w:space="0" w:color="000000"/>
            </w:pBdr>'''
            borders = parse_xml(borders_xml)
            pPr.append(borders)
            formatted_count += 1
    
    doc.save(output_path)
    print(f"Formatted {formatted_count} YAML blocks")

if __name__ == '__main__':
    format_yaml_blocks('1225全书定稿.docx', '1225全书定稿_yaml_formatted.docx')