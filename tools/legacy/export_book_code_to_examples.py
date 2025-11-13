#!/usr/bin/env python3
"""
Export all fenced code blocks from the canonical book into examples/ and
produce a links-only variant of the book where code blocks are replaced by
links to the exported files.

Inputs:
- book/1022.2025.newbook.md (canonical source)

Outputs:
- examples/99_book_exports/newbook__blockNN.<ext>
- book/1022.2025.newbook.links.md (book with code blocks replaced by links)

Idempotent: Re-runs will overwrite the exported files and regenerate the links
variant deterministically using stable block numbering based on traversal order.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BOOK_SRC = REPO_ROOT / "book/1022.2025.newbook.md"
BOOK_OUT = REPO_ROOT / "book/1022.2025.newbook.links.md"
EXPORT_DIR = REPO_ROOT / "examples/99_book_exports"


def slugify(title: str) -> str:
    """Make a filesystem-friendly slug from a heading title (supports CJK)."""
    t = title.strip()
    # Normalize all whitespace to single dashes
    t = re.sub(r"\s+", "-", t)
    # Remove unsafe characters for Windows paths
    t = re.sub(r"[<>:\"/\\|\?\*]", "", t)
    # Collapse repeated dashes
    t = re.sub(r"-+", "-", t)
    t = t.strip("-._")
    return t or "untitled"


def parse_headings_with_positions(text: str):
    """Return list of dicts: {level, title, start} for all headings."""
    heads = []
    for m in re.finditer(r"^(#{1,6})\s+(.*)$", text, flags=re.MULTILINE):
        level = len(m.group(1))
        title = m.group(2).strip()
        heads.append({"level": level, "title": title, "start": m.start()})
    return heads


def split_num_title(title: str) -> tuple[str | None, str]:
    """Extract a leading numeric outline like '3.3.2 ' or '3-3-2 '.

    Returns a tuple like ('03-03-02', rest).
    """
    m = re.match(r"^(\d+(?:[\.\- ]\d+)*)\s+(.+)$", title)
    if not m:
        return None, title
    # Be robust: pull out all digit runs to form the numeric key
    nums = re.findall(r"\d+", m.group(1))
    numkey = '-'.join(f"{int(n):02d}" for n in nums)
    rest = m.group(2).strip()
    return numkey, rest


def remove_source_suffix(t: str) -> str:
    """Remove trailing/embedded source suffix like '（来自：...）' or '(来自：...)'."""
    # Remove any full-width or half-width parentheses that contain '来自：'
    t = re.sub(r"\s*（来自：[^）]+）\s*", " ", t)
    t = re.sub(r"\s*\(来自：[^)]+\)\s*", " ", t)
    # Collapse spaces
    t = re.sub(r"\s+", " ", t).strip()
    return t


def heading_segment(h) -> str:
    # Clean up title by removing any source suffix first
    clean_title = remove_source_suffix(h["title"])
    numkey, rest = split_num_title(clean_title)
    if numkey:
        return f"{numkey}-{slugify(remove_source_suffix(rest))}"
    return f"L{h['level']}-{slugify(clean_title)}"


def lang_to_ext(lang: str | None) -> str:
    if not lang:
        return ".txt"
    l = lang.lower().strip()
    mapping = {
        "python": ".py",
        "py": ".py",
        "bash": ".sh",
        "sh": ".sh",
        "shell": ".sh",
        "powershell": ".ps1",
        "ps": ".ps1",
        "ps1": ".ps1",
        "yaml": ".yaml",
        "yml": ".yaml",
        "json": ".json",
        "sql": ".sql",
        "java": ".java",
        "scala": ".scala",
        "ini": ".ini",
        "toml": ".toml",
        "xml": ".xml",
        "markdown": ".md",
        "md": ".md",
        "text": ".txt",
        "txt": ".txt",
    }
    return mapping.get(l, ".txt")


def export_code_blocks(book_text: str) -> tuple[str, list[Path]]:
    """
    Find fenced blocks ```lang\n...\n``` and export. Replace with link.
    Returns: (links-only text, list of exported file paths)
    """
    # Regex to match fenced code blocks; capture optional language.
    # Use MULTILINE and DOTALL to span lines. Split the pattern across
    # short raw string parts to keep source lines under the limit.
    fence_re = re.compile(
        r"^```\s*([\w+-]*)\s*\n"
        r"(.*?)\n```\s*$",
        re.MULTILINE | re.DOTALL,
    )

    headings = parse_headings_with_positions(book_text)

    exported: list[Path] = []
    block_idx = 0

    def nearest_context(block_start: int):
        """Find nearest preceding H2/H3/H4 headings."""
        h2 = h3 = h4 = None
        for h in headings:
            if h["start"] <= block_start:
                if h["level"] == 2:
                    h2 = h
                    h3 = None
                    h4 = None
                elif h["level"] == 3:
                    h3 = h
                    h4 = None
                elif h["level"] == 4:
                    h4 = h
            else:
                break
        return h2, h3, h4

    def pick_short_slug(h2, h3, h4) -> tuple[str, int]:
        """Return (slug, level) preferring deepest numeric outline among H4/H3/H2.
        Slug is either numeric key (e.g., 14-02-01) or 'Lx-<slugified-title>' fallback.
        """
        for h in (h4, h3, h2):
            if not h:
                continue
            numkey, rest = split_num_title(h["title"]) 
            if numkey:
                return numkey, h["level"]
        # Fallback: deepest available slugified title
        for h in (h4, h3, h2):
            if h:
                return f"L{h['level']}-{slugify(h['title'])}", h["level"]
        return "L0-untitled", 0

    def short_display_title(h2, h3, h4) -> str:
        """Human-facing short title for the deepest available heading.
        Rules:
        - Use the deepest title (H4 > H3 > H2)
        - Trim leading numeric outline like "13-01-01 " or "13.1.1 "
        - Remove trailing source suffix like "（来自：...）"
        - Collapse whitespace
        """
        def _trim(t: str) -> str:
            # Remove leading numeric outline (variants with '-', '.', or spaces)
            t2 = re.sub(r"^(\d+(?:[-\. ]\d+)*)(\s+)", "", t)
            # Remove source suffix variants
            t2 = remove_source_suffix(t2)
            # Normalize spaces
            t2 = re.sub(r"\s+", " ", t2).strip()
            return t2 or "Untitled"

        for h in (h4, h3, h2):
            if h:
                return _trim(h["title"])
        return "Untitled"

    def _derive_disp_from_dirname(dirname: str) -> str:
        """Derive a short human title from a directory name segment.
        Examples:
          '13-01-01-可观测性三大支柱-（来自：...）' -> '可观测性三大支柱'
          'L4-分布式追踪-（来自：...）' -> '分布式追踪'
        """
        title = dirname
        # Drop leading Lx- marker
        title = re.sub(r'^L\d+-', '', title)
        # Drop numeric key like 13-01-01-
        title = re.sub(r'^(\d{2}(?:-\d{2})*-?)', '', title)
        # Replace dashes with spaces for readability
        title = title.replace('-', ' ')
        # Remove source suffix and normalize spaces
        title = remove_source_suffix(title)
        title = re.sub(r"\s+", " ", title).strip()
        return title or '示例'

    def _derive_disp_from_url(url: str) -> str:
        # Use the last directory segment as basis
        p = url.split('#', 1)[0].split('?', 1)[0]
        parts = Path(p).parts
        if len(parts) >= 2:
            dirname = parts[-2]
            return _derive_disp_from_dirname(dirname)
        return '示例'

    def repl(match: re.Match[str]) -> str:
        nonlocal block_idx
        block_idx += 1
        lang = (match.group(1) or "").strip() or None
        code = match.group(2)
        start = match.start()

        ext = lang_to_ext(lang)
        # Build semantic directory path from headings
        h2, h3, h4 = nearest_context(start)
        parts = [EXPORT_DIR]
        if h2:
            parts.append(Path(heading_segment(h2)))
        if h3:
            parts.append(Path(heading_segment(h3)))
        if h4:
            parts.append(Path(heading_segment(h4)))
        export_dir = Path(*parts)
        export_dir.mkdir(parents=True, exist_ok=True)
        short_slug, _lvl = pick_short_slug(h2, h3, h4)
        fname = f"{short_slug}__block{block_idx:03d}{ext}"
        out_path = export_dir / fname
        # Normalize line endings and ensure trailing newline
        data = code.rstrip("\n") + "\n"
        out_path.write_text(data, encoding="utf-8")
        exported.append(out_path)

        rel = out_path.relative_to(REPO_ROOT).as_posix()
        # Replace block with a more readable link text using directory-derived title
        disp = _derive_disp_from_dirname(export_dir.name)
        return f"> 示例脚本：[{disp} · {fname}]({rel})\n\n> 语言：{lang or 'text'}"

    links_text = fence_re.sub(repl, book_text)

    # Second pass: upgrade legacy links that still point to old filenames
    # Pattern example:
    # > 示例脚本：[newbook__block001.yaml](examples/.../newbook__block001.yaml)
    # Legacy pattern that references old-style filenames; split into parts
    legacy_re = re.compile(
        r"^>\s*示例脚本：\[[^\]]*\]\("
        r"[^)]*/newbook__block(\d{3})(\.[^)]+)\)",
        re.MULTILINE,
    )

    def repl_legacy(m: re.Match[str]) -> str:
        # Find heading context at this position
        pos = m.start()
        h2, h3, h4 = nearest_context(pos)
        short_slug, _lvl = pick_short_slug(h2, h3, h4)
        num = m.group(1)
        ext = m.group(2)
        # Recompute export dir to build URL
        parts = [EXPORT_DIR]
        if h2:
            parts.append(Path(heading_segment(h2)))
        if h3:
            parts.append(Path(heading_segment(h3)))
        if h4:
            parts.append(Path(heading_segment(h4)))
        export_dir = Path(*parts)
        rel_dir = export_dir.relative_to(REPO_ROOT).as_posix()
        new_fname = f"{short_slug}__block{num}{ext}"
        new_rel = f"{rel_dir}/{new_fname}"
        disp = _derive_disp_from_url(new_rel)
        return f"> 示例脚本：[{disp} · {new_fname}]({new_rel})"

    links_text = legacy_re.sub(repl_legacy, links_text)

    # Final pass: ensure visible texts follow "章节短标题 + 文件名" regardless
    # of earlier paths. Keep regex literal parts short.
    any_link_re = re.compile(
        r"^>\s*示例脚本：\[[^\]]*\]\(([^)]+)\)",
        re.MULTILINE,
    )

    def repl_any(m: re.Match[str]) -> str:
        pos = m.start()
        h2, h3, h4 = nearest_context(pos)
        # Prefer deriving from the URL path to ensure consistency
        url = m.group(1)
        disp = _derive_disp_from_url(url)
        fname = Path(url.split('#', 1)[0].split('?', 1)[0]).name
        return f"> 示例脚本：[{disp} · {fname}]({url})"

    links_text = any_link_re.sub(repl_any, links_text)
    return links_text, exported


def main() -> int:
    if not BOOK_SRC.exists():
        print(f"ERROR: Book not found: {BOOK_SRC}", file=sys.stderr)
        return 2
    src = BOOK_SRC.read_text(encoding="utf-8")
    # Clean previous exports for this book (newbook__block* under EXPORT_DIR)
    if EXPORT_DIR.exists():
        # Remove previously generated files following either scheme:
        #  - newbook__blockNN.* (legacy)
        #  - *__blockNN.* (current)
        # Remove previously generated files following either legacy or current scheme
        old1 = list(EXPORT_DIR.rglob("newbook__block*"))
        old2 = list(EXPORT_DIR.rglob("*__block*"))
        for p in old1 + old2:
            try:
                if p.is_file():
                    p.unlink()
            except Exception:
                # ignore removal errors
                pass
    links_text, exported = export_code_blocks(src)

    BOOK_OUT.write_text(links_text, encoding="utf-8")
    # Avoid overly long source lines by composing the message in parts
    msg = (
        f"Exported {len(exported)} code blocks to {EXPORT_DIR.relative_to(REPO_ROOT)}; "
        f"links book written: {BOOK_OUT.relative_to(REPO_ROOT)}"
    )
    print(msg)
    # Return non-zero if nothing exported? No — zero to be idempotent.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
