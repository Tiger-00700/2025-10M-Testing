"""Extract fenced code blocks from chapter files in chapter/第5篇-*.md
and write them into examples/第5篇/ as individual files.

Usage: python tools/extract_chapter_codeblocks_to_examples.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAPTER_GLOB = ROOT / 'chapter' / '第5篇-*.md'
OUT_DIR = ROOT / 'examples' / '第5篇'
OUT_DIR.mkdir(parents=True, exist_ok=True)

code_fence_re = re.compile(r"```(\w+)?\n(.*?)\n```", re.DOTALL)
chapter_files = list(Path(ROOT / 'chapter').glob('第5篇-*.md'))
summary = []
for chap in chapter_files:
    text = chap.read_text(encoding='utf-8')
    matches = list(code_fence_re.finditer(text))
    if not matches:
        continue
    # derive chapter number
    m = re.search(r'第(\d+)章', chap.name)
    chapnum = m.group(1) if m else chap.stem
    counter = 1
    for i, match in enumerate(matches, start=1):
        lang = match.group(1) or 'txt'
        code = match.group(2).rstrip() + '\n'
        ext = lang
        # sanitize ext
        ext = 'py' if ext == 'python' else ext
        # create filename
        fname = f"{chapnum:0>2}-{counter:03}__block.{ext}" if isinstance(chapnum, str) else f"{chapnum}-{counter:03}__block.{ext}"
        outpath = OUT_DIR / fname
        # avoid overwriting existing: append suffix if exists
        suffix = 1
        while outpath.exists():
            outpath = OUT_DIR / f"{fname[:-len(ext)-1]}-{suffix}.{ext}"
            suffix += 1
        outpath.write_text(code, encoding='utf-8')
        summary.append((chap.name, outpath.name, outpath.stat().st_size))
        counter += 1

# write a summary file
report = OUT_DIR / 'extraction_report.txt'
with report.open('w', encoding='utf-8') as f:
    for chapname, fname, size in summary:
        f.write(f"{chapname} -> {fname} ({size} bytes)\n")

print(f"Extracted {len(summary)} code blocks to {OUT_DIR}")
print(f"Wrote report: {report}")
