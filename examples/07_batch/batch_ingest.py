#!/usr/bin/env python3
"""Simple batch ingest example that reads a local sample CSV and prints a count.

This is intentionally dependency-free (uses csv from stdlib).
"""

import csv
from pathlib import Path

DATA = Path(__file__).parent / "sample_data.csv"

def main():
	if not DATA.exists():
		print(f"Sample data not found: {DATA}")
		return
	with DATA.open(newline='') as fh:
		reader = csv.DictReader(fh)
		rows = list(reader)
	print(f"Read {len(rows)} rows from {DATA}")
	# print first row as example
	if rows:
		print("First row:", rows[0])

if __name__ == '__main__':
	main()
