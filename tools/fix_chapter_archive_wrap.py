#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wrap legacy visible content in chapter files into a single archived HTML comment block,
keeping only the minimal navigation stub visible. Also enforce proper MD025 suppression
comment at the very top.

Usage:
  python tools/fix_chapter_archive_wrap.py <chapter-md> [<chapter-md> ...]
If no args given, runs on all files in chapter/.
"""
import sys
import re
from pathlib import Path
from typing import List, Tuple

ROOT = Path(__file__).resolve().parents[1]
CHAPTER_DIR = ROOT / "chapter"

MD025_COMMENT = "<!-- markdownlint-disable MD025 -->"

# Heuristic markers to locate the end of the stub
AUGMENTED_LINK = "book/1022.2025.newbook.augmented.md"
CANONICAL_LINK = "book/1022.2025.newbook.md"

ARCHIVE_BEGIN = "<!-- archived-content:begin -->"
ARCHIVE_END = "<!-- archived-content:end -->"


def wrap_file(p: Path) -> Tuple[bool, str]:
    text = p.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    changed = False

    # Ensure MD025 suppression at the very top
    # If first non-empty line is not the comment, insert it above
    idx_first_nonempty = 0
    while idx_first_nonempty < len(lines) and not lines[idx_first_nonempty].strip():
        idx_first_nonempty += 1
    if idx_first_nonempty >= len(lines):
        return False, "empty file"
    if lines[idx_first_nonempty].strip() != MD025_COMMENT:
        lines.insert(idx_first_nonempty, MD025_COMMENT)
        changed = True

    s = "\n".join(lines)
    # If already has a proper archived block (begin and end), skip wrapping
    if ARCHIVE_BEGIN in s and ARCHIVE_END in s:
        return changed, "already archived"

    # Find stub end by the augmented link first, else by canonical link
    stub_end_idx = None
    for i, line in enumerate(lines):
        if AUGMENTED_LINK in line:
            stub_end_idx = i
            break
    if stub_end_idx is None:
        for i, line in enumerate(lines):
            if CANONICAL_LINK in line:
                stub_end_idx = i
                break

    if stub_end_idx is None:
        return changed, "stub link not found"

    # Move forward to the next non-empty line after the link line
    j = stub_end_idx + 1
    while j < len(lines) and not lines[j].strip():
        j += 1

    # If nothing after stub, nothing to wrap
    if j >= len(lines):
        return changed, "no content after stub"

    # Insert archive markers; wrap from j to end
    new_lines: List[str] = []
    new_lines.extend(lines[:j])
    new_lines.append(ARCHIVE_BEGIN)
    new_lines.extend(lines[j:])
    new_lines.append(ARCHIVE_END)

    new_text = "\n".join(new_lines) + ("\n" if text.endswith("\n") else "")
    if new_text != text:
        p.write_text(new_text, encoding="utf-8")
        changed = True
        return changed, "wrapped"
    return changed, "no-op"


def main(argv: List[str]) -> int:
    if len(argv) > 1:
        targets = [Path(a) if Path(a).is_absolute() else (ROOT / a) for a in argv[1:]]
    else:
        targets = sorted((CHAPTER_DIR).glob("*.md"))

    touched = 0
    results: List[str] = []
    for p in targets:
        if not p.exists():
            results.append(f"SKIP {p.name}: not found")
            continue
        chg, msg = wrap_file(p)
        results.append(f"{p.name}: {msg}")
        if chg:
            touched += 1
    print("\n".join(results))
    print(f"Changed files: {touched}/{len(targets)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
