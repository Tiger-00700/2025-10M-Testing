import re
from pathlib import Path
from typing import List

TARGET = Path(__file__).resolve().parents[1] / "book" / "1022.2025.newbook.md"

heading_re = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
list_item_re = re.compile(r"^\s*(?:[-*+]\s+|\d+\.\s+)")
blockquote_re = re.compile(r"^\s*>\s*")


def load_lines(path: Path) -> List[str]:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    return text.split("\n")


def save_lines(path: Path, lines: List[str]):
    path.write_text("\n".join(lines), encoding="utf-8")


def ensure_blank_before(lines: List[str], idx: int) -> int:
    if idx <= 0:
        return idx
    if lines[idx - 1].strip() != "":
        lines.insert(idx, "")
        return idx + 1
    return idx


def ensure_blank_after(lines: List[str], idx: int):
    nxt = idx + 1
    if nxt >= len(lines) or lines[nxt].strip() != "":
        lines.insert(nxt, "")


def fix_headings(lines: List[str]):
    i = 0
    while i < len(lines):
        if heading_re.match(lines[i]):
            i = ensure_blank_before(lines, i)
            ensure_blank_after(lines, i)
            i += 1
        else:
            i += 1


def find_list_blocks(lines: List[str]) -> List[tuple]:
    blocks = []
    i = 0
    n = len(lines)
    while i < n:
        if list_item_re.match(lines[i]):
            start = i
            j = i + 1
            while j < n and (
                list_item_re.match(lines[j])
                or lines[j].strip() == ""
                or blockquote_re.match(lines[j])
            ):
                # include blank lines and quote continuations inside list block
                # but stop at a new heading
                if heading_re.match(lines[j]):
                    break
                j += 1
            end = j - 1
            # adjust start to first non-blank of this block
            while (
                start > 0
                and lines[start].strip() == ""
                and list_item_re.match(lines[start + 1])
            ):
                start += 1
            blocks.append((start, end))
            i = j
        else:
            i += 1
    return blocks


def fix_lists(lines: List[str]):
    blocks = find_list_blocks(lines)
    # apply from bottom to top to keep indices stable
    for start, end in sorted(blocks, key=lambda x: x[0], reverse=True):
        # ensure blank before the list block
        start = ensure_blank_before(lines, start)
        # ensure blank after the list block.
        # compute new end index after potential insertion at start
        end = end + (1 if start > 0 and lines[start - 1].strip() == "" else 0)
        # walk forward to last actual list item (skip trailing blanks inside)
        last = end
        while last >= start and lines[last].strip() == "":
            last -= 1
        if last >= start:
            ensure_blank_after(lines, last)


def main():
    if not TARGET.exists():
        raise SystemExit(f"Target not found: {TARGET}")
    lines = load_lines(TARGET)
    fix_headings(lines)
    fix_lists(lines)
    save_lines(TARGET, lines)
    print(f"Fixed heading/list blanks for {TARGET}")

if __name__ == "__main__":
    main()
