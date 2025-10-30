#!/usr/bin/env python3
"""
Print-readiness check for Markdown content.

Checks:
- No HTML comments (<!-- ... -->)
- No empty headings (e.g., '#', '## ' with no text)
- No placeholder keywords: TODO, FIXME, TBD (outside fenced code blocks)

Exit codes:
- 0: no issues
- 1: issues found

Usage: python tools/print_readiness_check.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IGNORE_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "tools/_md013_suggest",
    "tools/editorial-issues",
    ".github",
}

# Precompiled regexes
RE_HTML_COMMENT = re.compile(r"<!--(.|\n)*?-->")
RE_EMPTY_HEADING = re.compile(r"^\s{0,3}#{1,6}\s*(?:#+\s*)?$")
RE_PLACEHOLDER = re.compile(r"\b(TODO|FIXME|TBD)\b")
RE_FENCE = re.compile(r"^\s*```")


def is_ignored(path: Path) -> bool:
    parts = set(path.parts)
    return any(d in parts for d in IGNORE_DIRS)


def scan_file(path: Path) -> list[tuple[int, str]]:
    issues: list[tuple[int, str]] = []
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        # Best-effort: skip files we can't read
        return issues

    # Check HTML comments anywhere
    if RE_HTML_COMMENT.search(text):
        # Report first match line only to keep output concise
        for idx, line in enumerate(text.splitlines(), start=1):
            if "<!--" in line:
                issues.append((idx, "HTML comment found (<!-- ... -->)"))
                break

    # Now line-by-line checks avoiding fenced code blocks
    in_fence = False
    for lineno, line in enumerate(text.splitlines(), start=1):
        if RE_FENCE.match(line):
            in_fence = not in_fence
            continue

        if in_fence:
            continue

        # Empty heading
        if RE_EMPTY_HEADING.match(line):
            # Ensure no alphanumeric after hashes
            # If line contains only hashes and spaces, it's empty
            stripped = line.strip().strip('#').strip()
            if not stripped:
                issues.append((lineno, "Empty heading (no title text)"))

        # Placeholder keywords
        if RE_PLACEHOLDER.search(line):
            issues.append((lineno, "Placeholder keyword (TODO/FIXME/TBD)"))

    return issues


def main() -> int:
    md_files = [
        p for p in ROOT.rglob("*.md")
        if not is_ignored(p)
    ]
    all_issues: list[tuple[Path, int, str]] = []
    for p in sorted(md_files):
        issues = scan_file(p)
        for lineno, msg in issues:
            all_issues.append((p, lineno, msg))

    if all_issues:
        print("Print-readiness issues found:")
        for p, lineno, msg in all_issues[:500]:  # cap output
            rel = p.relative_to(ROOT)
            print(f" - {rel}:{lineno}: {msg}")
        if len(all_issues) > 500:
            print(f" ... and {len(all_issues) - 500} more")
        print(f"Total issues: {len(all_issues)}")
        return 1
    else:
        print("Print-readiness: OK (no issues)")
        return 0


if __name__ == "__main__":
    sys.exit(main())
