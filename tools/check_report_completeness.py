import os
import sys
import re
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
REPORT_DIR = os.path.join(REPO, 'tools', 'reports')

REQUIRED_SECTIONS = [
    r'^#\s+.+',             # title
    r'##\s+摘要|##\s+Summary',
    r'##\s+证据|##\s+Evidence',
    r'##\s+结论|##\s+Conclusion',
    r'##\s+签署|##\s+Sign-off',
]

def file_has_sections(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        return all(re.search(pattern, content, flags=re.MULTILINE) for pattern in REQUIRED_SECTIONS)
    except Exception:
        return False

def main():
    if not os.path.isdir(REPORT_DIR):
        print(f"No report dir: {REPORT_DIR}")
        sys.exit(0)
    window_days = int(os.environ.get('REPORT_COMPLETENESS_WINDOW_DAYS', '3'))
    cutoff = datetime.now() - timedelta(days=window_days)
    files = []
    for f in os.listdir(REPORT_DIR):
        if not f.endswith('.md'):
            continue
        # Exclude templates and unrelated markdown; focus on generated reports
        if f.startswith('pre_release_check_') or f.startswith('report_diff_') or f.startswith('ingest_'):
            full = os.path.join(REPORT_DIR, f)
            try:
                mtime = datetime.fromtimestamp(os.path.getmtime(full))
            except Exception:
                mtime = None
            if mtime and mtime < cutoff:
                continue
            files.append(full)
    if not files:
        print("No markdown reports found; skipping completeness check.")
        sys.exit(0)
    total = len(files)
    complete = sum(1 for f in files if file_has_sections(f))
    ratio = (complete / total) * 100.0 if total else 100.0
    stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    out_path = os.path.join(REPORT_DIR, f'report_completeness_{stamp}.md')
    with open(out_path, 'w', encoding='utf-8') as out:
        out.write('# Report Completeness Summary\n\n')
        out.write(f'- Total reports: {total}\n')
        out.write(f'- Complete reports: {complete}\n')
        out.write(f'- Completeness ratio: {ratio:.2f}%\n\n')
        out.write('## Checked Files\n')
        for f in sorted(files):
            out.write(f'- {os.path.basename(f)}\n')
        out.write('\n')
        out.write('## Criteria\n')
        out.write('- Must contain sections: 标题/摘要/证据/结论/签署 (or English equivalents).\n')
    print(f"Wrote completeness report: {out_path}")
    # Gate CI if below threshold (default 60%)
    threshold = float(os.environ.get('REPORT_COMPLETENESS_THRESHOLD', '60'))
    if ratio < threshold:
        print(f"Completeness {ratio:.2f}% below threshold {threshold:.2f}%")
        sys.exit(2)

if __name__ == '__main__':
    main()
