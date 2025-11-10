#!/usr/bin/env bash
set -euo pipefail

# Run lightweight smoke tests for example directories.
# On Linux runners: run .sh or .py examples. Skip PowerShell files.

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

DIRS=(
  "examples/advanced_methods"
  "examples/01_ecosystem"
  "examples/07_batch"
  "examples/08_analysis"
  "examples/10_tdms"
  "examples/11_automation"
  "examples/17_practices"
  "examples/18_performance"
  "examples/20_trends"
  "examples/21_career_paths"
)

failed=0
for d in "${DIRS[@]}"; do
  echo "\n=== Smoke: $d ==="
  path="$ROOT_DIR/$d"
  if [ ! -d "$path" ]; then
    echo "  SKIP: directory not found"
    continue
  fi
  # prefer shell script
  if [ -x "$path/smoke.sh" ] || [ -f "$path/smoke.sh" ]; then
    echo "  Running smoke.sh"
    bash "$path/smoke.sh" || { echo "smoke.sh failed for $d"; failed=1; }
    continue
  fi
  # prefer python examples
  py=$(ls "$path"/*.py 2>/dev/null | head -n1 || true)
  if [ -n "$py" ]; then
    echo "  Running python $py"
    python3 "$py" || { echo "python example failed for $d"; failed=1; }
    continue
  fi
  # fallback: if only README exists, just print it
  if [ -f "$path/README.md" ]; then
    echo "  INFO: Only README present for $d"
    continue
  fi
  echo "  WARN: No runnable example found for $d"
done

if [ "$failed" -ne 0 ]; then
  echo "One or more smoke tests failed"
  exit 1
fi

echo "All smoke tests passed (or directories skipped)."
