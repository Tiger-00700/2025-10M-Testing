from docx import Document

doc = Document('1225全书定稿_final_standardized_fixed.docx')

# Check anchor 020 specifically
for i, para in enumerate(doc.paragraphs):
    text = para.text.strip()
    if '[锚点020]' in text and '应用场景分类表' in text:
        print(f'Anchor [锚点020] at paragraph {i}:')
        lines = text.split('\n')
        for j, line in enumerate(lines):
            if '版本' in line:
                print(f'  Line {j}: "{line}"')
        break