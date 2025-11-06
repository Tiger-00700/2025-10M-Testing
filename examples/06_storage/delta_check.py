#!/usr/bin/env python3
"""
delta_check.py: Time-travel diff for CSV snapshots.

Compares two CSV files (old vs new) by key columns and reports added, removed,
and changed rows. Exits 0 if no differences, 2 if differences found, 3 on error.

Usage:
  python delta_check.py --old data/snapshot_v1.csv --new data/snapshot_v2.csv --key id --compare name,amount

If --compare is omitted, compares all non-key columns.
"""
import argparse, csv, sys
from typing import List, Dict, Tuple

def read_csv(path: str, key_cols: List[str]) -> Tuple[Dict[Tuple, Dict[str,str]], List[str]]:
    with open(path, newline='', encoding='utf-8') as f:
        rdr = csv.DictReader(f)
        headers = rdr.fieldnames or []
        missing = [k for k in key_cols if k not in headers]
        if missing:
            raise ValueError(f"Missing key columns in {path}: {missing}")
        data = {}
        for row in rdr:
            key = tuple(row[k] for k in key_cols)
            data[key] = row
        return data, headers

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--old', required=True)
    ap.add_argument('--new', required=True)
    ap.add_argument('--key', required=True, help='Comma-separated key columns')
    ap.add_argument('--compare', help='Comma-separated non-key columns to compare; default all others')
    ap.add_argument('--fail-on', default='changed,added,removed', help='What differences cause non-zero: any of changed,added,removed')
    args = ap.parse_args()

    key_cols = [c.strip() for c in args.key.split(',') if c.strip()]
    if not key_cols:
        print('ERROR: no key columns provided', file=sys.stderr)
        return 3

    try:
        old, old_headers = read_csv(args.old, key_cols)
        new, new_headers = read_csv(args.new, key_cols)
    except Exception as e:
        print(f'ERROR: {e}', file=sys.stderr)
        return 3

    compare_cols = None
    if args.compare:
        compare_cols = [c.strip() for c in args.compare.split(',') if c.strip()]
    else:
        compare_cols = [h for h in new_headers if h not in key_cols]

    added = [k for k in new.keys() if k not in old]
    removed = [k for k in old.keys() if k not in new]
    changed = []
    for k in new.keys() & old.keys():
        a, b = old[k], new[k]
        diffs = {c: (a.get(c,''), b.get(c,'')) for c in compare_cols if a.get(c,'') != b.get(c,'')}
        if diffs:
            changed.append((k, diffs))

    def fmt_key(k):
        return ','.join(map(str,k))

    print(f'Keys: {key_cols}')
    print(f'Compare: {compare_cols}')
    print(f'Added: {len(added)} | Removed: {len(removed)} | Changed: {len(changed)}')
    if added:
        print('> Added keys: ' + '; '.join(fmt_key(k) for k in added))
    if removed:
        print('> Removed keys: ' + '; '.join(fmt_key(k) for k in removed))
    if changed:
        for k, diffs in changed[:10]:
            diff_str = ', '.join(f"{c}:{v0}->{v1}" for c,(v0,v1) in diffs.items())
            print(f'> Changed {fmt_key(k)}: {diff_str}')
        if len(changed) > 10:
            print(f'> ... and {len(changed)-10} more changed rows')

    fail_on = {x.strip() for x in args.fail_on.split(',') if x.strip()}
    fail = False
    if 'added' in fail_on and added: fail = True
    if 'removed' in fail_on and removed: fail = True
    if 'changed' in fail_on and changed: fail = True

    if fail:
        return 2
    return 0

if __name__ == '__main__':
    sys.exit(main())
