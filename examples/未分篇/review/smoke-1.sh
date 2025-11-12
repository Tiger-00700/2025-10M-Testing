#!/usr/bin/env bash
# Placeholder example file.
set -euo pipefail
echo "[examples/03_environment] smoke: environment quick-check"
python - <<'PY'
import sys
print('python check: ok')
sys.exit(0)
PY
exit 0
#!/usr/bin/env bash
# Placeholder example file.
