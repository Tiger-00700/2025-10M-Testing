"""
Prepare candidate archive-pattern fixes for chapter/*.md files.

Rules applied conservatively:
  - Ensure first non-empty line is exactly: <!-- markdownlint-disable MD025 -->
  - Normalize archived-content markers to a single pair per file:
      <!-- archived-content:start -->
      ... (entire original body) ...
      <!-- archived-content:end -->
    All existing archived-content start/end markers (commented or bare) are
    removed before wrapping, to avoid nesting or duplicates.

Outputs candidate files next to originals as
  chapter/<stem>.archivefix.candidate.md

Writes a timestamped summary report to tools/reports/.
Never overwrites originals; safe for review.
"""
from __future__ import annotations

import datetime as dt
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHAPTER_DIR = ROOT / "chapter"
REPORTS = ROOT / "tools" / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)

MD025_REQ = "<!-- markdownlint-disable MD025 -->"

START_PATTERNS = (
    re.compile(r"^\s*<!--\s*archived-content:(?:start|begin)\s*-->\s*$", re.IGNORECASE),
    re.compile(r"^\s*archived-content:(?:start|begin)\s*$", re.IGNORECASE),
)
END_PATTERNS = (
    re.compile(r"^\s*<!--\s*archived-content:end\s*-->\s*$", re.IGNORECASE),
    re.compile(r"^\s*archived-content:end\s*$", re.IGNORECASE),
)

BARE_MD025 = re.compile(r"^\s*markdownlint-disable\s+MD025\s*$", re.IGNORECASE)


def first_non_empty_index(lines: list[str]) -> int | None:
    for i, ln in enumerate(lines):
        if ln.strip():
            return i
    return None


def strip_existing_archive_markers(lines: list[str]) -> list[str]:
    out: list[str] = []
    for ln in lines:
        s = ln.rstrip("\n").rstrip("\r")
        if any(pat.match(s) for pat in START_PATTERNS):
            continue
        if any(pat.match(s) for pat in END_PATTERNS):
            continue
        out.append(ln)
    return out


def normalize_md025_and_wrap(text: str) -> tuple[str, dict[str, bool]]:
    lines = text.splitlines()
    changed = {
        "added_md025": False,
        "normalized_md025": False,
        "wrapped_archive": False,
        "removed_existing_markers": False,
    }

    # Drop any leading bare MD025 or duplicate occurrences; keep body separately
    # Also remove exact MD025_REQ if not at the first non-empty line later
    # We'll rebuild the header and archive block from scratch

    # Remove all MD025 variants
    body_lines: list[str] = []
    md025_seen = False
    for ln in lines:
        s = ln.strip()
        if s == MD025_REQ or BARE_MD025.match(s):
            md025_seen = True
            continue
        body_lines.append(ln)
    if md025_seen:
        changed["normalized_md025"] = True

    # Remove any existing archived markers from body
    stripped = strip_existing_archive_markers(body_lines)
    if len(stripped) != len(body_lines):
        changed["removed_existing_markers"] = True

    # Build output: MD025 header + single archive block around full body
    out_lines: list[str] = []
    out_lines.append(MD025_REQ)
    out_lines.append("")
    out_lines.append("<!-- archived-content:start -->")
    # Preserve original body as-is (without previous markers/MD025 lines)
    # Ensure trailing newline handling by joining with \n later
    out_lines.extend(stripped)
    out_lines.append("<!-- archived-content:end -->")
    changed["wrapped_archive"] = True

    return "\n".join(out_lines) + "\n", changed


def main() -> int:
    chapters = sorted(CHAPTER_DIR.glob("*.md"))
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    report = REPORTS / f"chapter_archive_fix_candidates_{ts}.txt"

    total = 0
    wrote = 0
    with report.open("w", encoding="utf-8") as rep:
        rep.write(f"Prepare archive fix candidates @ {ts}\n")
        rep.write(f"Chapters: {len(chapters)}\n\n")

        for ch in chapters:
            total += 1
            text = ch.read_text(encoding="utf-8", errors="ignore")
            fixed, changed = normalize_md025_and_wrap(text)

            # Only write candidate if there is any difference
            if fixed != (text if text.endswith("\n") else text + "\n"):
                candidate = ch.with_name(ch.stem + ".archivefix.candidate.md")
                candidate.write_text(fixed, encoding="utf-8")
                wrote += 1
                rep.write(
                    f"{ch.relative_to(ROOT)} -> {candidate.name} "
                    f"[added_md025={changed['added_md025']},"
                    f" normalized_md025={changed['normalized_md025']},"
                    f" removed_markers={changed['removed_existing_markers']},"
                    f" wrapped_archive={changed['wrapped_archive']}]\n"
                )
            else:
                rep.write(f"{ch.relative_to(ROOT)} -> NO_CHANGE\n")

        rep.write("\nSummary:\n")
        rep.write(f"  Candidates written: {wrote}/{total}\n")

    print(f"REPORT: {report}")
    print(f"CANDIDATES_WRITTEN: {wrote}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
