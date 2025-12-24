import re

def fix_section_structure():
    # Read the book
    with open('book/1208.2025.newbook.update.md', 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix the malformed section headers created by the previous script
    # Pattern: ##### X.Y.1  Title -> ##### X.Y.1 Title (remove extra space)
    content = re.sub(r'##### (\d+\.\d+\.1)  ', r'##### \1 ', content)

    # Fix the sub-sub-sections that were incorrectly created
    # Pattern: ###### X.Y.1 .Z Title -> ##### X.Y.Z Title
    content = re.sub(r'###### (\d+\.\d+)\.1 \.(\d+) ([^\n]*)', r'##### \1.\2 \3', content)

    # Write back
    with open('book/1208.2025.newbook.update.md', 'w', encoding='utf-8') as f:
        f.write(content)

    print("Fixed section structure")

if __name__ == "__main__":
    fix_section_structure()