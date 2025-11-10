#!/usr/bin/env python3
"""Tiny EDA example that reads a CSV and prints basic stats (uses only stdlib).

Replace with richer notebooks or pandas-based scripts as needed.
"""

import csv
from pathlib import Path

DATA = Path(__file__).parent / "sample_data.csv"

def summarize(path):
	with path.open(newline='') as fh:
		reader = csv.DictReader(fh)
		values = [row for row in reader]
	print(f"Rows: {len(values)}")
	if values:
		print("Sample row:", values[0])

if __name__ == '__main__':
	if not DATA.exists():
		print(f"Sample data not found: {DATA}")
	else:
		summarize(DATA)

