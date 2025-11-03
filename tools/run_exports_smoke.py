import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
EXPORTS = ROOT / "examples" / "99_book_exports"
REPORTS = ROOT / "tools" / "reports"

def py_syntax_check(path: Path) -> tuple[bool, str]:
    try:
        import py_compile
        py_compile.compile(str(path), doraise=True)
        return True, "compiled"
    except Exception as e:
        return False, str(e)


def main():
    REPORTS.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    report = REPORTS / f"exports-smoke-{ts}.md"

    if not EXPORTS.exists():
        report.write_text("No exports folder found. Skipped.\n", encoding="utf-8")
        print(f"No exports found: {EXPORTS}")
        return

    rows = []
    total = 0
    passed = 0

    for path in EXPORTS.rglob('*'):
        if path.is_dir():
            continue
        total += 1
        status = "skipped"
        detail = ""
        if path.suffix.lower() == ".py":
            ok, msg = py_syntax_check(path)
            status = "pass" if ok else "fail"
            detail = msg
            if ok:
                passed += 1
        elif path.suffix.lower() in (".sql", ".md", ".json", ".yml", ".yaml", ".ps1", ".sh", ".bat"):
            # basic presence check only
            status = "pass"
            detail = "basic-check"
            passed += 1
        else:
            status = "skipped"
            detail = "unsupported-type"
        rows.append((str(path.relative_to(ROOT)), status, detail))

    lines = ["# Exports Smoke Report", "", f"Scanned files: {total}", f"Passed: {passed}", "", "| File | Status | Detail |", "|---|---|---|"]
    for f, s, d in rows:
        lines.append(f"| {f} | {s} | {d} |")

    report.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote exports smoke report to {report}")

if __name__ == "__main__":
    main()
