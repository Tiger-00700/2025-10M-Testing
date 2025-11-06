Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# One-click typesetting bundle builder
# Inputs: frozen manuscript markdown; Outputs: HTML/DOCX/PDF (best-effort) + resources zipped

$repoRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSCommandPath))
$src = Join-Path $repoRoot 'book/1022.2025.newbook.augmented.frozen.md'
if(-not (Test-Path $src)) { throw "Frozen manuscript not found: $src" }

$ts = Get-Date -Format 'yyyyMMdd-HHmmss'
$releaseRoot = Join-Path $repoRoot "tools/releases"
New-Item -ItemType Directory -Force -Path $releaseRoot | Out-Null
$outDir = Join-Path $releaseRoot "book-$ts"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$bookMd = Join-Path $outDir 'book.md'
Copy-Item -LiteralPath $src -Destination $bookMd -Force

Write-Host "==> Generate formats (best-effort)"
function Resolve-Pandoc {
    $cmd = Get-Command pandoc -ErrorAction SilentlyContinue
    if($cmd){ return $cmd.Source }
    $candidates = @(
        (Join-Path $Env:LOCALAPPDATA 'Pandoc/pandoc.exe'),
        'C:\\Program Files\\Pandoc\\pandoc.exe',
        'C:\\Program Files (x86)\\Pandoc\\pandoc.exe'
    )
    foreach($p in $candidates){ if(Test-Path $p){ return $p } }
    return $null
}
function Get-PdfEngines {
    $engines = @()
    if(Get-Command xelatex -ErrorAction SilentlyContinue){ $engines += 'xelatex' }
    if(Get-Command wkhtmltopdf -ErrorAction SilentlyContinue){ $engines += 'wkhtmltopdf' }
    return $engines
}
$pandocPath = Resolve-Pandoc
$tplDir = Join-Path $repoRoot 'tools/templates'
$refDocx = Join-Path $tplDir 'reference.docx'
$metaYaml = Join-Path $tplDir 'metadata.yaml'
$cssSrc = Join-Path $tplDir 'book.css'
$cssDst = $null
if(Test-Path $cssSrc){
    $cssDst = Join-Path $outDir 'book.css'
    Copy-Item -LiteralPath $cssSrc -Destination $cssDst -Force
}
$generated = @()
$failed = @()

if($pandocPath) {
    Write-Host "Using pandoc at $pandocPath"
    try {
        $htmlArgs = @('-s','--toc','-f','gfm','-t','html5','-o',(Join-Path $outDir 'book.html'))
        if($cssDst){ $htmlArgs += @('--css',(Split-Path -Leaf $cssDst)) }
        if(Test-Path $metaYaml){ $htmlArgs += @('--metadata-file',$metaYaml) }
        Push-Location $outDir
        & $pandocPath @htmlArgs $bookMd | Out-Null
        Pop-Location
        $generated += 'HTML'
    } catch { $failed += 'HTML' }
    try {
        $docxArgs = @('-s','-f','gfm','-t','docx','-o',(Join-Path $outDir 'book.docx'))
        if(Test-Path $refDocx){ $docxArgs += @('--reference-doc',$refDocx) }
        if(Test-Path $metaYaml){ $docxArgs += @('--metadata-file',$metaYaml) }
        & $pandocPath @docxArgs $bookMd | Out-Null
        $generated += 'DOCX'
    } catch { $failed += 'DOCX' }
    # Try PDF via XeLaTeX, fallback to wkhtmltopdf if available
    $pdfTarget = Join-Path $outDir 'book.pdf'
    $pdfOk = $false
    $engines = Get-PdfEngines
    foreach($engine in $engines){
        try {
            $pdfArgs = @('-s','-f','gfm','-o',$pdfTarget,("--pdf-engine={0}" -f $engine))
            if(Test-Path $metaYaml){ $pdfArgs += @('--metadata-file',$metaYaml) }
            & $pandocPath @pdfArgs $bookMd | Out-Null
            if(Test-Path $pdfTarget) { $pdfOk = $true; break }
        } catch { }
    }
    if($pdfOk) { $generated += 'PDF' } else { $failed += 'PDF' }
} else {
    Write-Warning 'pandoc not found in PATH; attempting Python markdown fallback for HTML only.'
    $py = Join-Path $repoRoot '.venv/Scripts/python.exe'
    if(-not (Test-Path $py)) { $py = 'python' }
    $md2html = Join-Path $repoRoot 'tools/md_to_html.py'
    if(Test-Path $md2html) {
        & $py $md2html $bookMd (Join-Path $outDir 'book.html')
        if($LASTEXITCODE -eq 0 -and (Test-Path (Join-Path $outDir 'book.html'))) {
            $generated += 'HTML'
        } else {
            Write-Warning "Python fallback failed with exit code $LASTEXITCODE"; $failed += 'HTML'
        }
    } else {
        Write-Warning 'md_to_html.py not found; cannot render HTML fallback.'
        $failed += 'HTML'
    }
}

Write-Host "==> Collect resources"
$reportsDir = Join-Path $outDir 'reports'
New-Item -ItemType Directory -Force -Path $reportsDir | Out-Null
@('tools/reports/organized-latest.md','tools/reports/toc-latest.txt') | ForEach-Object {
    $p = Join-Path $repoRoot $_
    if(Test-Path $p) { Copy-Item -LiteralPath $p -Destination $reportsDir -Force }
}

$appendixDir = Join-Path $outDir 'appendices'
New-Item -ItemType Directory -Force -Path $appendixDir | Out-Null
Get-ChildItem -LiteralPath (Join-Path $repoRoot 'book') -Filter '附录-*.md' -File | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination $appendixDir -Force
}

$examplesSrc = Join-Path $repoRoot 'examples/99_book_exports'
if(Test-Path $examplesSrc) {
    $examplesDst = Join-Path $outDir 'examples/99_book_exports'
    New-Item -ItemType Directory -Force -Path $examplesDst | Out-Null
    Copy-Item -LiteralPath $examplesSrc -Destination (Join-Path $outDir 'examples') -Force -Recurse
}

Write-Host "==> Write bundle manifest"
$manifest = @{
    timestamp = $ts
    manuscript = [IO.Path]::GetFileName($bookMd)
    generated = $generated
    failed = $failed
} | ConvertTo-Json -Depth 5
Set-Content -LiteralPath (Join-Path $outDir 'bundle.json') -Value $manifest -Encoding UTF8

Write-Host "==> Copy templates (if any)"
if(Test-Path $tplDir){
    $tplOut = Join-Path $outDir 'templates'
    New-Item -ItemType Directory -Force -Path $tplOut | Out-Null
    Get-ChildItem -LiteralPath $tplDir -File | ForEach-Object { Copy-Item -LiteralPath $_.FullName -Destination $tplOut -Force }
}

Write-Host "==> Create ZIP"
$zipPath = "$outDir.zip"
if(Test-Path $zipPath) { Remove-Item -LiteralPath $zipPath -Force }
Add-Type -AssemblyName 'System.IO.Compression.FileSystem'
[System.IO.Compression.ZipFile]::CreateFromDirectory($outDir, $zipPath)

Write-Host "[OK] Typeset bundle created: $outDir"
Write-Host "      ZIP: $zipPath"
if($generated.Count) { Write-Host ("      Generated: {0}" -f ($generated -join ', ')) }
if($failed.Count) { Write-Host ("      Skipped/failed: {0}" -f ($failed -join ', ')) }
