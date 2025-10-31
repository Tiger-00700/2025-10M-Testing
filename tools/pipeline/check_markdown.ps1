Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$repoRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSCommandPath))
$targets = @()
$orgLatest = Join-Path $repoRoot 'tools/reports/organized-latest.md'
$augBook = Join-Path $repoRoot 'book/1022.2025.newbook.augmented.md'
$fig = Join-Path $repoRoot 'book/附录-图表目录.md'
$code = Join-Path $repoRoot 'book/附录-代码清单.md'
$scr = Join-Path $repoRoot 'book/附录-脚本索引.md'
if(Test-Path $orgLatest){ $targets += Get-Item -LiteralPath $orgLatest }
if(Test-Path $augBook){ $targets += Get-Item -LiteralPath $augBook }
if(Test-Path $fig){ $targets += Get-Item -LiteralPath $fig }
if(Test-Path $code){ $targets += Get-Item -LiteralPath $code }
if(Test-Path $scr){ $targets += Get-Item -LiteralPath $scr }

$errors = New-Object System.Collections.Generic.List[string]

function Add-Error($msg){ $script:errors.Add($msg) }

foreach($t in $targets){
  $lines = Get-Content -LiteralPath $t.FullName
  $isAugmented = ($t.FullName -like '*newbook.augmented.md')
  $checkLinks = ($t.FullName -like '*organized-latest.md')
  $inFence = $false; $fenceLang = ''
  for($i=0;$i -lt $lines.Count;$i++){
    $line = $lines[$i]
    # code fence open/close
    if($line -match '^\s*```'){ 
      if(-not $inFence){
        $m = [regex]::Match($line,'^\s*```\s*([A-Za-z0-9_+-]*)')
        $fenceLang = $m.Groups[1].Value
        if([string]::IsNullOrWhiteSpace($fenceLang)){
          if($isAugmented){
            # only enforce for generated blocks with explicit marker
            $start = [Math]::Max(0, $i-5)
            $window = $lines[$start..$i]
            if($window -contains '<!-- augment:code -->'){
              Add-Error( ('{0}:{1}: code fence missing language label (generated block)' -f $t.FullName, ($i+1)) )
            }
          } else {
            Add-Error( ('{0}:{1}: code fence missing language label' -f $t.FullName, ($i+1)) )
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
        if($path -match '^(http|https)://'){ continue }
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
        if($href -match '^(http|https|mailto):'){ continue }
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
  exit 1
} else {
  Write-Host 'Markdown checks passed.'
}
