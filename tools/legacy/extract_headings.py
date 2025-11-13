"""Generate a hierarchical outline from the canonical augmented frozen manuscript.

Reads headings (# to ######) preserving order and writes an indented outline
with metadata (timestamp, source path, heading count).

Usage:
    python tools/extract_headings.py

Output:
    book/1022.2025.newbook.outline.generated.md

Idempotent: re-generates file each run.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

SOURCE_REL = Path("book/1022.2025.newbook.augmented.frozen.md")
DEST_REL = Path("book/1022.2025.newbook.outline.generated.md")

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")


def extract_headings(text: str):
    for line_no, line in enumerate(text.splitlines(), start=1):
        m = HEADING_RE.match(line)
        if m:
            hashes, title = m.groups()
            level = len(hashes)
            yield {
                "line": line_no,
                "level": level,
                "title": title,
            }


def build_outline(headings):
    lines = []
    for h in headings:
        indent = "  " * (h["level"] - 1)
        # Include line number for traceability.
        lines.append(f"{indent}- (L{h['line']}) {h['title']}")
    return "\n".join(lines)


def main():
    source_path = SOURCE_REL
    if not source_path.exists():
        raise SystemExit(f"Source file not found: {source_path}")

    text = source_path.read_text(encoding="utf-8")
    headings = list(extract_headings(text))
    outline_body = build_outline(headings)

    ts = datetime.now(timezone.utc).isoformat()
    meta = (
        "<!-- Generated outline -->\n"
        f"<!-- source: {source_path.as_posix()} -->\n"
        f"<!-- generated_utc: {ts} -->\n"
        f"<!-- total_headings: {len(headings)} -->\n"
    )
    dest_path = DEST_REL
    dest_path.write_text(f"{meta}\n\n{outline_body}\n", encoding="utf-8")
    print(
        f"Outline written: {dest_path} (headings={len(headings)})"  # noqa: T201
    )


if __name__ == "__main__":  # pragma: no cover
    main()
