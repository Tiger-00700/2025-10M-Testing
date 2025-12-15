import os
import sys
import subprocess
from datetime import datetime

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PYTHON = sys.executable  # use current venv python

COMMANDS = [
    [PYTHON, os.path.join(REPO, 'tools', 'pipeline', 'pre_release_check.py'), '--output', os.path.join(REPO, 'tools', 'reports', 'pre_release_check.md')],
    [PYTHON, os.path.join(REPO, 'tools', 'validate_contracts.py')],
    [PYTHON, os.path.join(REPO, 'tools', 'validate_quality_rules.py')],
    [PYTHON, os.path.join(REPO, 'tools', 'check_report_completeness.py')],
    [PYTHON, os.path.join(REPO, 'tools', 'strategy_hit_summary.py')],
]


def run(cmd):
    start = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[START {start}] {' '.join(cmd)}")
    res = subprocess.run(cmd, cwd=REPO)
    code = res.returncode
    end = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[END   {end}] exit_code={code}\n")
    return code


def main():
    failures = []
    for cmd in COMMANDS:
        code = run(cmd)
        if code != 0:
            failures.append((cmd, code))
    if failures:
        print("Summary: some commands failed:")
        for cmd, code in failures:
            print(f" - exit_code={code} :: {' '.join(cmd)}")
        sys.exit(1)
    else:
        print("Summary: all commands succeeded.")
        sys.exit(0)


if __name__ == '__main__':
    main()
