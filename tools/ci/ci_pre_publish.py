import os
import sys
import subprocess
from datetime import datetime

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PYTHON = sys.executable
AGG = os.path.join(REPO, 'tools', 'ci', 'first_reports.py')


def run(cmd):
    print(f"[CI] Run: {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=REPO).returncode


def main():
    stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    print(f"[CI] Pre-publish start: {stamp}")
    code = run([PYTHON, AGG])
    if code != 0:
        print(f"[CI] Pre-publish FAILED, exit_code={code}")
        sys.exit(code)
    print("[CI] Pre-publish OK: reports generated under tools/reports")
    sys.exit(0)


if __name__ == '__main__':
    main()
