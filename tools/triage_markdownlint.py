#!/usr/bin/env python3
"""
Parse the raw markdownlint stdout (tools/markdownlint-project-raw.txt)
and produce a prioritized, project-focused triage report.

Outputs:
- tools/content-lint-triage.json
- tools/content-lint-triage.txt

This script is safe to run multiple times.
"""
import re
import json
from collections import defaultdict, Counter

RAW_PATH = "tools/markdownlint-project-raw.txt"
OUT_JSON = "tools/content-lint-triage.json"
OUT_TXT = "tools/content-lint-triage.txt"

# Rules we consider high priority for readability/print:
PRIORITY_RULES = ["MD022", "MD032", "MD013", "MD047", "MD009", "MD040", "MD041"]

def main():
    try:
        text = open(RAW_PATH, encoding='utf-8').read().splitlines()
    except FileNotFoundError:
        print(f"Missing {RAW_PATH}")
        return

    entry_re = re.compile(r"^(?P<file>[^:]+):(?P<line>\d*):?(?P<col>\d*)?\s*(?P<code>MD\d{2,3})")
    per_file = defaultdict(Counter)
    rule_totals = Counter()
    entries = []

    for ln in text:
        m = entry_re.search(ln)
        if not m:
            continue
        file = m.group('file').strip()
        code = m.group('code')
        per_file[file][code] += 1
        rule_totals[code] += 1
        entries.append({'file': file, 'code': code, 'raw': ln})

    # Build prioritized per-file list (sort by priority then count)
    report = {'summary': {}, 'files': {}}
    report['summary']['total_files'] = len(per_file)
    report['summary']['total_issues'] = sum(rule_totals.values())
    report['summary']['top_rules'] = rule_totals.most_common(20)

    for f, counts in per_file.items():
        items = []
        for code, cnt in counts.items():
            pr = PRIORITY_RULES.index(code) if code in PRIORITY_RULES else len(PRIORITY_RULES)
            items.append({'rule': code, 'count': cnt, 'priority': pr})
        items.sort(key=lambda x: (x['priority'], -x['count'], x['rule']))
        report['files'][f] = items

    # write JSON
    open(OUT_JSON, 'w', encoding='utf-8').write(json.dumps(report, ensure_ascii=False, indent=2))

    # write human readable text
    with open(OUT_TXT, 'w', encoding='utf-8') as fh:
        fh.write(f"Content lint triage (from {RAW_PATH})\n")
        fh.write(f"Files with issues: {report['summary']['total_files']}\n")
        fh.write(f"Total reported issues: {report['summary']['total_issues']}\n\n")
        fh.write("Top rules overall:\n")
        for r,c in report['summary']['top_rules']:
            fh.write(f"  {r}: {c}\n")
        fh.write('\nFiles (prioritized rules):\n')
        for f, items in sorted(report['files'].items(), key=lambda kv: (-sum(i['count'] for i in kv[1]), kv[0])):
            fh.write(f"\n{f}\n")
            for it in items:
                fh.write(f"  {it['rule']}: {it['count']}\n")

    print(f"Wrote {OUT_JSON} and {OUT_TXT}")

if __name__ == '__main__':
    main()
