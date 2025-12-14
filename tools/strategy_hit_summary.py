import os
import re
from datetime import datetime, timedelta

REPORT_DIR = os.path.join(os.path.dirname(__file__), 'reports')

TEMPLATES = [
    'examples/12_governance/policy_access_control.md',
    'examples/12_governance/change_freeze_waiver.md',
]

SECTION_MARKERS = [
    '摘要', '证据', '结论', '签署'
]

def list_recent_reports(hours: int = 24):
    now = datetime.now()
    cutoff = now - timedelta(hours=hours)
    files = []
    if not os.path.isdir(REPORT_DIR):
        return files
    for name in os.listdir(REPORT_DIR):
        if not name.endswith('.md'):
            continue
        path = os.path.join(REPORT_DIR, name)
        try:
            mtime = datetime.fromtimestamp(os.path.getmtime(path))
        except Exception:
            continue
        if mtime >= cutoff:
            files.append(path)
    return sorted(files)

def scan_strategy_hits(report_path: str):
    hits = { 'policy_refs': 0, 'waiver_refs': 0, 'sections_present': 0 }
    text = ''
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception:
        return hits

    # Template references
    hits['policy_refs'] = len(re.findall(r'policy_access_control\.md', text))
    hits['waiver_refs'] = len(re.findall(r'change_freeze_waiver\.md', text))

    # Compliance sections
    present = 0
    for marker in SECTION_MARKERS:
        if marker in text:
            present += 1
    hits['sections_present'] = present
    return hits

def main():
    reports = list_recent_reports(hours=72)
    total_policy = 0
    total_waiver = 0
    fully_structured = 0

    lines = []
    lines.append(f"# 策略命中摘要\n")
    lines.append(f"时间窗口：近72小时\n")
    lines.append(f"报告数量：{len(reports)}\n")
    lines.append("\n## 明细\n")

    for rp in reports:
        hits = scan_strategy_hits(rp)
        total_policy += hits['policy_refs']
        total_waiver += hits['waiver_refs']
        if hits['sections_present'] == len(SECTION_MARKERS):
            fully_structured += 1
        lines.append(f"- {os.path.basename(rp)} | policy_refs={hits['policy_refs']} | waiver_refs={hits['waiver_refs']} | sections={hits['sections_present']}/{len(SECTION_MARKERS)}\n")

    lines.append("\n## 汇总\n")
    lines.append(f"- 模板引用次数（访问治理）：{total_policy}\n")
    lines.append(f"- 模板引用次数（冻结豁免）：{total_waiver}\n")
    lines.append(f"- 完全四段结构报告数：{fully_structured}/{len(reports)}\n")

    out_name = f"strategy_hit_summary_{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
    out_path = os.path.join(REPORT_DIR, out_name)
    try:
        with open(out_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"Wrote summary: {out_path}")
    except Exception as e:
        print(f"Error writing summary: {e}")

if __name__ == '__main__':
    main()
