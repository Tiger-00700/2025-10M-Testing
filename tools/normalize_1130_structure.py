from __future__ import annotations

import re
import sys
from datetime import datetime
import argparse
from pathlib import Path


CHAPTER_RE = re.compile(r"^###\s+第(\d+)章\s")


def is_fence(line: str) -> bool:
    l = line.lstrip()
    return l.startswith("```") or l.startswith("~~~")


def extract_blockquote_block(lines: list[str], start: int) -> tuple[int, list[str]]:
    n = len(lines)
    block: list[str] = []
    i = start
    while i < n and lines[i].lstrip().startswith(">"):
        block.append(lines[i])
        i += 1
    return i, block


def normalize_heading_jumps(lines: list[str]) -> list[str]:
    out: list[str] = []
    in_code = False
    last_level = 0
    for L in lines:
        if is_fence(L):
            in_code = not in_code
            out.append(L)
            continue
        if in_code:
            out.append(L)
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", L)
        if m:
            lvl = len(m.group(1))
            text = m.group(2)
            if last_level == 0:
                last_level = lvl
            else:
                if lvl > last_level + 1:
                    lvl = last_level + 1
                    L = ("#" * lvl) + " " + text
            last_level = lvl
            out.append(L)
        else:
            out.append(L)
    return out


def remove_adjacent_duplicate_examples(lines: list[str]) -> list[str]:
    out: list[str] = []
    i = 0
    n = len(lines)
    in_code = False
    while i < n:
        L = lines[i]
        if is_fence(L):
            in_code = not in_code
            out.append(L)
            i += 1
            continue
        if in_code:
            out.append(L)
            i += 1
            continue
        # Detect a blockquote examples header
        if re.match(r"^\s*>\s*示例参考[：:]\s*$", L):
            # capture first block (header + its quoted list or quoted blanks)
            j = i
            j_end, first_block = extract_blockquote_block(lines, j)
            # look ahead skipping pure blank lines
            k = j_end
            while k < n and lines[k].strip() == "":
                k += 1
            # if next block also starts with '> 示例参考' capture and compare
            if k < n and re.match(r"^\s*>\s*示例参考[：:]\s*$", lines[k]):
                k_end, second_block = extract_blockquote_block(lines, k)
                if [s.rstrip() for s in first_block] == [s.rstrip() for s in second_block]:
                    # skip the duplicate second block and any blanks between
                    out.extend(first_block)
                    i = k_end
                    continue
            # no adjacent duplicate found
            out.extend(first_block)
            i = j_end
            continue
        out.append(L)
        i += 1
    return out


def reorder_chapters(lines: list[str]) -> list[str]:
    # Find chapter starts
    in_code = False
    starts: list[tuple[int, int]] = []  # (index, chapter_no)
    for idx, L in enumerate(lines):
        if is_fence(L):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = CHAPTER_RE.match(L)
        if m:
            try:
                num = int(m.group(1))
            except ValueError:
                continue
            starts.append((idx, num))

    if not starts:
        return lines

    # Build chapter slices
    slices: list[tuple[int, int, int]] = []  # (start, end, number)
    for i, (s, num) in enumerate(starts):
        e = starts[i + 1][0] if i + 1 < len(starts) else len(lines)
        slices.append((s, e, num))

    # Determine if misordered
    numbers = [num for _, _, num in slices]
    if numbers == sorted(numbers):
        return lines  # already ordered

    # Preserve front matter before first chapter
    front = lines[:slices[0][0]]
    # Sort chapters by (number, original index) to maintain stability for duplicates
    sorted_slices = sorted(enumerate(slices), key=lambda t: (t[1][2], t[0]))
    out = list(front)
    for _, (s, e, _num) in sorted_slices:
        out.extend(lines[s:e])
        # ensure a blank line between chapters
        if len(out) > 0 and out[-1].strip() != "":
            out.append("\n")
    return out


def collapse_blank_lines(lines: list[str]) -> list[str]:
    out: list[str] = []
    blank = 0
    for L in lines:
        if L.strip() == "":
            blank += 1
            if blank <= 1:
                out.append("")
        else:
            blank = 0
            out.append(L.rstrip("\n"))
    return [l + "\n" for l in out]


def _chapter_ranges(lines: list[str]) -> list[tuple[int, int, int]]:
    """Return list of (start_index, end_index, chapter_no)."""
    in_code = False
    starts: list[tuple[int, int]] = []
    for idx, L in enumerate(lines):
        if is_fence(L):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = CHAPTER_RE.match(L)
        if m:
            try:
                num = int(m.group(1))
            except ValueError:
                continue
            starts.append((idx, num))
    if not starts:
        return []
    ranges: list[tuple[int, int, int]] = []
    for i, (s, num) in enumerate(starts):
        e = starts[i + 1][0] if i + 1 < len(starts) else len(lines)
        ranges.append((s, e, num))
    return ranges


def _normalize_example_block_signature(block: list[str]) -> str:
    """Create a normalized signature for an '> 示例参考' block to compare content.
    Strip leading '>' and whitespace, drop blank lines, and normalize spaces.
    """
    norm: list[str] = []
    for L in block:
        s = L.lstrip()
        if not s.startswith(">"):
            # Only consider the quoted part for signature
            continue
        content = s[1:].strip()
        if content == "":
            continue
        # collapse internal whitespace for robust comparison
        content = re.sub(r"\s+", " ", content)
        norm.append(content)
    return "\n".join(norm)


def dedupe_nonadjacent_examples_within_chapters(lines: list[str]) -> list[str]:
    out = list(lines)
    ranges = _chapter_ranges(out)
    if not ranges:
        return out
    result: list[str] = []
    last_end = 0
    for s, e, chap_no in ranges:
        # copy text before this chapter unchanged
        result.extend(out[last_end:s])
        chapter_lines = out[s:e]
        seen: set[str] = set()
        i = 0
        n = len(chapter_lines)
        in_code = False
        while i < n:
            L = chapter_lines[i]
            if is_fence(L):
                in_code = not in_code
                result.append(L)
                i += 1
                continue
            if in_code:
                result.append(L)
                i += 1
                continue
            if re.match(r"^\s*>\s*示例参考[：:]\s*$", L):
                j_end, block = extract_blockquote_block(chapter_lines, i)
                sig = _normalize_example_block_signature(block)
                if sig and sig in seen:
                    # skip duplicate block
                    i = j_end
                    # optional: skip following blank lines
                    while i < n and chapter_lines[i].strip() == "":
                        i += 1
                    continue
                if sig:
                    seen.add(sig)
                result.extend(block)
                i = j_end
                continue
            result.append(L)
            i += 1
        last_end = e
    # tail after last chapter
    result.extend(out[last_end:])
    return result


def fix_subsection_numbering(lines: list[str]) -> list[str]:
    """Ensure headings with numeric prefixes match the containing chapter number.
    Example: inside 第2章, '#### 1.1 标题' -> '#### 2.1 标题'. Skip code and blockquotes.
    """
    out = list(lines)
    ranges = _chapter_ranges(out)
    if not ranges:
        return out
    result: list[str] = []
    last_end = 0
    for s, e, chap_no in ranges:
        # copy pre-chapter text
        result.extend(out[last_end:s])
        chapter_lines = out[s:e]
        in_code = False
        for idx, L in enumerate(chapter_lines):
            # keep the chapter title line intact
            if idx == 0 and CHAPTER_RE.match(L):
                result.append(L)
                continue
            if is_fence(L):
                in_code = not in_code
                result.append(L)
                continue
            if in_code or L.lstrip().startswith('>'):
                result.append(L)
                continue
            m = re.match(r"^(#{2,6})\s+(\d+(?:\.\d+)*)([ .、])\s*(.*)$", L)
            if m:
                hashes, numseq, sep, rest = m.groups()
                parts = numseq.split('.')
                try:
                    first = int(parts[0])
                except Exception:
                    result.append(L)
                    continue
                if first != chap_no:
                    parts[0] = str(chap_no)
                    new_num = '.'.join(parts)
                    L = f"{hashes} {new_num}{sep}{rest}".rstrip()
            result.append(L)
        last_end = e
    result.extend(out[last_end:])
    return result


def fix_subsection_numbering_sequential(lines: list[str]) -> list[str]:
    """Strictly renumber subsections in encounter order within each chapter.
    Rules:
      - Force prefix to chapter number.
      - For depth=2 (N.x): x starts at 1 and increments by 1 across chapter.
      - For depth>=3: follow the most recent parent at depth-1; child index starts at 1 and increments by 1 per parent tuple.
      - Skip code fences and blockquotes. Keep chapter title line intact.
    """
    out = list(lines)
    ranges = _chapter_ranges(out)
    if not ranges:
        return out
    result: list[str] = []
    last_end = 0
    for s, e, chap_no in ranges:
        result.extend(out[last_end:s])
        chapter_lines = out[s:e]
        in_code = False
        # parent -> next expected child index
        next_index: dict[tuple[int, ...], int] = {}
        # track last corrected number sequence by depth
        last_by_depth: dict[int, list[int]] = {}
        for idx, L in enumerate(chapter_lines):
            if idx == 0 and CHAPTER_RE.match(L):
                result.append(L)
                continue
            if is_fence(L):
                in_code = not in_code
                result.append(L)
                continue
            if in_code or L.lstrip().startswith('>'):
                result.append(L)
                continue
            m = re.match(r"^(#{2,6})\s+(\d+(?:\.\d+)*)([ .、])\s*(.*)$", L)
            if not m:
                result.append(L)
                continue
            hashes, numseq, sep, rest = m.groups()
            # depth from numeric sequence
            parts_raw = [int(p) for p in numseq.split('.') if p.isdigit()]
            if not parts_raw:
                result.append(L)
                continue
            depth = len(parts_raw)
            # compute parent tuple for this depth
            if depth == 2:
                parent = (chap_no,)
            else:
                # try to use last_by_depth[depth-1] as parent
                parent_seq = last_by_depth.get(depth - 1)
                if parent_seq is None:
                    # fallback to the longest available shallower parent, pad with 1s
                    pdepth = max([d for d in last_by_depth.keys() if d < depth], default=1)
                    if pdepth >= 2:
                        parent_seq = last_by_depth[pdepth][:]
                    else:
                        parent_seq = [chap_no]
                    # pad to required parent length (depth-1)
                    while len(parent_seq) < depth - 1:
                        parent_seq.append(1)
                parent = tuple([chap_no] + parent_seq[1:]) if parent_seq and parent_seq[0] == chap_no else tuple(parent_seq)
                if len(parent) != depth - 1:
                    # ensure correct chapter prefix and length
                    base = [chap_no]
                    base.extend(parent[1:depth - 1] if len(parent) > 1 else [])
                    while len(base) < depth - 1:
                        base.append(1)
                    parent = tuple(base)

            # next index for this parent
            nxt = next_index.get(parent, 1)
            corrected = list(parent) + [nxt]
            next_index[parent] = nxt + 1
            last_by_depth[depth] = corrected
            # store/update shallower parent last sequences
            last_by_depth[len(parent)] = list(parent)

            new_num = '.'.join(str(x) for x in corrected)
            new_line = f"{hashes} {new_num}{sep}{rest}".rstrip()
            result.append(new_line)

        last_end = e
    result.extend(out[last_end:])
    return result


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix-numbering", action="store_true", help="Strictly renumber subsections within chapters")
    args = ap.parse_args()
    target = root / "book" / "1130.2025.newbook.md"
    if not target.exists():
        print(f"Target not found: {target}")
        return 2
    original = target.read_text(encoding="utf-8", errors="ignore").splitlines(keepends=True)

    # Pass 1: reorder misordered chapter sections
    lines = reorder_chapters([l.rstrip("\n") for l in original])
    # Pass 2: remove adjacent duplicate '示例参考' blocks
    lines = remove_adjacent_duplicate_examples(lines)
    # Pass 3: constrain heading jumps
    lines = normalize_heading_jumps(lines)
    # Pass 4: non-adjacent example dedupe within chapters
    lines = dedupe_nonadjacent_examples_within_chapters(lines)
    # Pass 5: numbering fixes
    if args.fix_numbering:
        lines = fix_subsection_numbering_sequential(lines)
    else:
        # conservative: only align chapter prefix
        lines = fix_subsection_numbering(lines)
    # Pass 6: collapse excessive blank lines
    lines = collapse_blank_lines(lines)

    out_text = "".join(lines)
    orig_text = "".join(original)
    if out_text != orig_text:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = target.with_suffix(f".md.bak_struct_{ts}")
        backup.write_text(orig_text, encoding="utf-8")
        target.write_text(out_text, encoding="utf-8")
        print(f"Normalized {target} (backup at {backup})")
    else:
        print("No structural changes were necessary.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
