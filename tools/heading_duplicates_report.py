"""Generate a heading duplication report.

Source: book/1022.2025.newbook.augmented.frozen.md
Output: tools/reports/heading-duplicates-<ts>.md

Report sections:
1. Summary statistics (total headings, unique, duplicated count, top N duplicates)
2. Top N duplicated headings table (title | count | levels | first_line | lines)
3. Detailed distribution for each duplicated heading (occurrence line numbers with level)

Normalization: strip leading #'s, spaces, and trailing inline comments; keep original
case and CJK characters. Headings compared by exact normalized text.
"""

from __future__ import annotations

import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

SRC = Path("book/1022.2025.newbook.augmented.frozen.md")
REPORT_DIR = Path("tools/reports")
TOP_N = 50

HEAD_RE = re.compile(r"^(?P<hash>#{1,6})\s+(?P<title>.*\S)\s*$")


def parse_headings_with_paths(text: str):
    """Parse headings and compute hierarchical path context for each occurrence.

    Returns a list of tuples: (line_no, level, title, path_str)
    where path_str is like: 第一篇 / 第1章 / 1.1 节标题 / 学习目标
    """
    stack: list[tuple[int, str]] = []  # (level, title)
    result: list[tuple[int, int, str, str]] = []
    for i, line in enumerate(text.splitlines(), start=1):
        m = HEAD_RE.match(line)
        if not m:
            continue
        level = len(m.group("hash"))
        title = m.group("title").strip()
        # Maintain stack
        while stack and stack[-1][0] >= level:
            stack.pop()
        stack.append((level, title))
        path = " / ".join(t for _, t in stack)
        result.append((i, level, title, path))
    return result


def build_report(headings_with_paths):
    groups: dict[str, list[tuple[int, int, str]]] = defaultdict(list)
    for line_no, level, title, path in headings_with_paths:
        groups[title].append((line_no, level, path))

    total = sum(len(v) for v in groups.values())
    unique = sum(1 for v in groups.values() if len(v) == 1)
    duplicated_titles = {k: v for k, v in groups.items() if len(v) > 1}
    duplicated_count = sum(len(v) for v in duplicated_titles.values())

    # Sort by occurrence count desc, then by earliest line
    top = sorted(
        duplicated_titles.items(), key=lambda kv: (-len(kv[1]), kv[1][0][0])
    )[:TOP_N]

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines: list[str] = []
    lines.append(f"# Heading Duplication Report ({ts} UTC)")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"Total headings: {total}")
    lines.append(f"Unique headings: {unique}")
    lines.append(
        "Duplicated headings: "
        + str(len(duplicated_titles))
        + " (occurrences="
        + str(duplicated_count)
        + ")"
    )
    lines.append(f"Top N: {TOP_N}")
    lines.append("")
    lines.append("## Top Duplicates")
    lines.append("| Title | Count | Levels | First Line | First Path | All Lines |")
    lines.append("|-------|-------|--------|------------|------------|-----------|")
    for title, occ in top:
        count = len(occ)
        levels = ",".join(str(lvl) for _, lvl, _ in occ[:5])
        if len(occ) > 5:
            levels += "..."
        first_line, _, first_path = occ[0]
        all_lines = ",".join(str(l) for l, _, _ in occ[:10])
        if len(occ) > 10:
            all_lines += "..."
        # Escape pipe for Markdown tables
        safe_title = title.replace("|", "\\|")
        safe_first_path = first_path.replace("|", "\\|")
        row = (
            "| " + safe_title + " | " + str(count) + " | " + levels + " | " + str(first_line)
            + " | " + safe_first_path + " | " + all_lines + " |"
        )
        lines.append(row)

    lines.append("")
    lines.append("## Detailed Distribution")
    for title, occ in top:
        lines.append(f"### {title}")
        lines.append("Line | Level | Path")
        lines.append("---- | ----- | ----")
        for ln, lvl, path in occ:
            safe_path = path.replace('|', '\\|')
            lines.append(f"{ln} | {lvl} | {safe_path}")
        lines.append("")

    return "\n".join(lines) + "\n"


def main():
    if not SRC.exists():
        raise SystemExit(f"Source not found: {SRC}")
    text = SRC.read_text(encoding="utf-8")
    headings = parse_headings_with_paths(text)
    report = build_report(headings)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    ts_simple = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = REPORT_DIR / f"heading-duplicates-{ts_simple}.md"
    path.write_text(report, encoding="utf-8")
    print(f"Report written: {path.as_posix()}")


if __name__ == "__main__":
    main()
