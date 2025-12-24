import re

def remove_duplicate_sections():
    # Read the book
    with open('book/1208.2025.newbook.update.md', 'r', encoding='utf-8') as f:
        content = f.read()

    # Split content by section headers
    sections = re.split(r'(^#{4,5} \d+(?:\.\d+)+ .*$)', content, flags=re.MULTILINE)

    # Rebuild content, keeping only the first occurrence of each section header
    seen_headers = set()
    result_parts = []

    i = 0
    while i < len(sections):
        part = sections[i]
        if i % 2 == 1:  # This is a header (odd indices after split)
            # Extract section number
            header_match = re.match(r'#{4,5} (\d+(?:\.\d+)+)', part)
            if header_match:
                section_num = header_match.group(1)
                if section_num in seen_headers:
                    # Skip this duplicate section (header + content)
                    i += 2  # Skip header and next content part
                    continue
                else:
                    seen_headers.add(section_num)

        result_parts.append(part)
        i += 1

    # Join back
    result = ''.join(result_parts)

    # Write back
    with open('book/1208.2025.newbook.update.md', 'w', encoding='utf-8') as f:
        f.write(result)

    print(f"Removed duplicate sections. Kept {len(seen_headers)} unique section headers.")

if __name__ == "__main__":
    remove_duplicate_sections()