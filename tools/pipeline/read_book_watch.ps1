param(
    [string]$Source = $(Join-Path (Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSCommandPath))) 'book/1022.2025.newbook.augmented.frozen.md'),
    [int]$Port = 9876,
    [int]$DebounceMs = 400,
    [string]$PandocPath,
    [switch]$AlsoPdf,
    [ValidateSet('xelatex','wkhtmltopdf')][string]$PdfEngine
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$repoRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSCommandPath))
$tplDir = Join-Path $repoRoot 'tools/templates'
$outDir = Join-Path $repoRoot 'tools/releases/preview'
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$bookMd = Join-Path $outDir 'book.md'
$htmlOut = Join-Path $outDir 'book.html'
$token = Join-Path $outDir 'reload.token'

function Write-Token {
    Set-Content -LiteralPath $token -Value (Get-Date -Format o) -Encoding UTF8
}

function Render {
    param([switch]$Quiet)
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
    function Add-ToPathIfDirExists($dir){ if($dir -and (Test-Path $dir)){ if(-not ($env:PATH -split ';' | Where-Object { $_ -eq $dir })) { $env:PATH = "$dir;" + $env:PATH } } }
    function Resolve-PdfEngine {
        param([string]$Hint)
        if($Hint){ return $Hint }
        # Try PATH first
        if(Get-Command xelatex -ErrorAction SilentlyContinue){ return 'xelatex' }
        if(Get-Command wkhtmltopdf -ErrorAction SilentlyContinue){ return 'wkhtmltopdf' }
        # Extend PATH with common locations then retry
        $miUser = Join-Path $Env:LOCALAPPDATA 'Programs/MiKTeX/miktex/bin/x64'
        $miSys  = Join-Path $Env:ProgramFiles 'MiKTeX/miktex/bin/x64'
        $tlRoot = 'C:/texlive'
        $wkSys = Join-Path $Env:ProgramFiles 'wkhtmltopdf/bin'
        Add-ToPathIfDirExists $miUser; Add-ToPathIfDirExists $miSys
        if(Test-Path $tlRoot){ Get-ChildItem -LiteralPath $tlRoot -Directory -ErrorAction SilentlyContinue | ForEach-Object { Add-ToPathIfDirExists (Join-Path $_.FullName 'bin/windows') } }
        Add-ToPathIfDirExists $wkSys
        if(Get-Command xelatex -ErrorAction SilentlyContinue){ return 'xelatex' }
        if(Get-Command wkhtmltopdf -ErrorAction SilentlyContinue){ return 'wkhtmltopdf' }
        return $null
    }
    $pandocPath = Resolve-Pandoc -Hint $PandocPath
    $pdfEngine = Resolve-PdfEngine -Hint $PdfEngine
    $metaYaml = Join-Path $tplDir 'metadata.yaml'
    $cssSrc = Join-Path $tplDir 'book.css'
    $cssDst = $null
    if(Test-Path $cssSrc){
        $cssDst = Join-Path $outDir 'book.css'
        Copy-Item -LiteralPath $cssSrc -Destination $cssDst -Force
    }
    if($pandocPath) {
        if(-not $Quiet){ Write-Host "[watch] Using pandoc at $pandocPath" -ForegroundColor Green }
        $pandocArgs = @('-s','--toc','-f','gfm','-t','html5','-o',(Split-Path -Leaf $htmlOut))
        if($cssDst){ $pandocArgs += @('--css',(Split-Path -Leaf $cssDst)) }
        if(Test-Path $metaYaml){ $pandocArgs += @('--metadata-file',$metaYaml) }
        Push-Location $outDir
        & $pandocPath @pandocArgs $bookMd | Out-Null
        Pop-Location
        if($AlsoPdf){
            $pdfOut = Join-Path $outDir 'book.pdf'
            $pdfOk = $false
            if($pdfEngine){
                try {
                    $pdfStdout = Join-Path $outDir ("pandoc_pdf.{0}.out.log" -f $pdfEngine)
                    $pdfStderr = Join-Path $outDir ("pandoc_pdf.{0}.err.log" -f $pdfEngine)
                    $pdfArgs = @('-s','-f','gfm','-o',(Split-Path -Leaf $pdfOut),"--pdf-engine=$pdfEngine")
                    if(Test-Path $metaYaml){ $pdfArgs += @('--metadata-file',(Split-Path -Leaf $metaYaml)) }
                    Push-Location $outDir
                    Start-Process -FilePath $pandocPath -ArgumentList ($pdfArgs + (Split-Path -Leaf $bookMd)) -RedirectStandardOutput $pdfStdout -RedirectStandardError $pdfStderr -NoNewWindow -Wait | Out-Null
                    Pop-Location
                    if(Test-Path $pdfOut){ $pdfOk = $true } else { Write-Warning ("[watch] PDF failed, see logs: {0}; {1}" -f $pdfStdout, $pdfStderr) }
                } catch { Write-Warning "[watch] PDF exception: $($_.Exception.Message)" }
            }
            if(-not $pdfOk){
                Write-Warning "[watch] PDF not generated. Install XeLaTeX (TeX Live/MiKTeX) or wkhtmltopdf, or pass -PdfEngine xelatex|wkhtmltopdf."
                $checker = Join-Path $repoRoot 'tools/pipeline/check_pdf_deps.ps1'
                if(Test-Path $checker){
                    Write-Host "[watch] 推荐执行一次依赖检查：" -ForegroundColor Yellow
                    Write-Host "pwsh -NoProfile -ExecutionPolicy Bypass -File `"$checker`" -Prefer xelatex" -ForegroundColor DarkCyan
                }
            } elseif(-not $Quiet) {
                Write-Host "[watch] PDF updated: $pdfOut" -ForegroundColor Magenta
            }
        }
    } else {
        if(-not $Quiet){ Write-Warning '[watch] pandoc not found; using Python fallback renderer (HTML only).' }
            $py = Join-Path $repoRoot '.venv311/Scripts/python.exe'
            if(-not (Test-Path $py)) { $py = 'python' }
        $md2html = Join-Path $repoRoot 'tools/md_to_html.py'
        if(-not (Test-Path $md2html)) { throw "Python renderer not found: $md2html" }
        & $py $md2html $bookMd $htmlOut | Out-Null
    }
    if(Test-Path $htmlOut){ if(-not $Quiet){ Write-Host "[watch] HTML updated: $htmlOut" -ForegroundColor Cyan } ; Write-Token }
}

# Optionally refresh frozen manuscript if chapter/appendix changed
function Invoke-FreezeManuscript {
    $freezePy = Join-Path $repoRoot 'tools/freeze_manuscript.py'
    if(Test-Path $freezePy){
        $py = Join-Path $repoRoot '.venv311/Scripts/python.exe'
        if(-not (Test-Path $py)) { $py = 'python' }
        try {
            & $py $freezePy | Out-Null
        } catch {
            Write-Warning "[watch] freeze script failed: $($_.Exception.Message)"
        }
    }
}

# Initial render
Render

# Start preview server
$pyExe = Join-Path $repoRoot '.venv311/Scripts/python.exe'
if(-not (Test-Path $pyExe)) { $pyExe = 'python' }
$serverScript = Join-Path $repoRoot 'tools/server/preview_server.py'
if(-not (Test-Path $serverScript)) { throw "Preview server not found: $serverScript" }
$serverLog = Join-Path $outDir 'server.out.log'
$serverErr = Join-Path $outDir 'server.err.log'
$argList = '"{0}" --dir "{1}" --port {2}' -f $serverScript, $outDir, $Port
$server = Start-Process -FilePath $pyExe -ArgumentList $argList -RedirectStandardOutput $serverLog -RedirectStandardError $serverErr -WindowStyle Hidden -PassThru

# Wait briefly and verify server is listening (non-blocking retries)
$ok = $false
for($i=0; $i -lt 8 -and -not $ok; $i++){
    Start-Sleep -Milliseconds 250
    try {
        $probe = Invoke-WebRequest -UseBasicParsing -TimeoutSec 1 -Uri ("http://127.0.0.1:{0}/__reload" -f $Port)
        if($probe.StatusCode -ge 200){ $ok = $true }
    } catch { }
}
if(-not $ok){
    Write-Warning "[watch] Server didn't start on 127.0.0.1:$Port. Checking logs: $serverLog ; $serverErr"
    if(Test-Path $serverLog){ Write-Host '--- server stdout (tail) ---'; Get-Content -Tail 50 $serverLog | Write-Host }
    if(Test-Path $serverErr){ Write-Host '--- server stderr (tail) ---'; Get-Content -Tail 50 $serverErr | Write-Host }
}

$url = "http://127.0.0.1:$Port/book.html"
Start-Process $url
Write-Host "[watch] Serving $outDir at $url" -ForegroundColor Yellow

# Setup watchers
$fsw = New-Object System.IO.FileSystemWatcher
$fsw.Path = (Split-Path -Parent $Source)
$fsw.Filter = (Split-Path -Leaf $Source)
$fsw.IncludeSubdirectories = $false
$fsw.EnableRaisingEvents = $true

$fswTpl = New-Object System.IO.FileSystemWatcher
$fswTpl.Path = $tplDir
$fswTpl.Filter = '*'
$fswTpl.IncludeSubdirectories = $false
$fswTpl.EnableRaisingEvents = $true

# Watch chapter directory (*.md)
$chapDir = Join-Path $repoRoot 'chapter'
if(Test-Path $chapDir){
    $fswChap = New-Object System.IO.FileSystemWatcher
    $fswChap.Path = $chapDir
    $fswChap.Filter = '*.md'
    $fswChap.IncludeSubdirectories = $false
    $fswChap.EnableRaisingEvents = $true
}

# Watch book/附录-*.md
$bookDir = Join-Path $repoRoot 'book'
if(Test-Path $bookDir){
    $fswApp = New-Object System.IO.FileSystemWatcher
    $fswApp.Path = $bookDir
    $fswApp.Filter = '附录-*.md'
    $fswApp.IncludeSubdirectories = $false
    $fswApp.EnableRaisingEvents = $true
}

$pending = $false
$building = $false

$action = {
    if($building){ $script:pending = $true; return }
    $script:building = $true
    Start-Sleep -Milliseconds $using:DebounceMs
    try {
    Invoke-FreezeManuscript
        Render -Quiet
    } finally { $script:building = $false }
    if($script:pending){ $script:pending = $false; Render -Quiet }
}

$handlers = @()
$handlers += Register-ObjectEvent -InputObject $fsw -EventName Changed -Action $action
$handlers += Register-ObjectEvent -InputObject $fsw -EventName Created -Action $action
$handlers += Register-ObjectEvent -InputObject $fsw -EventName Renamed -Action $action
$handlers += Register-ObjectEvent -InputObject $fswTpl -EventName Changed -Action $action
$handlers += Register-ObjectEvent -InputObject $fswTpl -EventName Created -Action $action
$handlers += Register-ObjectEvent -InputObject $fswTpl -EventName Renamed -Action $action
if($fswChap){
    $handlers += Register-ObjectEvent -InputObject $fswChap -EventName Changed -Action $action
    $handlers += Register-ObjectEvent -InputObject $fswChap -EventName Created -Action $action
    $handlers += Register-ObjectEvent -InputObject $fswChap -EventName Renamed -Action $action
}
if($fswApp){
    $handlers += Register-ObjectEvent -InputObject $fswApp -EventName Changed -Action $action
    $handlers += Register-ObjectEvent -InputObject $fswApp -EventName Created -Action $action
    $handlers += Register-ObjectEvent -InputObject $fswApp -EventName Renamed -Action $action
}

Write-Host "[watch] Watching for changes. Press Ctrl+C to stop." -ForegroundColor Green
try {
    while($true){ Start-Sleep -Seconds 1 }
} finally {
    foreach($h in $handlers){ Unregister-Event -SubscriptionId $h.Id -ErrorAction SilentlyContinue }
    $fsw.Dispose(); $fswTpl.Dispose(); if($fswChap){ $fswChap.Dispose() }; if($fswApp){ $fswApp.Dispose() }
    if($server -and -not $server.HasExited){ try { $server.CloseMainWindow() | Out-Null; Start-Sleep 1; if(-not $server.HasExited){ $server.Kill() } } catch {} }
}
