"""Apply merged drafts to produce a new merged book version.

Reads merge drafts from book/merge_drafts/ and applies them to the frozen
augmented source, replacing source sections with merged content while
preserving traceability markers and skipping blocks when original headings
cannot be resolved.

Outputs the merged result to book/1022.2025.newbook.merged.md. This tool does
not modify the frozen source file.
"""

from __future__ import annotations

import re
from pathlib import Path
# datetime/timezone were previously used for timestamping but are not needed
# for current conservative merging behavior (kept as a note).

BOOK_SRC = Path("book/1022.2025.newbook.augmented.frozen.md")
MERGE_DIR = Path("book/merge_drafts")
OUT_PATH = Path("book/1022.2025.newbook.merged.md")

MERGED_HEADER_RE = re.compile(r"^### \u3010合并稿\u3011(.*)$")
ORIG_LINE_RE = re.compile(r"^- A[：:]行\s*(\d+).*- B[：:]行\s*(\d+)", re.MULTILINE)
LINE_A_RE = re.compile(r"^- A[：:]行\s*(\d+)")
LINE_B_RE = re.compile(r"^- B[：:]行\s*(\d+)")
HEADING_RE = re.compile(r"^(#{1,6})\s+.*\S\s*$")


def latest_merge_draft() -> Path | None:
    candidates = sorted(
        MERGE_DIR.glob("merge-drafts-*.md"),
        key=lambda p: p.name,
        reverse=True,
    )
    return candidates[0] if candidates else None


def load_sections(text: str):
    lines = text.splitlines()
    headings = []  # list of (line_no, level)
    for i, l in enumerate(lines, start=1):
        m = HEADING_RE.match(l)
        if m:
            headings.append((i, len(m.group(1))))
    return lines, headings


def block_end(line_no: int, level: int, headings):
    for ln, lvl in headings:
        if ln > line_no and lvl <= level:
            return ln - 1
    return None  # until EOF


def main():
    # Ensure source exists
    if not BOOK_SRC.exists():
        print("[apply_merge] Source book missing. Skipping apply step.")
        return

    draft = latest_merge_draft()
    # If no drafts, write passthrough merged (equal to frozen) and exit gracefully
    if not draft or not draft.exists():
    src_text = BOOK_SRC.read_text(encoding="utf-8")
    OUT_PATH.write_text(src_text, encoding="utf-8")
    msg = "[apply_merge] No merge drafts found. Wrote passthrough merged = " + OUT_PATH.as_posix()
    msg += " (copied from frozen)"
    print(msg)
        return

    draft_text = draft.read_text(encoding="utf-8")
    book_text = BOOK_SRC.read_text(encoding="utf-8")
    book_lines, book_headings = load_sections(book_text)

    draft_lines = draft_text.splitlines()

    # Parse merged blocks with A/B line metadata
    merged_blocks = []  # (a_line, b_line, merged_content_lines)
    i = 0
    while i < len(draft_lines):
        line = draft_lines[i]
        if line.startswith("## [") and "合并建议" in line:
            # Collect meta until merged header
            meta_lines = []
            j = i + 1
            a_line = b_line = None
            while j < len(draft_lines):
                ml = draft_lines[j]
                if MERGED_HEADER_RE.match(ml):
                    break
                meta_lines.append(ml)
                # Try to extract A/B lines from accumulated meta
                meta_blob = "\n".join(meta_lines)
                m = ORIG_LINE_RE.search(meta_blob)
                if m:
                    a_line = int(m.group(1))
                    b_line = int(m.group(2))
                else:
                    ma = LINE_A_RE.search(ml)
                    mb = LINE_B_RE.search(ml)
                    if ma:
                        a_line = int(ma.group(1))
                    if mb:
                        b_line = int(mb.group(1))
                j += 1
            if a_line and b_line and j < len(draft_lines):
                # Collect merged section until next '---' delimiter or next suggestion block
                merged_content = []
                k = j + 1
                while k < len(draft_lines):
                    if draft_lines[k].startswith("---") and merged_content:
                        break
                    if draft_lines[k].startswith("## [") and merged_content:
                        break
                    merged_content.append(draft_lines[k])
                    k += 1
                merged_blocks.append((a_line, b_line, merged_content))
                i = k
            else:
                i = j + 1
        else:
            i += 1

    # Build replacement map
    replacements = []  # (start_line, end_line, new_lines)
    to_delete_ranges = []  # (start_line, end_line)

    for a_line, b_line, merged_content in merged_blocks:
        # Find heading level for A and B
        a_level = b_level = None
        for ln, lvl in book_headings:
            if ln == a_line:
                a_level = lvl
            if ln == b_line:
                b_level = lvl
        if a_level is None or b_level is None:
            continue
        a_end = block_end(a_line, a_level, book_headings) or len(book_lines)
        b_end = block_end(b_line, b_level, book_headings) or len(book_lines)
    # Prepare merged block with markers
    marker_start = "<!-- MERGED-BEGIN a_line=" + str(a_line) + " b_line=" + str(b_line)
    marker_start += " source=" + draft.name + " -->"
    marker_end = "<!-- MERGED-END -->"
        # Ensure the original heading line is preserved at the top of replacement
        orig_heading_line = book_lines[a_line - 1]
        new_block = [marker_start, orig_heading_line] + merged_content + [marker_end]
        replacements.append((a_line, a_end, new_block))
        to_delete_ranges.append((b_line, b_end))

    # Apply replacements and deletions
    # We'll mark lines to skip
    skip = set()
    for s, e in to_delete_ranges:
        for ln in range(s, e + 1):
            skip.add(ln)

    # Build final output
    out_lines = []
    rep_map = {start: (end, new_lines) for start, end, new_lines in replacements}
    ln = 1
    while ln <= len(book_lines):
        if ln in rep_map:
            end, new_lines = rep_map[ln]
            out_lines.extend(new_lines)
            ln = end + 1
            continue
        if ln in skip:
            ln += 1
            continue
        out_lines.append(book_lines[ln - 1])
        ln += 1

    # If no replacements and no deletions, still produce passthrough merged
    if not replacements and not to_delete_ranges:
        src_text = BOOK_SRC.read_text(encoding="utf-8")
        OUT_PATH.write_text(src_text, encoding="utf-8")
        msg = "[apply_merge] No applicable merged blocks. Wrote passthrough merged = " + OUT_PATH.as_posix()
        msg += " (copied from frozen)"
        print(msg)
        return
    OUT_PATH.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    msg2 = "Merged book written: " + OUT_PATH.as_posix()
    msg2 += " (replaced " + str(len(replacements)) + " blocks, removed " + str(len(to_delete_ranges)) + " duplicates)"
    print(msg2)


if __name__ == "__main__":
    main()
