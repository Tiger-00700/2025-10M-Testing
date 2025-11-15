#!/usr/bin/env python3
"""
Conservative prefixer for repeated short headings (学习目标/小结/练习).

Usage:
  python tools/formatting/prefix_duplicate_headings.py -i INPUT.md -o OUTPUT.md

Behavior:
  - Scans headings and tracks the most recent heading that contains a numeric section like "1.2".
  - When encountering a heading that is exactly one of the short titles, it prefixes the heading text
    with the most recent numeric section if available, otherwise a § marker. It preserves the heading level.
  - Writes to OUTPUT.md (non-destructive).
"""
import argparse
import re
from pathlib import Path

SHORT_TITLES = {"学习目标", "小结", "练习"}

SECTION_NUM_RE = re.compile(r"^#{1,6}\s*([0-9]+(?:\.[0-9]+)*)\s*(.*)$")
SHORT_HEADING_RE = re.compile(r"^(#{1,6})\s*(%s)\s*$" % "|".join(map(re.escape, SHORT_TITLES)))


def prefix_file(input_path: Path, output_path: Path):
    with input_path.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    current_section = None
    out_lines = []

    for idx, line in enumerate(lines):
        m_sec = SECTION_NUM_RE.match(line)
        if m_sec:
            # store numeric section like 1.2
            current_section = m_sec.group(1)
            out_lines.append(line)
            continue

        m_short = SHORT_HEADING_RE.match(line)
        if m_short:
            hashes, title = m_short.group(1), m_short.group(2)
            if current_section:
                new_line = f"{hashes} {current_section} {title}\n"
            else:
                new_line = f"{hashes} § {title}\n"
            out_lines.append(new_line)
            continue

        out_lines.append(line)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as f:
        f.writelines(out_lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True, help="输入 markdown 文件")
    parser.add_argument("-o", "--output", required=True, help="输出候选文件路径")
    args = parser.parse_args()

    inp = Path(args.input)
    out = Path(args.output)
    if not inp.exists():
        raise SystemExit(f"输入文件不存在: {inp}")

    prefix_file(inp, out)
    print(f"Wrote MD024 candidate: {out}")


if __name__ == '__main__':
    main()
