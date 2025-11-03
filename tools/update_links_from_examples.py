import argparse
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


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
BLOCK_NAME_RE = re.compile(
	r"(?P<name>\d+(?:-\d+)*__block\d+\.(?:[A-Za-z0-9]+))"
)


def find_replacement(
	link_text: str, link_url: str, examples_index: Dict[str, List[Path]], examples_root: Path
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
			# Build a repo-root relative URL with forward slashes
			rel = matches[0].relative_to(examples_root.parent).as_posix()
			return (link_text, rel)

	# Nothing better found
	return (link_text, norm_url)


def update_book_links(book_path: Path, examples_root: Path, dry_run: bool = False) -> Tuple[int, int]:
	"""Update examples links in the book based on existing files.

	Returns (checked_count, updated_count).
	"""
	examples_index = build_examples_index(examples_root)

	original = book_path.read_text(encoding="utf-8")
	lines = original.splitlines()

	checked = 0
	updated = 0
	new_lines: List[str] = []

	for line in lines:
		def _replace(match: re.Match) -> str:
			nonlocal checked, updated
			text = match.group("text")
			url = match.group("url")
			new_text, new_url = find_replacement(text, url, examples_index, examples_root)
			checked += 1 if new_url.startswith("examples/") else 0
			if new_url != url:
				updated += 1
			return f"[{new_text}]({new_url})"

		# Replace all markdown links in the line
		new_line = LINK_RE.sub(_replace, line)
		new_lines.append(new_line)

	if not dry_run and new_lines != lines:
		# Preserve Windows newlines if file appears to use CRLF
		newline = "\r\n" if "\r\n" in original else "\n"
		book_path.write_text(newline.join(new_lines) + newline, encoding="utf-8")

	return checked, updated


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

	checked, updated = update_book_links(book_path, examples_root, dry_run=args.dry_run)
	print(f"Checked links: {checked}; Updated: {updated}; Dry-run: {args.dry_run}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main(sys.argv[1:]))

