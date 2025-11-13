import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPORTS = ROOT / "examples" / "99_book_exports"

SKIP_KEYWORDS = (
    # avoid heavy deps
    "pyspark", "spark", "kafka", "hdfs", "requests", "pandas", "numpy",
)


def is_lightweight(py_path: Path) -> bool:
    try:
        text = py_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return False
    if sum(1 for _ in text.splitlines()) > 60:  # limit size
        return False
    tl = text.lower()
    if any(k in tl for k in SKIP_KEYWORDS):
        return False
    return True


def import_from_path(py_path: Path):
    spec = importlib.util.spec_from_file_location(py_path.stem, py_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load spec for {py_path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[py_path.stem] = mod
    spec.loader.exec_module(mod)
    return mod


def test_lightweight_exports_smoke():
    assert EXPORTS.exists(), "exports dir missing"
    py_files = sorted(EXPORTS.glob("*.py"))
    tested = 0
    for py in py_files:
        if not is_lightweight(py):
            continue
        mod = import_from_path(py)
        # if module exposes example(), call it
        ex = getattr(mod, "example", None)
        if callable(ex):
            ex()
        tested += 1
        if tested >= 10:
            break
    assert tested > 0, "no lightweight exports tested"
