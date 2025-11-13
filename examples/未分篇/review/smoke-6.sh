# Placeholder example file.
#!/usr/bin/env bash
set -euo pipefail
echo "Running smoke for examples/10_tdms"
if [ -f read_tdms.py ]; then
	python read_tdms.py
	echo "read_tdms.py executed"
	exit 0
fi
if [ -f preview_tdms.sh ]; then
	bash preview_tdms.sh
	echo "preview_tdms.sh executed"
	exit 0
fi
echo "No runnable TDMS example found; passing"
exit 0
