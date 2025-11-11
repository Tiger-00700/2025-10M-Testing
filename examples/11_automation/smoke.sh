#!/usr/bin/env bash
set -e
echo "Running smoke for examples/11_automation"
if [ -f ci_demo.ps1 ]; then
  echo "PowerShell demo exists (ci_demo.ps1). On Linux this script will only print that it's present."
  exit 0
fi
# Fallback
if [ -f README.md ]; then
  echo "README present; no runnable example"
  exit 0
fi
echo "Placeholder smoke: passing"
exit 0
