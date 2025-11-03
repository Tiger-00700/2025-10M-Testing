import runpy
import sys
import os
from pathlib import Path
from trace import Trace
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
EXPORTS = ROOT / "examples" / "99_book_exports"
REPORTS = ROOT / "tools" / "reports"


def main():
    REPORTS.mkdir(parents=True, exist_ok=True)
    if not EXPORTS.exists():
        print(f"No exports at {EXPORTS}")
        return

    py_files = sorted(EXPORTS.glob('newbook__block*.py'))
    tracer = Trace(count=True, trace=False, ignoremods=('trace',), ignoredirs=(str(ROOT / '.git'),))

    # Build a runner that imports each file in a fresh globals dict
    failed = []
    for f in py_files:
        try:
            # Use tracer.runctx to execute the file
            code = compile(f.read_text(encoding='utf-8'), str(f), 'exec')
            tracer.runctx(code, {"__name__": "__main__"}, {})
        except Exception as e:
            failed.append((f, str(e)))

    results = tracer.results()
    cov = results.counts  # dict of {(filename, lineno): count}

    # Summarize coverage by file for exported files
    lines = ["# Exports Coverage (trace) Report", ""]
    total_exec = 0
    total_lines = 0
    for f in py_files:
        fname = str(f)
        # Count executable lines (approx) and executed ones
        executed = 0
        all_lines = 0
        for (fn, lineno), count in cov.items():
            if fn == fname:
                executed += 1 if count else 0
        try:
            src_lines = f.read_text(encoding='utf-8').splitlines()
            # Approximate: count non-empty, non-comment lines
            all_lines = sum(1 for s in src_lines if s.strip() and not s.strip().startswith('#'))
        except Exception:
            all_lines = 0
        total_exec += executed
        total_lines += all_lines
        pct = (executed / all_lines * 100.0) if all_lines else 0.0
        lines.append(f"- {f.name}: {executed}/{all_lines} lines ≈ {pct:.1f}%")

    if failed:
        lines.append("")
        lines.append("## Import failures")
        for f, err in failed[:50]:
            lines.append(f"- {f.name}: {err}")

    lines.append("")
    overall = (total_exec / total_lines * 100.0) if total_lines else 0.0
    lines.append(f"Overall (approx.): {total_exec}/{total_lines} lines ≈ {overall:.1f}%")

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    report = REPORTS / f"exports-trace-coverage-{ts}.md"
    report.write_text("\n".join(lines), encoding='utf-8')
    print(f"Wrote coverage report to {report}")


if __name__ == '__main__':
    main()
