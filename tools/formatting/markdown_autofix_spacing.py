#!/usr/bin/env python3
"""
Safe markdown autofix: add missing blank lines around headings/lists/code fences
and normalize ordered list prefixes to `1.` for a single-file run.

Usage:
  python tools/formatting/markdown_autofix_spacing.py -i input.md -o output.md

This script is conservative: it does NOT modify code block contents and writes
the fixed output to a new file (does not overwrite input by default).
"""
import argparse
import re
from pathlib import Path


def is_heading(line: str) -> bool:
    return bool(re.match(r"^#{1,6}\s+", line))


def is_list_item(line: str) -> bool:
    return bool(re.match(r"^\s*([-*+]\s+|\d+\.\s+)", line))


def is_fence(line: str) -> bool:
    return line.strip().startswith("```")


def normalize_ordered_prefix(line: str) -> str:
    m = re.match(r"^(\s*)\d+\.(\s+)(.*)$", line)
    if m:
        return f"{m.group(1)}1.{m.group(2)}{m.group(3)}\n"
    return line


def run_fix(lines):
    out = []
    in_fence = False
    i = 0
    n = len(lines)
    fence_delim = None

    def last_out_blank():
        if not out:
            return True
        return out[-1].strip() == ""

    while i < n:
        line = lines[i]

        if is_fence(line):
            # toggle fence state
            fence_line = line
            if not in_fence:
                # entering fence: ensure previous blank line
                if not last_out_blank():
                    out.append("\n")
                out.append(fence_line)
                in_fence = True
                fence_delim = fence_line.strip()
                i += 1
                continue
            else:
                # exiting fence
                out.append(fence_line)
                in_fence = False
                fence_delim = None
                # if next original line is not blank, add a blank line
                if i + 1 < n and lines[i+1].strip() != "":
                    out.append("\n")
                i += 1
                continue

        if in_fence:
            out.append(line)
            i += 1
            continue

        # Outside fences: headings and lists
        if is_heading(line):
            if not last_out_blank():
                out.append("\n")
            out.append(line)
            # if next line exists and is non-blank and not a heading or list, add blank line for separation
            if i + 1 < n and lines[i+1].strip() != "" and not is_heading(lines[i+1]) and not is_list_item(lines[i+1]) and not is_fence(lines[i+1]):
                out.append("\n")
            i += 1
            continue

        if is_list_item(line):
            # ensure previous blank
            if not last_out_blank():
                out.append("\n")
            # normalize ordered list prefixes
            if re.match(r"^\s*\d+\.\s+", line):
                fixed = normalize_ordered_prefix(line)
                out.append(fixed)
            else:
                out.append(line)
            i += 1
            # do not force blank after list items (lists are multi-line constructs)
            continue

        # fenced code blocks and lists/headings handled above; default: pass-through
        out.append(line)
        i += 1

    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("-i", "--input", required=True, help="Input markdown file")
    p.add_argument("-o", "--output", required=True, help="Output markdown file (fixed)")
    args = p.parse_args()

    inp = Path(args.input)
    outp = Path(args.output)

    if not inp.exists():
        print(f"Input file not found: {inp}")
        raise SystemExit(1)

    with inp.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    fixed = run_fix(lines)

    # write a small header comment into output to note automated fixes
    header = [f"<!-- generated-by: tools/formatting/markdown_autofix_spacing.py -->\n", "\n"]
    outp.parent.mkdir(parents=True, exist_ok=True)
    with outp.open("w", encoding="utf-8", newline="\n") as f:
        f.writelines(header + fixed)

    # simple counts for user info
    print(f"Wrote fixed file: {outp} (original lines: {len(lines)}, output lines: {len(header)+len(fixed)})")


if __name__ == "__main__":
    main()
