Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$repoRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSCommandPath))
$organizedLatest = Join-Path $repoRoot 'tools/reports/organized-latest.md'
$examplesDir = Join-Path $repoRoot 'examples'
$appendixDir = Join-Path $repoRoot 'appendix'

if (-not (Test-Path $organizedLatest)) { throw "Organized latest not found: $organizedLatest" }

$lines = Get-Content -LiteralPath $organizedLatest

# Capture heading stack for context
$items = @()
$stack = New-Object System.Collections.Stack
for($i=0;$i -lt $lines.Count;$i++){
  $line = $lines[$i]
  $hm = [regex]::Match($line, '^(#{1,6})\s+(.*)')
  if($hm.Success){
    $lvl = $hm.Groups[1].Value.Length
    $title = $hm.Groups[2].Value.Trim()
    while($stack.Count -gt 0 -and $stack.Peek().Level -ge $lvl){ [void]$stack.Pop() }
    $null = $stack.Push([pscustomobject]@{ Level=$lvl; Title=$title })
    continue
  }
  # Images
  foreach($m in [regex]::Matches($line, '!\[(.*?)\]\((.*?)\)')){
    $path = $m.Groups[2].Value
    $ctx = ($stack.ToArray() | Sort-Object Level | ForEach-Object { $_.Title }) -join ' > '
    $items += [pscustomobject]@{ Type='image'; Alt=$m.Groups[1].Value; Path=$path; Context=$ctx; Line=$i+1 }
  }
  # Code fence openers
  $fm = [regex]::Match($line, '^\s*```(\w+)?')
  if($fm.Success){
    $lang = ($fm.Groups[1].Value)
    $ctx = ($stack.ToArray() | Sort-Object Level | ForEach-Object { $_.Title }) -join ' > '
    $items += [pscustomobject]@{ Type='code'; Lang=$lang; Context=$ctx; Line=$i+1 }
  }
}

# Write appendices
$bookDir = Join-Path $repoRoot 'book'
$figOut = Join-Path $bookDir '附录-图表目录.md'
$codeOut = Join-Path $bookDir '附录-代码清单.md'
$scrOut = Join-Path $bookDir '附录-脚本索引.md'

# 图表目录
$fig = @('# 附录：图表目录','')
$ix = 1
foreach($it in $items | Where-Object { $_.Type -eq 'image' }){
  $fig += ('- 图 {0}: {1} ({2})  —— 位置: {3}' -f $ix, ($it.Alt -replace '\s+',' '), $it.Path, $it.Context)
  $ix++
}
$fig | Set-Content -LiteralPath $figOut -Encoding UTF8

# 代码清单
$cod = @('# 附录：代码清单','')
$jx = 1
foreach($it in $items | Where-Object { $_.Type -eq 'code' }){
  $lang = if([string]::IsNullOrWhiteSpace($it.Lang)){'(未标注)'}else{$it.Lang}
  $cod += ('- 代码块 {0}: {1}  —— 位置: {2}（第{3}行）' -f $jx, $lang, $it.Context, $it.Line)
  $jx++
}
$cod | Set-Content -LiteralPath $codeOut -Encoding UTF8

# 脚本索引（来自 /appendix 与 /examples）
$si = @('# 附录：脚本索引','')
$files = @()
if(Test-Path $examplesDir){ $files += Get-ChildItem -Path $examplesDir -Recurse -File }
if(Test-Path $appendixDir){ $files += Get-ChildItem -Path $appendixDir -Recurse -File }
foreach($f in $files){
  $rel = (Resolve-Path -LiteralPath $f.FullName).Path.Replace($repoRoot + [IO.Path]::DirectorySeparatorChar, '')
  $si += ('- {0}' -f $rel)
}
$si | Set-Content -LiteralPath $scrOut -Encoding UTF8

Write-Host ('Appendices written: {0}, {1}, {2}' -f ($figOut.Replace($repoRoot + [IO.Path]::DirectorySeparatorChar, '')), ($codeOut.Replace($repoRoot + [IO.Path]::DirectorySeparatorChar, '')), ($scrOut.Replace($repoRoot + [IO.Path]::DirectorySeparatorChar, '')))
