#!/usr/bin/env python3
"""A small pandas-based EDA example for examples/08_analysis.

This script prefers pandas for richer output. If pandas is not available,
it falls back to a minimal stdlib CSV reader that prints head and simple
numeric statistics so smoke tests can run without heavy deps on Windows.
"""

from pathlib import Path
import csv
import statistics
from typing import List, Dict, Any

DATA = Path(__file__).parent / "sample_data.csv"

try:
    import pandas as pd
except Exception:
    pd = None


def describe_with_stdlib(rows: List[Dict[str, str]]) -> Dict[str, Dict[str, Any]]:
    # compute simple stats for numeric columns
    if not rows:
        return {}
    cols = list(rows[0].keys())
    stats = {}
    for c in cols:
        vals = []
        for r in rows:
            v = r.get(c, "")
            try:
                fv = float(v)
            except Exception:
                continue
            vals.append(fv)
        if vals:
            stats[c] = {
                'count': len(vals),
                'mean': statistics.mean(vals),
                'stdev': statistics.pstdev(vals) if len(vals) > 1 else 0.0,
                'min': min(vals),
                'max': max(vals),
            }
    return stats


def run_with_stdlib(path: Path):
    if not path.exists():
        print(f"Sample data not found: {path}")
        return
    with path.open(newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    print("Head (first 5 rows):")
    for r in rows[:5]:
        print(r)
    print("\nSimple numeric statistics:")
    stats = describe_with_stdlib(rows)
    if not stats:
        print("  No numeric columns detected or no data.")
        return
    for col, s in stats.items():
        print(f"  {col}: count={s['count']}, mean={s['mean']:.4f}, stdev={s['stdev']:.4f}, min={s['min']}, max={s['max']}")


def main():
    path = DATA
    if pd is not None:
        # pandas available: give richer output
        df = pd.read_csv(path, parse_dates=[0])
        print("Head:")
        print(df.head())
        print("\nDescribe():")
        print(df.describe(include='all'))
    else:
        # fallback to stdlib
        run_with_stdlib(path)


if __name__ == '__main__':
    main()

