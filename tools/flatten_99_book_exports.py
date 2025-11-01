#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Flatten examples/99_book_exports by moving its contents one level up into examples/.
Also updates book/1022.2025.newbook.links.md to remove '99_book_exports' from links.

Behavior:
- For each file/dir under examples/99_book_exports, move to examples/<subpath>.
- If a destination path already exists, the script will skip that entry and report it.
- After a successful move of all entries, remove the now-empty examples/99_book_exports directory if empty.
- Update book/1022.2025.newbook.links.md by replacing 'examples/99_book_exports/' with 'examples/'.

Idempotent:
- If nothing to move, does nothing.
- Link rewrite is a safe no-op if already flattened.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = REPO_ROOT / "examples"
EXPORTS = EXAMPLES / "99_book_exports"
LINKS_BOOK = REPO_ROOT / "book" / "1022.2025.newbook.links.md"


def move_contents() -> dict:
    summary = {"moved": 0, "skipped": 0, "errors": 0}
    if not EXPORTS.exists():
        return summary

    # Move top-level entries under 99_book_exports to examples/
    for entry in sorted(EXPORTS.iterdir()):
        dest = EXAMPLES / entry.name
        try:
            if dest.exists():
                # If both are directories, try to merge tree (non-destructive):
                if entry.is_dir() and dest.is_dir():
                    for root, dirs, files in os.walk(entry):
                        rel_root = Path(root).relative_to(EXPORTS)
                        target_root = EXAMPLES / rel_root
                        target_root.mkdir(parents=True, exist_ok=True)
                        for d in dirs:
                            (target_root / d).mkdir(parents=True, exist_ok=True)
                        for f in files:
                            src_f = Path(root) / f
                            dst_f = target_root / f
                            if dst_f.exists():
                                summary["skipped"] += 1
                                continue
                            shutil.move(str(src_f), str(dst_f))
                            summary["moved"] += 1
                    # After merging, remove the now empty dir
                    try:
                        shutil.rmtree(entry)
                    except Exception:
                        pass
                    continue
                # Otherwise skip to avoid overwriting
                summary["skipped"] += 1
                continue

            shutil.move(str(entry), str(dest))
            summary["moved"] += 1
        except Exception:
            summary["errors"] += 1

    # Try to remove the exports dir if empty
    try:
        # If it's empty, rmdir succeeds; else ignore
        EXPORTS.rmdir()
    except OSError:
        # Not empty or other error — ignore
        pass

    return summary


def rewrite_links() -> dict:
    summary = {"updated": 0, "unchanged": 0}
    if not LINKS_BOOK.exists():
        return summary
    text = LINKS_BOOK.read_text(encoding="utf-8")
    occurrences = text.count("examples/99_book_exports/")
    new_text = text.replace("examples/99_book_exports/", "examples/")
    if occurrences:
        LINKS_BOOK.write_text(new_text, encoding="utf-8", newline="\n")
        summary["updated"] = occurrences
    else:
        summary["unchanged"] = 1
    return summary


def main():
    moves = move_contents()
    links = rewrite_links()
    print("Flatten 99_book_exports summary:")
    print(f"  moved:   {moves['moved']}")
    print(f"  skipped: {moves['skipped']}")
    print(f"  errors:  {moves['errors']}")
    if links.get("updated", 0):
        print(f"  links updated: {links['updated']}")
    else:
        print("  links unchanged")


if __name__ == "__main__":
    main()
