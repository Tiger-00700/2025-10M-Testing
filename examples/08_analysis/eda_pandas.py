#!/usr/bin/env python3
"""A small pandas-based EDA example for examples/08_analysis.

This script reads sample_data.csv (already included) and prints basic statistics.
"""

import pandas as pd
from pathlib import Path

DATA = Path(__file__).parent / "sample_data.csv"

def main():
    if not DATA.exists():
        print(f"Sample data not found: {DATA}")
        return
    df = pd.read_csv(DATA, parse_dates=[0])
    print("Head:")
    print(df.head())
    print("\nDescribe():")
    print(df.describe(include='all'))

if __name__ == '__main__':
    main()
