import re
from pathlib import Path


def parse_book(src: Path):
    lines = src.read_text(encoding="utf-8", errors="ignore").splitlines()
    in_fence = False
    fence_pat = re.compile(r"^\s*(```|~~~)")

    current_part = None
    current_chap = None
    current_section = None
    current_buffer = []

    outputs = []  # [(part_label, chap_label, sec_label, filename_title, content_lines)]

    def flush_current():
        nonlocal current_section, current_buffer
        if current_section is not None and current_buffer:
            outputs.append((current_part, current_chap, current_section[0], current_section[1], current_buffer[:]))
        current_section = None
        current_buffer = []

    def extract_part_label(t: str):
        m = re.search(r"第\s*([0-9０-９一二三四五六七八九十百千]+)\s*篇", t)
        if m:
            num = re.sub(r"\s+", "", m.group(1))
            return f"第{num}篇"
        return None

    def extract_chap_label(t: str):
        m = re.search(r"第\s*([0-9０-９一二三四五六七八九十百千]+)\s*章", t)
        if m:
            num = re.sub(r"\s+", "", m.group(1))
            return f"第{num}章"
        return None

    def extract_sec_number_and_title(t: str):
        m = re.match(r"\s*([0-9]+(?:\.[0-9]+)+)\s+(.*)$", t)
        if m:
            return m.group(1), m.group(2).strip()
        return None, None

    for raw in lines:
        line = raw.rstrip("\n")
        if fence_pat.match(line):
            in_fence = not in_fence
            # keep fence lines inside buffers if inside a section
            if current_section is not None:
                current_buffer.append(line)
            continue

        if in_fence:
            if current_section is not None:
                current_buffer.append(line)
            continue

        m = re.match(r"^\s*(#{1,6})\s+(.*)$", line)
        if m:
            level = len(m.group(1))
            text = m.group(2).strip()

            # Detect part/chapter
            if level == 2:
                # New part: flush pending section
                flush_current()
                pl = extract_part_label(text)
                if pl:
                    current_part = pl
                else:
                    # non-standard H2, keep as-is
                    current_part = text
                current_chap = None
                continue

            if level == 3:
                # New chapter: flush pending section
                flush_current()
                cl = extract_chap_label(text)
                if cl:
                    current_chap = cl
                else:
                    current_chap = text
                continue

            if level == 4:
                # New section: flush previous section and start new
                flush_current()
                sec_num, sec_title = extract_sec_number_and_title(text)
                if sec_num:
                    # file title uses number + title without spaces
                    file_component = f"{sec_num}{sec_title.replace(' ', '')}"
                    current_section = (f"{sec_num} {sec_title}", file_component)
                else:
                    # no number, still capture but filename uses raw title
                    fc = re.sub(r"\s+", "", text)
                    current_section = (text, fc)
                # include the heading itself
                current_buffer.append(line)
                continue

            # Lower headings (#####...) inside a section: keep content
            if current_section is not None:
                current_buffer.append(line)
            continue

        # Non-heading line
        if current_section is not None:
            current_buffer.append(line)

    # Flush last
    flush_current()

    return outputs


def sanitize_filename(name: str) -> str:
    # Remove characters illegal on Windows paths
    name = re.sub(r"[\\/:*?\"<>|]", "-", name)
    # Collapse repeated dashes
    name = re.sub(r"-+", "-", name).strip('-')
    return name


def write_sections(outputs, dest_dir: Path):
    dest_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for part_label, chap_label, sec_label, file_component, content_lines in outputs:
        if not part_label or not chap_label or not file_component:
            # skip if structure context missing
            continue
        filename = f"{part_label}-{chap_label}-{file_component}.md"
        filename = sanitize_filename(filename)
        out_path = dest_dir / filename
        # Ensure trailing newline
        text = "\n".join(content_lines)
        if not text.endswith("\n"):
            text += "\n"
        out_path.write_text(text, encoding="utf-8")
        written.append(out_path)
    return written


def main():
    src = Path("book/1022.2025.newbook.cleaned.md")
    dest = Path("chapter")
    outputs = parse_book(src)
    written = write_sections(outputs, dest)
    for p in written[:10]:
        print(p)
    print(f"TOTAL_WRITTEN={len(written)}")


if __name__ == "__main__":
    main()
