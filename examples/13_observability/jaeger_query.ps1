param(
  [string]$Base = 'http://localhost:16686',
  [Parameter(Mandatory=$true)][string]$Service,
  [string]$Operation = '',
  [int]$Limit = 20,
  [string]$Lookback = '1h'
)

$params = @{ service = $Service; limit = $Limit; lookback = $Lookback }
if ($Operation) { $params.operation = $Operation }
$qs = ($params.GetEnumerator() | ForEach-Object { "{0}={1}" -f [uri]::EscapeDataString($_.Key), [uri]::EscapeDataString([string]$_.Value) }) -join '&'
$url = "$($Base.TrimEnd('/'))/api/traces?$qs"
Write-Host "GET $url"
$resp = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 20
($resp.Content | ConvertFrom-Json).data | ForEach-Object {
  $traceId = $_.traceID
  $spans = $_.spans.Count
  Write-Host ("traceID={0} spans={1}" -f $traceId, $spans)
}
