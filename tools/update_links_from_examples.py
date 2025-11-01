#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Update links in book/1022.2025.newbook.links.md to point to actual files under examples/.

Strategy:
- Build an index of all files under examples/ (relative paths using forward slashes), keyed by basename.
- Parse all markdown links whose target starts with "examples/".
- For each link target:
  * If it points to an existing file -> keep.
  * If it points to an existing directory -> try to resolve by using the basename from the visible link text
    (e.g., "脚本：2-4__block1.sh" or "标题 · 12-05-02__block001.yaml").
  * If it points to a non-existing path -> attempt to map by basename extracted from visible text.
- Update links in-place and print a concise summary.

Notes:
- Non-unique basenames are resolved preferentially if a candidate path is under the originally linked directory path
  (for directory links) or if there's only a single global match; otherwise the link is left unchanged.
- Idempotent: running multiple times should not introduce further changes.
"""

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass
from typing import Dict, List, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
BOOK_PATH = os.path.join(ROOT, 'book', '1022.2025.newbook.links.md')
EXAMPLES_DIR = os.path.join(ROOT, 'examples')

LINK_RE = re.compile(r"\[([^\]]+)\]\((examples/[^)]+)\)")


def to_posix(p: str) -> str:
    return p.replace('\\', '/')


def build_examples_index(base_dir: str) -> Tuple[Dict[str, List[str]], set[str]]:
    """Walk examples/ and build:
    - basename -> [relative posix paths]
    - a set of all relative posix file paths
    """
    by_basename: Dict[str, List[str]] = {}
    all_paths: set[str] = set()
    for root, _, files in os.walk(base_dir):
        for fn in files:
            abs_path = os.path.join(root, fn)
            rel_path = os.path.relpath(abs_path, ROOT)
            rel_posix = to_posix(rel_path)
            all_paths.add(rel_posix)
            by_basename.setdefault(fn, []).append(rel_posix)
    return by_basename, all_paths


def extract_basename_from_text(link_text: str) -> str | None:
    """Try to extract a filename with extension from the visible text.
    Examples:
      - "脚本：2-4__block1.sh" -> 2-4__block1.sh
      - "CICD集成模式 · 12-05-02__block001.yaml" -> 12-05-02__block001.yaml
    """
    # Look for the last token that looks like a filename with an extension
    # Conservative pattern: letters/digits/_- and dots, at least one dot for extension
    m = re.findall(r"([0-9A-Za-z_\-]+__block\d+\.[A-Za-z0-9]+)", link_text)
    if m:
        return m[-1]
    # Fallback: any token with a dot that looks like a filename
    m2 = re.findall(r"([0-9A-Za-z_\-]+\.[A-Za-z0-9]+)", link_text)
    if m2:
        return m2[-1]
    return None


@dataclass
class LinkUpdate:
    original: str
    updated: str
    line_no: int
    reason: str


def update_book_links() -> int:
    by_basename, all_example_files = build_examples_index(EXAMPLES_DIR)

    with open(BOOK_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    updates: List[LinkUpdate] = []
    unresolved = 0
    unresolved_samples: List[Tuple[int, str, str]] = []  # (line_no, text, rel_posix)
    checked = 0

    # Precompute line starts for line number mapping
    line_starts = [0]
    for m in re.finditer("\n", content):
        line_starts.append(m.end())

    def line_no_for(pos: int) -> int:
        # binary search would be nicer, but this is fine for the file size
        lo, hi = 0, len(line_starts) - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            if line_starts[mid] <= pos:
                lo = mid + 1
            else:
                hi = mid - 1
        return hi + 1

    new_content = content
    offset = 0  # account for length shifts as we replace

    for m in LINK_RE.finditer(content):
        checked += 1
        text = m.group(1)
        rel_target = m.group(2)  # posix-like
        abs_target = os.path.join(ROOT, rel_target)
        abs_target = os.path.normpath(abs_target)
        rel_posix = to_posix(os.path.relpath(abs_target, ROOT))

        # If the link already points to a real file, skip
        if os.path.isfile(abs_target):
            continue

        # If the path is a directory, try to resolve within it based on the visible text basename
        replacement: str | None = None
        reason = ''
        if os.path.isdir(abs_target):
            base = extract_basename_from_text(text)
            # Collect all files under this directory subtree (relative posix)
            dir_files: List[str] = []
            for r, _, files in os.walk(abs_target):
                for fn in files:
                    ap = os.path.join(r, fn)
                    rp = os.path.relpath(ap, ROOT)
                    dir_files.append(to_posix(rp))

            # 1) If basename exists and matches within this dir subtree, prefer it
            if base and base in by_basename:
                dir_prefix = to_posix(rel_posix + '/')
                candidates = [p for p in by_basename[base] if to_posix(p).startswith(dir_prefix)]
                if len(candidates) == 1:
                    replacement = candidates[0]
                    reason = 'dir->file (unique within dir)'
                elif len(candidates) > 1:
                    candidates.sort(key=len)
                    replacement = candidates[0]
                    reason = 'dir->file (picked shortest within dir)'
                else:
                    # Fallback to global unique match
                    if len(by_basename[base]) == 1:
                        replacement = by_basename[base][0]
                        reason = 'dir->file (global unique)'

            # 2) If still not resolved, try heuristics within the directory files
            if not replacement and dir_files:
                # Try to use extension from the link text if any
                ext_match = re.findall(r"\.([A-Za-z0-9]+)\)?$|\.([A-Za-z0-9]+)$", text)
                ext = None
                if ext_match:
                    # ext_match is list of tuples due to alternation; pick the non-empty
                    last = ext_match[-1]
                    ext = (last[0] or last[1]).lower() if (last[0] or last[1]) else None

                candidates2 = dir_files[:]
                if ext:
                    candidates2 = [p for p in candidates2 if p.lower().endswith('.' + ext)]
                # Prefer names containing '__block' pattern
                block_pref = [p for p in candidates2 if '__block' in os.path.basename(p)]
                if len(block_pref) == 1:
                    replacement = block_pref[0]
                    reason = 'dir->file (by ext+__block)'
                elif len(block_pref) > 1:
                    block_pref.sort(key=len)
                    replacement = block_pref[0]
                    reason = 'dir->file (by ext+__block shortest)'
                else:
                    # If candidates2 is empty due to ext filter, fall back to any file in dir subtree
                    pool = candidates2 if candidates2 else dir_files
                    if len(pool) == 1:
                        replacement = pool[0]
                        reason = 'dir->file (only file)'
                    elif len(pool) > 1:
                        pool.sort(key=len)
                        replacement = pool[0]
                        reason = 'dir->file (picked shortest)'
        else:
            # Non-existing path: try to repair using basename from visible text
            base = extract_basename_from_text(text)
            if base and base in by_basename and len(by_basename[base]) == 1:
                replacement = by_basename[base][0]
                reason = 'missing->file (global unique)'
            else:
                # Heuristic: path looks like a semantic chapter directory under examples?
                # e.g., examples/第2篇/第2篇-第4章-4.3.3节
                m_sem = re.match(r"examples/(第\d+篇)/(第\d+篇-第\d+章-[^/]+)$", rel_posix)
                if m_sem:
                    part_dir, chapter_prefix = m_sem.group(1), m_sem.group(2)
                    # Extract extension hint from link text
                    ext_hint = None
                    em = re.findall(r"\.([A-Za-z0-9]+)", text)
                    if em:
                        ext_hint = em[-1].lower()
                    # Search all example files whose basename starts with chapter_prefix
                    prefix_candidates = []
                    for paths in by_basename.values():
                        for p in paths:
                            basefn = os.path.basename(p)
                            if basefn.startswith(chapter_prefix):
                                if ext_hint is None or basefn.lower().endswith('.' + ext_hint):
                                    prefix_candidates.append(p)
                    if len(prefix_candidates) == 1:
                        replacement = prefix_candidates[0]
                        reason = 'missing->file (by chapter prefix)'
                    elif len(prefix_candidates) > 1:
                        # Prefer those under the intended part directory
                        part_pref = [p for p in prefix_candidates if to_posix(p).startswith(f"examples/{part_dir}/")]
                        pool = part_pref if part_pref else prefix_candidates
                        pool.sort(key=len)
                        replacement = pool[0]
                        reason = 'missing->file (by chapter prefix shortest)'
                else:
                    # Special-case: 未编号章 directory links -> append filename from link text if any
                    if rel_posix.startswith('examples/第0篇/第0篇-未编号章'):
                        base2 = extract_basename_from_text(text)
                        if base2:
                            candidate = f"examples/第0篇/第0篇-未编号章/{base2}"
                            replacement = candidate
                            reason = 'missing->file (append basename under 未编号章)'

        if replacement and replacement != rel_posix:
            # Replace only the URL part inside the matched markdown link
            start, end = m.span(2)
            start += offset
            end += offset
            new_content = new_content[:start] + replacement + new_content[end:]
            delta = len(replacement) - (end - start)
            offset += delta
            updates.append(LinkUpdate(original=rel_posix, updated=replacement, line_no=line_no_for(m.start()), reason=reason))
        else:
            # Couldn't resolve, track unresolved when the current target is not a file
            if not os.path.isfile(abs_target):
                unresolved += 1
                if len(unresolved_samples) < 20:
                    unresolved_samples.append((line_no_for(m.start()), text, rel_posix))

    if updates:
        with open(BOOK_PATH, 'w', encoding='utf-8', newline='\n') as f:
            f.write(new_content)

    # Summary
    print('Update links from examples summary:')
    print(f'  checked links: {checked}')
    print(f'  updated links: {len(updates)}')
    print(f'  unresolved (non-file) links: {unresolved}')
    if unresolved_samples:
        print('  unresolved samples:')
        for ln, t, p in unresolved_samples:
            print(f'    line {ln}: [{t}]({p})')
    # Optional: print a few sample updates
    for u in updates[:10]:
        print(f"  line {u.line_no}: {u.reason}: {u.original} -> {u.updated}")

    return 0


if __name__ == '__main__':
    sys.exit(update_book_links())
