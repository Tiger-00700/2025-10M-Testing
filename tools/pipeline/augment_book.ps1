Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Paths
$repoRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSCommandPath))
$bookPath = Join-Path $repoRoot 'book/1022.2025.newbook.md'
$linksPath = Join-Path $repoRoot 'book/1022.2025.newbook.links.md'
$organizedLatest = Join-Path $repoRoot 'tools/reports/organized-latest.md'
$examplesDir = Join-Path $repoRoot 'examples'
$appendixDir = Join-Path $repoRoot 'appendix'
$outPath = Join-Path $repoRoot 'book/1022.2025.newbook.augmented.md'

if (Test-Path $linksPath) {
  Write-Host ("Using links-only book: {0}" -f ($linksPath.Replace($repoRoot + [IO.Path]::DirectorySeparatorChar, ''))) -ForegroundColor DarkGray
  $bookPath = $linksPath
}
if (-not (Test-Path $bookPath)) { throw "Book not found: $bookPath" }
if (-not (Test-Path $organizedLatest)) { throw "Organized latest not found: $organizedLatest (run organizer first)" }

# Helpers
function Get-Lines([string]$p){
  return Get-Content -LiteralPath $p
}

function Get-HeadingNodes([string[]]$lines){
  $nodes = @()
  for($i=0;$i -lt $lines.Count;$i++){
    $m = [regex]::Match($lines[$i], '^(#{1,6})\s+(.*)')
    if($m.Success){
      $level = $m.Groups[1].Value.Length
      $title = $m.Groups[2].Value.Trim()
      $nodes += [pscustomobject]@{ Level=$level; Title=$title; Line=$i }
    }
  }
  return $nodes
}

function Get-SectionRanges($nodes, $totalLines){
  # returns array of @{Start=int; End=int; Level=int; Title=string}
  $ranges = @()
  for($i=0;$i -lt $nodes.Count;$i++){
    $start = $nodes[$i].Line
    $level = $nodes[$i].Level
    # find next heading with level <= current
    $end = $totalLines-1
    for($j=$i+1;$j -lt $nodes.Count;$j++){
      if($nodes[$j].Level -le $level){ $end = $nodes[$j].Line - 1; break }
    }
    $ranges += [pscustomobject]@{ Start=$start; End=$end; Level=$level; Title=$nodes[$i].Title }
  }
  return $ranges
}

function Normalize([string]$s){
  $s = $s -replace '\s+', ''
  $s = $s -replace '[\p{P}-[._]]', ''  # keep dot/underscore for filenames
  $s = $s.ToLowerInvariant()
  return $s
}

function Guess-Lang([string]$ext){
  switch($ext.ToLowerInvariant()){
    '.py' { 'python' }
    '.ps1' { 'powershell' }
    '.sh' { 'bash' }
    '.sql' { 'sql' }
    '.java' { 'java' }
    '.scala' { 'scala' }
    '.yml' { 'yaml' }
    '.yaml' { 'yaml' }
    '.json' { 'json' }
    default { 'text' }
  }
}

function Load-TreeHeadings([string[]]$lines){
  (Get-HeadingNodes $lines) | ForEach-Object {
    [pscustomobject]@{ Level=$_.Level; Title=$_.Title; Key=(Normalize $_.Title) }
  }
}

function Find-BestHeading([string]$name, $headings){
  $k = Normalize $name
  $best = $null; $score = -1
  foreach($h in $headings){
    $overlap = 0
    # simple token overlap on substrings of 2 chars
    for($i=0;$i -lt ($k.Length-1);$i++){
      $bg = $k.Substring($i,2)
      if($h.Key.Contains($bg)){ $overlap++ }
    }
    if($overlap -gt $score){ $score=$overlap; $best=$h }
  }
  return $best
}

# Load contents
$bookLines = Get-Lines $bookPath
$bookNodes = Get-HeadingNodes $bookLines
$bookRanges = Get-SectionRanges $bookNodes $bookLines.Count

$orgLines = Get-Lines $organizedLatest
$orgHeadings = Load-TreeHeadings $orgLines

# Ensure per-chapter skeletons (for H2+ sections)
$insertions = New-Object 'System.Collections.Generic.Dictionary[int, System.Collections.Generic.List[string]]'
for($i=0;$i -lt $bookRanges.Count;$i++){
  $r = $bookRanges[$i]
  if($r.Level -ge 2){
    # Insert at end of section if not present
    $childLevel = [Math]::Min($r.Level+1,6)
    $s1 = ('{0} 学习目标' -f ('#' * $childLevel))
    $s2 = ('{0} 小结' -f ('#' * $childLevel))
    $s3 = ('{0} 练习' -f ('#' * $childLevel))
    $slice = $bookLines[$r.Start..$r.End] -join "`n"
    if($slice -notmatch [regex]::Escape($s1)){
      $blk = @()
      $blk += ''
      $blk += $s1
      $blk += ''
      $blk += $s2
      $blk += ''
      $blk += $s3
      if(-not $insertions.ContainsKey($r.End)){
        $insertions[$r.End] = New-Object 'System.Collections.Generic.List[string]'
      }
      $insertions[$r.End].Add(($blk -join "`n"))
    }
  }
}

# Gather attachments from examples/ and appendix/
$attachFiles = @()
if(Test-Path $examplesDir){ $attachFiles += Get-ChildItem -Path $examplesDir -Recurse -File }
if(Test-Path $appendixDir){ $attachFiles += Get-ChildItem -Path $appendixDir -Recurse -File }

foreach($f in $attachFiles){
  $name = [System.IO.Path]::GetFileNameWithoutExtension($f.Name)
  $target = Find-BestHeading $name $orgHeadings
  if(-not $target){ continue }
  # find in book the first heading whose normalized title contains target key
  $targetKey = $target.Key
  $cand = $bookNodes | Where-Object { (Normalize $_.Title).Contains($targetKey) } | Select-Object -First 1
  if(-not $cand){
    # fallback: same text match
    $cand = $bookNodes | Where-Object { $_.Title -eq $target.Title } | Select-Object -First 1
  }
  if(-not $cand){ continue }
  $br = $bookRanges | Where-Object { $_.Start -eq $cand.Line } | Select-Object -First 1
  if(-not $br){ continue }
  $childLevel = [Math]::Min($br.Level+1,6)
  $lang = Guess-Lang ([System.IO.Path]::GetExtension($f.Name))
  $hdr = ('{0} 附：示例与脚本 - {1}' -f ('#' * $childLevel), $f.Name) -join ''
  $rel = (Resolve-Path -LiteralPath $f.FullName).Path.Replace($repoRoot + [IO.Path]::DirectorySeparatorChar, '')
  $code = Get-Content -LiteralPath $f.FullName -Raw
  $blk = @()
  $blk += ''
  $blk += $hdr
  $blk += ''
  $blk += ('> Source: {0}' -f $rel)
  $blk += ''
  $blk += '<!-- augment:code -->'
  if([string]::IsNullOrWhiteSpace($lang)){
    $blk += '```'
  } else {
    $blk += ('```{0}' -f $lang)
  }
  $blk += $code
  $blk += '```'
  if(-not $insertions.ContainsKey($br.End)){
    $insertions[$br.End] = New-Object 'System.Collections.Generic.List[string]'
  }
  $insertions[$br.End].Add(($blk -join "`n"))
}

# Apply insertions from bottom to top to keep indices stable
$aug = New-Object System.Collections.Generic.List[string]
$aug.AddRange([string[]]$bookLines)
foreach($key in ($insertions.Keys | Sort-Object -Descending)){
  $content = ($insertions[$key] -join "`n")
  $aug.Insert($key+1, $content)
}

$aug -join "`n" | Set-Content -LiteralPath $outPath -Encoding UTF8
Write-Host ("Augmented book written: {0}" -f ($outPath.Replace($repoRoot + [IO.Path]::DirectorySeparatorChar, '')))
