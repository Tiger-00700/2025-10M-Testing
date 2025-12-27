from docx import Document
import re

def fix_yaml_formatting_in_docx(docx_path, output_path):
    """Fix YAML code block formatting in DOCX file"""
    doc = Document(docx_path)

    in_yaml_block = False
    yaml_paragraphs = []

    for para in doc.paragraphs:
        text = para.text.strip()

        # Check if we're entering a YAML code block
        if text == '```yaml' or text.startswith('```yaml'):
            in_yaml_block = True
            yaml_paragraphs = []
            continue

        # Check if we're exiting a YAML code block
        if in_yaml_block and (text == '```' or text.startswith('```')):
            in_yaml_block = False
            # Process the YAML block
            if yaml_paragraphs:
                fix_yaml_block(yaml_paragraphs)
            continue

        # Collect YAML content
        if in_yaml_block:
            yaml_paragraphs.append(para)

    doc.save(output_path)
    print("YAML formatting fixed in DOCX file")

def fix_yaml_block(yaml_paragraphs):
    """Fix the formatting of a YAML block"""
    if not yaml_paragraphs:
        return

    # Collect all YAML text
    yaml_text = ""
    for para in yaml_paragraphs:
        yaml_text += para.text + "\n"

    # Parse and reformat YAML
    try:
        import yaml
        # Try to parse the YAML
        yaml_data = yaml.safe_load(yaml_text)

        # Convert back to properly formatted YAML
        formatted_yaml = yaml.dump(yaml_data, default_flow_style=False, allow_unicode=True, indent=2)

        # Update the paragraphs with formatted content
        formatted_lines = formatted_yaml.strip().split('\n')

        for i, para in enumerate(yaml_paragraphs):
            if i < len(formatted_lines):
                para.text = formatted_lines[i]
            else:
                para.text = ""

    except Exception as e:
        print(f"Could not parse YAML block: {e}")
        # If YAML parsing fails, try basic text cleanup
        for para in yaml_paragraphs:
            # Remove excessive whitespace and fix basic formatting
            text = para.text.strip()
            # Fix broken lines that should be on the same line
            if text.endswith(':') and len(yaml_paragraphs) > 1:
                continue  # Keep as is for now
            para.text = text

if __name__ == '__main__':
    fix_yaml_formatting_in_docx('1225全书定稿_final.docx', '1225全书定稿_final_fixed.docx')