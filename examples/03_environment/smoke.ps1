<# Placeholder example file. #>
Write-Output "[examples/03_environment] smoke: environment quick-check"
python - <<'PY'
import sys
print('python check: ok')
sys.exit(0)
PY
exit 0
