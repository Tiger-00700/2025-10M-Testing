#!/usr/bin/env python3
"""Add placeholder markers to small text-like example files.

Usage:
  python tools/add_placeholders.py --max-bytes 2048 --max-files 150

Behavior:
- Scans examples/ for files with extensions .py,.sh,.md,.txt,.yaml,.yml
- Skips files that already contain the official markers used by check_placeholders.py
- For each file, writes a .bak copy and then prepends a language-appropriate placeholder marker.
- Prints modified files and exits with 0.
"""
from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
TEXT_EXTS = {".py", ".sh", ".md", ".txt", ".yaml", ".yml"}
MARKERS = ("Placeholder example file.", "Placeholder example README.")

COMMENT_FOR = {
    ".py": "# Placeholder example file.",
    ".sh": "# Placeholder example file.",
    ".md": "<!-- Placeholder example README. -->",
    ".txt": "Placeholder example file.",
    ".yaml": "# Placeholder example file.",
    ".yml": "# Placeholder example file.",
}


def has_marker(p: Path) -> bool:
    try:
        s = p.read_text(encoding="utf-8")
    except Exception:
        try:
            s = p.read_text(errors="ignore")
        except Exception:
            return False
    return any(m in s for m in MARKERS)


def looks_small(p: Path, max_bytes: int) -> bool:
    try:
        return p.stat().st_size <= max_bytes
    except Exception:
        return False


def add_marker(p: Path, marker: str) -> None:
    bak = p.with_suffix(p.suffix + ".bak")
    if not bak.exists():
        try:
            p.replace(bak)
        except Exception:
            # fallback: copy content
            try:
                bak.write_bytes(p.read_bytes())
            except Exception:
                pass
    # read original content from bak to avoid double-inserting
    try:
        content = bak.read_text(encoding="utf-8")
    except Exception:
        content = bak.read_text(errors="ignore")
    new = marker + "\n" + content
    p.write_text(new, encoding="utf-8")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-bytes", type=int, default=2048)
    ap.add_argument("--max-files", type=int, default=150)
    args = ap.parse_args(argv)

    if not EXAMPLES.exists():
        print("examples/ not found; nothing to do")
        return 0

    modified = []
    count = 0
    for p in sorted(EXAMPLES.rglob("*")):
        if not p.is_file():
            continue
        if p.suffix.lower() not in TEXT_EXTS:
            continue
        rel = p.relative_to(ROOT).as_posix()
        if has_marker(p):
            continue
        if not looks_small(p, args.max_bytes):
            continue
        # choose marker
        marker = COMMENT_FOR.get(p.suffix.lower(), "Placeholder example file.")
        add_marker(p, marker)
        modified.append(rel)
        count += 1
        if count >= args.max_files:
            break

    if modified:
        print(f"Inserted placeholders into {len(modified)} files:")
        for m in modified:
            print(" -", m)
    else:
        print("No files needed modification (or none matched criteria).")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
