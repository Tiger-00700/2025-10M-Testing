from __future__ import annotations
from pathlib import Path
import re
import sys

REPO = Path(__file__).resolve().parent.parent
BOOK = REPO / "book/1208.2025.newbook.md"
FRAMEWORK_DIR = REPO / "framework"

CN_NUM = {
    "一": 1,
    "二": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9,
    "十": 10,
}


def cn_to_int(token: str) -> int:
    if token in CN_NUM:
        return CN_NUM[token]
    if token.startswith("十"):
        return 10 + CN_NUM.get(token[1:], 0)
    if token.endswith("十"):
        return CN_NUM.get(token[0], 0) * 10
    return 0


def infer_level(title: str) -> str:
    m = re.search(r"（(入门|进阶|专家)）", title)
    if m:
        return f"{m.group(1)}篇"
    if "入门" in title:
        return "入门篇"
    if "进阶" in title:
        return "进阶篇"
    if "专家" in title:
        return "专家篇"
    return "篇"


def parse_parts(book_path: Path) -> list[dict]:
    text = book_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    parts: list[dict] = []
    current: dict | None = None
    for line in lines:
        m = re.match(r"## 第([一二三四五六七八九十]+)篇\s+(.+)", line)
        if m:
            if current:
                parts.append(current)
            num_cn = m.group(1)
            num = cn_to_int(num_cn)
            title = m.group(2).strip()
            level = infer_level(title)
            current = {
                "num": num,
                "title": title,
                "level": level,
                "content": line + "\n",
            }
            continue
        if current is not None:
            current["content"] += line + "\n"
    if current:
        parts.append(current)
    return parts


def normalize(text: str) -> str:
    return text.replace("\r\n", "\n").rstrip()


def main() -> int:
    errors: list[str] = []
    if not BOOK.exists():
        print(f"missing book: {BOOK}")
        return 2
    if not FRAMEWORK_DIR.exists():
        print(f"missing framework dir: {FRAMEWORK_DIR}")
        return 2

    parts = parse_parts(BOOK)
    expected_files = {}
    for p in parts:
        clean_title = re.sub(r"（.*?）", "", p["title"]).strip()
        fname = f"第{p['num']}篇-{p['level']}-{clean_title}.md"
        expected_files[fname] = p

    framework_files = {f.name: f for f in FRAMEWORK_DIR.glob("*.md")}

    # Check missing
    for fname, part in expected_files.items():
        if fname not in framework_files:
            errors.append(f"missing file: {fname}")
            continue
        fpath = framework_files[fname]
        fw_text = fpath.read_text(encoding="utf-8")
        if normalize(fw_text) != normalize(part["content"]):
            errors.append(
                f"content mismatch: {fname} (len book={len(part['content'])}, fw={len(fw_text)})"
            )

    # Check extra
    for fname in framework_files:
        if fname not in expected_files:
            errors.append(f"unexpected file: {fname}")

    if errors:
        print("Framework parts consistency FAILED:")
        for e in errors:
            print(" -", e)
        return 1
    print("Framework parts consistency PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
