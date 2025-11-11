#!/usr/bin/env python3
"""Tiny trend demo: generate a small series and print a simple trend (slope).

This example has no external deps and can run on CI runners.
"""
from statistics import mean

def generate_series(n=7):
	return [i + (i%3 - 1)*0.1 for i in range(n)]

def simple_slope(series):
	# compute simple difference-based slope estimate
	n = len(series)
	if n < 2:
		return 0.0
	diffs = [series[i+1] - series[i] for i in range(n-1)]
	return mean(diffs)

def main():
	s = generate_series()
	print("Series:", s)
	slope = simple_slope(s)
	print(f"Estimated slope (mean diff): {slope:.4f}")

if __name__ == '__main__':
	main()

