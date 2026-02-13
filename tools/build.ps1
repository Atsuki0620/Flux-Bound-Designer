$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptRoot
Set-Location $projectRoot

$pythonExe = Join-Path $projectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    throw "Virtual environment python not found: $pythonExe"
}

function Invoke-PythonChecked {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Args
    )
    & $pythonExe @Args
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed: python $($Args -join ' ')"
    }
}

Write-Host "[0/6] Ensuring pytest is available..."
& $pythonExe -c "import pytest"
if ($LASTEXITCODE -ne 0) {
    Write-Host "pytest not found in .venv. Installing pytest..."
    Invoke-PythonChecked -Args @("-m", "pip", "install", "pytest")
}

Write-Host "[1/6] Running tests..."
Invoke-PythonChecked -Args @("-m", "pytest", "-q")

Write-Host "[2/6] Running syntax check..."
Invoke-PythonChecked -Args @("-m", "py_compile", "app.py", "src\analysis.py", "run_streamlit_app.py")

Write-Host "[3/6] Cleaning old build outputs..."
$pathsToRemove = @("build", "dist", "FluxBoundDesigner.spec")
foreach ($path in $pathsToRemove) {
    if (Test-Path $path) {
        Remove-Item -Recurse -Force $path
    }
}

Write-Host "[4/6] Building with PyInstaller..."
Invoke-PythonChecked -Args @(
    "-m", "PyInstaller",
    "--noconfirm",
    "--clean",
    "--onedir",
    "--name", "FluxBoundDesigner",
    "--add-data", "app.py;.",
    "--add-data", "src;src",
    "--add-data", "sample_data.csv;.",
    "--collect-all", "streamlit",
    "--collect-all", "plotly",
    "--collect-all", "statsmodels",
    "--collect-all", "pandas",
    "--collect-all", "numpy",
    "run_streamlit_app.py"
)

Write-Host "[5/6] Verifying build outputs..."
& powershell -ExecutionPolicy Bypass -File .\tools\verify_build.ps1
if ($LASTEXITCODE -ne 0) {
    throw "verify_build.ps1 failed."
}

Write-Host "[6/6] Writing dist README from template..."
$templatePath = Join-Path $projectRoot "tools\templates\README.txt"
$readmePath = Join-Path $projectRoot "dist\FluxBoundDesigner\README.txt"

if (-not (Test-Path $templatePath)) {
    throw "Template file not found: $templatePath"
}

Copy-Item -Path $templatePath -Destination $readmePath -Force

Write-Host ""
Write-Host "Build completed successfully."
Write-Host "Output: dist\FluxBoundDesigner\FluxBoundDesigner.exe"
