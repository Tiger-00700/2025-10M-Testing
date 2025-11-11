#!/usr/bin/env bash
set -euo pipefail
echo "examples/17_practices: running tiny exercise"
echo "Question: sum numbers 1..5"
python - <<'PY'
print('sum(1..5)=', sum(range(1,6)))
PY
exit 0
