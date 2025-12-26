from docx import Document
from docx.shared import Pt
from docx.oxml.ns import nsdecls, qn
from docx.oxml import parse_xml

def optimize_yaml_in_docx(docx_path, output_path):
    doc = Document(docx_path)

    for paragraph in doc.paragraphs:
        # 假设YAML代码块在特定样式或包含'yaml'的段落
        if 'yaml' in paragraph.text.lower() or paragraph.style.name == 'Source Code':
            # 缩小字体
            for run in paragraph.runs:
                run.font.size = Pt(8)  # 缩小到8pt

            # 添加边框
            p = paragraph._element
            pPr = p.get_or_add_pPr()
            borders = parse_xml(r'<w:pBdr {}><w:top w:val="single" w:sz="4" w:space="0" w:color="000000"/><w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/><w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/><w:right w:val="single" w:sz="4" w:space="0" w:color="000000"/></w:pBdr>'.format(nsdecls('w')))
            pPr.append(borders)

    doc.save(output_path)

if __name__ == '__main__':
    optimize_yaml_in_docx('1225全书定稿.docx', '1225全书定稿_optimized.docx')