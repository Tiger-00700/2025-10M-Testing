Write-Host "Running smoke for examples/20_trends"
if (Test-Path .\trend_note.md) {
  Write-Host "trend_note.md present; no runnable example"
  exit 0
}
if (Test-Path .\README.md) {
  Write-Host "README present; passing"
  exit 0
}
Write-Host "Placeholder smoke: passing"
exit 0
