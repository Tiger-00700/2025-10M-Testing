from pathlib import Path
import re
import shutil

repo = Path(__file__).resolve().parents[2]
book = repo / "book/1208.2025.newbook.md"
chapter_dir = repo / "chapter"

if not book.exists():
    raise SystemExit(f"book file not found: {book}")

# Clean existing chapter directory
if chapter_dir.exists():
    for p in list(chapter_dir.iterdir()):
        if p.is_file():
            p.unlink()
        else:
            shutil.rmtree(p)
else:
    chapter_dir.mkdir(parents=True, exist_ok=True)

lines = book.read_text(encoding="utf-8").splitlines()
part = 0
blocks = []
current = None

for line in lines:
    if line.startswith("## 第") and "篇" in line:
        part += 1
    m = re.match(r"### 第(\d+)章\s+(.+)", line)
    if m:
        if current:
            blocks.append(current)
        title_full = m.group(2).strip()
        title_clean = re.sub(r"【.*?】", "", title_full).strip()
        safe_title = title_clean.replace("/", "／")
        current = {
            "part": part,
            "chapter": int(m.group(1)),
            "safe_title": safe_title,
            "lines": [line + "\n"],
        }
        continue
    if current:
        current["lines"].append(line + "\n")

if current:
    blocks.append(current)

for b in blocks:
    fname = f"第{b['part']}篇-第{b['chapter']}章-{b['safe_title']}.md"
    (chapter_dir / fname).write_text("".join(b["lines"]), encoding="utf-8")

print(f"wrote {len(blocks)} chapters to {chapter_dir}")
