# Simple script to check chapter numbering continuity
$filePath = 'e:\DONT_TOUCH\10M-2025-Testing\book\1208.2025.newbook.update.md'
$content = Get-Content -Path $filePath -Encoding UTF8

# Variables to store extracted data
$volumes = @()
$chapters = @()
$sections = @()
$subsections = @()

# Extract all headings
for ($i = 0; $i -lt $content.Length; $i++) {
    $line = $content[$i]
    $lineNumber = $i + 1
    
    # Extract volumes (## 第X篇)
    if ($line -match '##\s*第(\d+)篇') {
        $volNum = [int]$matches[1]
        $volumes += [PSCustomObject]@{Num = $volNum; Line = $lineNumber; Text = $line}
    }
    
    # Extract chapters (### 第X章)
    if ($line -match '###\s*第(\d+)章') {
        $chapNum = [int]$matches[1]
        $chapters += [PSCustomObject]@{Num = $chapNum; Line = $lineNumber; Text = $line}
    }
    
    # Extract sections (#### X.Y)
    if ($line -match '####\s*(\d+)\.(\d+)') {
        $chapNum = [int]$matches[1]
        $secNum = [int]$matches[2]
        $sections += [PSCustomObject]@{Chap = $chapNum; Sec = $secNum; Line = $lineNumber; Text = $line}
    }
    
    # Extract subsections (##### X.Y.Z)
    if ($line -match '#####\s*(\d+)\.(\d+)\.(\d+)') {
        $chapNum = [int]$matches[1]
        $secNum = [int]$matches[2]
        $subSecNum = [int]$matches[3]
        $subsections += [PSCustomObject]@{Chap = $chapNum; Sec = $secNum; SubSec = $subSecNum; Line = $lineNumber; Text = $line}
    }
}

# Sort all extracted data
$volumes = $volumes | Sort-Object -Property Num
$chapters = $chapters | Sort-Object -Property Num
$sections = $sections | Sort-Object -Property Chap, Sec
$subsections = $subsections | Sort-Object -Property Chap, Sec, SubSec

# Check for continuity and issues
$issues = @()

# Check volumes
Write-Host "=== Checking Volumes (篇) ==="
$expectedVol = 1
foreach ($vol in $volumes) {
    if ($vol.Num -ne $expectedVol) {
        Write-Host "ERROR: Missing volume $expectedVol at line $($vol.Line)"
        $issues += @("Missing volume $expectedVol")
        $expectedVol++
    }
    Write-Host "Volume $($vol.Num) at line $($vol.Line): $($vol.Text)"
    $expectedVol++
}

# Check chapters
Write-Host "\n=== Checking Chapters (章) ==="
$expectedChap = 1
foreach ($chap in $chapters) {
    if ($chap.Num -ne $expectedChap) {
        Write-Host "ERROR: Missing chapter $expectedChap at line $($chap.Line)"
        $issues += @("Missing chapter $expectedChap")
        $expectedChap++
    }
    Write-Host "Chapter $($chap.Num) at line $($chap.Line): $($chap.Text)"
    $expectedChap++
}

# Check sections (first few chapters only)
Write-Host "\n=== Checking Sections (节) - First 5 chapters ==="
$chapNumbers = $sections | Select-Object -ExpandProperty Chap | Sort-Object -Unique
$chapCount = 0
foreach ($chapNum in $chapNumbers) {
    if ($chapCount -ge 5) { break }
    $chapSections = $sections | Where-Object { $_.Chap -eq $chapNum } | Sort-Object -Property Sec
    $expectedSec = 1
    
    Write-Host "\nChapters $chapNum sections:"
    foreach ($sec in $chapSections) {
        if ($sec.Sec -ne $expectedSec) {
            Write-Host "ERROR: Chapter $chapNum missing section $expectedSec at line $($sec.Line)"
            $issues += @("Chapter $chapNum missing section $expectedSec")
            $expectedSec++
        }
        Write-Host "  Section $($sec.Sec): $($sec.Text)"
        $expectedSec++
    }
    $chapCount++
}

# Check subsections (show issues only)
Write-Host "\n=== Checking Subsections (小节) - Issues only ==="
$subsectionIssues = 0
$chapNumbers = $subsections | Select-Object -ExpandProperty Chap | Sort-Object -Unique

foreach ($chapNum in $chapNumbers) {
    $secNumbers = $subsections | Where-Object { $_.Chap -eq $chapNum } | Select-Object -ExpandProperty Sec | Sort-Object -Unique
    
    foreach ($secNum in $secNumbers) {
        $secSubsections = $subsections | Where-Object { $_.Chap -eq $chapNum -and $_.Sec -eq $secNum } | Sort-Object -Property SubSec
        $expectedSubSec = 1
        
        foreach ($subSec in $secSubsections) {
            if ($subSec.SubSec -ne $expectedSubSec) {
                Write-Host "ERROR: Chapter $chapNum, Section $secNum missing subsection $expectedSubSec at line $($subSec.Line)"
                $issues += @("Chapter $chapNum, Section $secNum missing subsection $expectedSubSec")
                $subsectionIssues++
                $expectedSubSec++
            }
            $expectedSubSec++
        }
    }
}

if ($subsectionIssues -eq 0) {
    Write-Host "No issues found in subsections"
}

# Summary
Write-Host "\n=== SUMMARY ==="
Write-Host "File: $filePath"
Write-Host "Total Volumes: $($volumes.Count)"
Write-Host "Total Chapters: $($chapters.Count)"
Write-Host "Total Sections: $($sections.Count)"
Write-Host "Total Subsections: $($subsections.Count)"
Write-Host "Total Issues Found: $($issues.Count)"

if ($issues.Count -gt 0) {
    Write-Host "\nIssues:"
    $issues | ForEach-Object { Write-Host "- $_" }
} else {
    Write-Host "\nAll numbering is continuous and correct!"
}

# Save results to file
$issues | Out-File -FilePath 'e:\DONT_TOUCH\10M-2025-Testing\chapter_issues.txt' -Encoding UTF8
Write-Host "\nIssues saved to chapter_issues.txt"
