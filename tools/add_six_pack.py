import re
from pathlib import Path
from typing import List

BOOK = Path(__file__).resolve().parents[1] / "book" / "1022.2025.newbook.md"

heading_re = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
code_fence_re = re.compile(r"^\s*(```|~~~)")

TOP_BLOCKS = [
    ("> 【先修知识】", [
        (
            "- 基础：Linux/网络/SQL/"
            " 一种脚本语言（如 Python）"
        ),
        "- 大数据入门：分布式/存储与计算分离/批流概念",
        "- 本章上下文：建议先通读本篇导读与术语表"
    ]),
    ("> 【学习目标】", [
        (
            "- 能说清本章的核心概念与边界，"
            " 形成 3~5 条要点"
        ),
        "- 能完成 1 个与本章紧密相关的动手实践",
        (
            "- 能制定最低可行的验收标准（SLO/指标/样例）"
        )
    ]),
    ("> 【核心术语】", [
        "- 请补充本章关键术语及中英对照（参考术语表）"
    ]),
]

BOTTOM_BLOCK = (
    "> 【小结】",
    [
        "- 用 3~5 条项目化要点复盘本章内容",
        "- 指出易错点/反模式与纠正建议",
        "- 给出可延伸阅读或下一步实践方向"
    ]
)


def load_lines(p: Path) -> List[str]:
    text = p.read_text(encoding="utf-8")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text.split("\n")


def save_lines(p: Path, lines: List[str]):
    p.write_text("\n".join(lines), encoding="utf-8")


def ensure_blank(lines: List[str], idx: int) -> int:
    if idx < len(lines) and (idx == 0 or lines[idx - 1].strip() != ""):
        lines.insert(idx, "")
        idx += 1
    return idx


def has_marker(lines: List[str], start: int, end: int, marker: str) -> bool:
    for i in range(start, min(end, len(lines))):
        if lines[i].strip().startswith(marker):
            return True
    return False


def find_h3_sections(lines: List[str]) -> List[tuple]:
    sections = []
    for i, ln in enumerate(lines):
        m = heading_re.match(ln)
        if m and len(m.group(1)) == 3:
            # find end
            j = i + 1
            while j < len(lines):
                n = heading_re.match(lines[j])
                if n and len(n.group(1)) <= 3:
                    break
                j += 1
            sections.append((i, j))
    return sections


def insert_top_blocks(lines: List[str], start: int, end: int) -> int:
    i = start + 1
    # skip immediate blank line to insert after heading neatly
    if i < len(lines) and lines[i].strip() == "":
        i += 1
    inserted = 0
    for marker, bullets in TOP_BLOCKS:
        if not has_marker(lines, start, end, marker):
            i = ensure_blank(lines, i)
            lines.insert(i, marker)
            i += 1
            for b in bullets:
                lines.insert(i, b)
                i += 1
            lines.insert(i, "")
            i += 1
            inserted += 1
    return inserted


def insert_bottom_block(lines: List[str], start: int, end: int) -> int:
    # before exercises block if exists, else before section end
    insert_at = end
    for k in range(end - 1, start, -1):
        s = lines[k].strip()
        if s.startswith("> 【课后思考/练习题】"):
            insert_at = k
            break
    if has_marker(lines, start, end, BOTTOM_BLOCK[0]):
        return 0
    insert_at = ensure_blank(lines, insert_at)
    lines.insert(insert_at, BOTTOM_BLOCK[0])
    insert_at += 1
    for b in BOTTOM_BLOCK[1]:
        lines.insert(insert_at, b)
        insert_at += 1
    lines.insert(insert_at, "")
    return 1


def main():
    if not BOOK.exists():
        raise SystemExit(f"Book not found: {BOOK}")
    lines = load_lines(BOOK)
    sections = find_h3_sections(lines)
    total_top = 0
    total_bottom = 0
    # process from bottom to keep indices stable
    for (start, end) in reversed(sections):
        total_top += insert_top_blocks(lines, start, end)
        total_bottom += insert_bottom_block(lines, start, end)
    save_lines(BOOK, lines)
    print(f"Inserted top blocks: {total_top}, bottom blocks: {total_bottom}")

if __name__ == "__main__":
    main()
