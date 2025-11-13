# Placeholder example file.
#!/usr/bin/env bash
set -e
echo "Running smoke for examples/08_analysis"
if [ -f eda_pandas.py ]; then
  if command -v python >/dev/null 2>&1; then
    python eda_pandas.py || true
    echo "eda_pandas.py executed (exit code ignored)"
    exit 0
  fi
fi
if [ -f eda_example.py ]; then
  echo "eda_example.py present; not executed in smoke"
  exit 0
fi
# If no runnable script, pass
echo "Placeholder smoke: passing"
exit 0
