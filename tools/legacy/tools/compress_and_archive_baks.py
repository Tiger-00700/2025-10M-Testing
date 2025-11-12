"""Compress all *.bak files into tools/reports/bak_backup-<timestamp>.zip
and then remove the original .bak files. Also write a manifest file listing
the archived files. Safe operation: creates tools/reports if missing.

Run from repo root with the project's Python.
"""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import datetime
import sys

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "tools" / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)

timestamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
archive_path = REPORTS / f"bak_backup-{timestamp}.zip"
manifest_path = REPORTS / f"bak_backup-{timestamp}.manifest.txt"

bak_files = sorted([p for p in ROOT.rglob("*.bak") if p.is_file()])
if not bak_files:
    print("No .bak files found. Nothing to do.")
    sys.exit(0)

with ZipFile(archive_path, "w", compression=ZIP_DEFLATED) as zf:
    for p in bak_files:
        # store relative paths in the archive
        rel = p.relative_to(ROOT)
        zf.write(p, arcname=str(rel))

with manifest_path.open("w", encoding="utf-8") as mf:
    for p in bak_files:
        mf.write(str(p.relative_to(ROOT)) + "\n")

print(f"Archived {len(bak_files)} .bak files to: {archive_path}")
print(f"Wrote manifest to: {manifest_path}")

# Now remove the original .bak files
removed = 0
for p in bak_files:
    try:
        p.unlink()
        removed += 1
    except Exception as e:
        print(f"Failed to remove {p}: {e}")

print(f"Removed {removed} .bak files from working tree.")

# Exit with non-zero if archive exists but no removal happened (unexpected)
if archive_path.exists() and removed == 0:
    sys.exit(2)

sys.exit(0)
