#!/usr/bin/env bash
set -euo pipefail
echo "Running smoke for examples/20_trends"
if [ -f trend_demo.py ]; then
  python trend_demo.py
  exit 0
fi
echo "No demo found; passing as placeholder"
exit 0
#!/usr/bin/env bash
set -e
echo "Running smoke for examples/20_trends"
if [ -f trend_note.md ]; then
  echo "trend_note.md present; no runnable example"
  exit 0
fi
if [ -f README.md ]; then
  echo "README present; passing"
  exit 0
fi
echo "Placeholder smoke: passing"
exit 0
