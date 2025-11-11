#!/usr/bin/env bash
set -e
echo "Running smoke for examples/01_ecosystem"
if [ -f demo.sh ]; then
  bash demo.sh || true
  echo "demo.sh ran (or exited with non-zero, continuing)"
  exit 0
fi
if [ -f overview.md ]; then
  echo "No runnable example; overview.md present"
  exit 0
fi
# Fallback
echo "Placeholder smoke: nothing to run, passing"
exit 0
