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
  $s = ($s -replace '特性|性质|特征', '特点')
  $s = ($s -replace '部署|构建|安装', '搭建')
  $s = ($s -replace '分类', '类型')
  $s = ($s -replace '意义|价值', '重要性')
  $s = ($s -replace '海量数据', '大数据')
  $s = ($s -replace '比较', '对比')
  $s = ($s -replace "[\p{P}\p{S}]", ' ')
  $s = Normalize-Whitespace $s
  return $s
}

function Get-AliasKeys([string]$norm) {
  # Allow outline headings with numeric prefixes (e.g., "1.1 标题") to trigger aliases
  $normStripped = ( ($norm -replace '^\s*\d+(?:\.\d+)*\s*', ' ') ).Trim()
  $aliases = @{
  # 第四篇 11.1 自动化测试概述通用小节
  '定义与价值'=@('自动化测试概述');
  '必要性'=@('自动化测试概述');
  '分类'=@('自动化测试概述');
  '发展历程'=@('自动化测试概述');
  '挑战'=@('自动化测试概述');

  # 第四篇 11.2 框架设计中的架构类小节
  '分布式测试架构'=@('测试自动化框架设计');
  '数据流架构'=@('测试自动化框架设计');
    '大数据的概念与特点'=@('大数据概念与特点','大数据概念','大数据定义','大数据简介','大数据概述','大数据特点','大数据特性');
    '概述'=@('简介','总览','引言');
    '架构设计原则'=@('架构原则','设计原则','架构要点','架构准则');
    '生态系统层次'=@('生态系统层级','生态分层');
    '技术栈及其应用场景'=@('技术栈与应用场景','技术栈应用场景','技术栈和应用场景');
    '测试环境类型与特点'=@('测试环境类型','环境类型与特点','环境类型','类型与特点','测试环境特点');
    '测试环境类型'=@('测试环境类型与特点','环境类型');
    '测试环境特点对比'=@('测试环境特点','特点对比','环境类型与特点','类型与特点','测试环境类型与特点');
    '本地测试环境搭建'=@('本地环境搭建','搭建本地测试环境','本地测试环境部署','本地环境部署','本地测试环境构建','本地测试环境安装');
  '单机模式搭建'=@('单机模式环境搭建','单机部署','单机模式部署','单机模式安装','单机安装','单机构建','本地测试环境搭建');
  '伪分布式模式搭建'=@('伪分布式部署','伪分布式环境搭建','伪分布式安装','伪分布式构建','本地测试环境搭建');
  '基于 docker 的本地环境'=@('docker 本地环境','docker 环境搭建','基于 docker 的环境','基于 docker 的本地测试环境','docker 本地测试环境','docker compose 本地环境','docker 环境准备与配置');
  '数据存储重要性'=@('数据存储的重要性','存储重要性','数据存储意义','数据存储价值','数据存储作用','数据存储地位','存储的重要性','数据存储测试目标');
    '测试环境需求分析与规划'=@('测试环境需求分析','测试环境规划','环境需求分析与规划');
    '测试环境需求分析维度'=@('测试环境需求维度','环境需求分析维度','需求分析维度','需求分析的维度','测试环境类型需求分析');
    '集群测试环境搭建'=@('集群环境搭建','集群测试环境部署');
    '硬件配置要求'=@('集群测试环境搭建');
    '云测试环境配置'=@('云测试环境');
    '主流云平台对比'=@('云测试环境配置','云测试环境');
    '数据脱敏技术'=@('数据脱敏技术详解','数据脱敏测试','数据加密与脱敏测试');
    '数据脱敏验证方法'=@('数据脱敏测试','数据加密与脱敏测试');
    '敏感数据测试最佳实践'=@('测试数据安全管理最佳实践','敏感数据测试治理');

    # 第五篇 15.x 行业案例：若细分行业小节无独立标题，则回填到章节总览
    '金融行业大数据测试案例'=@('第 15 章 行业大数据测试案例分析','行业大数据测试案例分析');
    '电商行业大数据测试案例'=@('第 15 章 行业大数据测试案例分析','行业大数据测试案例分析');
    '医疗健康行业大数据测试案例'=@('第 15 章 行业大数据测试案例分析','行业大数据测试案例分析');
    '交通物流行业大数据测试案例'=@('第 15 章 行业大数据测试案例分析','行业大数据测试案例分析');
    '制造业大数据测试案例'=@('第 15 章 行业大数据测试案例分析','行业大数据测试案例分析');
    '政府/公共部门大数据测试案例'=@('第 15 章 行业大数据测试案例分析','行业大数据测试案例分析');
    '电信行业大数据测试案例'=@('第 15 章 行业大数据测试案例分析','行业大数据测试案例分析');

    # 第五篇 16.x 项目实施：若细分管理小节无独立标题，回填到 16 章
    '测试项目规划与管理'=@('第 16 章 大数据测试项目实施与实战经验');
    '目标与范围界定'=@('测试项目规划与管理','第 16 章 大数据测试项目实施与实战经验');
    '里程碑与迭代计划'=@('测试项目规划与管理','第 16 章 大数据测试项目实施与实战经验');
    '风险识别与缓解'=@('测试项目规划与管理','第 16 章 大数据测试项目实施与实战经验');
    '测试团队组建与管理'=@('第 16 章 大数据测试项目实施与实战经验');
    '团队角色与职责'=@('测试团队组建与管理','第 16 章 大数据测试项目实施与实战经验');
    '能力模型与招聘优先级'=@('测试团队组建与管理','第 16 章 大数据测试项目实施与实战经验');
    '培训与知识库建设'=@('测试团队组建与管理','第 16 章 大数据测试项目实施与实战经验');
    '测试环境与资源管理'=@('第 16 章 大数据测试项目实施与实战经验');
    '环境分层策略'=@('测试环境与资源管理','第 16 章 大数据测试项目实施与实战经验');
    '环境版本控制与可复现性'=@('测试环境与资源管理','第 16 章 大数据测试项目实施与实战经验');
    '资源预算与成本控制'=@('测试环境与资源管理','第 16 章 大数据测试项目实施与实战经验');
    '测试执行与进度控制'=@('第 16 章 大数据测试项目实施与实战经验');
    '测试范畴的优先级与mvp策略'=@('测试执行与进度控制','第 16 章 大数据测试项目实施与实战经验');
    '自动化优先级矩阵'=@('测试执行与进度控制','第 16 章 大数据测试项目实施与实战经验');
    '进度跟踪与度量'=@('测试执行与进度控制','第 16 章 大数据测试项目实施与实战经验');
    '风险控制与应急响应'=@('第 16 章 大数据测试项目实施与实战经验');
    '发布检查表与回滚playbook'=@('风险控制与应急响应','第 16 章 大数据测试项目实施与实战经验');
    '灰度/canary策略与监控断言'=@('风险控制与应急响应','第 16 章 大数据测试项目实施与实战经验');
    '事故演练与rca流程'=@('风险控制与应急响应','第 16 章 大数据测试项目实施与实战经验');

    # 16.6 评估与持续优化
    '测试项目评估与持续优化'=@('第 16 章 大数据测试项目实施与实战经验');
    '测试效能指标'=@('进度跟踪与度量','测试执行与进度控制','第 16 章 大数据测试项目实施与实战经验');
    '经验复盘与沉淀'=@('第 16 章 大数据测试项目实施与实战经验');
    '与产品/开发的协作机制'=@('第 16 章 大数据测试项目实施与实战经验');

    # 第17章 实战经验精要（如缺独立内容，回填相关章节）
    '第 17 章 大数据测试实战经验精要【专家】'=@('第 16 章 大数据测试项目实施与实战经验');
    '要点速览'=@('第 16 章 大数据测试项目实施与实战经验');
    '大规模测试团队的组织经验'=@('测试团队组建与管理','第 16 章 大数据测试项目实施与实战经验');
    '复杂环境下的环境管理要点'=@('测试环境与资源管理','第 16 章 大数据测试项目实施与实战经验');
    '敏感数据测试治理'=@('10.5 敏感数据保护测试','数据脱敏技术','数据加密与脱敏测试');
    '自动化推广实务'=@('测试自动化技术选型','自动化测试概述','测试自动化框架设计');
    '性能瓶颈定位与优化技巧'=@('环境性能优化','资源瓶颈识别测试');
    '常见落地陷阱与规避'=@('测试最佳实践');

    # 第19章 CI/CD、质量门与治理
    '大数据环境质量门示例'=@('质量门示例');
    '常见断言类型'=@('断言类型');
    '合规检查'=@('合规检查自动化');
    '测试数据管理'=@('数据版本控制与复用');

    # 泛化小节（H6常见词）回填到相关父级
    '流程优化'=@('持续交付最佳实践','测试项目评估与持续优化');
    '转型成功要素'=@('持续测试文化与团队协作','第 16 章 大数据测试项目实施与实战经验');

    # 第21章 人才与发展：补齐团队与职业发展
    '工具链升级策略'=@('团队管理实践','测试团队转型路径','持续交付最佳实践');
    '工具引入与选型'=@('测试自动化技术选型','团队管理实践');
    '自动化框架重构'=@('测试自动化框架设计');
    '监控工具整合策略'=@('可观测性测试最佳实践与案例');
    '云测试环境构建与管理'=@('3.1.5 云测试环境');
    '工具链集成与持续交付'=@('持续交付最佳实践','CI/CD流水线设计与实践');
    '大数据测试职业发展路径'=@('21.3 个人发展规划','职业发展路径');
    '技术专家路线'=@('职业发展路径','21.3 个人发展规划');
    '管理路线'=@('职业发展路径','21.3 个人发展规划');
    '架构师路线'=@('职业发展路径','21.3 个人发展规划');
    'devops 路线'=@('职业发展路径','21.3 个人发展规划');
    '培训咨询路线'=@('职业发展路径','21.3 个人发展规划');
    '大数据测试认证与培训'=@('21.3 个人发展规划');
    '推荐认证'=@('大数据测试认证与培训','21.3 个人发展规划');
    '培训资源'=@('大数据测试认证与培训','21.3 个人发展规划');
    '企业内部培训体系'=@('大数据测试认证与培训','21.3 个人发展规划');
    '大数据测试行业展望'=@('1.5 大数据测试的挑战与机遇');
    '职业发展机遇'=@('1.5 大数据测试的挑战与机遇','21.3 个人发展规划');
    '持续学习建议'=@('21.3 个人发展规划','职业发展路径');
    '附录 e 示例仓与可运行实验'=@('快速上手实验');
  }
  $out = New-Object System.Collections.Generic.List[string]
  foreach ($k in $aliases.Keys) {
    $kNorm = (Normalize-Title $k)
    if ($norm -eq $kNorm -or $normStripped -eq $kNorm) {
      # include the key itself as an alias target to allow prefix/equality matches when titles embed extra text
      $out.Add($kNorm)
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
    $hit = $index | Where-Object {
      $curr = $_
      $currNorm = $curr.NormKey
      $currNoNum = (Normalize-Title ( $curr.Title -replace '^\s*\d+(?:\.\d+)*\s*', ' ' ))
      (($currNorm -eq $alias) -or ($currNoNum -eq $alias) -or ($currNoNum.StartsWith($alias))) -and ($prefLevel -le 0 -or $curr.Level -eq $prefLevel)
    }
    if ($hit) { return @{ mode='alias'; node=$hit[0]; score=0.98 } }
    # alias any-level fall back
    $hitAny = $index | Where-Object {
      $curr = $_
      $currNorm = $curr.NormKey
      $currNoNum = (Normalize-Title ( $curr.Title -replace '^\s*\d+(?:\.\d+)*\s*', ' ' ))
      ($currNorm -eq $alias) -or ($currNoNum -eq $alias) -or ($currNoNum.StartsWith($alias))
    }
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
  # slightly relax thresholds to recover borderline matches (deeper levels can be a bit looser)
  $threshold = if ($prefLevel -le 2) { 0.62 } elseif ($prefLevel -eq 3) { 0.66 } elseif ($prefLevel -eq 4) { 0.70 } else { 0.66 }
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
