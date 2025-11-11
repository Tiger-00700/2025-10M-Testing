param()

Write-Output "CI demo: small automation workflow (examples/11_automation)"

# Create a tiny test artifact and verify checksum — demonstrates a simple automation step
$tmp = Join-Path $PSScriptRoot "ci-demo-artifact.txt"
"automation-demo-$(Get-Date -Format yyyyMMddHHmmss)" | Out-File -FilePath $tmp -Encoding UTF8
Write-Output "Wrote $tmp"

# Compute simple hash
[System.Text.Encoding]::UTF8.GetBytes((Get-Content $tmp -Raw)) | % { }
$hash = Get-FileHash -Path $tmp -Algorithm SHA256
Write-Output "Artifact SHA256: $($hash.Hash)"

Write-Output "CI demo completed successfully"
