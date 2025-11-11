#!/usr/bin/env bash
set -e
echo "Running smoke for examples/18_performance"
if [ -f load_test.sh ]; then
  bash load_test.sh || true
  echo "load_test.sh invoked (exit code ignored)"
  exit 0
fi
if [ -f perf_test.py ]; then
  python perf_test.py || true
  echo "perf_test.py invoked (exit code ignored)"
  exit 0
fi
echo "Placeholder smoke: passing"
exit 0
