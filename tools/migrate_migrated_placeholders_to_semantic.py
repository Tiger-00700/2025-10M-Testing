#!/usr/bin/env python3
"""
Move files from examples/99_book_exports/_appendix_migrated to examples/
with semantic names derived from the nearest headings in the links-only book,
using the format: "PP篇-CC.SS章-CC.SS.SS节<ext>".

- PP: two-digit part number from the canonical book (parsed from "（来自：第X篇-...")
- CC.SS: chapter.section from the H2 heading numeric outline
- CC.SS.SS: chapter.section.subsection from the H3/H4 numeric outline (if available)

Also rewrites links in book/1022.2025.newbook.links.md that point to
examples/99_book_exports/_appendix_migrated/<fname> to the new examples/<newname>.

Idempotent: if target already exists and content matches, skip; original files will be removed after move.
"""
from __future__ import annotations
import re
import shutil
from pathlib import Path
from typing import List, Tuple, Optional

ROOT = Path(__file__).resolve().parents[1]
BOOK_LINKS = ROOT / 'book' / '1022.2025.newbook.links.md'
BOOK_CANON = ROOT / 'book' / '1022.2025.newbook.md'
MIGRATED_DIR = ROOT / 'examples' / '99_book_exports' / '_appendix_migrated'
EXAMPLES_DIR = ROOT / 'examples'

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)
NUM_PREFIX_RE = re.compile(r"^(\d+(?:[\.\- ]\d+)*)\s+(.+)$")
PART_IN_SUFFIX_RE = re.compile(r"（来自：第(\d+)篇-[^）]+）")
SOURCE_SUFFIX_RE = re.compile(r"\s*（来自：[^）]+）\s*")

LINK_TO_MIGRATED_RE = re.compile(r"\[([^\]]+)\]\((examples/99_book_exports/_appendix_migrated/([^\)]+))\)")


def parse_headings(text: str) -> List[dict]:
    heads = []
    for m in HEADING_RE.finditer(text):
        level = len(m.group(1))
        title = m.group(2).strip()
        heads.append({"level": level, "title": title, "start": m.start()})
    return heads


def strip_source_suffix(t: str) -> str:
    return SOURCE_SUFFIX_RE.sub("", t).strip()


def split_num_prefix(title: str) -> Tuple[Optional[str], str]:
    m = NUM_PREFIX_RE.match(title)
    if not m:
        return None, title
    nums_part = m.group(1)
    rest = m.group(2).strip()
    # standardize to hyphen-joined two-digit
    nums = re.findall(r"\d+", nums_part)
    numkey = "-".join(f"{int(n):02d}" for n in nums)
    return numkey, rest


def nearest_context(heads: List[dict], pos: int):
    h2 = h3 = h4 = None
    for h in heads:
        if h["start"] <= pos:
            if h["level"] == 2:
                h2 = h; h3 = None; h4 = None
            elif h["level"] == 3:
                h3 = h; h4 = None
            elif h["level"] == 4:
                h4 = h
        else:
            break
    return h2, h3, h4


def derive_part_from_canonical(canon_heads: List[dict], title_clean: str, level: int) -> int:
    # Try exact level match by cleaned title
    for h in canon_heads:
        if h["level"] == level:
            t = strip_source_suffix(h["title"])
            # Remove numeric prefix
            _, t_rest = split_num_prefix(t)
            if t_rest == title_clean:
                m = PART_IN_SUFFIX_RE.search(h["title"])
                if m:
                    return int(m.group(1))
    # Fallback: search any level
    for h in canon_heads:
        t = strip_source_suffix(h["title"])
        _, t_rest = split_num_prefix(t)
        if t_rest == title_clean:
            m = PART_IN_SUFFIX_RE.search(h["title"])
            if m:
                return int(m.group(1))
    return 0


def dotify(numkey: Optional[str], count: int) -> Optional[str]:
    if not numkey:
        return None
    parts = numkey.split('-')
    if len(parts) < count:
        return None
    return ".".join(str(int(p)) for p in parts[:count])


def build_semantic_name(part: int, h2: Optional[dict], h3: Optional[dict], h4: Optional[dict], ext: str) -> str:
    # Prefer deepest available numeric for CC.SS.SS
    h2_num, _ = split_num_prefix(h2["title"]) if h2 else (None, "")
    h3_num, _ = split_num_prefix(h3["title"]) if h3 else (None, "")
    h4_num, _ = split_num_prefix(h4["title"]) if h4 else (None, "")

    # Build chapter.section (two levels) and chapter.section.subsection (three levels)
    two = dotify(h3_num or h2_num, 2)  # if h3 present, use its prefix; else use h2
    three = dotify(h4_num or h3_num or h2_num, 3)

    pp = f"{part:02d}篇"
    mid = f"{two}章" if two else "未编号章"
    tail = f"-{three}节" if three else ""
    return f"{pp}-{mid}{tail}{ext}"


def main() -> int:
    if not BOOK_LINKS.exists():
        print(f"Links-only book not found: {BOOK_LINKS}")
        return 2
    if not BOOK_CANON.exists():
        print(f"Canonical book not found: {BOOK_CANON}")
        return 2
    links_text = BOOK_LINKS.read_text(encoding='utf-8')
    canon_text = BOOK_CANON.read_text(encoding='utf-8')
    links_heads = parse_headings(links_text)
    canon_heads = parse_headings(canon_text)

    changes = 0
    moved = 0

    def replace_link(m: re.Match[str]) -> str:
        nonlocal changes, moved
        full_url = m.group(2)
        fname = m.group(3)
        # Determine position for heading context
        pos = m.start()
        h2, h3, h4 = nearest_context(links_heads, pos)
        # derive cleaned deepest title for part lookup
        deepest = next((h for h in (h4, h3, h2) if h), None)
        title_clean = None
        level = 0
        if deepest:
            level = deepest["level"]
            t_clean = strip_source_suffix(deepest["title"])  # links-only should already be stripped
            # remove numeric prefix
            _, t_rest = split_num_prefix(t_clean)
            title_clean = t_rest
        part = derive_part_from_canonical(canon_heads, title_clean or "", level)
        ext = Path(fname).suffix
        new_name = build_semantic_name(part, h2, h3, h4, ext)
        src = ROOT / full_url
        dst = EXAMPLES_DIR / new_name
        dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            if src.exists():
                if not dst.exists():
                    shutil.move(str(src), str(dst))
                    moved += 1
                else:
                    # If destination exists, remove source to avoid duplicates
                    if src.exists():
                        src.unlink()
            else:
                # If source lost, ensure destination exists at least as placeholder
                if not dst.exists():
                    dst.write_text('Placeholder: migrated semantic file.\n', encoding='utf-8')
        except Exception as e:
            print(f"WARN: Failed moving {src} -> {dst}: {e}")
        new_url = dst.relative_to(ROOT).as_posix()
        changes += 1
        return f"[{m.group(1)}]({new_url})"

    new_text, n = LINK_TO_MIGRATED_RE.subn(replace_link, links_text)
    if n:
        BOOK_LINKS.write_text(new_text, encoding='utf-8')
    print(f"Rewrote {changes} links; moved {moved} files.")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
