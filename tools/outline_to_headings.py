"""Convert generated outline bullets to Markdown headings.

Input:  book/篇章结构.new.md  (bulleted, indented outline lines like: "  - (L27) 标题")
Output: book/篇章内容.md       (Markdown headings #..###### matching original levels)

Rules:
- Each level of indentation is 2 spaces. Heading level = (indent_spaces // 2) + 1.
- Keep the original title text.
- Preserve the source line number as an inline HTML comment (e.g., <!-- L27 -->).
- Preserve existing HTML comments at the top (metadata).
"""

from __future__ import annotations

import re
from pathlib import Path

SRC = Path("book/篇章结构.new.md")
DST = Path("book/篇章内容.md")

LINE_RE = re.compile(r"^(?P<indent> *)(?:- |\*)\s*\(L(?P<line>\d+)\)\s*(?P<title>.*?)\s*$")


def convert_line(line: str) -> str | None:
    m = LINE_RE.match(line)
    if not m:
        return None
    indent_spaces = len(m.group("indent"))
    lvl = (indent_spaces // 2) + 1
    # Clamp heading level between 1 and 6
    lvl = max(1, min(6, lvl))
    title = m.group("title")
    lno = m.group("line")
    return f"{'#' * lvl} {title} <!-- L{lno} -->"


def main():
    if not SRC.exists():
        raise SystemExit(f"Source not found: {SRC}")
    lines = SRC.read_text(encoding="utf-8").splitlines()

    out_lines: list[str] = []
    for idx, raw in enumerate(lines):
        if raw.strip().startswith("<!--"):
            # Keep metadata comments as-is
            out_lines.append(raw)
            continue
        converted = convert_line(raw)
        if converted is not None:
            out_lines.append(converted)
        else:
            # Skip empty lines, but preserve a single blank line between blocks
            if raw.strip() == "":
                if out_lines and out_lines[-1] != "":
                    out_lines.append("")
            else:
                # Non-outline line; keep as-is to avoid data loss
                out_lines.append(raw)

    # Ensure file ends with newline
    content = "\n".join(out_lines) + "\n"
    DST.write_text(content, encoding="utf-8")
    print(f"Written {DST} with {len(out_lines)} lines")


if __name__ == "__main__":
    main()
