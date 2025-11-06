param(
  [string]$Base = 'http://localhost:16686',
  [Parameter(Mandatory=$true)][string]$Service,
  [string]$Operation = '',
  [int]$Limit = 20,
  [string]$Lookback = '1h',
  [int]$MinCount = 1
)

Write-Host "[jaeger_assert.ps1] service=$Service op=$Operation lookback=$Lookback limit=$Limit min-count=$MinCount"

try {
  $params = @{ service = $Service; limit = $Limit; lookback = $Lookback }
  if ($Operation) { $params.operation = $Operation }
  $qs = ($params.GetEnumerator() | ForEach-Object { "{0}={1}" -f [uri]::EscapeDataString($_.Key), [uri]::EscapeDataString([string]$_.Value) }) -join '&'
  $url = "$($Base.TrimEnd('/'))/api/traces?$qs"
}
catch {
  Write-Error "Failed to build request URL: $($_.Exception.Message)"
  exit 3
}

try {
  $resp = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 20
}
catch {
  Write-Error "Request failed: $($_.Exception.Message)"
  Write-Host "Hint: Test connectivity -> Invoke-WebRequest -Uri '$($Base.TrimEnd('/'))/api/services' -UseBasicParsing" -ForegroundColor Yellow
  exit 3
}

try {
  $json = $resp.Content | ConvertFrom-Json
  $traces = @($json.data)
  $count = $traces.Count
  Write-Host "Found $count traces for service=$Service (operation=$($Operation -ne '' ? $Operation : '*')) lookback=$Lookback"
}
catch {
  Write-Error "Parse failed: $($_.Exception.Message)"
  exit 3
}

if ($count -ge $MinCount) {
  exit 0
} else {
  Write-Error "Assertion failed: expected at least $MinCount traces, got $count"
  exit 2
}
