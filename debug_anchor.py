from docx import Document

doc = Document('1225全书定稿_final_standardized_fixed.docx')

# Debug: show exactly what metadata is extracted for anchor 020
for i, para in enumerate(doc.paragraphs):
    text = para.text.strip()
    if '[锚点020]' in text and '应用场景分类表' in text:
        print('Raw text:')
        print(repr(text[:300]))
        print()

        lines = text.split('\n')
        print('All lines:')
        for j, line in enumerate(lines[:15]):  # First 15 lines
            print(f'  {j}: {repr(line)}')
        print()

        # Extract metadata
        metadata_lines = []
        for line in lines:
            if line.strip().startswith('**') and not line.strip().startswith('>**'):
                print(f'Content starts at line with: {repr(line)}')
                break
            metadata_lines.append(line)

        metadata_text = '\n'.join(metadata_lines)
        print('Extracted metadata:')
        print(repr(metadata_text))
        print()

        print('Version checks on metadata:')
        print(f'  "版本: v1.0" in metadata: {"版本: v1.0" in metadata_text}')
        print(f'  "**版本**:" in metadata: {"**版本**:" in metadata_text}')
        break