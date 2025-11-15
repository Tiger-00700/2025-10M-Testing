"""
Safely fix Markdown links that point to "examples/..." from files under
"book/" or "chapter/" by rewriting them to "../examples/..." so that they
resolve correctly relative to those folders.

Features:
- Parses only Markdown link targets (images and links), preserving titles and anchors
- Skips external links and in-document anchors
- Dry-run mode to preview changes without writing files
- Writes a timestamped summary report to tools/reports/

Usage:
  python tools/fix_examples_links_relative.py --dry-run
  python tools/fix_examples_links_relative.py --apply

Optional:
  python tools/fix_examples_links_relative.py --sources book/*.md chapter/*.md
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path
from typing import Iterable, List, Tuple


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "tools" / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)


# ![alt](target "title") or [text](target "title")
LINK_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)|\[[^\]]*\]\(([^)]+)\)")


def _is_external(url: str) -> bool:
    u = url.strip()
    if not u:
        return True
    u_lower = u.lower()
    return (
        u_lower.startswith("http://")
        or u_lower.startswith("https://")
        or u_lower.startswith("mailto:")
        or u_lower.startswith("javascript:")
        or u_lower.startswith("#")
    )


def _split_target_and_title(raw: str) -> Tuple[str, str]:
    s = raw.strip()
    if not s:
        return s, ""
    if s.startswith("<") and s.endswith(">"):
        return s[1:-1].strip(), ""
    # If quoted URL, keep the rest (title) as-is
    if s.startswith("\"") or s.startswith("'"):
        m = re.match(r'^(\"[^\"]*\"|\'[^\']*\')(\s+.*)?$', s)
        if m:
            url = m.group(1).strip().strip('"\'')
            title = (m.group(2) or "").lstrip()
            return url, title
    # Unquoted: first whitespace separates URL and optional title
    parts = s.split(None, 1)
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], parts[1]


def _strip_anchor(url: str) -> Tuple[str, str]:
    if url.startswith('#'):
        return url, ""
    if '#' in url:
        base, frag = url.split('#', 1)
        return base, '#' + frag
    return url, ""


def _gather_markdown_files(patterns: Iterable[str]) -> List[Path]:
    files: List[Path] = []
    for pat in patterns:
        files.extend(sorted(ROOT.glob(pat)))
    # unique files only
    seen = set()
    result: List[Path] = []
    for p in files:
        if p.is_file() and p not in seen:
            seen.add(p)
            result.append(p)
    return result


def _rewrite_target(md_path: Path, target: str) -> Tuple[bool, str]:
    # Only rewrite if file is under book/ or chapter/ and target starts with examples/
    try:
        rel = md_path.relative_to(ROOT)
    except ValueError:
        return False, target
    top = rel.parts[0] if rel.parts else ""
    if top not in {"book", "chapter"}:
        return False, target
    if target.startswith("examples/"):
        return True, "../" + target
    return False, target


def process_file(md_path: Path) -> Tuple[int, int, str]:
    text = md_path.read_text(encoding="utf-8", errors="ignore")
    out = []
    idx = 0
    changed = 0
    matches = list(LINK_RE.finditer(text))
    for m in matches:
        out.append(text[idx:m.start()])
        raw = m.group(1) if m.group(1) is not None else m.group(2)
        if raw is None:
            out.append(m.group(0))
            idx = m.end()
            continue
        url, title = _split_target_and_title(raw)
        if _is_external(url):
            out.append(m.group(0))
            idx = m.end()
            continue
        base_url, anchor = _strip_anchor(url)
        if base_url.startswith('#'):
            out.append(m.group(0))
            idx = m.end()
            continue
        do_rewrite, new_base = _rewrite_target(md_path, base_url)
        if do_rewrite:
            changed += 1
            new_target = new_base + anchor
            # Reassemble raw with title if present
            new_raw = new_target if not title else f"{new_target} {title}"
            # Rebuild original link text: we don't know alt/text; use original prefix/suffix
            prefix = text[m.start():m.start()+1]  # '!' or '['
            # We need the full original, but simpler is to replace inside (...)
            original = m.group(0)
            new = re.sub(r"\(([^)]*)\)", f"({new_raw})", original, count=1)
            out.append(new)
        else:
            out.append(m.group(0))
        idx = m.end()
    out.append(text[idx:])
    new_text = "".join(out)
    return len(matches), changed, new_text


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", nargs="*", default=["book/*.md", "chapter/*.md"], help="Glob patterns for Markdown sources (relative to repo root)")
    ap.add_argument("--dry-run", action="store_true", help="Preview changes without writing files")
    ap.add_argument("--apply", action="store_true", help="Apply changes to files")
    args = ap.parse_args(argv)

    if not args.dry_run and not args.apply:
        # Default to dry-run for safety
        args.dry_run = True

    sources = _gather_markdown_files(args.sources)
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    report = REPORTS / f"examples_links_fix_{ts}.txt"

    total_links = 0
    total_changed = 0
    changed_files: List[Tuple[Path, int]] = []

    with report.open("w", encoding="utf-8") as rep:
        rep.write(f"Examples links fix report @ {ts}\n")
        rep.write(f"Sources: {len(sources)} files\n")
        rep.write(f"Mode: {'DRY-RUN' if args.dry_run and not args.apply else 'APPLY'}\n\n")

        for md in sources:
            links, changed, new_text = process_file(md)
            total_links += links
            if changed:
                total_changed += changed
                changed_files.append((md, changed))
                rep.write(f"CHANGED({changed}): {md.relative_to(ROOT)}\n")
                if args.apply:
                    md.write_text(new_text, encoding="utf-8")

        rep.write("\nSummary:\n")
        rep.write(f"  Total links scanned: {total_links}\n")
        rep.write(f"  Files changed: {len(changed_files)}\n")
        rep.write(f"  Links rewritten: {total_changed}\n")

    print(f"REPORT: {report}")
    print(f"FILES_CHANGED: {len(changed_files)}")
    print(f"LINKS_REWRITTEN: {total_changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
