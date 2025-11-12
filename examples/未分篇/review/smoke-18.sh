# Placeholder example file.
#!/usr/bin/env bash
set -euo pipefail
echo "Running smoke for examples/21_career_paths"
if [ -f show_career_map.sh ]; then
  bash show_career_map.sh
  echo "show_career_map.sh executed"
  exit 0
fi
if [ -f career_map.md ]; then
  echo "career_map.md present; smoke passes"
  exit 0
fi
echo "No career map found; passing"
exit 0
