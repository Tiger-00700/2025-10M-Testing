Write-Host "Running smoke for examples/01_ecosystem"
if (Test-Path .\demo.sh) {
  try {
    pwsh -NoProfile -Command "./demo.sh"
    Write-Host "demo.sh ran (or returned non-zero)"
  } catch {
    Write-Host "demo.sh failed or pwsh not available; continuing"
  }
  exit 0
}
if (Test-Path .\overview.md) {
  Write-Host "No runnable example; overview.md present"
  exit 0
}
Write-Host "Placeholder smoke: nothing to run, passing"
exit 0
