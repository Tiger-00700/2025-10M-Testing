import re
from pathlib import Path
from typing import List

BOOK = Path(__file__).resolve().parents[1] / "book" / "1022.2025.newbook.md"
TITLE = "# 大数据全栈测试：从理论到实战"

heading_re = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
code_fence_re = re.compile(r"^(```|~~~)")


def load_lines(p: Path) -> List[str]:
    return p.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n").split("\n")


def write_lines(p: Path, lines: List[str]) -> None:
    p.write_text("\n".join(lines), encoding="utf-8")


def ensure_title(lines: List[str]) -> List[str]:
    # find first non-blank line
    idx = 0
    while idx < len(lines) and lines[idx].strip() == "":
        idx += 1
    if idx < len(lines) and lines[idx].strip() == TITLE:
        # already has exact title
        return lines
    # insert title at very top with a blank line after
    return [TITLE, ""] + lines


def shift_headings(lines: List[str]) -> List[str]:
    out: List[str] = []
    inside_code = False
    for i, line in enumerate(lines):
        # toggle code fence
        if code_fence_re.match(line.strip()):
            inside_code = not inside_code
            out.append(line)
            continue
        # skip shifting the title itself
        if line.strip() == TITLE:
            out.append(line)
            continue
        if not inside_code:
            m = heading_re.match(line)
            if m:
                hashes, title = m.group(1), m.group(2)
                level = len(hashes)
                new_level = min(level + 1, 6)
                out.append("#" * new_level + " " + title)
                continue
        out.append(line)
    return out


def main():
    if not BOOK.exists():
        raise SystemExit(f"Book not found: {BOOK}")
    lines = load_lines(BOOK)
    lines = ensure_title(lines)
    lines = shift_headings(lines)
    write_lines(BOOK, lines)
    print("Applied title and shifted heading levels (H1->H2, etc.).")


if __name__ == "__main__":
    main()
