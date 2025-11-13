import re
from pathlib import Path
from datetime import datetime
from typing import List, Set, Tuple

BOOK = Path(__file__).resolve().parents[1] / "book" / "1022.2025.newbook.md"
REPORTS = Path(__file__).resolve().parents[1] / "tools" / "reports"

anchor_re = re.compile(r'^\s*<a\s+id="([^"]+)"\s*></a>\s*$', re.IGNORECASE)
md_link_re = re.compile(r"\[[^\]]*\]\((?:\./)?1022\.2025\.newbook\.md#([^)\s]+)\)")
section_num_re = re.compile(r"^(\d+(?:\.\d+)+)\s+")
heading_re = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


def load_lines(p: Path) -> List[str]:
    return p.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n").split("\n")


def gather_anchors(lines: List[str]) -> Set[str]:
    anchors: Set[str] = set()
    for ln in lines:
        m = anchor_re.match(ln)
        if m:
            anchors.add(m.group(1))
    return anchors


def gather_links(lines: List[str]) -> List[Tuple[int, str, str]]:
    links = []
    for i, ln in enumerate(lines):
        for m in md_link_re.finditer(ln):
            links.append((i + 1, ln.strip(), m.group(1)))
    return links


def find_numbering_anomalies(lines: List[str]) -> List[str]:
    anomalies: List[str] = []
    current_chapter: str | None = None
    seen_in_chapter: Set[str] = set()
    for i, ln in enumerate(lines):
        hm = heading_re.match(ln)
        if hm:
            level = len(hm.group(1))
            title = hm.group(2)
            if level == 3 and not section_num_re.match(title):
                # chapter without numeric lead is acceptable in some places; skip
                current_chapter = title
                seen_in_chapter.clear()
                continue
            if level == 4:
                nm = section_num_re.match(title)
                if nm:
                    num = nm.group(1)
                    if num in seen_in_chapter:
                        anomalies.append(f"Line {i+1}: duplicate section number {num} under chapter '{current_chapter or ''}'")
                    else:
                        seen_in_chapter.add(num)
    return anomalies


def main():
    REPORTS.mkdir(parents=True, exist_ok=True)
    if not BOOK.exists():
        raise SystemExit(f"Book not found: {BOOK}")
    lines = load_lines(BOOK)
    anchors = gather_anchors(lines)
    links = gather_links(lines)

    broken = [(ln, src, aid) for (ln, src, aid) in links if aid not in anchors]
    # orphan anchors: anchors never linked
    referenced = {aid for (_, _, aid) in links}
    orphan = sorted([a for a in anchors if a not in referenced])
    anomalies = find_numbering_anomalies(lines)

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    out = ["# Links & Anchors Report", "", f"Anchors: {len(anchors)}", f"Links: {len(links)}", f"Broken: {len(broken)}", f"Orphan anchors: {len(orphan)}", ""]
    if broken:
        out.append("## Broken links")
        out.append("")
        out.append("| Line | Excerpt | Target |")
        out.append("|---|---|---|")
        for ln, src, aid in broken[:200]:
            safe_src = src.replace('|', '\\|')[:120]
            out.append(f"| {ln} | {safe_src} | {aid} |")
        if len(broken) > 200:
            out.append(f"... and {len(broken)-200} more")
        out.append("")
    if orphan:
        out.append("## Orphan anchors (no links)")
        out.append("")
        for a in orphan[:300]:
            out.append(f"- {a}")
        if len(orphan) > 300:
            out.append(f"... and {len(orphan)-300} more")
        out.append("")
    if anomalies:
        out.append("## Numbering anomalies")
        out.append("")
        for a in anomalies:
            out.append(f"- {a}")
        out.append("")

    report = REPORTS / f"links-anchors-{ts}.md"
    report.write_text("\n".join(out), encoding="utf-8")
    print(f"Wrote links & anchors report to {report}")

if __name__ == "__main__":
    main()
