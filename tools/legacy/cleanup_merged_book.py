"""
Cleanup the merged book source by removing small, noisy artifacts.

What it does:
 - Remove duplicate <!-- anchor:xxx --> lines (keep the first occurrence).
 - Remove <!-- Placeholder --> and empty template sections (学习目标/小结/练习).
 - Collapse multiple blank lines into a single blank line.
 - Optionally drop headings that have no content (unless followed by subheadings).

Input  : book/1022.2025.newbook.merged.md
Output : book/1022.2025.newbook.cleaned.md
"""
import re
from pathlib import Path

SRC = Path("book/1022.2025.newbook.merged.md")
OUT = Path("book/1022.2025.newbook.cleaned.md")

ANCHOR_RE = re.compile(r"<!--\s*anchor:([\w-]+)\s*-->")
PLACEHOLDER_RE = re.compile(r"<!--\s*Placeholder\s*-->")
TEMPLATE_HEADINGS = ["学习目标", "小结", "练习"]
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


def remove_duplicate_anchors(lines):
    seen = set()
    out = []
    for line in lines:
        m = ANCHOR_RE.match(line)
        if m:
            anchor = m.group(1)
            if anchor in seen:
                continue
            seen.add(anchor)
        out.append(line)
    return out


def remove_placeholders_and_empty_templates(lines):
    out = []
    i = 0
    while i < len(lines):
        # Remove <!-- Placeholder -->
        if PLACEHOLDER_RE.match(lines[i]):
            i += 1
            continue
        # Remove empty template sections
        m = HEADING_RE.match(lines[i])
        if m and m.group(2).strip() in TEMPLATE_HEADINGS:
            # Check if next non-blank is heading or EOF
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j >= len(lines) or HEADING_RE.match(lines[j]):
                # Empty section, skip heading and blanks
                i = j
                continue
        out.append(lines[i])
        i += 1
    return out


def collapse_blank_lines(lines):
    out = []
    prev_blank = False
    for line in lines:
        if not line.strip():
            if prev_blank:
                continue
            prev_blank = True
        else:
            prev_blank = False
        out.append(line)
    return out


def remove_empty_headings(lines):
    out = []
    i = 0
    while i < len(lines):
        m = HEADING_RE.match(lines[i])
        if m:
            # Look ahead for next non-blank, non-heading line
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j >= len(lines) or HEADING_RE.match(lines[j]):
                # No content, skip heading and blanks
                i = j
                continue
        out.append(lines[i])
        i += 1
    return out


def main():
    lines = SRC.read_text(encoding="utf-8").splitlines()
    lines = remove_duplicate_anchors(lines)
    lines = remove_placeholders_and_empty_templates(lines)
    lines = collapse_blank_lines(lines)
    lines = remove_empty_headings(lines)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Cleaned book written: {OUT}")

if __name__ == "__main__":
    main()
