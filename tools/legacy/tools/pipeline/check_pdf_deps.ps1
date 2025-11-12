param(
    [ValidateSet('xelatex','wkhtmltopdf','auto')][string]$Prefer = 'auto',
    [switch]$Install,
    [switch]$NonInteractive
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Test-Cmd { param([string]$Name) return [bool](Get-Command $Name -ErrorAction SilentlyContinue) }

$haveXe = Test-Cmd 'xelatex'
$haveWk = Test-Cmd 'wkhtmltopdf'
$haveWinget = Test-Cmd 'winget'
$haveChoco  = Test-Cmd 'choco'

Write-Host "[deps] xelatex:  " -NoNewline; if($haveXe){ Write-Host 'FOUND' -ForegroundColor Green } else { Write-Host 'MISSING' -ForegroundColor Yellow }
Write-Host "[deps] wkhtmltopdf:" -NoNewline; if($haveWk){ Write-Host 'FOUND' -ForegroundColor Green } else { Write-Host 'MISSING' -ForegroundColor Yellow }
Write-Host "[deps] winget:    " -NoNewline; if($haveWinget){ Write-Host 'FOUND' -ForegroundColor Green } else { Write-Host 'MISSING' -ForegroundColor Yellow }
Write-Host "[deps] choco:     " -NoNewline; if($haveChoco){ Write-Host 'FOUND' -ForegroundColor Green } else { Write-Host 'MISSING' -ForegroundColor Yellow }

function Suggest-XeLaTeX {
    if($haveChoco){
        Write-Host "# Chocolatey (管理员 PowerShell)" -ForegroundColor Cyan
        Write-Host "choco install miktex -y" -ForegroundColor White
    }
    if($haveWinget){
        Write-Host "# Winget (管理员 PowerShell)" -ForegroundColor Cyan
        Write-Host "winget install MiKTeX.MiKTeX" -ForegroundColor White
    }
    Write-Host "# 安装完成后，请确保 xelatex 在 PATH 中并重启终端。" -ForegroundColor DarkGray
}

function Suggest-Wkhtmltopdf {
    if($haveChoco){
        Write-Host "# Chocolatey (管理员 PowerShell)" -ForegroundColor Cyan
        Write-Host "choco install wkhtmltopdf -y" -ForegroundColor White
    }
    if($haveWinget){
        Write-Host "# Winget (管理员 PowerShell)" -ForegroundColor Cyan
        Write-Host "winget install wkhtmltopdf" -ForegroundColor White
    }
    Write-Host "# 安装完成后，确保 wkhtmltopdf 在 PATH 中并重启终端。" -ForegroundColor DarkGray
}

# Decide target
$target = $Prefer
if($target -eq 'auto'){
    if($haveXe){ $target = 'xelatex' }
    elseif($haveWk){ $target = 'wkhtmltopdf' }
    else { $target = 'xelatex' } # prefer xelatex by default
}

Write-Host "[deps] Target engine: $target" -ForegroundColor Magenta

# If Install requested, attempt install via available manager
if($Install){
    if($target -eq 'xelatex' -and -not $haveXe){
        if($haveChoco){ & choco install miktex -y; exit $LASTEXITCODE }
        elseif($haveWinget){ & winget install MiKTeX.MiKTeX; exit $LASTEXITCODE }
        else { Write-Warning 'No package manager (winget/choco) found. Install MiKTeX manually from https://miktex.org/download'; exit 1 }
    }
    if($target -eq 'wkhtmltopdf' -and -not $haveWk){
        if($haveChoco){ & choco install wkhtmltopdf -y; exit $LASTEXITCODE }
        elseif($haveWinget){ & winget install wkhtmltopdf; exit $LASTEXITCODE }
        else { Write-Warning 'No package manager (winget/choco) found. Download from https://wkhtmltopdf.org/downloads.html'; exit 1 }
    }
}

# Otherwise: only suggest commands
if($target -eq 'xelatex' -and -not $haveXe){
    Write-Host "[suggest] 安装 XeLaTeX (MiKTeX) 指令：" -ForegroundColor Yellow
    Suggest-XeLaTeX
}
elseif($target -eq 'wkhtmltopdf' -and -not $haveWk){
    Write-Host "[suggest] 安装 wkhtmltopdf 指令：" -ForegroundColor Yellow
    Suggest-Wkhtmltopdf
}
else {
    Write-Host "[deps] 所需 PDF 引擎已就绪。" -ForegroundColor Green
}
