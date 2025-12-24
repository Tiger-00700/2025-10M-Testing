import re
import os

# Read the entire book file
with open('e:\\DONT_TOUCH\\10M-2025-Testing\\book\\1208.2025.newbook.update.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Split into lines
lines = content.split('\n')

# Output directory
output_dir = 'e:\\DONT_TOUCH\\10M-2025-Testing\\chapter-new'

# Patterns
pian_pattern = re.compile(r'^## (第.+篇)')
zhang_pattern = re.compile(r'^### (第\d+章)')

current_pian = None
chapters = {}  # dict of (pian, zhang) -> content

current_zhang = None
chapter_content = []
in_chapter = False

for line in lines:
    # Check for pian
    pian_match = pian_pattern.match(line)
    if pian_match:
        current_pian = pian_match.group(1)
        continue
    
    # Check for zhang
    zhang_match = zhang_pattern.match(line)
    if zhang_match:
        # If we were in a chapter, save it
        if in_chapter and current_pian and current_zhang:
            chapters[(current_pian, current_zhang)] = chapter_content
        
        # Start new chapter
        current_zhang = zhang_match.group(1)
        chapter_content = [line]  # Include the title
        in_chapter = True
    elif in_chapter:
        chapter_content.append(line)

# Save the last chapter
if in_chapter and current_pian and current_zhang:
    chapters[(current_pian, current_zhang)] = chapter_content

# Write all chapters
for (pian, zhang), content in chapters.items():
    filename = f"{pian}-{zhang}.md"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))