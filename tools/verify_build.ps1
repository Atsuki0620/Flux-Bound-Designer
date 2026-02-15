$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptRoot
Set-Location $projectRoot

$distRoot = Join-Path $projectRoot "dist\AppStart"
$requiredPaths = @(
    "dist\AppStart\AppStart.exe",
    "dist\AppStart\_internal\app.py",
    "dist\AppStart\_internal\src\analysis.py",
    "dist\AppStart\_internal\sample_data.csv"
)

$results = @()
foreach ($path in $requiredPaths) {
    $exists = Test-Path $path
    $results += [PSCustomObject]@{
        Path = $path
        Exists = $exists
    }
}

Write-Host "Required files check:"
$results | Format-Table -AutoSize

$missing = $results | Where-Object { -not $_.Exists }
if ($missing.Count -gt 0) {
    throw "Build verification failed. Missing required files."
}

$dirSizeBytes = (Get-ChildItem -Path $distRoot -Recurse -File | Measure-Object -Property Length -Sum).Sum
$dirSizeMb = [Math]::Round($dirSizeBytes / 1MB, 2)

Write-Host ""
Write-Host "Build size:"
Write-Host ("- dist\AppStart = {0} MB" -f $dirSizeMb)

if ($dirSizeMb -lt 20) {
    Write-Warning "Build size is unexpectedly small (< 20 MB). Verify packaging content."
}
if ($dirSizeMb -gt 800) {
    Write-Warning "Build size is large (> 800 MB). Consider reducing collect-all usage."
}

Write-Host ""
Write-Host "Build verification passed."
