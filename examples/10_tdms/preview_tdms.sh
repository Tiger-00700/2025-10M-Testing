#!/usr/bin/env bash
# Placeholder example file.
set -euo pipefail
echo "examples/10_tdms preview"
if [ -f read_tdms.py ]; then
	echo "Invoking read_tdms.py"
	python read_tdms.py
fi

echo "Preview complete"
exit 0
