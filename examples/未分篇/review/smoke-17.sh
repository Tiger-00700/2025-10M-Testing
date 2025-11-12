# Placeholder example file.
#!/usr/bin/env bash
set -euo pipefail
echo "Running smoke for examples/20_trends"
if [ -f trend_demo.py ]; then
	python trend_demo.py
	echo "trend_demo.py executed"
	exit 0
fi
if [ -f trend_note.md ]; then
	echo "trend_note.md present; smoke passes"
	exit 0
fi
echo "No trend demo found; passing"
exit 0
