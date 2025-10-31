<#
.SYNOPSIS
  Assemble book content by outline with exact and fuzzy matching (fixed PartKey + outline proximity).

.DESCRIPTION
  Reads outline from 'book/篇章结构.md', assembles content primarily from
  'book/1022.2025.newbook.md' (base) and backfills from 'book/1022.2025.book.md' (source).
  Uses normalization, alias mapping, and bigram Dice fuzzy matching with level-aware thresholds,
  plus same-篇 proximity via per-node PartKey. Outputs organized manuscript and logs under tools/reports.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function New-ReportsDir {
  $dir = Join-Path -Path 'tools' -ChildPath 'reports'
  if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir | Out-Null }
  return $dir
}

function Normalize-Whitespace([string]$s) {
  if (-not $s) { return '' }
  return ($s -replace "\s+", ' ').Trim()
}

function Remove-Invisible([string]$s) {
  if (-not $s) { return '' }
  $pattern = "[\u200B-\u200F\u202A-\u202E\u2066-\u2069]"
  return ($s -replace $pattern, '')
}

function Unify-Punctuation([string]$s) {
  if (-not $s) { return '' }
  $map = @{}
  $map[[string][char]0xFF0C] = ','  # ，
  $map[[string][char]0x3001] = ','  # 、
  $map[[string][char]0x3002] = '.'  # 。
  $map[[string][char]0xFF1A] = ':'  # ：
  $map[[string][char]0xFF1B] = ';'  # ；
  $map[[string][char]0xFF08] = '('  # （
  $map[[string][char]0xFF09] = ')'  # ）
  $map[[string][char]0x3010] = '['  # 【
  $map[[string][char]0x3011] = ']'  # 】
  $map[[string][char]0x201C] = '"'  # “
  $map[[string][char]0x201D] = '"'  # ”
  $map[[string][char]0x2018] = "'"  # ‘
  $map[[string][char]0x2019] = "'"  # ’
  $map[[string][char]0x300A] = ''    # 《
  $map[[string][char]0x300B] = ''    # 》
  foreach ($k in $map.Keys) { $s = $s.Replace($k, $map[$k]) }
  return $s
}

function Convert-ChineseNumerals([string]$s) {
  if (-not $s) { return '' }
  $digits = @{'零'='0';'一'='1';'二'='2';'三'='3';'四'='4';'五'='5';'六'='6';'七'='7';'八'='8';'九'='9'}
  foreach ($k in $digits.Keys) { $s = $s -replace $k, $digits[$k] }
  $s = $s -replace '第\s*([0-9一二三四五六七八九十百千]+)\s*[章节篇]', '$1'
  $s = $s -replace '[章节篇附录]',''
  return $s
}

function Normalize-Title([string]$s) {
  $s = Remove-Invisible $s
  $s = Unify-Punctuation $s
  $s = Convert-ChineseNumerals $s
  # drop bracketed/parenthetical segments entirely
  $s = ($s -replace "\([^\)]*\)", ' ')
  $s = ($s -replace "\[[^\]]*\]", ' ')
  $s = ($s -replace "[\[\](){}<>]", ' ')
  $s = ($s -replace "[`"'“”‘’]", '')
  $s = ($s -replace "\s+", ' ').Trim().ToLowerInvariant()
  return $s
}

function Normalize-ForFuzzy([string]$s) {
  $s = Normalize-Title $s
  # drop numbering like 9, 9.1, 4.1.1 and other digits to improve title-only similarity
  $s = ($s -replace '^\s*\d+(?:\.\d+)*\s*', ' ')
  $s = ($s -replace '\d+', ' ')
  # unify common conjunctions and synonyms to improve matching recall
  $s = ($s -replace '[与及和]', '与')
  $s = ($s -replace '特性|性质', '特点')
  $s = ($s -replace '部署|构建|安装', '搭建')
  $s = ($s -replace '分类', '类型')
  $s = ($s -replace '意义|价值', '重要性')
  $s = ($s -replace "[\p{P}\p{S}]", ' ')
  $s = Normalize-Whitespace $s
  return $s
}

function Get-AliasKeys([string]$norm) {
  $aliases = @{
    '概述'=@('简介','总览','引言');
    '架构设计原则'=@('架构原则','设计原则','架构要点','架构准则');
    '生态系统层次'=@('生态系统层级','生态分层');
    '技术栈及其应用场景'=@('技术栈与应用场景','技术栈应用场景','技术栈和应用场景');
    '测试环境类型与特点'=@('测试环境类型','环境类型与特点','环境类型','类型与特点','测试环境特点');
    '本地测试环境搭建'=@('本地环境搭建','搭建本地测试环境','本地测试环境部署','本地环境部署');
    '单机模式搭建'=@('单机模式环境搭建','单机部署','单机模式部署');
    '伪分布式模式搭建'=@('伪分布式部署','伪分布式环境搭建');
    '基于 docker 的本地环境'=@('docker 本地环境','docker 环境搭建','基于 docker 的环境');
    '数据存储重要性'=@('数据存储的重要性','存储重要性');
    '测试环境需求分析与规划'=@('测试环境需求分析','测试环境规划','环境需求分析与规划');
    '测试环境需求分析维度'=@('测试环境需求维度','环境需求分析维度','需求分析维度')
  }
  $out = New-Object System.Collections.Generic.List[string]
  foreach ($k in $aliases.Keys) {
    if ($norm -eq (Normalize-Title $k)) {
      foreach ($v in $aliases[$k]) { $out.Add((Normalize-Title $v)) }
    }
  }
  return $out
}

function Get-Bigrams([string]$s) {
  if (-not $s) { return @() }
  $s = ($s -replace '\s+', '')
  $res = @()
  for ($i=0; $i -lt $s.Length-1; $i++) { $res += $s.Substring($i,2) }
  return $res
}

function FuzzyScore([string]$a, [string]$b) {
  $aN = Normalize-ForFuzzy $a
  $bN = Normalize-ForFuzzy $b
  if ([string]::IsNullOrWhiteSpace($aN) -or [string]::IsNullOrWhiteSpace($bN)) { return 0.0 }
  if ($aN -eq $bN) { return 1.0 }
  $A = (Get-Bigrams $aN)
  $B = (Get-Bigrams $bN)
  $lenA = @($A).Length
  $lenB = @($B).Length
  if ($lenA -eq 0 -or $lenB -eq 0) { return 0.0 }
  $setA = @{}
  foreach ($x in $A) { if ($setA.ContainsKey($x)) { $setA[$x]++ } else { $setA[$x]=1 } }
  $inter=0
  foreach ($y in $B) { if ($setA.ContainsKey($y) -and $setA[$y] -gt 0) { $inter++; $setA[$y]-- } }
  $score = (2.0 * $inter) / ($lenA + $lenB)
  if ($aN.Length -ge 4 -and $bN.Contains($aN)) { $score = [Math]::Min(1.0, $score + 0.05) }
  if ($bN.Length -ge 4 -and $aN.Contains($bN)) { $score = [Math]::Min(1.0, $score + 0.05) }
  return [Math]::Round($score,3)
}

class SectionNode {
  [int]$Level
  [string]$Title
  [string]$NormKey
  [int]$StartLine
  [int]$EndLine
  [string]$PartKey
}

function Build-SectionIndex([string[]]$lines) {
  $nodes = New-Object System.Collections.Generic.List[SectionNode]
  $currentPartKey = ''
  for ($i=0; $i -lt $lines.Length; $i++) {
    $line = $lines[$i]
    if ($line -match '^(#+)\s+(.*)$') {
      $level = $Matches[1].Length
      $title = $Matches[2].Trim()
      if ($level -le 2) { $currentPartKey = (Normalize-Title $title) }
      $node = [SectionNode]::new()
      $node.Level=$level; $node.Title=$title; $node.NormKey=(Normalize-Title $title)
      $node.StartLine=$i; $node.PartKey=$currentPartKey
      $nodes.Add($node)
    }
  }
  for ($j=0; $j -lt $nodes.Count; $j++) {
    $curr = $nodes[$j]
    $nextStart = $lines.Length
    for ($k=$j+1; $k -lt $nodes.Count; $k++) {
      if ($nodes[$k].Level -le $curr.Level) { $nextStart = $nodes[$k].StartLine; break }
    }
    $curr.EndLine = $nextStart - 1
  }
  return $nodes
}

function Find-Candidate([System.Collections.Generic.List[SectionNode]]$index, [string]$query, [int]$prefLevel, [string]$prefPart) {
  $norm = Normalize-Title $query
  $exact = $index | Where-Object { $_.NormKey -eq $norm -and ($prefLevel -le 0 -or $_.Level -eq $prefLevel) }
  if ($exact) { return @{ mode='exact'; node=$exact[0]; score=1.0 } }
  foreach ($alias in (Get-AliasKeys $norm)) {
    $hit = $index | Where-Object { $_.NormKey -eq $alias -and ($prefLevel -le 0 -or $_.Level -eq $prefLevel) }
    if ($hit) { return @{ mode='alias'; node=$hit[0]; score=0.98 } }
    # alias any-level fall back
    $hitAny = $index | Where-Object { $_.NormKey -eq $alias }
    if ($hitAny) { return @{ mode='alias-any'; node=$hitAny[0]; score=0.96 } }
  }
  $exactAny = $index | Where-Object { $_.NormKey -eq $norm }
  if ($exactAny) { return @{ mode='exact-any'; node=$exactAny[0]; score=0.96 } }
  $best=$null; $bestScore=0.0
  foreach ($n in $index) {
    $s = FuzzyScore $query $n.Title
    if ($prefPart -and $n.PartKey -eq $prefPart) { $s = [Math]::Min(1.0, $s + 0.10) }
    if ($prefLevel -gt 0 -and $n.Level -eq $prefLevel) { $s = [Math]::Min(1.0, $s + 0.03) }
    if ($s -gt $bestScore) { $bestScore=$s; $best=$n }
  }
  # slightly relax thresholds to recover borderline matches
  $threshold = if ($prefLevel -le 2) { 0.62 } elseif ($prefLevel -eq 3) { 0.66 } else { 0.70 }
  if ($best -and $bestScore -ge $threshold) { return @{ mode='fuzzy'; node=$best; score=$bestScore } }
  return $null
}

function Read-FileLines([string]$path) {
  if (-not (Test-Path $path)) { throw "File not found: $path" }
  return [System.IO.File]::ReadAllLines($path, [System.Text.Encoding]::UTF8)
}

function Assemble-ByOutline {
  param(
    [string]$OutlinePath = 'book/篇章结构.md',
    [string]$BasePath = 'book/1022.2025.newbook.md',
    [string]$SourcePath = 'book/1022.2025.book.md'
  )
  $reportDir = New-ReportsDir
  $ts = (Get-Date).ToString('yyyyMMdd-HHmmss')
  $outPath = Join-Path $reportDir "organized-$ts.md"
  $logPath = Join-Path $reportDir "organize-log-$ts.md"
  $tocPath = Join-Path $reportDir "toc-$ts.txt"

  $outline = Read-FileLines $OutlinePath
  $base = Read-FileLines $BasePath
  $src = Read-FileLines $SourcePath

  $baseNodes = Build-SectionIndex $base
  $srcNodes  = Build-SectionIndex $src

  $log = New-Object System.Collections.Generic.List[string]
  $toc = New-Object System.Collections.Generic.List[string]
  $out = New-Object System.Collections.Generic.List[string]
  $missingCount=0

  $outlinePartKey = ''
  for ($i=0; $i -lt $outline.Length; $i++) {
    $ln = $outline[$i]
    if ($ln -match '^(#+)\s+(.*)$') {
      $lvl=$Matches[1].Length; $title=$Matches[2].Trim()
  if ($lvl -le 2) { $outlinePartKey = (Normalize-Title $title) }
  if ($title -match '篇章结构' -or (Normalize-Title $title) -match '篇章结构') { continue }
      $toc.Add(("{0} {1}" -f ('#'*$lvl), $title))

      $segmentName = 'base'
      $cand = Find-Candidate $baseNodes $title $lvl $outlinePartKey
      if (-not $cand) { $cand = Find-Candidate $srcNodes $title $lvl $outlinePartKey; if ($cand) { $segmentName='src' } }
      if ($cand) {
        $node = $cand.node
        $segment = if ($segmentName -eq 'src') { $src } else { $base }
        $content = $segment[ $node.StartLine .. $node.EndLine ]
        $heading = ("{0} {1}" -f ('#'*$lvl), $title)
        $out.Add($heading)
        if ($content.Count -gt 1) { $out.AddRange([string[]]($content[1..($content.Count-1)])) }
        $out.Add('')
        $log.Add("OK    [$($cand.mode):$($cand.score)]  $lvl    $title -> $($node.Title)")
      } else {
        $out.Add(("{0} {1}" -f ('#'*$lvl), $title))
        $out.Add("[MISSING] 该小节在现有稿件中未找到匹配内容，待补充。")
        $out.Add('')
        $missingCount++
        $log.Add("MISS  -       $lvl    $title")
      }
    }
  }

  [IO.File]::WriteAllLines($outPath, $out, [Text.Encoding]::UTF8)
  [IO.File]::WriteAllLines($logPath, @("Missing=$missingCount"; '') + $log, [Text.Encoding]::UTF8)
  [IO.File]::WriteAllLines($tocPath, $toc, [Text.Encoding]::UTF8)

  Write-Host "Assembled: $outPath"
  Write-Host "Log: $logPath"
  Write-Host "TOC: $tocPath"
  Write-Host "Missing: $missingCount"
}

if ($MyInvocation.InvocationName -ne '.') {
  Assemble-ByOutline @Args
}
