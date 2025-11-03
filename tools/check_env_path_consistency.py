#!/usr/bin/env python3
"""
Check for consistent usage of the environment examples path in the repository.

Policy (post-rename):
- examples/03_env must NOT exist and must NOT be referenced in book/ or chapter/.
- examples/03_environment must exist.

Exit codes:
- 0: OK
- 1: Violations found
"""
from __future__ import annotations
import sys
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANNED = "examples/03_env"
REQUIRED = ROOT / "examples/03_environment"
SCAN_DIRS = [ROOT / "book", ROOT / "chapter"]


def scan_text_refs() -> list[tuple[Path, int, str]]:
    hits: list[tuple[Path, int, str]] = []
    pattern = re.compile(re.escape(BANNED))
    for base in SCAN_DIRS:
        if not base.exists():
            continue
        for p in base.rglob("*.md"):
            try:
                text = p.read_text(encoding="utf-8")
            except Exception:
                try:
                    text = p.read_text(errors="ignore")
                except Exception:
                    continue
            for i, line in enumerate(text.splitlines(), start=1):
                if pattern.search(line):
                    hits.append((p.relative_to(ROOT), i, line.strip()))
    return hits


def main() -> int:
    violations: list[str] = []

    # 1) Directory existence checks
    banned_dir = ROOT / BANNED
    if banned_dir.exists():
        violations.append(f"BANNED directory exists: {banned_dir}")

    if not REQUIRED.exists():
        violations.append(f"REQUIRED directory missing: {REQUIRED}")

    # 2) Text reference checks in book/ and chapter/
    refs = scan_text_refs()
    if refs:
        violations.append("BANNED references found in markdown files:")
        for file, line_no, line in refs:
            violations.append(f"  - {file}:{line_no}: {line}")

    if violations:
        print("[ENV PATH CONSISTENCY CHECK] Violations:")
        for v in violations:
            print(v)
        return 1

    print("[ENV PATH CONSISTENCY CHECK] OK: No 'examples/03_env' references and 'examples/03_environment' exists.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
