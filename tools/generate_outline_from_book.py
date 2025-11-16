import re
from pathlib import Path


def clean_text_for_anchor(text: str) -> str:
    s = text.strip()
    # remove full-width brackets and ASCII brackets
    s = s.replace("【", "").replace("】", "")
    s = s.replace("[", "").replace("]", "")
    # collapse spaces
    s = re.sub(r"\s+", "", s)
    return s


def build_chapter_anchor(chapter_text: str) -> str:
    # Expect formats like: "第 1 章 标题【入门】" or "第1章 标题【专家】"
    t = chapter_text.strip()
    # Extract the leading '第..章'
    m = re.search(r"第\s*([0-9０-９]+)\s*章", t)
    if not m:
        # Fallback: whole text
        return clean_text_for_anchor(t)
    cleaned_num = re.sub(r"\s+", "", m.group(1))
    prefix = f"第{cleaned_num}章"
    # Remainder after 章
    rest = re.split(r"第\s*[0-9０-９]+\s*章", t, maxsplit=1)
    tail = rest[1] if len(rest) > 1 else ""
    return f"{prefix}-{clean_text_for_anchor(tail)}".rstrip("-")


def build_section_anchor(section_text: str) -> str:
    # Expect formats like: "1.1 标题" / "2.3.4 标题"
    t = section_text.strip()
    m = re.match(r"([0-9]+(?:\.[0-9]+)*)\s+(.*)$", t)
    if not m:
        return clean_text_for_anchor(t)
    nums = m.group(1).replace(".", "")
    title = clean_text_for_anchor(m.group(2))
    return f"{nums}-{title}".rstrip("-")


def generate_outline(input_md: Path, output_md: Path) -> None:
    lines = input_md.read_text(encoding="utf-8", errors="ignore").splitlines()

    in_fence = False
    title = None
    out_lines = []

    for i, raw in enumerate(lines):
        line = raw.rstrip("\n")
        # track code fences
        if re.match(r"^\s*(```|~~~)", line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        if line.startswith("# ") and title is None:
            title = line[2:].strip()
            continue

    if not title:
        title = input_md.stem

    out_lines.append(f"# {title}")

    in_fence = False
    for raw in lines:
        line = raw.rstrip("\n")
        if re.match(r"^\s*(```|~~~)", line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        # Part (篇) as H2
        if line.startswith("## "):
            txt = line[3:].strip()
            if ("第" in txt and "篇" in txt) or txt.startswith("第"):
                out_lines.append(f"## {txt}")
            continue

        # Chapter as H3
        if line.startswith("### "):
            txt = line[4:].strip()
            # Heuristic: chapter lines often contain 第..章
            if "章" in txt and "第" in txt:
                out_lines.append(f"### {txt}")
            continue

        # Section as H4
        if line.startswith("#### "):
            txt = line[5:].strip()
            # Accept both numbered and non-numbered; we try to build reasonable anchor
            out_lines.append(f"#### {txt}")

    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n".join(out_lines) + "\n", encoding="utf-8")


def main():
    src = Path("book/1022.2025.newbook.cleaned.md")
    dst = Path("chapter/1022.2025.newbook.大纲.md")
    generate_outline(src, dst)


if __name__ == "__main__":
    main()
