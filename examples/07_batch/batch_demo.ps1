param()
Write-Output "examples/07_batch: running batch demo (PowerShell)"
$out = Join-Path $env:TEMP ([System.Guid]::NewGuid().ToString())
New-Item -ItemType Directory -Path $out | Out-Null
$infile = Join-Path $out 'sample_input.csv'
[System.IO.File]::WriteAllText($infile, 'id,amount\n1,10\n2,15\n3,7\n4,20\n')

$result = (Import-Csv -Path $infile | Measure-Object -Property amount -Sum).Sum
$resultFile = Join-Path $out 'result.csv'
[System.IO.File]::WriteAllText($resultFile, "total,$result\n")
Write-Output "result:`n$(Get-Content $resultFile -Raw)"
Write-Output "wrote outputs to $out"
Exit 0
