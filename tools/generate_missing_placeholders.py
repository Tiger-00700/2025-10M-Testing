"""
Generate placeholder files for missing locally referenced assets in Markdown.

Safety constraints:
- Only create files under whitelisted roots: examples/, appendix/
- Types supported: scripts, attachments (images and other are skipped by default)
- Dry-run by default; use --apply to actually write files

Placeholders strategy:
- scripts: create minimal language-appropriate comment banner
- attachments (text-like): small text note inside; (binary-like: create zero-byte)

Usage:
  python tools/generate_missing_placeholders.py --dry-run
  python tools/generate_missing_placeholders.py --apply --types scripts attachments
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "tools" / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)

LINK_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)|\[[^\]]*\]\(([^)]+)\)")

IMG_EXT = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp"}
ATT_EXT = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".csv", ".zip", ".tar", ".gz", ".json", ".yaml", ".yml", ".txt", ".md"}
CODE_EXT = {".py", ".sh", ".ps1", ".bat", ".sql", ".java", ".scala", ".js", ".ts", ".go", ".rb", ".rs", ".c", ".cpp", ".h", ".cs", ".kt", ".psm1", ".tf"}

ALLOWED_ROOTS = {ROOT / "examples", ROOT / "appendix"}


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


def _strip_title(url: str) -> str:
    s = url.strip()
    if not s:
        return s
    if s.startswith("<") and s.endswith(">"):
        return s[1:-1].strip()
    if s.startswith("\"") or s.startswith("'"):
        import re as _re
        m = _re.match(r"^([\"\'])(.*?)(\1)", s)
        if m:
            return m.group(2)
    return s.split()[0]


def _strip_anchor(url: str) -> str:
    if url.startswith('#'):
        return url
    if '#' in url:
        return url.split('#', 1)[0]
    return url


def _gather_markdown_files(patterns: Iterable[str]) -> List[Path]:
    files: List[Path] = []
    for pat in patterns:
        files.extend(sorted(ROOT.glob(pat)))
    seen = set()
    result: List[Path] = []
    for p in files:
        if p.is_file() and p not in seen:
            seen.add(p)
            result.append(p)
    return result


def _resolve_ref(base: Path, ref: str) -> Path:
    return (base.parent / ref).resolve()


def _type_of(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in CODE_EXT:
        return "scripts"
    if ext in ATT_EXT:
        return "attachments"
    if ext in IMG_EXT:
        return "images"
    return "other"


def _is_under_allowed_roots(path: Path, extra: List[Path] | None = None) -> bool:
    try:
        path = path.resolve()
    except Exception:
        return False
    if not str(path).startswith(str(ROOT)):
        return False
    bases = list(ALLOWED_ROOTS)
    if extra:
        bases.extend(extra)
    for base in bases:
        try:
            path.relative_to(base)
            return True
        except ValueError:
            continue
    return False


def _placeholder_text(ext: str) -> str:
    ts = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    note = f"Placeholder asset generated on {ts}. Replace with real content.\n"
    if ext in {".py"}:
        return f"# {note}"
    if ext in {".sh"}:
        return f"#!/usr/bin/env bash\n# {note}"
    if ext in {".ps1", ".psm1"}:
        return f"# {note}"
    if ext in {".bat"}:
        return f"@echo off\r\nREM {note}"
    if ext in {".sql"}:
        return f"-- {note}"
    if ext in {".js", ".ts", ".java", ".scala", ".go", ".rb", ".rs", ".c", ".cpp", ".h", ".cs", ".kt", ".tf"}:
        return f"// {note}"
    # text-like attachments
    if ext in {".txt", ".md", ".csv", ".json", ".yaml", ".yml"}:
        return note
    # default text note
    return note


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", nargs="*", default=["book/*.md", "chapter/*.md"], help="Glob patterns (relative to repo root)")
    ap.add_argument("--types", nargs="*", default=["scripts", "attachments"], choices=["scripts", "attachments", "images", "other"], help="Asset types to generate placeholders for")
    ap.add_argument("--allow-roots", nargs="*", default=[], help="Extra allowed roots (relative to repo root), e.g., examples/99_book_exports")
    ap.add_argument("--apply", action="store_true", help="Write placeholders to disk")
    ap.add_argument("--limit", type=int, default=10000, help="Maximum placeholders to consider (safety)")
    args = ap.parse_args(argv)

    sources = _gather_markdown_files(args.sources)
    extra_roots: List[Path] = []
    for r in args.allow_roots:
        p = (ROOT / r).resolve()
        if p.exists() or True:
            extra_roots.append(p)
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    report = REPORTS / f"placeholders_plan_{ts}.txt"

    planned: List[Tuple[Path, Path, str]] = []  # (md, target_path, type)

    for md in sources:
        text = md.read_text(encoding="utf-8", errors="ignore")
        for m in LINK_RE.finditer(text):
            raw = m.group(1) if m.group(1) is not None else m.group(2)
            if raw is None:
                continue
            url = _strip_title(raw)
            if _is_external(url):
                continue
            url2 = _strip_anchor(url)
            if not url2 or url2.startswith('#'):
                continue
            target = _resolve_ref(md, url2)
            if target.exists():
                continue
            t = _type_of(target)
            if t not in args.types:
                continue
            if not _is_under_allowed_roots(target, extra_roots):
                continue
            planned.append((md, target, t))

    # de-duplicate targets while preserving an example source
    unique: Dict[Path, Tuple[Path, str]] = {}
    for md, tgt, t in planned:
        if tgt not in unique:
            unique[tgt] = (md, t)

    items = list(unique.items())[: args.limit]

    created = 0
    with report.open("w", encoding="utf-8") as rep:
        rep.write(f"Placeholder generation plan @ {ts}\n")
        rep.write(f"Apply: {args.apply}\n")
        rep.write(f"Types: {', '.join(args.types)}\n")
        if extra_roots:
            rep.write("Extra roots:\n")
            for er in extra_roots:
                rep.write(f"  - {er}\n")
        rep.write(f"Planned unique targets: {len(unique)} (limited to {len(items)})\n\n")
        for tgt, (md, t) in items:
            rel = tgt.relative_to(ROOT)
            rep.write(f"[{t}] {rel}  (referenced from {md.relative_to(ROOT)})\n")
            if args.apply:
                tgt.parent.mkdir(parents=True, exist_ok=True)
                ext = tgt.suffix.lower()
                # Binary-like attachments: create zero-byte file
                if t == "attachments" and ext in {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".zip", ".tar", ".gz"}:
                    tgt.touch(exist_ok=True)
                else:
                    content = _placeholder_text(ext)
                    # Use utf-8 for text
                    tgt.write_text(content, encoding="utf-8")
                created += 1

    print(f"REPORT: {report}")
    print(f"PLANNED: {len(items)}; CREATED: {created}")
    return 0


if __name__ == "__main__":
    import sys as _sys
    raise SystemExit(main(_sys.argv[1:]))
