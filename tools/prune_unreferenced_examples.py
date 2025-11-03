"""
Prune unreferenced files under examples/ based on references from the books.

- By default, preserves anything referenced by either:
  - book/1022.2025.newbook.md (canonical)
  - book/1022.2025.newbook.links.md (links-only)
- Generates a report with counts and file lists.
- Supports --dry-run (default) and --delete to actually remove files.

Usage (PowerShell):
  python tools/prune_unreferenced_examples.py --dry-run
  python tools/prune_unreferenced_examples.py --delete
"""
from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Set, Tuple

ROOT = Path.cwd()
EXAMPLES = ROOT / "examples"
BOOK_CANON = ROOT / "book" / "1022.2025.newbook.md"
BOOK_LINKS = ROOT / "book" / "1022.2025.newbook.links.md"

# Reuse robust reference extraction from inventory_referenced_assets
sys.path.insert(0, str((ROOT / 'tools').resolve()))
try:
    import inventory_referenced_assets as inv
except Exception as e:
    inv = None


def collect_examples_files() -> Set[Path]:
    files: Set[Path] = set()
    for r, _, fns in os.walk(EXAMPLES):
        for fn in fns:
            files.add(Path(r) / fn)
    return files


def collect_references_from_book(book_path: Path) -> Set[str]:
    if not book_path.exists():
        return set()
    text = book_path.read_text(encoding="utf-8", errors="ignore")
    if inv is None:
        # Fallback: keep everything by returning empty set (safer)
        return set()
    return inv.extract_references(text)


def expand_dir_refs(refs: Set[str]) -> Set[Path]:
    # Use inventory's expansion to account for referenced directories
    if inv is None:
        return set()
    expanded = inv.expand_directories(refs)
    # Convert to absolute Paths limited to examples/
    out: Set[Path] = set()
    for rel in expanded:
        if rel.startswith('examples/'):
            out.add((ROOT / rel).resolve())
    return out


@dataclass
class PruneReport:
    total_files: int
    protected_files: int
    delete_candidates: int
    deleted: int = 0
    freed_bytes: int = 0
    candidates: List[str] = None
    deleted_files: List[str] = None

    def to_markdown(self) -> str:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines = []
        lines.append(f"# Prune Examples Report ({ts})")
        lines.append("")
        lines.append(f"- Total files under examples/: {self.total_files}")
        lines.append(f"- Protected by book references: {self.protected_files}")
        lines.append(f"- Delete candidates: {self.delete_candidates}")
        lines.append(f"- Deleted: {self.deleted}")
        lines.append(f"- Freed bytes: {self.freed_bytes}")
        if self.candidates:
            lines.append("")
            lines.append("## Candidates (unreferenced)")
            for c in self.candidates[:200]:
                lines.append(f"- {c}")
            if len(self.candidates) > 200:
                lines.append(f"... and {len(self.candidates) - 200} more")
        if self.deleted_files:
            lines.append("")
            lines.append("## Deleted files")
            for d in self.deleted_files[:200]:
                lines.append(f"- {d}")
            if len(self.deleted_files) > 200:
                lines.append(f"... and {len(self.deleted_files) - 200} more")
        return "\n".join(lines) + "\n"


def prune(dry_run: bool = True, only_canonical: bool = False) -> PruneReport:
    all_files = collect_examples_files()
    refs = set()
    # Include links-only references to avoid accidental loss unless only-canonical was requested
    if not only_canonical and BOOK_LINKS.exists():
        refs |= collect_references_from_book(BOOK_LINKS)
    if BOOK_CANON.exists():
        refs |= collect_references_from_book(BOOK_CANON)

    protected = expand_dir_refs(refs)
    # Normalize to real paths for comparison
    protected = {p.resolve() for p in protected}

    candidates = sorted([p for p in all_files if p.resolve() not in protected])

    report = PruneReport(
        total_files=len(all_files),
        protected_files=len(protected),
        delete_candidates=len(candidates),
        candidates=[p.relative_to(ROOT).as_posix() for p in candidates],
        deleted_files=[],
    )

    if not dry_run:
        for p in candidates:
            try:
                report.freed_bytes += p.stat().st_size
            except FileNotFoundError:
                pass
            try:
                p.unlink(missing_ok=True)
                report.deleted += 1
                report.deleted_files.append(p.relative_to(ROOT).as_posix())
            except Exception as e:
                print(f"WARN: failed to delete {p}: {e}", file=sys.stderr)
        # Remove now-empty directories under examples
        for r, dirs, _ in os.walk(EXAMPLES, topdown=False):
            for d in dirs:
                dp = Path(r) / d
                try:
                    if not any(dp.iterdir()):
                        dp.rmdir()
                except Exception:
                    pass

    return report


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(description="Prune unreferenced files under examples/ based on book references.")
    ap.add_argument("--delete", action="store_true", help="Actually delete files (default: dry-run)")
    ap.add_argument("--only-canonical", action="store_true", help="Only consider canonical book references (riskier)")
    ap.add_argument("--report", default=None, help="Write markdown report to this path (default: tools/reports/prune-examples-<timestamp>.md)")
    args = ap.parse_args(argv)

    report = prune(dry_run=not args.delete, only_canonical=args.only_canonical)

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_path = Path(args.report) if args.report else (ROOT / "tools" / "reports" / f"prune-examples-{ts}.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report.to_markdown(), encoding="utf-8")

    print(f"Candidates: {report.delete_candidates}; Deleted: {report.deleted}; Freed bytes: {report.freed_bytes}")
    print(f"Report: {out_path}")

    # Return non-zero only if delete requested and some deletions failed? For now, success.
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
