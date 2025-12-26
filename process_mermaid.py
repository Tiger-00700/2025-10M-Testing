import re
import subprocess
import os
import tempfile

def convert_mermaid_to_image(mermaid_code, output_path):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False, encoding='utf-8') as f:
        f.write(mermaid_code)
        temp_file = f.name

    try:
        subprocess.run([r'C:\Users\peace\AppData\Roaming\npm\mmdc.cmd', '-i', temp_file, '-o', output_path], check=True)
    except subprocess.CalledProcessError:
        print(f"Failed to convert Mermaid to image: {output_path}")
    finally:
        os.unlink(temp_file)

def process_markdown(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    mermaid_pattern = re.compile(r'```mermaid\n(.*?)\n```', re.DOTALL)
    image_counter = 0

    def replace_mermaid(match):
        nonlocal image_counter
        mermaid_code = match.group(1)
        image_path = f'mermaid_{image_counter}.png'
        convert_mermaid_to_image(mermaid_code, image_path)
        image_counter += 1
        return f'![Mermaid Diagram]({image_path})'

    new_content = mermaid_pattern.sub(replace_mermaid, content)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

if __name__ == '__main__':
    process_markdown('book/1225.2025.newbook.md', 'book/1225_processed.md')