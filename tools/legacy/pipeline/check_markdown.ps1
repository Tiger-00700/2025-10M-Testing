Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$repoRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSCommandPath))
$reportDir = Join-Path $repoRoot 'tools/reports'

# Config via environment variables
$cfg = @{}
$cfg.External = -not ($env:CHECK_EXTERNAL -eq '0')
$cfg.ExternalTimeoutSec = if([string]::IsNullOrWhiteSpace($env:CHECK_EXTERNAL_TIMEOUT)){ 10 } else { [int]$env:CHECK_EXTERNAL_TIMEOUT }
$cfg.ExternalFailOnWarn = ($env:CHECK_EXTERNAL_FAIL_ON_WARN -eq '1')
$cfg.Scope = if([string]::IsNullOrWhiteSpace($env:CHECK_SCOPE)){ 'organized' } else { $env:CHECK_SCOPE }
$cfg.CodeFenceMode = if([string]::IsNullOrWhiteSpace($env:CHECK_CODEFENCE_MODE)){ 'augmented-only' } else { $env:CHECK_CODEFENCE_MODE }
[System.Collections.Generic.HashSet[string]]$cfg.ExternalSkipDomains = [System.Collections.Generic.HashSet[string]]::new()
if(-not [string]::IsNullOrWhiteSpace($env:CHECK_EXTERNAL_SKIP_DOMAINS)){
  foreach($d in $env:CHECK_EXTERNAL_SKIP_DOMAINS.Split(',',[System.StringSplitOptions]::RemoveEmptyEntries)){
    [void]$cfg.ExternalSkipDomains.Add($d.Trim().ToLowerInvariant())
  }
}
$targets = @()
$orgLatest = Join-Path $repoRoot 'tools/reports/organized-latest.md'
$augBook = Join-Path $repoRoot 'book/1022.2025.newbook.augmented.md'
$fig = Join-Path $repoRoot 'book/附录-图表目录.md'
$code = Join-Path $repoRoot 'book/附录-代码清单.md'
$scr = Join-Path $repoRoot 'book/附录-脚本索引.md'
# Allow excluding organized reports via env var (CHECK_INCLUDE_ORGANIZED=0)
$includeOrganized = -not ($env:CHECK_INCLUDE_ORGANIZED -eq '0')
if($includeOrganized -and (Test-Path $orgLatest)){ $targets += Get-Item -LiteralPath $orgLatest }
if(Test-Path $augBook){ $targets += Get-Item -LiteralPath $augBook }
if(Test-Path $fig){ $targets += Get-Item -LiteralPath $fig }
if(Test-Path $code){ $targets += Get-Item -LiteralPath $code }
if(Test-Path $scr){ $targets += Get-Item -LiteralPath $scr }

$errors = New-Object System.Collections.Generic.List[string]
[System.Collections.Generic.List[string]]$warnings = [System.Collections.Generic.List[string]]::new()
[System.Collections.Generic.HashSet[string]]$failedExternal = [System.Collections.Generic.HashSet[string]]::new()
[System.Collections.Generic.HashSet[string]]$warnedExternal = [System.Collections.Generic.HashSet[string]]::new()
$externalCache = @{}

function Get-HttpClient {
  if(-not $script:httpClient){
    $handler = [System.Net.Http.HttpClientHandler]::new()
    $handler.AllowAutoRedirect = $true
    $script:httpClient = [System.Net.Http.HttpClient]::new($handler)
    $script:httpClient.Timeout = [TimeSpan]::FromSeconds($cfg.ExternalTimeoutSec)
    $script:httpClient.DefaultRequestHeaders.UserAgent.ParseAdd('Mozilla/5.0 (MarkdownChecker/1.0)')
    $script:httpClient.DefaultRequestHeaders.Accept.ParseAdd('text/html,application/xhtml+xml,*/*')
  }
  return $script:httpClient
}

function Test-ExternalUrl([string]$url){
  if($externalCache.ContainsKey($url)){ return $externalCache[$url] }
  if(-not $cfg.External){
    $externalCache[$url] = @{ Status='skip'; Code=$null; Message='external checks disabled' }
    return $externalCache[$url]
  }
  try {
    $u = [Uri]$url
    $host = $u.Host.ToLowerInvariant()
    foreach($dom in $cfg.ExternalSkipDomains){ if($host -like "*${dom}") { 
      $externalCache[$url] = @{ Status='skip'; Code=$null; Message="domain skipped: $dom" }
      return $externalCache[$url]
    }}
  } catch {}
  $client = Get-HttpClient
  $result = @{ Status='fail'; Code=$null; Message=$null }
  try {
    $req = [System.Net.Http.HttpRequestMessage]::new([System.Net.Http.HttpMethod]::Head, $url)
    $resp = $client.Send($req, [System.Net.Http.HttpCompletionOption]::ResponseHeadersRead)
    $code = [int]$resp.StatusCode
    $resp.Dispose(); $req.Dispose()
    if($code -eq 405 -or $code -eq 501){
      # fallback to GET with headers-only completion
      $req2 = [System.Net.Http.HttpRequestMessage]::new([System.Net.Http.HttpMethod]::Get, $url)
      $resp2 = $client.Send($req2, [System.Net.Http.HttpCompletionOption]::ResponseHeadersRead)
      $code = [int]$resp2.StatusCode
      $resp2.Dispose(); $req2.Dispose()
    }
    $result.Code = $code
    if($code -ge 200 -and $code -lt 400){
      $result.Status = 'ok'
    } elseif($code -in 401,403,429){
      $result.Status = 'warn'
    } else {
      $result.Status = 'fail'
    }
  } catch {
    $msg = $_.Exception.Message
    $result.Message = $msg
    if($msg -match '(timed out|resolve|Name or service not known|No such host|SSL|certificate)'){
      $result.Status = 'warn'
    } else {
      $result.Status = 'fail'
    }
  }
  $externalCache[$url] = $result
  return $result
}

function Add-Error($msg){ $script:errors.Add($msg) }
function Add-Warn($msg){ $script:warnings.Add($msg) }

foreach($t in $targets){
  $lines = Get-Content -LiteralPath $t.FullName
  $isAugmented = ($t.FullName -like '*newbook.augmented.md')
  $checkLinks = ($cfg.Scope -eq 'all') -or ($t.FullName -like '*organized-latest.md')
  $inFence = $false; $fenceLang = ''
  for($i=0;$i -lt $lines.Count;$i++){
    $line = $lines[$i]
    # code fence open/close
    if($line -match '^\s*```'){ 
      if(-not $inFence){
        $m = [regex]::Match($line,'^\s*```\s*([A-Za-z0-9_+-]*)')
        $fenceLang = $m.Groups[1].Value
        if([string]::IsNullOrWhiteSpace($fenceLang)){
          if($cfg.CodeFenceMode -eq 'all'){
            Add-Error( ('{0}:{1}: code fence missing language label' -f $t.FullName, ($i+1)) )
          } elseif($isAugmented){
            # only enforce for generated blocks with explicit marker
            $start = [Math]::Max(0, $i-5)
            $window = $lines[$start..$i]
            if($window -contains '<!-- augment:code -->'){
              Add-Error( ('{0}:{1}: code fence missing language label (generated block)' -f $t.FullName, ($i+1)) )
            }
          }
        }
        $inFence = $true
      } else {
        $inFence = $false
      }
      continue
    }
    if($inFence){ continue }
    if($checkLinks){
      # image links
      foreach($m in [regex]::Matches($line,'!\[(.*?)\]\((.*?)\)')){
        $path = $m.Groups[2].Value
        if($path -match '^(http|https)://'){
          $res = Test-ExternalUrl $path
          if($res.Status -eq 'fail'){
            if(-not $failedExternal.Contains($path)){
              Add-Error( ('{0}:{1}: external image link unreachable -> {2} (status={3})' -f $t.FullName, ($i+1), $path, ($res.Code ?? $res.Message)) )
              [void]$failedExternal.Add($path)
            }
          } elseif($res.Status -eq 'warn'){
            if(-not $warnedExternal.Contains($path)){
              Add-Warn ('{0}:{1}: external image link check warning -> {2} (status={3})' -f $t.FullName, ($i+1), $path, ($res.Code ?? $res.Message))
              [void]$warnedExternal.Add($path)
            }
          }
          continue
        }
        $full = Join-Path (Split-Path -Parent $t.FullName) $path
        if(-not (Test-Path $full)){
          # try repo-root relative
          $full2 = Join-Path $repoRoot $path
          if(-not (Test-Path $full2)){
            Add-Error( ('{0}:{1}: missing image file -> {2}' -f $t.FullName, ($i+1), $path) )
          }
        }
      }
      # markdown links
      foreach($m in [regex]::Matches($line,'\[(.*?)\]\((.*?)\)')){
        $href = $m.Groups[2].Value
        if($href -match '^(http|https)://'){
          $res = Test-ExternalUrl $href
          if($res.Status -eq 'fail'){
            if(-not $failedExternal.Contains($href)){
              Add-Error( ('{0}:{1}: external link unreachable -> {2} (status={3})' -f $t.FullName, ($i+1), $href, ($res.Code ?? $res.Message)) )
              [void]$failedExternal.Add($href)
            }
          } elseif($res.Status -eq 'warn'){
            if(-not $warnedExternal.Contains($href)){
              Add-Warn ('{0}:{1}: external link check warning -> {2} (status={3})' -f $t.FullName, ($i+1), $href, ($res.Code ?? $res.Message))
              [void]$warnedExternal.Add($href)
            }
          }
          continue
        }
        if($href -match '^(mailto):'){ continue }
        if($href -match '#'){
          $parts = $href.Split('#',2)
          $hrefPath = $parts[0]
        } else { $hrefPath = $href }
        if([string]::IsNullOrWhiteSpace($hrefPath)){
          continue
        }
        $full = Join-Path (Split-Path -Parent $t.FullName) $hrefPath
        if(-not (Test-Path $full)){
          $full2 = Join-Path $repoRoot $hrefPath
          if(-not (Test-Path $full2)){
            Add-Error( ('{0}:{1}: broken link -> {2}' -f $t.FullName, ($i+1), $href) )
          }
        }
      }
    }
  }
}

if($errors.Count -gt 0){
  Write-Host 'Markdown checks found issues:'
  $errors | ForEach-Object { Write-Host ' - ' $_ }
  # Also write warnings if present
  if($warnings.Count -gt 0){
    Write-Host 'Warnings:' -ForegroundColor Yellow
    $warnings | ForEach-Object { Write-Host ' - ' $_ -ForegroundColor Yellow }
  }
  # Write report file
  New-Item -ItemType Directory -Force -Path $reportDir | Out-Null
  $ts = Get-Date -Format 'yyyyMMdd-HHmmss'
  $reportPath = Join-Path $reportDir ("markdown-check-$ts.md")
  @(
    '# Markdown Check Report'
    "- Timestamp: $ts"
    "- Scope: $($cfg.Scope)"
    "- External checks: $($cfg.External) (timeout=$($cfg.ExternalTimeoutSec)s, failOnWarn=$($cfg.ExternalFailOnWarn))"
    ''
    '## Errors'
  ) + ($errors | ForEach-Object { "- $_" }) + @('','## Warnings') + ($warnings | ForEach-Object { "- $_" }) | Set-Content -LiteralPath $reportPath -Encoding UTF8
  exit 1
} else {
  if($warnings.Count -gt 0){
    if($cfg.ExternalFailOnWarn){ $exitCode = 1 } else { $exitCode = 0 }
    Write-Host "Markdown checks passed with warnings ($($warnings.Count))." -ForegroundColor Yellow
    New-Item -ItemType Directory -Force -Path $reportDir | Out-Null
    $ts = Get-Date -Format 'yyyyMMdd-HHmmss'
    $reportPath = Join-Path $reportDir ("markdown-check-$ts.md")
    @(
      '# Markdown Check Report'
      "- Timestamp: $ts"
      "- Scope: $($cfg.Scope)"
      "- External checks: $($cfg.External) (timeout=$($cfg.ExternalTimeoutSec)s, failOnWarn=$($cfg.ExternalFailOnWarn))"
      ''
      '## Errors'
      '- (none)'
      ''
      '## Warnings'
    ) + ($warnings | ForEach-Object { "- $_" }) | Set-Content -LiteralPath $reportPath -Encoding UTF8
    if($exitCode -ne 0){ exit $exitCode }
  } else {
    Write-Host 'Markdown checks passed.'
  }
}
