#!/usr/bin/env bash
set -e
echo "Running smoke for examples/21_career_paths"
if [ -f career_map.md ]; then
  echo "career_map.md present; no runnable example"
  exit 0
fi
if [ -f README.md ]; then
  echo "README present; passing"
  exit 0
fi
echo "Placeholder smoke: passing"
exit 0
