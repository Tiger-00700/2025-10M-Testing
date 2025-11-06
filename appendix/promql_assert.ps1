param(
  [Parameter(Mandatory=$true)][string]$PromUrl,
  [Parameter(Mandatory=$true)][string]$Query,
  [ValidateSet('gt','ge','lt','le','eq','ne')][string]$Op = 'gt',
  [Parameter(Mandatory=$true)][double]$Threshold
)

Write-Host "[promql_assert.ps1] Query: $Query, Op: $Op, Threshold: $Threshold"
$encoded = [uri]::EscapeDataString($Query)
$url = "$PromUrl/api/v1/query?query=$encoded"
try {
  $resp = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 20
} catch {
  Write-Error "Request failed: $($_.Exception.Message)"
  exit 3
}

try {
  $json = $resp.Content | ConvertFrom-Json
  $values = @()
  foreach ($r in $json.data.result) {
    if ($r.value.Count -ge 2) { $values += [double]$r.value[1] }
  }
} catch {
  Write-Error "Parse failed: $($_.Exception.Message)"
  exit 3
}

if (-not $values -or $values.Count -eq 0) {
  Write-Error "No numeric values returned"
  exit 3
}

function Compare-Num($a, $b, $op){
  switch ($op) {
    'gt' { return $a -gt $b }
    'ge' { return $a -ge $b }
    'lt' { return $a -lt $b }
    'le' { return $a -le $b }
    'eq' { return $a -eq $b }
    'ne' { return $a -ne $b }
  }
}

$failed = @()
foreach ($v in $values) {
  $ok = Compare-Num -a $v -b $Threshold -op $Op
  if ($ok) { Write-Host "value=$v op=$Op threshold=$Threshold => PASS" }
  else { Write-Warning "value=$v op=$Op threshold=$Threshold => FAIL"; $failed += $v }
}

if ($failed.Count -gt 0) { Write-Error "Assertion failed for: $($failed -join ', ')"; exit 2 }
Write-Host "Assertion passed for all $($values.Count) series"
exit 0
