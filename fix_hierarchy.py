import re

def fix_section_hierarchy():
    # Read the book
    with open('book/1208.2025.newbook.update.md', 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern to find sections like ##### X.Y.1 Title
    # We need to convert these to #### X.Y Title (main section)
    # And convert ###### X.Y.1 SubTitle to ##### X.Y.1 SubTitle (subsection)

    # First, handle the main sections: ##### X.Y.1 Title -> #### X.Y Title
    def convert_main_section(match):
        level = match.group(1)  # #####
        section_num = match.group(2)  # X.Y.1
        title = match.group(3)  # Title

        # Extract X.Y from X.Y.1
        parts = section_num.split('.')
        if len(parts) == 3 and parts[2] == '1':
            main_section_num = f"{parts[0]}.{parts[1]}"
            return f"#### {main_section_num} {title}"
        return match.group(0)

    # Apply the conversion for main sections
    content = re.sub(r'(#####) (\d+\.\d+\.1)([^\n]*)', convert_main_section, content)

    # Now handle subsections: ###### X.Y.1 SubTitle -> ##### X.Y.1 SubTitle
    def convert_subsection(match):
        level = match.group(1)  # ######
        section_num = match.group(2)  # X.Y.1
        title = match.group(3)  # SubTitle

        return f"##### {section_num} {title}"

    content = re.sub(r'(######) (\d+\.\d+\.\d+)([^\n]*)', convert_subsection, content)

    # Write back
    with open('book/1208.2025.newbook.update.md', 'w', encoding='utf-8') as f:
        f.write(content)

    print("Fixed section hierarchy - added main sections")

if __name__ == "__main__":
    fix_section_hierarchy()