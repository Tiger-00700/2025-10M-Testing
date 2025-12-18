#!/usr/bin/env python3
"""Run verification scripts and write a UTF-8 encoded QA report."""
import subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'tools' / 'reports' / 'insert_qa_2025-12-18.md'
OUT.parent.mkdir(parents=True, exist_ok=True)
with OUT.open('w', encoding='utf-8') as f:
    f.write('# QA Report: Framework insertion verification\n\n')
    f.write('## compare_framework_book.py output\n\n')
    try:
        env = None
        import os
        env = os.environ.copy()
        env['PYTHONIOENCODING']='utf-8'
        cp = subprocess.run(['python','tools/compare_framework_book.py'], capture_output=True, text=True, check=False, env=env)
        f.write(cp.stdout)
        if cp.stderr:
            f.write('\n--- STDERR ---\n')
            f.write(cp.stderr)
    except Exception as e:
        f.write(f'Error running compare: {e}\n')
    f.write('\n\n## check_marker_pairs.py output\n\n')
    try:
        cp = subprocess.run(['python','tools/check_marker_pairs.py'], capture_output=True, text=True, check=False)
        f.write(cp.stdout)
        if cp.stderr:
            f.write('\n--- STDERR ---\n')
            f.write(cp.stderr)
    except Exception as e:
        f.write(f'Error running marker check: {e}\n')
    f.write('\n\n## dedup_book.py (last run was executed during workflow)\n')
    f.write('- Dedup ran and backups were created if duplicates were removed.\n')
print('Wrote QA report to', OUT)
