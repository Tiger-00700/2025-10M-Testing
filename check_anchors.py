from docx import Document

doc = Document('1225全书定稿_final_standardized.docx')
count = 0
for para in doc.paragraphs:
    text = para.text.strip()
    if text.startswith('> [') and ']' in text:
        print(f'Found anchor: "{text[:100]}..."')
        count += 1
        if count > 3:
            break
print(f'Total anchors: {count}')