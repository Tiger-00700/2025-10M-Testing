#!/usr/bin/env python3
"""
Lightweight smoke runner for examples/第5篇 Python files.

For each `.py` under `examples/第5篇` (excluding `legacy_placeholders`),
this script runs the file in a subprocess with a short timeout and records
whether it exited cleanly, raised an exception, or timed out.

Outputs `examples/第5篇/smoke_report.txt` with a per-file summary.
"""
from __future__ import annotations

import sys
import subprocess
from pathlib import Path
from datetime import datetime


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "examples" / "第5篇"
REPORT = TARGET / "smoke_report.txt"

TIMEOUT_SECONDS = 8
MAX_OUTPUT_CHARS = 2000

EXTERNAL_KEYWORDS = [
    "hdfs",
    "pymongo",
    "mongodb",
    "kubernetes",
    "docker",
    "spark",
    "flink",
    "requests",
    "boto3",
    "mysql",
    "psycopg2",
    "redis",
]


def find_py_files() -> list[Path]:
    if not TARGET.exists():
        return []
    files = [p for p in TARGET.rglob("*.py") if "legacy_placeholders" not in p.parts]
    # exclude the runner itself if copied into examples
    files = [p for p in files if p.name != Path(__file__).name]
    return sorted(files)


def run_file(py: Path) -> dict:
    result = {
        "file": str(py.relative_to(ROOT)),
        "status": "unknown",
        "code": None,
        "error": None,
        "runner": "python",
        "external": False,
    }

    text = ""
    try:
        text = py.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        text = ""

    # detect pytest-style files
    is_pytest = any(t in text for t in ("import pytest", "@pytest", "def test_"))
    needs_external = any(k.lower() in text.lower() for k in EXTERNAL_KEYWORDS)
    result["external"] = bool(needs_external)

    # If the file looks like a pytest-style test fragment, skip executing it
    # because many fragments depend on project-level fixtures/helpers.
    if is_pytest:
        result["status"] = "skipped-test-fragment"
        result["runner"] = "skipped"
        result["error"] = "pytest-style test fragment detected; skipped by smoke runner"
        return result

    cmd = [sys.executable, str(py)]
    result["runner"] = "python"

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT_SECONDS)
        result["code"] = proc.returncode
        if proc.returncode == 0:
            result["status"] = "ok"
        else:
            result["status"] = "error"
            err = (proc.stderr or proc.stdout)[:MAX_OUTPUT_CHARS]
            result["error"] = err
    except subprocess.TimeoutExpired as e:
        result["status"] = "timeout"
        out = (e.stdout or "") + (e.stderr or "")
        result["error"] = (out[:MAX_OUTPUT_CHARS] + "... [truncated]") if out else "(no output)"
    except Exception as e:
        result["status"] = "failed"
        result["error"] = repr(e)
    return result


def main() -> int:
    files = find_py_files()
    now = datetime.utcnow().isoformat() + "Z"
    lines = [f"Smoke test report for examples/第5篇 - {now}", "", f"Python: {sys.executable}", "", "Summary:"]
    results = []
    skipped = []
    for p in files:
        lines.append(f"Running: {p.relative_to(ROOT)}")
        res = run_file(p)
        results.append(res)
        if res.get("status") == "skipped-test-fragment":
            skipped.append(res)
            lines.append(f"  SKIPPED (pytest fragment)")
            lines.append(f"    {res.get('error')}")
            lines.append("")
            continue
        if res["status"] == "ok":
            lines.append(f"  OK")
        elif res["status"] == "timeout":
            lines.append(f"  TIMEOUT (>{TIMEOUT_SECONDS}s)")
            lines.append(f"    {res['error']}")
        else:
            lines.append(f"  FAIL ({res['status']}, code={res.get('code')})")
            if res.get("error"):
                lines.append(f"    {res['error']}")
        lines.append("")

    # aggregate
    ok = sum(1 for r in results if r["status"] == "ok")
    to = sum(1 for r in results if r["status"] == "timeout")
    fail = len(results) - ok - to
    lines.insert(4, f"  files found: {len(results)}  ok: {ok}  fail: {fail}  timeout: {to}")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    # write a small README listing skipped pytest fragments and noted externals
    readme = TARGET / "README-smoke.md"
    rd_lines = ["Smoke test runner notes for examples/第5篇", "", "Skipped pytest-style fragments (auto-detected):", ""]
    for s in skipped:
        rd_lines.append(f"- {s['file']}: {s.get('error')}")
    rd_lines.append("")
    rd_lines.append("Files flagged as requiring external services or packages:")
    rd_lines.append("")
    for r in results:
        if r.get("external"):
            rd_lines.append(f"- {r['file']}")
    readme.write_text("\n".join(rd_lines), encoding="utf-8")
    print(REPORT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
