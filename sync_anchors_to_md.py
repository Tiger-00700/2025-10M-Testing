import re

def sync_anchors_to_md(docx_path, md_path, output_md_path):
    """Sync renumbered anchors from DOCX back to MD file"""

    # First, extract renumbered anchors from DOCX
    from docx import Document
    doc = Document(docx_path)
    docx_anchors = []

    for para in doc.paragraphs:
        text = para.text.strip()
        if ('锚点类型:' in text or '锚点方法:' in text or
            text.startswith('> [锚点') or text.startswith('> [第') or
            text.startswith('[锚点') or text.startswith('[第')):

            # Extract anchor ID
            match = re.search(r'\[([^\]]+)\]', text)
            if match:
                anchor_id = match.group(1)
                docx_anchors.append(anchor_id)

    print(f"Found {len(docx_anchors)} anchors in DOCX file")

    # Read MD file and find anchors to replace
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Find all anchor blocks in MD
    md_anchors = re.findall(r'> \*\*\[([^\]]+)\]\*\*', md_content)

    print(f"Found {len(md_anchors)} anchors in MD file")

    if len(docx_anchors) != len(md_anchors):
        print(f"Warning: Anchor count mismatch! DOCX: {len(docx_anchors)}, MD: {len(md_anchors)}")
        # Use the minimum count
        min_count = min(len(docx_anchors), len(md_anchors))
        docx_anchors = docx_anchors[:min_count]
        md_anchors = md_anchors[:min_count]

    # Create mapping from old to new anchor IDs
    anchor_mapping = {}
    for i, (old_id, new_id) in enumerate(zip(md_anchors, docx_anchors)):
        if old_id != new_id:
            anchor_mapping[old_id] = new_id

    print(f"Created {len(anchor_mapping)} anchor mappings")

    # Replace anchors in MD content
    def replace_anchor(match):
        old_id = match.group(1)
        if old_id in anchor_mapping:
            return f'> **[{anchor_mapping[old_id]}]**'
        return match.group(0)

    # Replace all anchor IDs
    updated_content = re.sub(r'> \*\*\[([^\]]+)\]\*\*', replace_anchor, md_content)

    # Write updated content to output file
    with open(output_md_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)

    print(f"Updated MD file saved to: {output_md_path}")
    print(f"Total replacements made: {len(anchor_mapping)}")

if __name__ == '__main__':
    sync_anchors_to_md(
        '1225全书定稿_renumbered.docx',
        'book/1225.2025.newbook.md',
        'book/1225.2025.newbook_synced.md'
    )