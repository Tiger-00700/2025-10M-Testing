"""Deduplicate consecutive duplicate sections in the canonical frozen book.

Source: book/1022.2025.newbook.augmented.frozen.md
Target: book/1022.2025.newbook.augmented.dedup.md
Report: tools/reports/dedupe_<utc>.log

Strategy (safe):
- Parse Markdown headings (#..######). Build blocks: heading line + its content
  until the next heading of the same or higher level.
- Remove only consecutive duplicate blocks where (level, normalized title, text)
  are identical. This avoids cross-chapter false positives.
- Preserve everything else verbatim.
"""

from __future__ import annotations

import hashlib
import os
import re
from datetime import datetime, timezone
from pathlib import Path

SRC = Path("book/1022.2025.newbook.augmented.frozen.md")
DST = Path("book/1022.2025.newbook.augmented.dedup.md")
REPORT_DIR = Path("tools/reports")

HEAD_RE = re.compile(r"^(?P<hash>#{1,6})\s+(?P<title>.*\S)\s*$")


class Block:
    __slots__ = ("level", "title", "start", "end", "lines", "_hash")

    def __init__(self, level: int, title: str, start: int):
        self.level = level
        self.title = title
        self.start = start  # 1-based line number
        self.end = start
        self.lines: list[str] = []
        self._hash: str | None = None

    def add_line(self, line: str):
        self.lines.append(line)
        self.end = self.start + len(self.lines) - 1

    def content_hash(self) -> str:
        if self._hash is None:
            # Normalize EOLs and trim trailing spaces per line for hashing stability
            norm = "\n".join(l.rstrip() for l in self.lines)
            h = hashlib.sha256()
            h.update(str(self.level).encode("utf-8"))
            h.update(b"|")
            h.update(self.title.strip().encode("utf-8"))
            h.update(b"|")
            h.update(norm.encode("utf-8"))
            self._hash = h.hexdigest()
        return self._hash


def parse_blocks(all_lines: list[str]):
    blocks: list[Block] = []
    preface: list[str] = []

    # Iterate and create a new block at each heading
    current: Block | None = None
    for i, raw in enumerate(all_lines, start=1):
        m = HEAD_RE.match(raw)
        if m:
            level = len(m.group("hash"))
            title = m.group("title").strip()
            # Start a new block
            current = Block(level, title, start=i)
            current.add_line(raw)
            blocks.append(current)
        else:
            if current is None:
                preface.append(raw)
            else:
                current.add_line(raw)
    return preface, blocks


def dedupe_blocks(blocks: list[Block]):
    kept: list[Block] = []
    removed_info: list[tuple[int, int, str]] = []  # (start, end, title)
    prev_hash: str | None = None
    for b in blocks:
        h = b.content_hash()
        if prev_hash == h:
            # consecutive duplicate, drop
            removed_info.append((b.start, b.end, b.title))
            # do not update prev_hash, maintain comparison to last kept
            continue
        kept.append(b)
        prev_hash = h
    return kept, removed_info


def write_output(preface: list[str], blocks: list[Block]):
    out_lines: list[str] = []
    out_lines.extend(preface)
    for b in blocks:
        out_lines.extend(b.lines)
    # Ensure trailing newline
    content = "\n".join(out_lines)
    if not content.endswith("\n"):
        content += "\n"
    DST.write_text(content, encoding="utf-8")
    return len(out_lines)


def write_report(removed_info: list[tuple[int, int, str]]):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report_path = REPORT_DIR / f"dedupe_{ts}.log"
    lines = [
        f"source: {SRC.as_posix()}",
        f"target: {DST.as_posix()}",
        f"removed_blocks: {len(removed_info)}",
        "-- details --",
    ]
    for start, end, title in removed_info[:500]:  # cap details to avoid huge logs
        lines.append(f"[{start}-{end}] {title}")
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


def main():
    if not SRC.exists():
        raise SystemExit(f"Source not found: {SRC}")
    all_text = SRC.read_text(encoding="utf-8")
    all_lines = all_text.splitlines()

    preface, blocks = parse_blocks(all_lines)
    kept, removed = dedupe_blocks(blocks)
    total_out = write_output(preface, kept)
    report_path = write_report(removed)
    print(
        f"Deduped: removed={len(removed)} blocks, out_lines={total_out}, report={report_path.as_posix()}"  # noqa: T201
    )


if __name__ == "__main__":
    main()
