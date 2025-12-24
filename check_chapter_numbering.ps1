# 检查文档篇-章-节号连续性的脚本
$filePath = 'e:\DONT_TOUCH\10M-2025-Testing\book\1208.2025.newbook.update.md'
$content = Get-Content -Path $filePath -Encoding UTF8

# 定义变量存储检查结果
$issues = @()
$volumes = @()
$chapters = @()
$sections = @()
$subsections = @()

# 提取所有篇、章、节、小节
for ($i = 0; $i -lt $content.Length; $i++) {
    $line = $content[$i]
    $lineNumber = $i + 1
    
    # 提取篇 (## 第X篇)
    if ($line -match '##\s*第(\d+)篇') {
        $volumeNum = [int]$matches[1]
        $volumes += [PSCustomObject]@{Number = $volumeNum; Line = $lineNumber; Text = $line}
    }
    
    # 提取章 (### 第X章)
    if ($line -match '###\s*第(\d+)章') {
        $chapterNum = [int]$matches[1]
        $chapters += [PSCustomObject]@{Number = $chapterNum; Line = $lineNumber; Text = $line}
    }
    
    # 提取节 (#### X.Y)
    if ($line -match '####\s*(\d+)\.(\d+)') {
        $chapterNum = [int]$matches[1]
        $sectionNum = [int]$matches[2]
        $sections += [PSCustomObject]@{Chapter = $chapterNum; Section = $sectionNum; Line = $lineNumber; Text = $line}
    }
    
    # 提取小节 (##### X.Y.Z)
    if ($line -match '#####\s*(\d+)\.(\d+)\.(\d+)') {
        $chapterNum = [int]$matches[1]
        $sectionNum = [int]$matches[2]
        $subsectionNum = [int]$matches[3]
        $subsections += [PSCustomObject]@{Chapter = $chapterNum; Section = $sectionNum; Subsection = $subsectionNum; Line = $lineNumber; Text = $line}
    }
}

# 检查篇号连续性
Write-Host "=== 检查篇号连续性 ==="
for ($i = 1; $i -le $volumes.Count; $i++) {
    $volume = $volumes | Where-Object { $_.Number -eq $i }
    if (-not $volume) {
        $issues += [PSCustomObject]@{Type = "Missing Volume"; Description = "第$i篇缺失"; Line = 0}
        Write-Host "❌ 第$i篇缺失"
    } else {
        Write-Host "✅ 第$i篇存在 (行号: $($volume.Line))"
    }
}

# 检查章号连续性
Write-Host "\n=== 检查章号连续性 ==="
for ($i = 1; $i -le $chapters.Count; $i++) {
    $chapter = $chapters | Where-Object { $_.Number -eq $i }
    if (-not $chapter) {
        $issues += [PSCustomObject]@{Type = "Missing Chapter"; Description = "第$i章缺失"; Line = 0}
        Write-Host "❌ 第$i章缺失"
    } else {
        Write-Host "✅ 第$i章存在 (行号: $($chapter.Line))"
    }
}

# 检查节号连续性
Write-Host "\n=== 检查节号连续性 (显示前10个章节的检查结果) ==="
$chapterNumbers = $sections | Select-Object -ExpandProperty Chapter | Sort-Object -Unique
$maxChaptersToShow = 10
$chaptersShown = 0

foreach ($chapterNum in $chapterNumbers) {
    if ($chaptersShown -ge $maxChaptersToShow) {
        Write-Host "... 省略剩余章节的检查结果 ..."
        break
    }
    
    $chapterSections = $sections | Where-Object { $_.Chapter -eq $chapterNum } | Sort-Object -Property Section
    $expectedSection = 1
    $hasIssue = $false
    
    Write-Host "\n📚 第$chapterNum章的节号检查:"
    
    foreach ($section in $chapterSections) {
        if ($section.Section -ne $expectedSection) {
            # 检查是否有缺失的节
            for ($s = $expectedSection; $s -lt $section.Section; $s++) {
                $issues += [PSCustomObject]@{Type = "Missing Section"; Description = "第$chapterNum章第$s节缺失"; Line = $section.Line}
                Write-Host "  ❌ 第$chapterNum章第$s节缺失"
                $hasIssue = $true
            }
        }
        $expectedSection = $section.Section + 1
    }
    
    if (-not $hasIssue) {
        Write-Host "  ✅ 第$chapterNum章的节号连续 (共$($chapterSections.Count)节)"
    }
    
    $chaptersShown++
}

# 检查小节号连续性
Write-Host "\n=== 检查小节号连续性 (显示有问题的章节) ==="
$subsectionIssues = 0

foreach ($chapterNum in $chapterNumbers) {
    $chapterSections = $sections | Where-Object { $_.Chapter -eq $chapterNum } | Select-Object -ExpandProperty Section | Sort-Object -Unique
    
    foreach ($sectionNum in $chapterSections) {
        $sectionSubsections = $subsections | Where-Object { $_.Chapter -eq $chapterNum -and $_.Section -eq $sectionNum } | Sort-Object -Property Subsection
        
        if ($sectionSubsections.Count -gt 0) {
            $expectedSubsection = 1
            $hasIssue = $false
            
            foreach ($subsection in $sectionSubsections) {
                if ($subsection.Subsection -ne $expectedSubsection) {
                    # 检查是否有缺失的小节
                    for ($ss = $expectedSubsection; $ss -lt $subsection.Subsection; $ss++) {
                        $issues += [PSCustomObject]@{Type = "Missing Subsection"; Description = "第$chapterNum章第$sectionNum.$ss小节缺失"; Line = $subsection.Line}
                        Write-Host "❌ 第$chapterNum章第$sectionNum.$ss小节缺失 (在第$($subsection.Line)行发现$chapterNum.$sectionNum.$($subsection.Subsection))"
                        $hasIssue = $true
                        $subsectionIssues++
                    }
                }
                $expectedSubsection = $subsection.Subsection + 1
            }
            
            if ($hasIssue) {
                Write-Host ""
            }
        }
    }
}

if ($subsectionIssues -eq 0) {
    Write-Host "✅ 所有小节号连续"
}

# 检查重复编号
Write-Host "\n=== 检查重复编号 ==="

# 检查重复篇号
$duplicateVolumes = $volumes | Group-Object -Property Number | Where-Object { $_.Count -gt 1 }
foreach ($dup in $duplicateVolumes) {
    $lines = ($dup.Group | Select-Object -ExpandProperty Line) -join ", "
    $issues += [PSCustomObject]@{Type = "Duplicate Volume"; Description = "第$($dup.Name)篇重复出现"; Line = $lines}
    Write-Host "❌ 第$($dup.Name)篇重复出现 (行号: $lines)"
}

# 检查重复章号
$duplicateChapters = $chapters | Group-Object -Property Number | Where-Object { $_.Count -gt 1 }
foreach ($dup in $duplicateChapters) {
    $lines = ($dup.Group | Select-Object -ExpandProperty Line) -join ", "
    $issues += [PSCustomObject]@{Type = "Duplicate Chapter"; Description = "第$($dup.Name)章重复出现"; Line = $lines}
    Write-Host "❌ 第$($dup.Name)章重复出现 (行号: $lines)"
}

# 检查重复节号
$duplicateSections = $sections | Group-Object -Property Chapter, Section | Where-Object { $_.Count -gt 1 }
foreach ($dup in $duplicateSections) {
    $chapSec = "第$($dup.Name.Split(',')[0])章第$($dup.Name.Split(',')[1])节"
    $lines = ($dup.Group | Select-Object -ExpandProperty Line) -join ", "
    $issues += [PSCustomObject]@{Type = "Duplicate Section"; Description = "$chapSec重复出现"; Line = $lines}
    Write-Host "❌ $chapSec重复出现 (行号: $lines)"
}

# 检查重复小节号
$duplicateSubsections = $subsections | Group-Object -Property Chapter, Section, Subsection | Where-Object { $_.Count -gt 1 }
foreach ($dup in $duplicateSubsections) {
    $parts = $dup.Name.Split(',')
    $chapSecSubsec = "第$($parts[0])章第$($parts[1]).$($parts[2])小节"
    $lines = ($dup.Group | Select-Object -ExpandProperty Line) -join ", "
    $issues += [PSCustomObject]@{Type = "Duplicate Subsection"; Description = "$chapSecSubsec重复出现"; Line = $lines}
    Write-Host "❌ $chapSecSubsec重复出现 (行号: $lines)"
}

if (($duplicateVolumes.Count + $duplicateChapters.Count + $duplicateSections.Count + $duplicateSubsections.Count) -eq 0) {
    Write-Host "✅ 没有发现重复编号"
}

# 输出检查总结
Write-Host "\n" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "📊 文档篇-章-节号检查总结" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "文件: $filePath" -ForegroundColor Cyan
Write-Host "总篇数: $($volumes.Count)" -ForegroundColor Cyan
Write-Host "总章数: $($chapters.Count)" -ForegroundColor Cyan
Write-Host "总节数: $($sections.Count)" -ForegroundColor Cyan
Write-Host "总小节数: $($subsections.Count)" -ForegroundColor Cyan
Write-Host "发现问题数: $($issues.Count)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if ($issues.Count -gt 0) {
    Write-Host "\n❌ 发现的问题详情:"
    
    # 按类型分组输出
    $issuesByType = $issues | Group-Object -Property Type
    foreach ($group in $issuesByType) {
        Write-Host "\n$($group.Name) ($($group.Count)个问题):"
        $group.Group | ForEach-Object {
            Write-Host "  - $($_.Description) (相关行号: $($_.Line))"
        }
    }
    
    # 保存问题到文件
    $issues | Export-Csv -Path 'e:\DONT_TOUCH\10M-2025-Testing\chapter_numbering_issues.csv' -Encoding UTF8 -NoTypeInformation
    Write-Host "\n问题详情已保存到: e:\DONT_TOUCH\10M-2025-Testing\chapter_numbering_issues.csv"
} else {
    Write-Host "\n✅ 文档篇-章-节号完全正确，无缺失、重复或格式错误！"
}
