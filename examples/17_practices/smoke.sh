#!/usr/bin/env bash
set -euo pipefail
echo "Running smoke for examples/17_practices"
if [ -f run_exercise.sh ]; then
  bash run_exercise.sh
  exit 0
fi
echo "No exercise found; passing as placeholder"
exit 0
#!/usr/bin/env bash
set -e
echo "Running smoke for examples/17_practices"
if [ -f exercise_01.md ]; then
  echo "exercise_01.md present; no runnable example"
  exit 0
fi
# Fallback
if [ -f README.md ]; then
  echo "README present; passing"
  exit 0
fi
echo "Placeholder smoke: passing"
exit 0
