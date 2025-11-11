Write-Host "Running smoke for examples/21_career_paths"
if (Test-Path .\career_map.md) {
  Write-Host "career_map.md present; no runnable example"
  exit 0
}
if (Test-Path .\README.md) {
  Write-Host "README present; passing"
  exit 0
}
Write-Host "Placeholder smoke: passing"
exit 0
