#!/usr/bin/env python3
"""
Annotate scope-notes in the book with a skeleton notice based on examples/<topic>/.skeleton markers.

Behavior:
- For each line matching '最小实操路径：examples/<topic>' in book/1022.2025.book.md:
  - If examples/<topic>/.skeleton exists: ensure the next line contains
    '- 注：本章示例为骨架占位，后续将补充内容'
  - Else: remove such annotation line if present.
- Also normalize the immediate '示例脚本：examples/<topic>/smoke.*' line:
  - If skeleton: ensure it ends with '；当前为骨架占位（.skeleton）'
  - Else: remove that suffix if present.

Non-destructive: only touches the book file.
"""
        """Annotate scope-notes in the book with a skeleton notice.

        The script scans for lines like '最小实操路径：examples/<topic>' and:
            - if examples/<topic>/.skeleton exists, ensures an annotation line is
                present directly after the H2; otherwise removes that annotation.
            - it also normalizes the adjacent '示例脚本：examples/<topic>/smoke.*' line
                by adding or removing the suffix '；当前为骨架占位（.skeleton）' as needed.

        This tool is non-destructive: it only edits the book file when necessary.
        """
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "book" / "1022.2025.book.md"
EXAMPLES = ROOT / "examples"

ANNOTATION_LINE = "- 注：本章示例为骨架占位，后续将补充内容"
SUFFIX = "；当前为骨架占位（.skeleton）"


def is_skeleton(topic: str) -> bool:
    return (EXAMPLES / topic / ".skeleton").exists()


def process_book(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []

    i = 0
    while i < len(lines):
        line = lines[i]
        out.append(line)

        # Match minimal path line
        m = re.search(r"最小实操路径：examples/([A-Za-z0-9_\-]+)", line)
        if m:
            topic = m.group(1)
            sk = is_skeleton(topic)

            # Look-ahead to see if next line is the annotation
            next_line = lines[i + 1] if (i + 1) < len(lines) else None
            if sk:
                # Ensure annotation present
                if next_line != ANNOTATION_LINE:
                    out.append(ANNOTATION_LINE)
                else:
                    # Already present; it will be added when we append next line below
                    pass
            else:
                # Ensure annotation absent
                if next_line == ANNOTATION_LINE:
                    # Skip consuming it by incrementing i extra
                    i += 1
                    # Also reflect removal by not appending it
            
            # Try to normalize the immediate '示例脚本' line after (which could be next or next-next)
            # We check up to the next 3 lines for a script line for this topic
            j = 1
            while j <= 3 and (i + j) < len(lines):
                l2 = lines[i + j]
                if re.search(fr"示例脚本：examples/{re.escape(topic)}/smoke\.\w+", l2):
                            # Preserve trailing CRLF artifacts and remove literal '\r' artifacts
                            base = l2.replace("\\r" + SUFFIX, "")
                    # Do not try to preserve trailing markers; keep line content as-is otherwise
                    trail = ""
                        # Do not try to preserve trailing markers; keep content as-is
                    if sk:
                        # Ensure exactly one suffix occurrence
                        base = base.replace(SUFFIX, "")
                        if SUFFIX not in base:
                            base = base + SUFFIX
                    else:
                        # Remove all occurrences
                        base = base.replace(SUFFIX, "")
                    lines[i + j] = base + trail
                    break
                # If we hit a blank line or a new heading, stop searching
                if l2.startswith("## ") or l2.startswith("### "):
                    break
                j += 1

        i += 1

    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


def main() -> int:
    if not BOOK.exists():
        print(f"Book file not found: {BOOK}")
        return 1
    original = BOOK.read_text(encoding="utf-8")
    updated = process_book(original)
    if updated != original:
        BOOK.write_text(updated, encoding="utf-8")
        print("Updated book annotations for skeleton topics.")
    else:
        print("No changes needed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
