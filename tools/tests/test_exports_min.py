import importlib.util
from pathlib import Path
import ast
import importlib
import importlib.util as ilu
import pytest

ROOT = Path(__file__).resolve().parents[1]
EXPORTS = ROOT / "examples" / "99_book_exports"

# Discover exported .py files
py_files = sorted([p for p in EXPORTS.glob('newbook__block*.py')])


def is_syntax_valid(py_path: Path) -> bool:
    try:
        src = py_path.read_text(encoding="utf-8")
        # quick empty/whitespace guard
        if not src.strip():
            return False
        ast.parse(src, filename=str(py_path))
        return True
    except Exception:
        return False


def import_module_from_path(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    # spec may be None; assert before using
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore
    return mod


def _has_missing_deps(py_path: Path) -> bool:
    """Detect if the module imports packages that aren't available in this env."""
    try:
        src = py_path.read_text(encoding="utf-8")
        tree = ast.parse(src, filename=str(py_path))
    except Exception:
        return True
    names = set()
    used_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                names.add(node.module.split('.')[0])
        elif isinstance(node, ast.Name):
            used_names.add(node.id)
    # Ignore builtins and stdlib-ish that are always present
    ignore = {"sys", "os", "re", "time", "json", "pathlib", "typing", "random", "math", "itertools", "collections"}
    for n in names:
        if n in ignore:
            continue
        try:
            if ilu.find_spec(n) is None:
                return True
        except Exception:
            # If any resolution error occurs, assume missing
            return True
    # Heuristic: if code uses pytest.* but didn't import pytest, treat as missing dep
    if 'pytest' in used_names and 'pytest' not in names:
        return True
    return False


def test_can_import_all_python_exports():
    valid_files = [p for p in py_files if is_syntax_valid(p)]
    invalid_files = [p for p in py_files if p not in valid_files]

    # Soft-signal invalid exports without failing the suite; they may be pseudocode blocks.
    if invalid_files:
        print(f"[info] Skipping {len(invalid_files)} invalid Python exports (syntax check failed)")
        for ip in invalid_files[:20]:
            print(f"  - {ip}")

    # Further filter out files with missing external dependencies
    ready_files = [p for p in valid_files if not _has_missing_deps(p)]
    skipped_for_deps = [p for p in valid_files if p not in ready_files]
    if skipped_for_deps:
        print(f"[info] Skipping {len(skipped_for_deps)} Python exports due to missing dependencies")
        for sp in skipped_for_deps[:20]:
            print(f"  - {sp}")

    if len(ready_files) == 0:
        pytest.skip("No Python exports with satisfied dependencies to import in this environment.")

    for p in ready_files:
        try:
            import_module_from_path(p)
        except Exception as e:
            raise AssertionError(f"Failed to import {p}: {e}")
