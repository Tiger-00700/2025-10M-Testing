from pathlib import Path
import sys
from datetime import datetime

try:
    import pytest  # type: ignore
except Exception as e:
    print(f"pytest not available: {e}")
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "tools" / "reports"
EXPORTS = ROOT / "examples" / "99_book_exports"


def main():
    REPORTS.mkdir(parents=True, exist_ok=True)
    if not EXPORTS.exists():
        print(f"No exports found at {EXPORTS}")
        sys.exit(0)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    xml = REPORTS / f"pytest-coverage-{ts}.xml"
    html = REPORTS / "coverage_html"
    # Run pytest with coverage for the exports folder and tests
    args = [
    "-q",
    "--maxfail=1",
    "--disable-warnings",
    "--cov=examples/99_book_exports",
    "--cov-report=term-missing",
    f"--cov-report=xml:{xml}",
    f"--cov-report=html:{html}",
    "tests",
    ]
    ret = pytest.main(args)
    sys.exit(ret)


if __name__ == "__main__":
    main()
