#!/usr/bin/env python3
"""
Enforce placeholder policy across examples/ to keep the repo consistent.

Rules:
- For small text files (<= max-bytes, default 2048) under examples/, ensure they contain a
  standard placeholder marker if they look like placeholders.
- Marker substring accepted (any of):
  - "Placeholder example file."
  - "Placeholder example README."
- Only checks text-like extensions: .py, .sh, .md, .txt, .yaml, .yml
- Skips files inside version control/CI folders (none expected under examples/).

Exit codes:
- 0: OK
- 1: Violations found

You can override threshold by: --max-bytes 4096
You can run in list-only mode by: --list-only (won't fail, just prints)
"""
from __future__ import annotations
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
TEXT_EXTS = {".py", ".sh", ".md", ".txt", ".yaml", ".yml"}
MARKERS = ("Placeholder example file.", "Placeholder example README.")


def is_text_like(p: Path) -> bool:
    return p.suffix.lower() in TEXT_EXTS


def looks_small(p: Path, max_bytes: int) -> bool:
    try:
        return p.stat().st_size <= max_bytes
    except FileNotFoundError:
        return False


def has_marker(p: Path) -> bool:
    try:
        content = p.read_text(encoding="utf-8")
    except Exception:
        try:
            content = p.read_text(errors="ignore")
        except Exception:
            return False
    return any(m in content for m in MARKERS)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Check placeholder policy for examples/")
    ap.add_argument("--max-bytes", type=int, default=2048, help="Max size to consider a file a placeholder candidate")
    ap.add_argument("--list-only", action="store_true", help="List violations but do not fail")
    args = ap.parse_args(argv)

    if not EXAMPLES.exists():
        print("examples/ folder not found; skipping")
        return 0

    violations: list[str] = []
    for p in EXAMPLES.rglob("*"):
        if not p.is_file():
            continue
        if not is_text_like(p):
            continue
        if looks_small(p, args.max_bytes) and not has_marker(p):
            # Likely a tiny placeholder but without marker
            rel = p.relative_to(ROOT)
            violations.append(f"{rel} (size={p.stat().st_size} bytes) missing placeholder marker")

    if violations:
        print("[PLACEHOLDER POLICY] Violations:")
        for v in violations:
            print(" -", v)
        if args.list_only:
            return 0
        return 1

    print("[PLACEHOLDER POLICY] OK: All small text files under examples/ carry placeholder markers.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
