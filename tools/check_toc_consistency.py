import re
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
MANUSCRIPT = ROOT / "book" / "1208.2025.newbook.md"
REPORTS_DIR = ROOT / "tools" / "reports"

PART_RE = re.compile(r"^##\s*(第[一二三四五六七]篇)\s*(.+)$", re.M)
CHAPTER_RE = re.compile(r"^###\s*第(\d+)章\s*(.+)$", re.M)

def extract_parts_and_chapters_from_readme(text: str):
    parts = []
    chapters = {}
    in_reorg = False
    for line in text.splitlines():
        if "目录（1208 重组版）" in line:
            in_reorg = True
            continue
        if not in_reorg:
            continue
        if line.startswith("###"):
            # end of reorg block
            break
        m_part = re.match(r"^\-\s*(第[一二三四五六七]篇)\s*(.+)$", line)
        if m_part:
            parts.append(m_part.group(1))
            continue
        m_ch = re.match(r"^\s*\-\s*第(\d+)章\s*(.+)$", line)
        if m_ch:
            num = int(m_ch.group(1))
            title = m_ch.group(2).strip()
            chapters[num] = title
    return parts, chapters

def extract_parts_and_chapters_from_md(text: str):
    parts = [m.group(1) for m in PART_RE.finditer(text)]
    chapters = {}
    for m in CHAPTER_RE.finditer(text):
        num = int(m.group(1))
        title = m.group(2).strip()
        chapters[num] = title
    return parts, chapters

def main():
    readme_text = README.read_text(encoding="utf-8")
    md_text = MANUSCRIPT.read_text(encoding="utf-8")

    rd_parts, rd_chapters = extract_parts_and_chapters_from_readme(readme_text)
    md_parts, md_chapters = extract_parts_and_chapters_from_md(md_text)

    report_lines = []
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    report_lines.append(f"TOC Consistency Report - {ts}")
    report_lines.append(f"README parts: {rd_parts}")
    report_lines.append(f"Manuscript parts: {md_parts}")

    # Compare parts order
    parts_ok = rd_parts == md_parts
    report_lines.append(f"Parts match: {parts_ok}")

    # Compare chapter titles by number
    mismatches = []
    missing_in_md = []
    missing_in_readme = []

    for num, rd_title in rd_chapters.items():
        md_title = md_chapters.get(num)
        if md_title is None:
            missing_in_md.append(num)
        elif normalize(rd_title) != normalize(md_title):
            mismatches.append((num, rd_title, md_title))

    for num in md_chapters.keys():
        if num not in rd_chapters:
            missing_in_readme.append(num)

    report_lines.append(f"Chapter count (README vs MD): {len(rd_chapters)} vs {len(md_chapters)}")
    report_lines.append(f"Missing in manuscript: {sorted(missing_in_md)}")
    report_lines.append(f"Missing in README: {sorted(missing_in_readme)}")

    if mismatches:
        report_lines.append("Title mismatches:")
        for num, rd_t, md_t in mismatches:
            report_lines.append(f"- 第{num}章\n  README: {rd_t}\n  Manuscript: {md_t}")
    else:
        report_lines.append("Title mismatches: None")

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / f"toc_consistency_{ts}.txt"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    print(f"Wrote report: {report_path}")


def normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("【", "[").replace("】", "]")).strip()

if __name__ == "__main__":
    main()
