"""Deduplicate consecutive identical headings in the slim chapter file.

Source: book/篇章内容.精简.md
Target: book/篇章内容.精简.去重.md

Rules:
- Only collapse if two or more consecutive heading lines have the same normalized text.
- Normalization: strip leading # and spaces, remove trailing HTML comment (<!-- ... -->), trim whitespace.
- Non-heading lines (comments, placeholders, blank lines) are kept verbatim; consecutive duplicates among them are not collapsed.
- Preserve first occurrence of each consecutive duplicate group.
"""

from __future__ import annotations

import re
from pathlib import Path

SRC = Path("book/篇章内容.精简.md")
DST = Path("book/篇章内容.精简.去重.md")

HEAD_LINE_RE = re.compile(r"^(?P<hash>#{1,6})\s+(?P<rest>.*)$")
COMMENT_RE = re.compile(r"\s*<!--.*?-->\s*$")


def normalize_heading(line: str) -> str | None:
    m = HEAD_LINE_RE.match(line)
    if not m:
        return None
    rest = m.group("rest")
    rest = COMMENT_RE.sub("", rest)  # remove trailing comment
    return rest.strip()


def dedupe(lines: list[str]):
    result: list[str] = []
    prev_norm: str | None = None
    duplicates_removed = 0
    for line in lines:
        norm = normalize_heading(line)
        if norm is None:
            # Non-heading resets duplicate tracking
            prev_norm = None
            result.append(line)
            continue
        if norm == prev_norm:
            duplicates_removed += 1
            continue
        result.append(line)
        prev_norm = norm
    return result, duplicates_removed


def main():
    if not SRC.exists():
        raise SystemExit(f"Source not found: {SRC}")
    lines = SRC.read_text(encoding="utf-8").splitlines()
    deduped, removed = dedupe(lines)
    content = "\n".join(deduped) + "\n"
    DST.write_text(content, encoding="utf-8")
    print(
        f"Deduped file written: {DST.as_posix()} (removed={removed}, original={len(lines)}, final={len(deduped)})"
    )


if __name__ == "__main__":
    main()
