#!/usr/bin/env bash
# Placeholder example file.
set -euo pipefail
echo "examples/18_performance: running micro-benchmark"
if [ -f perf_test.py ]; then
	echo "Invoking perf_test.py (small run)"
	python perf_test.py
	echo "Benchmark completed"
	exit 0
fi

echo "No perf_test.py found; nothing to run"
exit 0
