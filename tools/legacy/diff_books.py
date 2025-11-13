#!/usr/bin/env python3
"""
Diff two book markdown files and report section-level and
placeholder/template differences.

Usage:
    python tools/diff_books.py <fileA> <fileB>

Outputs a markdown diff summary including section headings,
placeholder/template counts and key differences.
"""
import sys as _sys
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

def uprint(s):
    try:
        _sys.stdout.buffer.write((s+'\n').encode('utf-8'))
    except Exception:
        print(s)

def main():
    if len(_sys.argv) != 3:
        print("Usage: python tools/diff_books.py <fileA> <fileB>")
        _sys.exit(1)
    fileA, fileB = Path(_sys.argv[1]), Path(_sys.argv[2])
    if not fileA.exists() or not fileB.exists():
        print(f"ERROR: file not found: {fileA if not fileA.exists() else fileB}")
        _sys.exit(2)
    textA = fileA.read_text(encoding='utf-8')
    textB = fileB.read_text(encoding='utf-8')
    pa, sa, suma, exa = count_placeholders(textA)
    pb, sb, sumb, exb = count_placeholders(textB)
    # Shorten long formatted lines to avoid E501
    a_name = fileA.name
    b_name = fileB.name
    uprint(f"# Diff Report: {a_name} vs {b_name}\n")
    uprint("| 类型 | {} | {} | 差异 |\n|---|---|---|---|".format(a_name, b_name))
    uprint("| Placeholder | {} | {} | {} |".format(pa, pb, f"{pb-pa:+}"))
    uprint("| 学习目标 | {} | {} | {} |".format(sa, sb, f"{sb-sa:+}"))
    uprint("| 小结 | {} | {} | {} |".format(suma, sumb, f"{sumb-suma:+}"))
    uprint("| 练习 | {} | {} | {} |\n".format(exa, exb, f"{exb-exa:+}"))
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
