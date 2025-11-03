import ast
from pathlib import Path
from datetime import datetime
import json
import importlib.util as ilu
import re

ROOT = Path(__file__).resolve().parents[1]
EXPORTS = ROOT / "examples" / "99_book_exports"
REPORTS = ROOT / "tools" / "reports"

SHELL_BUILTINS = {"cd","echo","exit","pwd","export","set","unset","read","alias","type","fg","bg","jobs","wait"}
POWERSHELL_BUILTINS = {"Write-Output","Write-Host","Set-Variable","Set-Content","Get-Content","cd","ls","dir","Set-Item","Get-Item"}


def analyze_python(files):
    modules_required = set()
    missing = set()
    per_file = {}
    for p in files:
        try:
            src = p.read_text(encoding='utf-8')
            tree = ast.parse(src, filename=str(p))
        except Exception:
            continue
        names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    names.add(a.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    names.add(node.module.split('.')[0])
        per_file[str(p)] = sorted(names)
        for n in names:
            modules_required.add(n)
            try:
                if ilu.find_spec(n) is None:
                    missing.add(n)
            except Exception:
                missing.add(n)
    return {
        "total_files": len(files),
        "unique_modules": sorted(modules_required),
        "missing_modules": sorted(missing),
        "per_file_imports": per_file,
    }


def analyze_shell(files):
    cmds = set()
    per_file = {}
    token_re = re.compile(r"^[ \t]*([A-Za-z0-9_.-]+)")
    for p in files:
        used = set()
        try:
            for ln in p.read_text(encoding='utf-8').splitlines():
                s = ln.strip()
                if not s or s.startswith('#'):
                    continue
                m = token_re.match(s)
                if not m:
                    continue
                cmd = m.group(1)
                if cmd in SHELL_BUILTINS:
                    continue
                if cmd.startswith('sudo') and len(s.split())>1:
                    cmd = s.split()[1]
                used.add(cmd)
                cmds.add(cmd)
        except Exception:
            pass
        per_file[str(p)] = sorted(used)
    return {"unique_commands": sorted(cmds), "per_file_commands": per_file, "total_files": len(files)}


def analyze_ps1(files):
    cmds = set()
    per_file = {}
    token_re = re.compile(r"^[ \t]*([A-Za-z0-9_.-]+)")
    for p in files:
        used = set()
        try:
            for ln in p.read_text(encoding='utf-8').splitlines():
                s = ln.strip()
                if not s or s.startswith('#'):
                    continue
                m = token_re.match(s)
                if not m:
                    continue
                cmd = m.group(1)
                if cmd in POWERSHELL_BUILTINS:
                    continue
                used.add(cmd)
                cmds.add(cmd)
        except Exception:
            pass
        per_file[str(p)] = sorted(used)
    return {"unique_commands": sorted(cmds), "per_file_commands": per_file, "total_files": len(files)}


def main():
    REPORTS.mkdir(parents=True, exist_ok=True)
    py_files = sorted(EXPORTS.glob('newbook__block*.py'))
    sh_files = sorted(EXPORTS.glob('newbook__block*.sh'))
    ps1_files = sorted(EXPORTS.glob('newbook__block*.ps1'))

    py = analyze_python(py_files)
    sh = analyze_shell(sh_files)
    ps1 = analyze_ps1(ps1_files)

    ts = datetime.now().strftime('%Y%m%d-%H%M%S')
    report = {
        "timestamp": ts,
        "python": py,
        "shell": sh,
        "powershell": ps1,
        "hints": {
            "python_pip_install": py["missing_modules"],
            "shell_requirements": sh["unique_commands"],
            "powershell_requirements": ps1["unique_commands"],
        }
    }
    out = REPORTS / f"min-env-report-{ts}.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"Wrote min environment report: {out}")


if __name__ == '__main__':
    main()
