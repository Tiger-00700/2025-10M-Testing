#!/usr/bin/env bash
set -euo pipefail
echo "examples/01_ecosystem demo"

cat <<'DIAG'
Data pipeline topology (ASCII art):

	[producer] ---> [ingest (stream/batch)] ---> [storage]
																				 \
																					-> [analysis]

DIAG

echo "Running a tiny synthetic data producer and consumer (stdout)..."
python - <<'PY'
import sys, time
for i in range(3):
		print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} PRODUCER value={i}")
		sys.stdout.flush()
		time.sleep(0.1)
print("Consumer: received 3 records (simulated)")
PY

echo "Demo complete. See README.md and overview.md for details."
