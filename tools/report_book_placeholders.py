#!/usr/bin/env python3
"""Report placeholder and template markers in a given book markdown file.

Counts occurrences of:
  - "Placeholder: migrated from book reference, please fill content."
  - 教学模板标题：学习目标 / 小结 / 练习（作为独立标题行）

Outputs: tools/reports/book-placeholders-<name>-<ts>.md
Prints a summary line for quick comparison.
"""
from __future__ import annotations
import argparse
import re
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]

HEAD_RE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', required=True, help='Path to markdown file relative to repo root')
    args = ap.parse_args(argv)

    src = ROOT / args.source
    if not src.exists():
        print(f"ERROR: source not found: {src}")
        return 2
    text = src.read_text(encoding='utf-8')

    placeholder_key = "Placeholder: migrated from book reference, please fill content."
    placeholder_count = text.count(placeholder_key)

    # Count template headings by exact title match
    h_study = h_summary = h_exercise = 0
    for line in text.splitlines():
        m = HEAD_RE.match(line)
        if not m:
            continue
        title = m.group(2).strip()
        if title == "学习目标":
            h_study += 1
        elif title == "小结":
            h_summary += 1
        elif title == "练习":
            h_exercise += 1

    reports = ROOT / 'tools' / 'reports'
    reports.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d-%H%M%S')
    out = reports / f"book-placeholders-{src.stem}-{ts}.md"
    lines = []
    lines.append(f"# Book Placeholder Report for {src.as_posix()} ({ts})")
    lines.append("")
    lines.append(f"- Placeholder blocks: {placeholder_count}")
    lines.append(f"- 学习目标 headings: {h_study}")
    lines.append(f"- 小结 headings: {h_summary}")
    lines.append(f"- 练习 headings: {h_exercise}")
    lines.append("")
    out.write_text('\n'.join(lines), encoding='utf-8')
    import sys
    print(f"Report written: {out}")
    # 强制 utf-8 输出，兼容 Windows 控制台
    summary = f"Placeholders: {placeholder_count}, 学习目标: {h_study}, 小结: {h_summary}, 练习: {h_exercise}\n"
    try:
        sys.stdout.buffer.write(summary.encode('utf-8'))
    except Exception:
        print(summary)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
