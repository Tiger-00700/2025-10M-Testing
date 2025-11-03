import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional


def build_examples_index(examples_root: Path) -> Dict[str, List[Path]]:
	"""Walk the examples directory and build an index of basename -> [paths].

	Includes files only. Basename is the filename with extension.
	"""
	index: Dict[str, List[Path]] = {}
	for root, _, files in os.walk(examples_root):
		for f in files:
			p = Path(root) / f
			basename = p.name
			index.setdefault(basename, []).append(p)
	return index


LINK_RE = re.compile(r"\[(?P<text>[^\]]+)\]\((?P<url>[^)]+)\)")
BLOCK_NAME_RE = re.compile(r"(?P<name>\d+(?:-\d+)*__block\d+\.(?:[A-Za-z0-9]+))")


def _tokens_from_path(path: str) -> List[str]:
	# Split on typical separators and keep non-empty parts
	raw = re.split(r"[\\/]+", path)
	tokens: List[str] = []
	for part in raw:
		if not part:
			continue
		# further split by -, _, space, and remove file extension dot
		sub = re.split(r"[\-_.\s]+", part)
		for s in sub:
			if s:
				tokens.append(s)
	return tokens


def _score_candidate(candidate_rel: str, hint_rel_dir: str) -> Tuple[int, int]:
	"""Score a candidate by overlap with hint dir tokens and common prefix length.

	Returns a tuple (score, common_prefix_len) for tie-breaking.
	"""
	cand_tokens = _tokens_from_path(candidate_rel)
	hint_tokens = _tokens_from_path(hint_rel_dir)

	# Basic overlap score
	overlap = len(set(cand_tokens) & set(hint_tokens))

	# Common prefix length by segments
	cand_segments = candidate_rel.split('/')
	hint_segments = hint_rel_dir.split('/')
	cpl = 0
	for a, b in zip(cand_segments, hint_segments):
		if a == b:
			cpl += 1
		else:
			break

	# Prefer deeper (more specific) paths slightly
	depth_bonus = len(cand_segments) // 10

	return overlap + cpl + depth_bonus, cpl


@dataclass
class LinkReport:
	total_links: int = 0
	examples_links_checked: int = 0
	updated: int = 0
	unchanged: int = 0
	unresolved: int = 0
	ambiguous: int = 0
	ambiguous_samples: List[Dict[str, object]] = None  # list of {text, url, candidates}

	def __post_init__(self):
		if self.ambiguous_samples is None:
			self.ambiguous_samples = []


def find_replacement(
	link_text: str,
	link_url: str,
	examples_index: Dict[str, List[Path]],
	examples_root: Path,
	report: Optional[LinkReport] = None,
	fail_on_tie: bool = True,
) -> Tuple[str, str]:
	"""Return (new_text, new_url) if a replacement is found; else return original.

	Strategy:
	- If url already points to an existing file under examples/, keep it.
	- If link_text contains a basename like `..__blockNNN.ext`, and that basename
	  resolves uniquely in examples index, rewrite url to that path (relative to repo root).
	- Otherwise, leave as-is.
	"""
	# Normalize url separators to forward slashes for markdown
	norm_url = link_url.replace("\\", "/")
	# Only process examples/ links
	if not norm_url.startswith("examples/"):
		return (link_text, link_url)

	# Check if current URL exists as a file
	current_path = (examples_root.parent / norm_url).resolve()
	if current_path.is_file():
		return (link_text, norm_url)

	# Try to extract a block filename from link text
	m = BLOCK_NAME_RE.search(link_text)
	if m:
		basename = m.group("name")
		matches = examples_index.get(basename, [])
		if len(matches) == 1:
			# Unique match
			rel = matches[0].relative_to(examples_root.parent).as_posix()
			return (link_text, rel)
		elif len(matches) > 1:
			# Use hint from current URL's directory to choose the best candidate
			hint_rel = norm_url[len("examples/") :]
			hint_dir = hint_rel if hint_rel.endswith('/') else '/'.join(hint_rel.split('/')[:-1])
			if hint_dir:
				scored: List[Tuple[int, int, Path]] = []
				for p in matches:
					rel_cand = p.relative_to(examples_root.parent).as_posix()
					score, cpl = _score_candidate(rel_cand, f"examples/{hint_dir}")
					scored.append((score, cpl, p))
				# pick best by score then common prefix; if tie exact, mark ambiguous
				scored.sort(key=lambda t: (t[0], t[1], t[2].as_posix()))
				best = scored[-1]
				# Check for tie
				ties = [s for s in scored if s[0] == best[0] and s[1] == best[1]]
				if len(ties) == 1:
					rel = best[2].relative_to(examples_root.parent).as_posix()
					return (link_text, rel)
				else:
					# ambiguous
					if report is not None:
						report.ambiguous += 1
						report.ambiguous_samples.append(
							{
								"text": link_text,
								"url": norm_url,
								"candidates": [p[2].relative_to(examples_root.parent).as_posix() for p in ties],
							}
						)
					# keep original URL if tie and failing on tie
					return (link_text, link_url)

	# Nothing better found
	# Mark unresolved if still not a file and nothing better found
	if report is not None:
		report.unresolved += 1
	return (link_text, norm_url)


def update_book_links(
	book_path: Path,
	examples_root: Path,
	dry_run: bool = False,
	fail_on_ambiguous: bool = False,
	report_json: Optional[Path] = None,
	report_md: Optional[Path] = None,
	mark_unresolved: bool = False,
	unresolved_suffix: str = "（失效）",
) -> Tuple[int, int, LinkReport]:
	"""Update examples links in the book based on existing files.

	Returns (checked_count, updated_count).
	"""
	examples_index = build_examples_index(examples_root)

	original = book_path.read_text(encoding="utf-8")
	lines = original.splitlines()

	checked = 0
	updated = 0
	report = LinkReport()
	new_lines: List[str] = []

	for line in lines:
		def _replace(match: re.Match) -> str:
			nonlocal checked, updated
			text = match.group("text")
			url = match.group("url")
			# Count only examples links in report
			if url.replace("\\", "/").startswith("examples/"):
				report.examples_links_checked += 1
			new_text, new_url = find_replacement(
				text, url, examples_index, examples_root, report=report
			)
			checked += 1 if new_url.startswith("examples/") else 0
			# If still unresolved and marking requested, annotate the link text
			if mark_unresolved and new_url.replace("\\", "/").startswith("examples/"):
				target = (examples_root.parent / new_url).resolve()
				if not target.is_file():
					new_text = f"{text}{unresolved_suffix}"
			if new_url != url:
				updated += 1
				report.updated += 1
			else:
				report.unchanged += 1
			report.total_links += 1
			return f"[{new_text}]({new_url})"

		# Replace all markdown links in the line
		new_line = LINK_RE.sub(_replace, line)
		new_lines.append(new_line)

	if not dry_run and new_lines != lines:
		# Preserve Windows newlines if file appears to use CRLF
		newline = "\r\n" if "\r\n" in original else "\n"
		book_path.write_text(newline.join(new_lines) + newline, encoding="utf-8")

	# Write reports if requested
	if report_json is not None:
		report_json.parent.mkdir(parents=True, exist_ok=True)
		report_json.write_text(json.dumps(asdict(report), ensure_ascii=False, indent=2), encoding="utf-8")
	if report_md is not None:
		report_md.parent.mkdir(parents=True, exist_ok=True)
		lines_out = []
		lines_out.append(f"# Link Check Report ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
		lines_out.append("")
		lines_out.append(f"- Total links scanned: {report.total_links}")
		lines_out.append(f"- examples/ links: {report.examples_links_checked}")
		lines_out.append(f"- Updated: {report.updated}")
		lines_out.append(f"- Unchanged: {report.unchanged}")
		lines_out.append(f"- Unresolved (still not a file): {report.unresolved}")
		lines_out.append(f"- Ambiguous (multiple candidates with tie): {report.ambiguous}")
		if report.ambiguous_samples:
			lines_out.append("")
			lines_out.append("## Ambiguous samples")
			for s in report.ambiguous_samples[:20]:
				lines_out.append(f"- {s['text']} -> {s['url']}")
				for c in s["candidates"]:
					lines_out.append(f"  - candidate: {c}")
		report_md.write_text("\n".join(lines_out) + "\n", encoding="utf-8")

	if fail_on_ambiguous and report.ambiguous > 0:
		print(f"ERROR: Ambiguous links detected: {report.ambiguous}", file=sys.stderr)
		sys.exit(4)

	return checked, updated, report


def main(argv: List[str]) -> int:
	parser = argparse.ArgumentParser(
		description="Update examples/ links in the links-only book to point to actual files under examples/."
	)
	parser.add_argument(
		"--book",
		default=str(Path("book") / "1022.2025.newbook.links.md"),
		help="Path to the links-only book markdown (default: book/1022.2025.newbook.links.md)",
	)
	parser.add_argument(
		"--examples",
		default=str(Path("examples")),
		help="Path to the examples directory (default: examples)",
	)
	parser.add_argument("--dry-run", action="store_true", help="Do not write changes, only report")
	parser.add_argument("--fail-on-ambiguous", action="store_true", help="Exit non-zero if ambiguous matches are found")
	parser.add_argument("--report-json", default=None, help="Write JSON report to this path")
	parser.add_argument("--report-md", default=None, help="Write Markdown report to this path")
	parser.add_argument("--mark-unresolved", action="store_true", help="Annotate unresolved examples links in the book text")
	parser.add_argument("--unresolved-suffix", default="（失效）", help="Suffix to append to link text when marking unresolved")

	args = parser.parse_args(argv)

	repo_root = Path.cwd()
	book_path = (repo_root / args.book).resolve()
	examples_root = (repo_root / args.examples).resolve()

	if not book_path.exists():
		print(f"Book not found: {book_path}", file=sys.stderr)
		return 2
	if not examples_root.exists():
		print(f"Examples dir not found: {examples_root}", file=sys.stderr)
		return 3

	# Default report paths if not provided and in dry-run
	report_json_path = Path(args.report_json) if args.report_json else None
	report_md_path = Path(args.report_md) if args.report_md else None
	if args.dry_run and (report_json_path is None or report_md_path is None):
		ts = datetime.now().strftime("%Y%m%d-%H%M%S")
		reports_dir = Path("tools") / "reports"
		report_json_path = report_json_path or (reports_dir / f"links-report-{ts}.json")
		report_md_path = report_md_path or (reports_dir / f"links-report-{ts}.md")

	checked, updated, rep = update_book_links(
		book_path,
		examples_root,
		dry_run=args.dry_run,
		fail_on_ambiguous=args.fail_on_ambiguous,
		report_json=report_json_path,
		report_md=report_md_path,
		mark_unresolved=args.mark_unresolved,
		unresolved_suffix=args.unresolved_suffix,
	)
	print(
		f"Checked links: {checked}; Updated: {updated}; Dry-run: {args.dry_run}; Ambiguous: {rep.ambiguous}; Unresolved: {rep.unresolved}"
	)
	return 0


if __name__ == "__main__":
	raise SystemExit(main(sys.argv[1:]))

