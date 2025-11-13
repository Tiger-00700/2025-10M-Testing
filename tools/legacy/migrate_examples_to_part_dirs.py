#!/usr/bin/env python3
"""
Move semantic example files from examples/ root into per-part directories and
rename them to the new convention, then update links in the links-only book.

New convention:
- Directory: examples/第{P}篇/
- Filename: 第{P}篇-第{C}章-{D}节{ext}
  where P = part number (no zero-padding),
        C = chapter number (first component of H2 numeric outline),
        D = dot-joined numeric outline up to three levels (e.g., 13.1.1 or 13.1)
        ext = original file extension

We derive P, C, D from the nearest H2/H3/H4 headings around each link's position.

Scope: Links currently pointing to examples/<basename> created by prior migration
(typically named like 'PP篇-CC.SS章-...' or similar).

Idempotent: if already under examples/第P篇/, only rename/update if basename differs.
"""
from __future__ import annotations
import re
import shutil
from pathlib import Path
from typing import List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
BOOK_LINKS = ROOT / 'book' / '1022.2025.newbook.links.md'
BOOK_CANON = ROOT / 'book' / '1022.2025.newbook.md'
EXAMPLES_DIR = ROOT / 'examples'

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)
NUM_PREFIX_RE = re.compile(r"^(\d+(?:[\.\- ]\d+)*)\s+(.+)$")
PART_IN_SUFFIX_RE = re.compile(r"（来自：第(\d+)篇-[^）]+）")
SOURCE_SUFFIX_RE = re.compile(r"\s*（来自：[^）]+）\s*")

# Match links to examples at repo root or under part-dirs we will normalize
LINK_RE = re.compile(r"\[([^\]]+)\]\((examples/([^/)]+\.[A-Za-z0-9]+))\)")
PARTDIR_LINK_RE = re.compile(r"\[([^\]]+)\]\((examples/第(\d+)篇/([^)/]+\.[A-Za-z0-9]+))\)")


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
    nums = [int(x) for x in re.findall(r"\d+", nums_part)]
    numkey = "-".join(f"{n:02d}" for n in nums)
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


def derive_part(canon_heads: List[dict], title_clean: str, level: int) -> int:
    # Try exact level match
    for h in canon_heads:
        if h["level"] == level:
            t = strip_source_suffix(h["title"])
            _, t_rest = split_num_prefix(t)
            if t_rest == title_clean:
                m = PART_IN_SUFFIX_RE.search(h["title"])
                if m:
                    return int(m.group(1))
    # Fallback any level
    for h in canon_heads:
        t = strip_source_suffix(h["title"])
        _, t_rest = split_num_prefix(t)
        if t_rest == title_clean:
            m = PART_IN_SUFFIX_RE.search(h["title"])
            if m:
                return int(m.group(1))
    return 0


def dotify(numkey: Optional[str], levels: int) -> Optional[str]:
    if not numkey:
        return None
    parts = [int(x) for x in numkey.split('-')]
    if not parts:
        return None
    levels = min(levels, len(parts))
    return ".".join(str(x) for x in parts[:levels])


def build_new_name(part: int, h2: Optional[dict], h3: Optional[dict], h4: Optional[dict], ext: str) -> Tuple[Path, str]:
    h2_num, _ = split_num_prefix(h2["title"]) if h2 else (None, "")
    h3_num, _ = split_num_prefix(h3["title"]) if h3 else (None, "")
    h4_num, _ = split_num_prefix(h4["title"]) if h4 else (None, "")
    # Chapter number = first component of H2 numeric
    chap = None
    if h2_num:
        chap = int(h2_num.split('-')[0])
    # D = up to 3-level dot-joined from deepest available numeric
    deepest = h4_num or h3_num or h2_num
    D = dotify(deepest, 3) or (str(chap) if chap is not None else None)
    # Directory and filename
    part_dir = EXAMPLES_DIR / f"第{part}篇"
    if chap is None and D is None:
        # Fallback
        fname = f"第{part}篇-未编号章{ext}"
    else:
        if chap is None:
            chap = int(D.split('.')[0])
        fname = f"第{part}篇-第{chap}章-{D}节{ext}"
    return part_dir, fname


def process() -> Tuple[int, int]:
    if not BOOK_LINKS.exists() or not BOOK_CANON.exists():
        raise SystemExit("Book files missing.")
    text = BOOK_LINKS.read_text(encoding='utf-8')
    canon = BOOK_CANON.read_text(encoding='utf-8')
    heads = parse_headings(text)
    canon_heads = parse_headings(canon)

    changes = 0
    moves = 0

    def rewrite_link(full_match: re.Match[str], url: str, basename: str) -> str:
        nonlocal changes, moves
        pos = full_match.start()
        h2, h3, h4 = nearest_context(heads, pos)
        deepest = next((h for h in (h4, h3, h2) if h), None)
        title_clean = ''
        level = 0
        if deepest:
            level = deepest['level']
            t = strip_source_suffix(deepest['title'])
            _, t_rest = split_num_prefix(t)
            title_clean = t_rest
        part = derive_part(canon_heads, title_clean, level)
        ext = Path(basename).suffix
        part_dir, new_fname = build_new_name(part, h2, h3, h4, ext)
        part_dir.mkdir(parents=True, exist_ok=True)
        src = ROOT / url
        dst = part_dir / new_fname
        try:
            if src.exists():
                if src.resolve() != dst.resolve():
                    if not dst.exists():
                        shutil.move(str(src), str(dst))
                        moves += 1
                    else:
                        # If destination exists, delete source to avoid duplicates
                        src.unlink(missing_ok=True)
            else:
                # Ensure destination placeholder exists
                if not dst.exists():
                    dst.write_text('Placeholder: migrated to part dir.\n', encoding='utf-8')
        except Exception as e:
            print(f"WARN: move failed {src} -> {dst}: {e}")
        new_url = dst.relative_to(ROOT).as_posix()
        changes += 1
        return f"[{full_match.group(1)}]({new_url})"

    # First: links at examples/<basename>
    def repl_root(m: re.Match[str]) -> str:
        return rewrite_link(m, m.group(2), m.group(3))

    new_text, n1 = LINK_RE.subn(repl_root, text)

    # Second: normalize already under examples/第P篇/ but wrong filename
    def repl_partdir(m: re.Match[str]) -> str:
        # We'll still recompute correct name and adjust if different
        return rewrite_link(m, m.group(1), m.group(3))

    # Note: PARTDIR_LINK_RE uses groups differently, adjust
    def repl_partdir_fixed(m: re.Match[str]) -> str:
        disp = m.group(1)
        pnum = m.group(2)
        tail = m.group(3)
        url = f"examples/第{pnum}篇/{tail}"
        class Dummy:
            def start(self):
                return m.start()
            def group(self, i):
                return [disp, url, tail][i]
        return rewrite_link(m, url, tail)

    new_text2, n2 = PARTDIR_LINK_RE.subn(repl_partdir_fixed, new_text)

    if n1 or n2:
        BOOK_LINKS.write_text(new_text2, encoding='utf-8')
    print(f"Updated {n1+n2} links; moved {moves} files.")
    return n1+n2, moves


def main() -> int:
    updated, moved = process()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
