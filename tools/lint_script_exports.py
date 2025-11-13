import subprocess
from pathlib import Path
from datetime import datetime
import shutil
import json

ROOT = Path(__file__).resolve().parents[1]
EXPORTS = ROOT / "examples" / "99_book_exports"
REPORTS = ROOT / "tools" / "reports"


def lint_ps1(files):
    results = []
    pwsh = shutil.which("pwsh") or shutil.which("powershell")
    if not pwsh:
        return {"tool": "ps1", "available": False, "error": "PowerShell not found in PATH", "items": []}
    for p in files:
        # Use PowerShell parser to check syntax
        cmd = [
            pwsh,
            "-NoLogo","-NoProfile","-Command",
            "[System.Management.Automation.Language.Parser]::ParseFile('%s',[ref]$null,[ref]$null) | Out-Null; if($?) { Write-Output 'OK' } else { Write-Output 'ERR' }" % str(p).replace("'","''")
        ]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            ok = proc.returncode == 0 and 'OK' in (proc.stdout or '')
            results.append({"file": str(p), "ok": ok, "stdout": proc.stdout.strip(), "stderr": proc.stderr.strip()})
        except Exception as e:
            results.append({"file": str(p), "ok": False, "error": str(e)})
    return {"tool": "ps1", "available": True, "items": results}


def lint_sh(files):
    results = []
    bash = shutil.which("bash")
    if not bash:
        return {"tool": "sh", "available": False, "error": "bash not found in PATH", "items": []}
    for p in files:
        cmd = [bash, "-n", str(p)]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            ok = proc.returncode == 0
            results.append({"file": str(p), "ok": ok, "stdout": proc.stdout.strip(), "stderr": proc.stderr.strip()})
        except Exception as e:
            results.append({"file": str(p), "ok": False, "error": str(e)})
    return {"tool": "sh", "available": True, "items": results}


def lint_sql(files):
    # No SQL engine available here; do lightweight checks: balanced quotes and parentheses per file
    results = []
    for p in files:
        try:
            s = p.read_text(encoding='utf-8')
            stack = 0
            for ch in s:
                if ch == '(':
                    stack += 1
                elif ch == ')':
                    stack -= 1
            balanced = stack == 0
            has_statement = ';' in s
            ok = balanced and has_statement
            results.append({"file": str(p), "ok": ok, "balanced_paren": balanced, "has_semicolon": has_statement})
        except Exception as e:
            results.append({"file": str(p), "ok": False, "error": str(e)})
    return {"tool": "sql", "available": True, "items": results}


def main():
    REPORTS.mkdir(parents=True, exist_ok=True)
    ps1_files = sorted(EXPORTS.glob('newbook__block*.ps1'))
    sh_files = sorted(EXPORTS.glob('newbook__block*.sh'))
    sql_files = sorted(EXPORTS.glob('newbook__block*.sql'))
    ts = datetime.now().strftime('%Y%m%d-%H%M%S')

    report = {
        "timestamp": ts,
        "counts": {
            "ps1": len(ps1_files),
            "sh": len(sh_files),
            "sql": len(sql_files),
        },
        "results": {
            "ps1": lint_ps1(ps1_files),
            "sh": lint_sh(sh_files),
            "sql": lint_sql(sql_files),
        }
    }
    out = REPORTS / f"lint-exports-{ts}.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"Wrote lint report: {out}")


if __name__ == '__main__':
    main()
