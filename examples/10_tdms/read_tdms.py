#!/usr/bin/env python3
# Placeholder example file.
"""Placeholder TDMS reader that demonstrates reading a small time-series CSV sample.

Real TDMS reading would use a dedicated library; this script shows how to read a small sample file.
"""

import csv
from pathlib import Path

DATA = Path(__file__).parent / "sample_time_series.csv"

def main():
	if not DATA.exists():
		print(f"Sample time-series not found: {DATA}")
		return
	with DATA.open(newline='') as fh:
		reader = csv.DictReader(fh)
		rows = list(reader)
	print(f"Read {len(rows)} time points")
	if rows:
		print("First point:", rows[0])

if __name__ == '__main__':
	main()

