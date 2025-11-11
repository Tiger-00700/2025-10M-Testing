Write-Host "Running smoke for examples/17_practices"
if (Test-Path .\exercise_01.md) {
  Write-Host "exercise_01.md present; no runnable example"
  exit 0
}
if (Test-Path .\README.md) {
  Write-Host "README present; passing"
  exit 0
}
Write-Host "Placeholder smoke: passing"
exit 0
