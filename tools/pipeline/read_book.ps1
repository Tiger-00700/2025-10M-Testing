param(
    [string]$Source = $(Join-Path (Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSCommandPath))) 'book/1022.2025.newbook.augmented.frozen.md'),
    [string]$PandocPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Quick preview: render the frozen manuscript to HTML and open in the browser
# Prefers Pandoc with templates; falls back to Python renderer with inline CSS

if(-not (Test-Path $Source)) { throw "Manuscript not found: $Source" }

$repoRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSCommandPath))
$tplDir = Join-Path $repoRoot 'tools/templates'
$outDir = Join-Path $repoRoot 'tools/releases/preview'
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$bookMd = Join-Path $outDir 'book.md'
Copy-Item -LiteralPath $Source -Destination $bookMd -Force

function Resolve-Pandoc {
    param([string]$Hint)
    if($Hint -and (Test-Path $Hint)) { return $Hint }
    $cmd = Get-Command pandoc -ErrorAction SilentlyContinue
    if($cmd) { return $cmd.Source }
    $candidates = @(
        (Join-Path $Env:LOCALAPPDATA 'Pandoc/pandoc.exe'),
        'C:\\Program Files\\Pandoc\\pandoc.exe',
        'C:\\Program Files (x86)\\Pandoc\\pandoc.exe'
    )
    foreach($p in $candidates){ if(Test-Path $p){ return $p } }
    return $null
}

$pandocPath = Resolve-Pandoc -Hint $PandocPath
$metaYaml = Join-Path $tplDir 'metadata.yaml'
$cssSrc = Join-Path $tplDir 'book.css'
$cssDst = $null
if(Test-Path $cssSrc){
    $cssDst = Join-Path $outDir 'book.css'
    Copy-Item -LiteralPath $cssSrc -Destination $cssDst -Force
}

$htmlOut = Join-Path $outDir 'book.html'

if($pandocPath) {
    Write-Host "[preview] Using pandoc at $pandocPath" -ForegroundColor Green
    $pandocArgs = @('-s','--toc','-f','gfm','-t','html5','-o',(Split-Path -Leaf $htmlOut))
    if($cssDst){ $pandocArgs += @('--css',(Split-Path -Leaf $cssDst)) }
    if(Test-Path $metaYaml){ $pandocArgs += @('--metadata-file',$metaYaml) }
    Push-Location $outDir
    & $pandocPath @pandocArgs $bookMd | Out-Null
    Pop-Location
} else {
    Write-Warning '[preview] pandoc not found; using Python fallback renderer (HTML only).'
    $py = Join-Path $repoRoot '.venv311/Scripts/python.exe'
    if(-not (Test-Path $py)) { $py = 'python' }
    $md2html = Join-Path $repoRoot 'tools/md_to_html.py'
    if(-not (Test-Path $md2html)) { throw "Python renderer not found: $md2html" }
    & $py $md2html $bookMd $htmlOut | Write-Host
}

if(-not (Test-Path $htmlOut)) { throw "HTML output was not produced: $htmlOut" }

Write-Host "[preview] Opening: $htmlOut" -ForegroundColor Yellow
Start-Process $htmlOut
