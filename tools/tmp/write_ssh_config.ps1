Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$userHome = $env:HOME
if ([string]::IsNullOrWhiteSpace($userHome)) { $userHome = $env:USERPROFILE }
if ([string]::IsNullOrWhiteSpace($userHome)) { throw 'Cannot determine HOME/USERPROFILE' }

$sshDir = Join-Path $userHome '.ssh'
if (-not (Test-Path -LiteralPath $sshDir)) {
  New-Item -ItemType Directory -Force -Path $sshDir | Out-Null
}

$configPath = Join-Path $sshDir 'config'
$configLines = @(
  'Host github.com',
  '  HostName github.com',
  '  User git',
  '  IdentityFile ~/.ssh/id_ed25519',
  '  IdentitiesOnly yes'
)
$configLines | Set-Content -LiteralPath $configPath -Encoding UTF8

Write-Host "Wrote SSH config to: $configPath" -ForegroundColor Green
Get-Content -LiteralPath $configPath