import csv
import re
from collections import OrderedDict, defaultdict
from datetime import datetime
from pathlib import Path


def strip_code_fences(text: str) -> str:
    lines = text.splitlines()
    out = []
    in_fence = False
    fence_pat = re.compile(r"^\s*(```|~~~)")
    for line in lines:
        if fence_pat.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(line)
    return "\n".join(out)


def strip_inline_code(text: str) -> str:
    return re.sub(r"`[^`]*`", "", text)


def normalize_markdown(text: str) -> str:
    s = text
    # Keep link/image text, drop URLs
    s = re.sub(r"!\[([^\]]*)\]\([^\)]+\)", r"\1", s)
    s = re.sub(r"\[([^\]]*)\]\([^\)]+\)", r"\1", s)
    # Remove emphasis markers
    s = s.replace("**", "").replace("__", "").replace("*", "").replace("_", "")
    # Remove heading markers at start
    s = re.sub(r"^\s*#{1,6}\s*", "", s, flags=re.MULTILINE)
    # Remove blockquote markers at start
    s = re.sub(r"^\s*>\s?", "", s, flags=re.MULTILINE)
    # Remove list markers at start
    s = re.sub(r"^\s*(?:[-+*]|\d+\.)\s+", "", s, flags=re.MULTILINE)
    # Remove HTML tags
    s = re.sub(r"<[^>]+>", "", s)
    # Unescape common entities
    s = s.replace("&nbsp;", " ").replace("&ensp;", " ").replace("&emsp;", " ")
    # Remove backslash escapes
    s = re.sub(r"\\([*_`#>\[\](){}.!+-])", r"\1", s)
    return s


def count_chars(s: str) -> int:
    s = re.sub(r"\s+", "", s)
    return len(s)


def char_breakdown(s: str) -> dict:
    # Compute per-category counts to support different publisher rules
    s = re.sub(r"\s+", "", s)
    def is_cjk(ch: str) -> bool:
        o = ord(ch)
        return (
            0x4E00 <= o <= 0x9FFF or  # CJK Unified Ideographs
            0x3400 <= o <= 0x4DBF or  # CJK Extension A
            0x20000 <= o <= 0x2A6DF or  # Extension B
            0x2A700 <= o <= 0x2B73F or  # Extension C
            0x2B740 <= o <= 0x2B81F or  # Extension D
            0x2B820 <= o <= 0x2CEAF or  # Extension E-F-G (broad)
            0xF900 <= o <= 0xFAFF or    # CJK Compatibility Ideographs
            0x2F800 <= o <= 0x2FA1F     # Compatibility Ideographs Supplement
        )

    def is_fullwidth_or_cjk_punct(ch: str) -> bool:
        o = ord(ch)
        return (
            0x3000 <= o <= 0x303F or  # CJK Symbols and Punctuation
            0xFF00 <= o <= 0xFFEF     # Halfwidth and Fullwidth Forms
        )

    def is_ascii_punct(ch: str) -> bool:
        return ch.isascii() and not ch.isalnum()

    cjk = 0
    ascii_alnum = 0
    punct_full = 0
    punct_ascii = 0
    other = 0

    for ch in s:
        if is_cjk(ch):
            cjk += 1
        elif ch.isascii() and ch.isalnum():
            ascii_alnum += 1
        elif is_fullwidth_or_cjk_punct(ch):
            punct_full += 1
        elif is_ascii_punct(ch):
            punct_ascii += 1
        else:
            other += 1

    total = cjk + ascii_alnum + punct_full + punct_ascii + other
    return {
        "total_nonspace": total,
        "cjk": cjk,
        "ascii_alnum": ascii_alnum,
        "punct_fullwidth": punct_full,
        "punct_ascii": punct_ascii,
        "other": other,
        # Common rollups for publisher variants
        "cjk_plus_all_punct": cjk + punct_full + punct_ascii,
        "cjk_plus_ascii_plus_all_punct": cjk + ascii_alnum + punct_full + punct_ascii,
    }


CAT_KEYS = [
    "total_nonspace",
    "cjk",
    "ascii_alnum",
    "punct_fullwidth",
    "punct_ascii",
    "other",
]


def zero_counts():
    return {k: 0.0 for k in CAT_KEYS}


def add_counts(acc: dict, bd: dict):
    for k in CAT_KEYS:
        acc[k] = acc.get(k, 0.0) + float(bd.get(k, 0.0))


def compute_variants(bd: dict) -> dict:
    cjk = bd.get("cjk", 0.0)
    aa = bd.get("ascii_alnum", 0.0)
    pf = bd.get("punct_fullwidth", 0.0)
    pa = bd.get("punct_ascii", 0.0)
    other = bd.get("other", 0.0)

    # Variant A: ascii_alnum=0.5, ascii_punct=1
    vA = cjk + pf + pa + other + 0.5 * aa
    # Variant B: ascii_alnum=0.5, ascii_punct=0.5
    vB = cjk + pf + 0.5 * pa + other + 0.5 * aa
    # Variant C: ascii_alnum=0.5, ascii_punct=0
    vC = cjk + pf + 0.0 * pa + other + 0.5 * aa
    return {
        "total_nonspace": bd.get("total_nonspace", 0.0),
        "variant_A_ascii05_punct1": vA,
        "variant_B_ascii05_punct05": vB,
        "variant_C_ascii05_punct0": vC,
    }


def parse_and_count(md_path: Path):
    raw = md_path.read_text(encoding="utf-8", errors="ignore")
    # Remove fenced code blocks, then inline code, then markdown syntax
    no_fences = strip_code_fences(raw)
    no_code = strip_inline_code(no_fences)
    clean = normalize_markdown(no_code)

    # Iterate by lines to attribute counts to current H2/H3/H4
    lines = clean.splitlines()
    total_bd = zero_counts()

    parts = OrderedDict()  # part_title -> bd dict
    chapters = OrderedDict()  # (part_title, chapter_title) -> bd dict
    sections = OrderedDict()  # (part_title, chapter_title, section_title) -> bd dict

    cur_part = None
    cur_chap = None
    cur_sec = None

    for line in lines:
        l = line.rstrip("\n")
        if not l.strip():
            continue

        # Detect headings after normalization:
        # We cannot rely on # markers; titles remain in text.
        # Therefore, we base on original raw lines at same index? Simpler approach:
        # Re-run heading detection on the original text for structure only.
        pass

    # Second pass for structure-aware counting using original markdown
    total = 0
    cur_part = None
    cur_chap = None
    cur_sec = None

    def classify_title(t: str) -> str | None:
        tt = t.strip()
        if re.match(r"^第\s*[0-9０-９一二三四五六七八九十百千]+\s*篇", tt):
            return "part"
        if re.match(r"^第\s*[0-9０-９一二三四五六七八九十百千]+\s*章", tt):
            return "chapter"
        if re.match(r"^\s*\d+(?:\.\d+)+\s+", tt):
            return "section"
        return None

    in_fence = False
    raw_lines = raw.splitlines()
    for raw_line in raw_lines:
        if re.match(r"^\s*(```|~~~)", raw_line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        # Identify headings by level
        m_h = re.match(r"^\s*(#{1,6})\s+(.*)$", raw_line)
        if m_h:
            title_txt = m_h.group(2).strip()
            # Clean the visible title text (drop markdown for counting too)
            title_clean = normalize_markdown(strip_inline_code(title_txt))
            kind = classify_title(title_clean)
            if kind == "part":
                cur_part = title_clean
                cur_chap = None
                cur_sec = None
                parts.setdefault(cur_part, zero_counts())
            elif kind == "chapter":
                cur_chap = title_clean
                cur_sec = None
                chapters.setdefault((cur_part, cur_chap), zero_counts())
            elif kind == "section":
                cur_sec = title_clean
                sections.setdefault((cur_part, cur_chap, cur_sec), zero_counts())
            # Count heading text as content
            bd = char_breakdown(title_clean)
            add_counts(total_bd, bd)
            if cur_part is not None:
                parts.setdefault(cur_part, zero_counts())
                add_counts(parts[cur_part], bd)
            if cur_chap is not None:
                chapters.setdefault((cur_part, cur_chap), zero_counts())
                add_counts(chapters[(cur_part, cur_chap)], bd)
            if cur_sec is not None:
                sections.setdefault((cur_part, cur_chap, cur_sec), zero_counts())
                add_counts(sections[(cur_part, cur_chap, cur_sec)], bd)
            continue

        # Non-heading content line
        line_clean = normalize_markdown(strip_inline_code(raw_line))
        bd = char_breakdown(line_clean)
        c = bd["total_nonspace"]
        if c == 0:
            continue
        add_counts(total_bd, bd)
        if cur_part is not None:
            parts.setdefault(cur_part, zero_counts())
            add_counts(parts[cur_part], bd)
        if cur_chap is not None:
            chapters.setdefault((cur_part, cur_chap), zero_counts())
            add_counts(chapters[(cur_part, cur_chap)], bd)
        if cur_sec is not None:
            sections.setdefault((cur_part, cur_chap, cur_sec), zero_counts())
            add_counts(sections[(cur_part, cur_chap, cur_sec)], bd)

    return total_bd, parts, chapters, sections


def to_qianzhi(n: int) -> str:
    return f"{n/1000:.1f}"


def render_report(total_bd, parts, chapters, sections) -> str:
    lines = []
    lines.append("# 出版社风格字数统计（Markdown 清洗后、不含代码块、不计空白）")
    lines.append("")
    total = int(total_bd.get("total_nonspace", 0))
    lines.append(f"- 总字数：{total}（约 {to_qianzhi(total)} 千字）")
    lines.append("")

    # Parts table
    if parts:
        lines.append("**按篇统计**")
        lines.append("")
        lines.append("- 统计口径：计入标题与正文，排除代码块，去除空白与 Markdown 语法、链接 URL 等")
        lines.append("")
        lines.append("| 篇 | 字数 | 千字 |")
        lines.append("|---|---:|---:|")
        for p, bd in parts.items():
            n = int(bd.get("total_nonspace", 0))
            lines.append(f"| {p} | {n} | {to_qianzhi(n)} |")
        lines.append("")

    # Chapters table
    if chapters:
        lines.append("**按章统计**")
        lines.append("")
        lines.append("| 篇 | 章 | 字数 | 千字 |")
        lines.append("|---|---|---:|---:|")
        for (p, ch), bd in chapters.items():
            n = int(bd.get("total_nonspace", 0))
            lines.append(f"| {p or ''} | {ch} | {n} | {to_qianzhi(n)} |")
        lines.append("")

    # Sections table
    if sections:
        lines.append("**按节统计**")
        lines.append("")
        lines.append("| 篇 | 章 | 节 | 字数 | 千字 |")
        lines.append("|---|---|---|---:|---:|")
        for (p, ch, s), bd in sections.items():
            n = int(bd.get("total_nonspace", 0))
            lines.append(f"| {p or ''} | {ch or ''} | {s} | {n} | {to_qianzhi(n)} |")
        lines.append("")

    return "\n".join(lines) + "\n"


def write_csv_and_excel(ts: str, total_bd, parts, chapters, sections):
    out_dir = Path("tools/reports")
    out_dir.mkdir(parents=True, exist_ok=True)

    # CSV: parts
    parts_csv = out_dir / f"wordcount_parts_{ts}.csv"
    with parts_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["篇", "total_nonspace", "A_ascii0.5_punct1", "B_ascii0.5_punct0.5", "C_ascii0.5_punct0", "千字_total"])
        for p, bd in parts.items():
            v = compute_variants(bd)
            tn = v["total_nonspace"]
            w.writerow([p, tn, v["variant_A_ascii05_punct1"], v["variant_B_ascii05_punct05"], v["variant_C_ascii05_punct0"], to_qianzhi(tn)])

    # CSV: chapters
    ch_csv = out_dir / f"wordcount_chapters_{ts}.csv"
    with ch_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["篇", "章", "total_nonspace", "A_ascii0.5_punct1", "B_ascii0.5_punct0.5", "C_ascii0.5_punct0", "千字_total"])
        for (p, ch), bd in chapters.items():
            v = compute_variants(bd)
            tn = v["total_nonspace"]
            w.writerow([p or "", ch, tn, v["variant_A_ascii05_punct1"], v["variant_B_ascii05_punct05"], v["variant_C_ascii05_punct0"], to_qianzhi(tn)])

    # CSV: sections
    sec_csv = out_dir / f"wordcount_sections_{ts}.csv"
    with sec_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["篇", "章", "节", "total_nonspace", "A_ascii0.5_punct1", "B_ascii0.5_punct0.5", "C_ascii0.5_punct0", "千字_total"])
        for (p, ch, s), bd in sections.items():
            v = compute_variants(bd)
            tn = v["total_nonspace"]
            w.writerow([p or "", ch or "", s, tn, v["variant_A_ascii05_punct1"], v["variant_B_ascii05_punct05"], v["variant_C_ascii05_punct0"], to_qianzhi(tn)])

    # Try to write Excel if openpyxl is available
    try:
        from openpyxl import Workbook
        wb = Workbook()

        # Summary sheet
        ws0 = wb.active
        ws0.title = "Summary"
        ws0.append(["指标", "值"]) 
        tvar = compute_variants(total_bd)
        ws0.append(["total_nonspace", tvar["total_nonspace"]])
        ws0.append(["A_ascii0.5_punct1", tvar["variant_A_ascii05_punct1"]])
        ws0.append(["B_ascii0.5_punct0.5", tvar["variant_B_ascii05_punct05"]])
        ws0.append(["C_ascii0.5_punct0", tvar["variant_C_ascii05_punct0"]])
        ws0.append(["总千字(total_nonspace)", to_qianzhi(tvar["total_nonspace"])])

        # Parts sheet
        ws1 = wb.create_sheet("Parts")
        ws1.append(["篇", "total_nonspace", "A_ascii0.5_punct1", "B_ascii0.5_punct0.5", "C_ascii0.5_punct0", "千字_total"]) 
        for p, bd in parts.items():
            v = compute_variants(bd)
            tn = v["total_nonspace"]
            ws1.append([p, tn, v["variant_A_ascii05_punct1"], v["variant_B_ascii05_punct05"], v["variant_C_ascii05_punct0"], to_qianzhi(tn)])

        # Chapters sheet
        ws2 = wb.create_sheet("Chapters")
        ws2.append(["篇", "章", "total_nonspace", "A_ascii0.5_punct1", "B_ascii0.5_punct0.5", "C_ascii0.5_punct0", "千字_total"]) 
        for (p, ch), bd in chapters.items():
            v = compute_variants(bd)
            tn = v["total_nonspace"]
            ws2.append([p or "", ch, tn, v["variant_A_ascii05_punct1"], v["variant_B_ascii05_punct05"], v["variant_C_ascii05_punct0"], to_qianzhi(tn)])

        # Sections sheet
        ws3 = wb.create_sheet("Sections")
        ws3.append(["篇", "章", "节", "total_nonspace", "A_ascii0.5_punct1", "B_ascii0.5_punct0.5", "C_ascii0.5_punct0", "千字_total"]) 
        for (p, ch, s), bd in sections.items():
            v = compute_variants(bd)
            tn = v["total_nonspace"]
            ws3.append([p or "", ch or "", s, tn, v["variant_A_ascii05_punct1"], v["variant_B_ascii05_punct05"], v["variant_C_ascii05_punct0"], to_qianzhi(tn)])

        xlsx_path = out_dir / f"wordcount_{ts}.xlsx"
        wb.save(xlsx_path)
    except Exception as e:
        # If openpyxl isn't installed, silently skip Excel generation.
        pass


def main():
    src = Path("book/1022.2025.newbook.cleaned.md")
    total_bd, parts, chapters, sections = parse_and_count(src)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    reports_dir = Path("tools/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    out_md = reports_dir / f"wordcount_{ts}.md"
    out_md.write_text(render_report(total_bd, parts, chapters, sections), encoding="utf-8")
    write_csv_and_excel(ts, total_bd, parts, chapters, sections)
    print(str(out_md))


if __name__ == "__main__":
    main()
