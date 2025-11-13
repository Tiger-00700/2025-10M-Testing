import ast
import json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
EXPORTS = ROOT / "examples" / "99_book_exports"
REPORTS = ROOT / "tools" / "reports"

HEAVY_DEPS = {"opentelemetry","hdfs","pyhive","pyspark","torch","tensorflow","pandas","numpy","kafka","confluent_kafka"}
CODE_TOKENS = ("def ","class ","import ","if ","for ","while ")


def analyze_python_file(p: Path):
    try:
        s = p.read_text(encoding='utf-8')
    except Exception as e:
        return {"file": str(p), "error": str(e)}
    lines = s.splitlines()
    total = max(1, len(lines))
    comment_ratio = sum(1 for l in lines if l.strip().startswith('#')) / total
    has_code_tokens = any(tok in s for tok in CODE_TOKENS)
    flags = []
    if comment_ratio > 0.8 or not has_code_tokens:
        flags.append({"reason": "narrative_heavy_python", "comment_ratio": round(comment_ratio,2)})
    # Import scan for heavy deps
    try:
        tree = ast.parse(s, filename=str(p))
    except Exception as e:
        # If it cannot be parsed, it's likely already downgraded in exporter; mark anyways
        flags.append({"reason": "syntax_error", "message": str(e)})
        return {"file": str(p), "flags": flags}
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                imports.add(a.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])
    heavy = sorted(HEAVY_DEPS.intersection(imports))
    if heavy:
        flags.append({"reason": "heavy_external_dependencies", "modules": heavy})
    return {"file": str(p), "flags": flags}


def main():
    REPORTS.mkdir(parents=True, exist_ok=True)
    py_files = sorted(EXPORTS.glob('newbook__block*.py'))
    items = [analyze_python_file(p) for p in py_files]
    ts = datetime.now().strftime('%Y%m%d-%H%M%S')
    out = REPORTS / f'export-warnings-{ts}.json'
    out.write_text(json.dumps({"generated_at": ts, "items": items}, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"Wrote export warnings report: {out}")

if __name__ == '__main__':
    main()
