from docx import Document

doc = Document('1225全书定稿.docx')
for i, para in enumerate(doc.paragraphs[:100]):
    text = para.text.strip()
    if '锚点' in text or '更新时间' in text or '时间戳' in text:
        print(f'Para {i}: "{text}"')