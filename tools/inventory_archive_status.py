"""
Validate archive pattern compliance for chapter/*.md files.

Policy (from project conventions):
  - All chapter/*.md files must start with `<!-- markdownlint-disable MD025 -->`.
  - Legacy content must be wrapped inside a single archived-content block.
    Start marker may be one of:
      * <!-- archived-content:start -->
      * <!-- archived-content:begin -->
      * archived-content:start (bare)
    End marker may be one of:
      * <!-- archived-content:end -->
      * archived-content:end (bare)

Writes a timestamped report under tools/reports/ and exits non-zero if
violations are detected.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path
from typing import List, Tuple, Iterable


ROOT = Path(__file__).resolve().parents[1]
CHAPTER_DIR = ROOT / "chapter"
REPORTS = ROOT / "tools" / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)


MD025_REQUIRED = "<!-- markdownlint-disable MD025 -->"

START_PATTERNS = (
    re.compile(r"<!--\s*archived-content:(?:start|begin)\s*-->\s*", re.IGNORECASE),
    re.compile(r"^\s*archived-content:(?:start|begin)\s*$", re.IGNORECASE | re.MULTILINE),
)

END_PATTERNS = (
    re.compile(r"<!--\s*archived-content:end\s*-->\s*", re.IGNORECASE),
    re.compile(r"^\s*archived-content:end\s*$", re.IGNORECASE | re.MULTILINE),
)


def _first_non_empty_line(text: str) -> str:
    for line in text.splitlines():
        if line.strip():
            return line.strip()
    return ""


def _count_matches(text: str, patterns: Tuple[re.Pattern, ...]) -> int:
    count = 0
    for pat in patterns:
        count += len(list(pat.finditer(text)))
    return count


def _gather_files(patterns: Iterable[str]) -> List[Path]:
    files: List[Path] = []
    for pat in patterns:
        files.extend(sorted(ROOT.glob(pat)))
    # unique
    seen = set()
    result: List[Path] = []
    for p in files:
        if p.is_file() and p not in seen:
            seen.add(p)
            result.append(p)
    return result


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--sources",
        nargs="*",
        default=["chapter/*.md"],
        help="Glob patterns (relative to repo root) for Markdown sources",
    )
    args = ap.parse_args(argv)

    chapters: List[Path] = _gather_files(args.sources)
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = REPORTS / f"archive_status_{ts}.txt"

    violations: List[Tuple[Path, str]] = []

    with report_path.open("w", encoding="utf-8") as rep:
        rep.write(f"Archive status report @ {ts}\n")
        rep.write(f"Chapters found: {len(chapters)}\n\n")

        for ch in chapters:
            text = ch.read_text(encoding="utf-8", errors="ignore")
            head = _first_non_empty_line(text)
            start_count = _count_matches(text, START_PATTERNS)
            end_count = _count_matches(text, END_PATTERNS)

            ok_head = (head == MD025_REQUIRED)
            ok_blocks = (start_count == 1 and end_count == 1)

            status = []
            if ok_head:
                status.append("MD025_OK")
            else:
                status.append("MD025_MISSING")
                violations.append((ch, "Missing required MD025 disable at top"))

            if ok_blocks:
                status.append("ARCHIVE_BLOCK_OK")
            else:
                status.append(f"ARCHIVE_BLOCK_INVALID(start:{start_count},end:{end_count})")
                violations.append((ch, f"Invalid archived-content block count (start:{start_count}, end:{end_count})"))

            rep.write(f"{ch.relative_to(ROOT)} :: {';'.join(status)}\n")

        rep.write("\nSummary:\n")
        rep.write(f"  Violations: {len(violations)}\n")
        if violations:
            rep.write("\nViolation details:\n")
            for path, msg in violations:
                rep.write(f"  - {path.relative_to(ROOT)} :: {msg}\n")

    print(f"REPORT: {report_path}")
    print(f"VIOLATIONS: {len(violations)}")
    return 0 if not violations else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
