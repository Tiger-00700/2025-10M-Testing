#!/usr/bin/env bash
set -euo pipefail

# Simple validator for example skeletons. Exits 1 if any directory is missing README or lacks a sample file.
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

missing=0
for d in "${DIRS[@]}"; do
  path="$ROOT_DIR/$d"
  echo "Checking $d"
  if [ ! -d "$path" ]; then
    echo "  MISSING: directory not found: $d"
    missing=1
    continue
  fi
  if [ ! -f "$path/README.md" ]; then
    echo "  MISSING: README.md in $d"
    missing=1
  fi
  # check for at least one sample file: .sh .py .md .ps1 .ipynb
  shopt -s nullglob || true
  samples=("$path"/*.sh "$path"/*.py "$path"/*.ps1 "$path"/*.ipynb "$path"/*.md)
  found=false
  for s in "${samples[@]}"; do
    # ignore README.md
    if [ "$(basename "$s")" != "README.md" ]; then
      found=true
      break
    fi
  done
  if [ "$found" = false ]; then
    echo "  MISSING: no sample files found in $d"
    missing=1
  fi
done

if [ "$missing" -ne 0 ]; then
  echo "Validation failed: some example directories are incomplete"
  exit 1
fi

echo "All example directories have README and at least one sample file."
