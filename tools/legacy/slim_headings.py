"""Generate a slimmed chapter file by filtering out routine sub-headings.

Source: book/篇章内容.md (Markdown headings with line-number comments)
Target: book/篇章内容.精简.md

Removes headings whose title is exactly one of: 学习目标 / 小结 / 练习.
Keeps all other lines intact (including metadata comments at the top).
Collapses consecutive blank lines to a single blank line.
"""

from __future__ import annotations

import re
from pathlib import Path

SRC = Path("book/篇章内容.md")
DST = Path("book/篇章内容.精简.md")

HEAD_RE = re.compile(r"^(?P<hash>#{1,6})\s+(?P<title>[^<]+?)(?:\s+<!--.*)?$")
FILTER_TITLES = {"学习目标", "小结", "练习"}


def should_filter(line: str) -> bool:
    m = HEAD_RE.match(line)
    if not m:
        return False
    title = m.group("title").strip()
    return title in FILTER_TITLES


def main():
    if not SRC.exists():
        raise SystemExit(f"Source not found: {SRC}")

    src_lines = SRC.read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    removed = 0
    for s in src_lines:
        if should_filter(s):
            removed += 1
            continue
        # Preserve comments and all other lines
        out.append(s)

    # Collapse multiple blank lines
    compact: list[str] = []
    for s in out:
        if s.strip() == "":
            if compact and compact[-1] == "":
                continue
        compact.append(s)

    content = "\n".join(compact) + "\n"
    DST.write_text(content, encoding="utf-8")
    print(
        f"Slim file written: {DST.as_posix()} (removed={removed}, total_out_lines={len(compact)})"
    )


if __name__ == "__main__":
    main()
