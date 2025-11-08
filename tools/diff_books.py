#!/usr/bin/env python3
"""
Diff two book markdown files and report section-level and placeholder/template differences.

Usage:
  python tools/diff_books.py <fileA> <fileB>

Outputs a markdown diff summary: section headings, placeholder/template counts, and key differences.
"""
import sys
import re
from pathlib import Path

def count_placeholders(text):
    placeholder_key = "Placeholder: migrated from book reference, please fill content."
    placeholder_count = text.count(placeholder_key)
    h_study = h_summary = h_exercise = 0
    head_re = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
    for line in text.splitlines():
        m = head_re.match(line)
        if not m:
            continue
        title = m.group(2).strip()
        if title == "学习目标":
            h_study += 1
        elif title == "小结":
            h_summary += 1
        elif title == "练习":
            h_exercise += 1
    return placeholder_count, h_study, h_summary, h_exercise

def main():
    if len(sys.argv) != 3:
        print("Usage: python tools/diff_books.py <fileA> <fileB>")
        sys.exit(1)
    fileA, fileB = Path(sys.argv[1]), Path(sys.argv[2])
    if not fileA.exists() or not fileB.exists():
        print(f"ERROR: file not found: {fileA if not fileA.exists() else fileB}")
        sys.exit(2)
    textA = fileA.read_text(encoding='utf-8')
    textB = fileB.read_text(encoding='utf-8')
    pa, sa, suma, exa = count_placeholders(textA)
    pb, sb, sumb, exb = count_placeholders(textB)
    import sys
    def uprint(s):
        try:
            sys.stdout.buffer.write((s+'\n').encode('utf-8'))
        except Exception:
            print(s)
    uprint(f"# Diff Report: {fileA.name} vs {fileB.name}\n")
    uprint(f"| 类型 | {fileA.name} | {fileB.name} | 差异 |\n|---|---|---|---|")
    uprint(f"| Placeholder | {pa} | {pb} | {pb-pa:+} |")
    uprint(f"| 学习目标 | {sa} | {sb} | {sb-sa:+} |")
    uprint(f"| 小结 | {suma} | {sumb} | {sumb-suma:+} |")
    uprint(f"| 练习 | {exa} | {exb} | {exb-exa:+} |\n")
    # 可选：输出 section heading 差异
    headsA = set(re.findall(r"^#{1,6} +.*", textA, re.M))
    headsB = set(re.findall(r"^#{1,6} +.*", textB, re.M))
    onlyA = headsA - headsB
    onlyB = headsB - headsA
    if onlyA:
        uprint("## 仅在A中出现的标题:")
        for h in sorted(onlyA):
            uprint(f"- {h}")
    if onlyB:
        uprint("## 仅在B中出现的标题:")
        for h in sorted(onlyB):
            uprint(f"- {h}")

if __name__ == "__main__":
    main()
