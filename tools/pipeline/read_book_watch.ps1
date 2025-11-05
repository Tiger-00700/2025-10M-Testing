param(
    [string]$Source = $(Join-Path (Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSCommandPath))) 'book/1022.2025.newbook.augmented.frozen.md'),
    [int]$Port = 9876,
    [int]$DebounceMs = 400
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
    $pandoc = Get-Command pandoc -ErrorAction SilentlyContinue
    $metaYaml = Join-Path $tplDir 'metadata.yaml'
    $cssSrc = Join-Path $tplDir 'book.css'
    $cssDst = $null
    if(Test-Path $cssSrc){
        $cssDst = Join-Path $outDir 'book.css'
        Copy-Item -LiteralPath $cssSrc -Destination $cssDst -Force
    }
    if($pandoc) {
        if(-not $Quiet){ Write-Host "[watch] Using pandoc at $($pandoc.Source)" -ForegroundColor Green }
        $pandocArgs = @('-s','--toc','-f','gfm','-t','html5','-o',(Split-Path -Leaf $htmlOut))
        if($cssDst){ $pandocArgs += @('--css',(Split-Path -Leaf $cssDst)) }
        if(Test-Path $metaYaml){ $pandocArgs += @('--metadata-file',$metaYaml) }
        Push-Location $outDir
        & $pandoc.Source @pandocArgs $bookMd | Out-Null
        Pop-Location
    } else {
        if(-not $Quiet){ Write-Warning '[watch] pandoc not found; using Python fallback renderer (HTML only).' }
        $py = Join-Path $repoRoot '.venv/Scripts/python.exe'
        if(-not (Test-Path $py)) { $py = 'python' }
        $md2html = Join-Path $repoRoot 'tools/md_to_html.py'
        if(-not (Test-Path $md2html)) { throw "Python renderer not found: $md2html" }
        & $py $md2html $bookMd $htmlOut | Out-Null
    }
    if(Test-Path $htmlOut){ if(-not $Quiet){ Write-Host "[watch] HTML updated: $htmlOut" -ForegroundColor Cyan } ; Write-Token }
}

# Initial render
Render

# Start preview server
$pyExe = Join-Path $repoRoot '.venv/Scripts/python.exe'
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

$pending = $false
$building = $false

$action = {
    if($building){ $script:pending = $true; return }
    $script:building = $true
    Start-Sleep -Milliseconds $using:DebounceMs
    try { Render -Quiet } finally { $script:building = $false }
    if($script:pending){ $script:pending = $false; Render -Quiet }
}

$handlers = @()
$handlers += Register-ObjectEvent -InputObject $fsw -EventName Changed -Action $action
$handlers += Register-ObjectEvent -InputObject $fsw -EventName Created -Action $action
$handlers += Register-ObjectEvent -InputObject $fsw -EventName Renamed -Action $action
$handlers += Register-ObjectEvent -InputObject $fswTpl -EventName Changed -Action $action
$handlers += Register-ObjectEvent -InputObject $fswTpl -EventName Created -Action $action
$handlers += Register-ObjectEvent -InputObject $fswTpl -EventName Renamed -Action $action

Write-Host "[watch] Watching for changes. Press Ctrl+C to stop." -ForegroundColor Green
try {
    while($true){ Start-Sleep -Seconds 1 }
} finally {
    foreach($h in $handlers){ Unregister-Event -SubscriptionId $h.Id -ErrorAction SilentlyContinue }
    $fsw.Dispose(); $fswTpl.Dispose()
    if($server -and -not $server.HasExited){ try { $server.CloseMainWindow() | Out-Null; Start-Sleep 1; if(-not $server.HasExited){ $server.Kill() } } catch {} }
}
