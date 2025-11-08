"""Generate a filtered heading duplication report excluding template or placeholder headings.

Source: book/1022.2025.newbook.augmented.frozen.md
Outputs:
  - tools/reports/heading-duplicates-filtered-<ts>.md
  - tools/reports/heading-duplicates-filtered-<ts>.csv

Filtering rules (excluded titles exactly matching any of):
  学习目标, 小结, 练习, Placeholder: migrated from book reference, please fill content.

Report sections (Markdown):
1. Summary statistics (total considered, unique, duplicated title count, occurrences)
2. Top duplicates table (Title | Count | First Line | First Path | Sample Lines)
3. Detailed distribution for top titles

CSV columns:
  title,count,first_line,first_path,all_lines

Implementation notes:
- We reuse logic similar to heading_duplicates_report.py but apply filtering early.
- Exact string comparison; we do not fuzzy match template variants here to keep it deterministic.
"""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

SRC = Path("book/1022.2025.newbook.augmented.frozen.md")
REPORT_DIR = Path("tools/reports")
TOP_N = 50

EXCLUDE_TITLES = {
    "学习目标",
    "小结",
    "练习",
    "Placeholder: migrated from book reference, please fill content.",
}

HEAD_RE = re.compile(r"^(?P<hash>#{1,6})\s+(?P<title>.*\S)\s*$")


def parse_headings_with_paths(text: str):
    stack: list[tuple[int, str]] = []  # (level, title)
    result: list[tuple[int, int, str, str]] = []
    for i, line in enumerate(text.splitlines(), start=1):
        m = HEAD_RE.match(line)
        if not m:
            continue
        level = len(m.group("hash"))
        title = m.group("title").strip()
        while stack and stack[-1][0] >= level:
            stack.pop()
        stack.append((level, title))
        path = " / ".join(t for _, t in stack)
        result.append((i, level, title, path))
    return result


def filter_headings(headings_with_paths):
    return [h for h in headings_with_paths if h[2] not in EXCLUDE_TITLES]


def build_markdown_and_csv(headings_with_paths):
    groups: dict[str, list[tuple[int, int, str]]] = defaultdict(list)
    for line_no, level, title, path in headings_with_paths:
        groups[title].append((line_no, level, path))

    total_considered = sum(len(v) for v in groups.values())
    unique = sum(1 for v in groups.values() if len(v) == 1)
    duplicated_titles = {k: v for k, v in groups.items() if len(v) > 1}
    duplicated_occurrences = sum(len(v) for v in duplicated_titles.values())

    top = sorted(
        duplicated_titles.items(), key=lambda kv: (-len(kv[1]), kv[1][0][0])
    )[:TOP_N]

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    md_lines: list[str] = []
    md_lines.append(f"# Filtered Heading Duplication Report ({ts} UTC)")
    md_lines.append("")
    md_lines.append("## Summary")
    md_lines.append(f"Excluded titles: {', '.join(sorted(EXCLUDE_TITLES))}")
    md_lines.append(f"Total considered headings: {total_considered}")
    md_lines.append(f"Unique headings: {unique}")
    md_lines.append(f"Duplicated titles: {len(duplicated_titles)} (occurrences={duplicated_occurrences})")
    md_lines.append(f"Top N: {TOP_N}")
    md_lines.append("")
    md_lines.append("## Top Duplicates")
    md_lines.append("| Title | Count | First Line | First Path | Sample Lines |")
    md_lines.append("|-------|-------|------------|------------|--------------|")
    for title, occ in top:
        count = len(occ)
        first_line, _, first_path = occ[0]
        sample_lines = ",".join(str(l) for l, _, _ in occ[:10]) + ("..." if len(occ) > 10 else "")
        safe_title = title.replace("|", "\\|")
        safe_first_path = first_path.replace("|", "\\|")
        md_lines.append(
            f"| {safe_title} | {count} | {first_line} | {safe_first_path} | {sample_lines} |"
        )

    md_lines.append("")
    md_lines.append("## Detailed Distribution")
    for title, occ in top:
        md_lines.append(f"### {title}")
        md_lines.append("Line | Level | Path")
        md_lines.append("---- | ----- | ----")
        for ln, lvl, path in occ:
            md_lines.append(f"{ln} | {lvl} | {path.replace('|','\\|')}")
        md_lines.append("")

    # CSV rows
    csv_rows = []
    for title, occ in top:
        count = len(occ)
        first_line, _, first_path = occ[0]
        all_lines = ",".join(str(l) for l, _, _ in occ)
        csv_rows.append({
            "title": title,
            "count": count,
            "first_line": first_line,
            "first_path": first_path,
            "all_lines": all_lines,
        })

    return "\n".join(md_lines) + "\n", csv_rows


def main():
    if not SRC.exists():
        raise SystemExit(f"Source not found: {SRC}")
    text = SRC.read_text(encoding="utf-8")
    headings = parse_headings_with_paths(text)
    filtered = filter_headings(headings)
    md_report, csv_rows = build_markdown_and_csv(filtered)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    ts_simple = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    md_path = REPORT_DIR / f"heading-duplicates-filtered-{ts_simple}.md"
    csv_path = REPORT_DIR / f"heading-duplicates-filtered-{ts_simple}.csv"
    md_path.write_text(md_report, encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["title","count","first_line","first_path","all_lines"])
        writer.writeheader()
        writer.writerows(csv_rows)
    print(f"Reports written: {md_path.as_posix()}, {csv_path.as_posix()}")


if __name__ == "__main__":
    main()
