# Placeholder example file.
# This script is a placeholder for the batch demo.
#!/usr/bin/env bash
set -euo pipefail
echo "examples/07_batch batch demo"
if [ -f batch_ingest.py ]; then
	echo "Invoking batch_ingest.py"
	python batch_ingest.py
fi

echo "Batch demo complete"
exit 0
