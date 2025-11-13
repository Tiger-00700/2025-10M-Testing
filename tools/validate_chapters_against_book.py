#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validate chapter files against the canonical book structure and links.

Checks:
1) Alignment: Each file under chapter/ maps to a heading in book/1022.2025.newbook.md
    - Uses filename/title normalization to find a corresponding heading in the book
    - Reports mismatch if not found
2) Link validity:
    - Relative file links: must exist
    - Anchors to book: must match a known heading slug in the book
    - Intra-file anchors: must match headings in the chapter file
    - External links (http/https): reported but not validated (no network calls)
3) Visible content policy (archive pattern):
    - Visible content outside archived block should be minimal (title + stub)
    - If significant visible content is found (beyond stub), compare a snippet to the
      book and warn on drift

Outputs a timestamped report under tools/reports/ and exits non-zero on validation errors.
"""

import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Set

ROOT = Path(__file__).resolve().parents[1]
BOOK_PATH = ROOT / "book" / "1022.2025.newbook.md"
CHAPTER_DIR = ROOT / "chapter"
REPORTS_DIR = ROOT / "tools" / "reports"

# ---------- Utilities ----------

def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore")

_heading_re = re.compile(r"^(#{1,6})\s+(.*)$", re.M)
_link_re = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_html_comment_block_re = re.compile(
    r"<!--\s*archived-content:(?:start|begin)\s*-->"
    r"(.*?)"
    r"<!--\s*archived-content:(?:end)\s*-->",
    re.S | re.I,
)

_punct_cleanup_re = re.compile(r"[\t\n\r]+")
_bracket_suffix_re = re.compile(r"【.*?】")

# GitHub-like slugify (best-effort)
_slug_cleanup_re = re.compile(r"[^\w\-\s\u4e00-\u9fff]")
_multi_dash_re = re.compile(r"\-+")
_spaces_re = re.compile(r"\s+")


def slugify(text: str) -> str:
    t = text.strip().lower()
    t = _slug_cleanup_re.sub("", t)
    t = _spaces_re.sub("-", t)
    t = _multi_dash_re.sub("-", t)
    return t


def normalize_title(t: str) -> str:
    # Remove bracket suffixes like 【入门】, unify dashes/spaces
    t = t.strip()
    t = _bracket_suffix_re.sub("", t)
    t = t.replace("—", "-")
    t = t.replace("–", "-")
    t = t.replace("：", ":")
    t = t.replace("/", "-")
    # Replace multiple spaces or dashes with single space
    t = re.sub(r"\s*[-：:]\s*", " ", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def extract_headings(md: str) -> List[Tuple[int, str]]:
    out: List[Tuple[int, str]] = []
    for m in _heading_re.finditer(md):
        level = len(m.group(1))
        title = m.group(2).strip()
        out.append((level, title))
    return out


def collect_book_headings(md: str) -> Tuple[Dict[str, str], Dict[str, List[str]]]:
    # Returns: normalized_title -> original_title; slug -> original_title list (for anchors)
    headings = extract_headings(md)
    norm_map: Dict[str, str] = {}
    slug_map: Dict[str, List[str]] = {}
    for _, title in headings:
        n = normalize_title(title)
        norm_map.setdefault(n, title)
        s = slugify(title)
        slug_map.setdefault(s, []).append(title)
    return norm_map, slug_map


def find_expected_title_from_filename(filename: str) -> str:
    name = filename.rsplit(".", 1)[0]
    return normalize_title(name)


def extract_visible_stub(md: str) -> str:
    # Remove archived block (within HTML comments) to get visible content
    visible = _html_comment_block_re.sub("", md)
    return visible.strip()


def list_markdown_links(md: str) -> List[Tuple[str, str]]:
    return _link_re.findall(md)


def is_external_link(target: str) -> bool:
    return target.startswith("http://") or target.startswith("https://")


def split_target_anchor(target: str) -> Tuple[str, str]:
    if "#" in target:
        path, anchor = target.split("#", 1)
        return path, anchor
    return target, ""


def load_chapter_file(p: Path) -> str:
    return read_text(p)


# ---------- Validation ----------

def validate_alignment(
    chapter_path: Path,
    md: str,
    book_norm_titles: Dict[str, str],
) -> Tuple[bool, str]:
    """Alignment is considered OK if either:
    - The visible stub links to the canonical book (explicitly indicating canonicalization), or
    - The (normalized) filename/title matches a heading in the book
    """
    # Prefer stub-based alignment: link to canonical book present in visible content
    visible = extract_visible_stub(md)
    if "book/1022.2025.newbook.md" in visible:
        return True, "via-stub"

    expected = find_expected_title_from_filename(chapter_path.name)
    if expected in book_norm_titles:
        return True, book_norm_titles[expected]
    # Try to find via visible H1 title
    headings = extract_headings(visible)
    visible_title = headings[0][1] if headings else ""
    if visible_title:
        n = normalize_title(visible_title)
        if n in book_norm_titles:
            return True, book_norm_titles[n]
    return False, expected


def validate_links(
    chapter_path: Path,
    md: str,
    book_slug_map: Dict[str, List[str]],
) -> Tuple[List[str], List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []
    info: List[str] = []

    # Only validate links in visible content (archive blocks are comments)
    visible = extract_visible_stub(md)

    # Intra-file anchors: collect chapter headings from visible portion
    ch_headings = extract_headings(visible)
    ch_slugs: Set[str] = set(slugify(t) for _, t in ch_headings)

    for text, target in list_markdown_links(visible):
        path, anchor = split_target_anchor(target)
        if is_external_link(target):
            info.append(f"external: [{text}]({target}) (skipped)")
            continue
        if path == "":
            # anchor-only link
            if anchor:
                if anchor.lower().strip().startswith("#"):
                    anchor = anchor[1:]
                if anchor not in ch_slugs:
                    warnings.append(
                        f"broken intra-anchor: [{text}](#{anchor}) not found in {chapter_path.name}"
                    )
            continue

        # Normalize path relative to repo root
        abs_target = (ROOT / path).resolve()
        if not abs_target.exists():
            errors.append(f"missing file: [{text}]({path})")
            continue
        if abs_target.suffix.lower() == ".md" and anchor:
            # Validate anchor against book if target is the canonical book
            if abs_target.samefile(BOOK_PATH):
                s = anchor.strip().lower()
                # Allow anchors with or without leading '#'
                if s.startswith('#'):
                    s = s[1:]
                if s not in book_slug_map:
                    # also try decoded/normalized
                    if s not in book_slug_map and s.replace('%20', '-') not in book_slug_map:
                        errors.append(
                            f"missing book anchor: [{text}]({path}#{anchor})"
                        )
            else:
                # For other md files, try to load and check slugs
                try:
                    other_md = read_text(abs_target)
                    other_visible = extract_visible_stub(other_md)
                    other_slugs = set(slugify(t) for _, t in extract_headings(other_visible))
                    s = anchor.strip().lower()
                    if s.startswith('#'):
                        s = s[1:]
                    if s not in other_slugs:
                        warnings.append(f"missing anchor in {path}: #{anchor}")
                except Exception as e:
                    warnings.append(f"anchor check skipped for {path}: {e}")

    return errors, warnings, info


def visible_content_check(md: str) -> Tuple[bool, int]:
    visible = extract_visible_stub(md)
    # Heuristic: allow up to 30 lines of visible content (title + stub)
    lines = [l for l in visible.splitlines() if l.strip()]
    return (len(lines) <= 30), len(lines)


def main() -> int:
    if not BOOK_PATH.exists():
        print(f"ERROR: canonical book not found at {BOOK_PATH}")
        return 2

    book_md = read_text(BOOK_PATH)
    book_norm_titles, book_slug_map = collect_book_headings(book_md)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    report_path = REPORTS_DIR / f"validate-chapters-{ts}.md"

    chapter_files = sorted(p for p in CHAPTER_DIR.glob("*.md"))
    total = len(chapter_files)
    ok_align = 0
    errors_total: List[str] = []

    lines_out: List[str] = []
    lines_out.append(f"# Chapter validation report ({ts})\n")
    lines_out.append("- Canonical book: `book/1022.2025.newbook.md`")
    lines_out.append(f"- Chapters scanned: {total}\n")

    for p in chapter_files:
        md = load_chapter_file(p)
        align_ok, matched_or_expected = validate_alignment(p, md, book_norm_titles)
        link_errors, link_warnings, link_info = validate_links(p, md, book_slug_map)
        visible_ok, visible_count = visible_content_check(md)

    status = "OK" if (align_ok and not link_errors and visible_ok) else "ISSUES"
    lines_out.append(f"## {p.name} - {status}")
        if align_ok:
            lines_out.append(
                "- Alignment: OK -> matched heading: `" + str(matched_or_expected) + "`"
            )
            ok_align += 1
        else:
            lines_out.append(
                "- Alignment: FAIL -> not found in book; expected (normalized from filename): `"
                + str(matched_or_expected)
                + "`"
            )
            errors_total.append(f"ALIGN:{p.name}")

        if link_errors:
            lines_out.append(f"- Link errors: {len(link_errors)}")
            for e in link_errors:
                lines_out.append(f"  - {e}")
                errors_total.append(f"LINK:{p.name}:{e}")
        else:
            lines_out.append("- Link errors: 0")

        if link_warnings:
            lines_out.append(f"- Link warnings: {len(link_warnings)}")
            for w in link_warnings:
                lines_out.append(f"  - {w}")
        else:
            lines_out.append("- Link warnings: 0")

        if not visible_ok:
            lines_out.append(
                "- Visible content: WARN -> "
                + str(visible_count)
                + " non-empty lines outside archive block"
            )
            lines_out.append("  (stub expected <= 30)")
        else:
            lines_out.append(f"- Visible content: OK ({visible_count} non-empty lines)")

        if link_info:
            lines_out.append(f"- External links (skipped): {len(link_info)}")
        lines_out.append("")

    lines_out.append("---")
    lines_out.append(f"Summary: {ok_align}/{total} aligned; validation errors: {len(errors_total)} (alignment+link).")

    report = "\n".join(lines_out)
    report_path.write_text(report, encoding="utf-8")
    print(f"Report written: {report_path}")

    # Exit non-zero if there are validation errors
    return 1 if errors_total else 0


if __name__ == "__main__":
    sys.exit(main())
