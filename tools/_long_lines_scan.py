import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
files = ["tools/validate_chapters_against_book.py", "tools/apply_markdown_autofixes.py"]
for fn in files:
    p = Path(fn)
    if not p.exists():
        print("MISSING", fn)
        continue
    print("\nFILE:", fn)
    for i, l in enumerate(p.read_text(encoding="utf-8").splitlines(), start=1):
        if len(l) > 88:
            print(f"{i:4d} {len(l):3d} {l[:240]}")
