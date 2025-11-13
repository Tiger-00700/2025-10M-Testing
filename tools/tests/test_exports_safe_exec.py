import ast
import importlib.util
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
EXPORTS = ROOT / "examples" / "99_book_exports"

ALLOWED_CALLS = {"len","range","print","sum","min","max","sorted","list","dict","set","tuple","enumerate","zip","any","all","abs","pow","round"}


def discover_candidates(py_path: Path):
    src = py_path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(src, filename=str(py_path))
    except Exception:
        return []
    cand = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and not node.args.args and not node.args.kwonlyargs and node.args.vararg is None and node.args.kwarg is None:
            # conservative body size
            if len(node.body) > 8:
                continue
            safe = True
            for n in ast.walk(node):
                if isinstance(n, ast.Import) or isinstance(n, ast.ImportFrom):
                    safe = False; break
                if isinstance(n, ast.Attribute):
                    safe = False; break
                if isinstance(n, ast.Call):
                    # allow only simple Name calls to whitelisted builtins
                    if isinstance(n.func, ast.Name):
                        if n.func.id not in ALLOWED_CALLS:
                            safe = False; break
                    else:
                        safe = False; break
            if safe:
                cand.append(node.name)
    return cand


def import_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore
    return mod


py_files = sorted(EXPORTS.glob('newbook__block*.py'))


def test_safe_function_examples_execute():
    executed = 0
    for p in py_files:
        cands = discover_candidates(p)
        if not cands:
            continue
        m = import_module(p)
        for name in cands[:2]:  # call at most two per module
            fn = getattr(m, name, None)
            if callable(fn):
                fn()  # should not raise
                executed += 1
    if executed == 0:
        pytest.skip("No safe candidate functions found to execute.")
