$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
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
& powershell -ExecutionPolicy Bypass -File .\verify_build.ps1
if ($LASTEXITCODE -ne 0) {
    throw "verify_build.ps1 failed."
}

Write-Host "[6/6] Writing dist README..."
$readmePath = Join-Path $projectRoot "dist\FluxBoundDesigner\README.txt"
@"
Flux Bound Designer (Spec-Finder) 配布パッケージ
=================================================

このフォルダには、Flux Bound Designer の実行に必要なファイルが含まれています。
通常は Python の追加インストールなしで起動できます。

【起動手順】
1. 「FluxBoundDesigner.exe」をダブルクリックします。
2. 数秒から十数秒待つと、ブラウザで画面が開きます。
3. 自動で開かない場合は、ブラウザで次を開いてください。
   http://localhost:8501

【アプリの基本操作】
1. 画面の手順に従って CSV をアップロードします。
2. 必要に応じて Min_Ele_Flow / Max_Ele_Flow を入力します。
3. 「解析実行」を押すと、回帰式・決定係数・交点・グラフが表示されます。

【注意事項】
- 本アプリはローカルPC上で Streamlit サーバー（ポート 8501）を起動します。
- 社内セキュリティソフトやファイアウォールの設定により、初回起動時に確認ダイアログが表示される場合があります。
- 起動中はコマンドウィンドウを閉じないでください（終了するとアプリも停止します）。

【うまく起動しない場合】
1. エクスプローラーのアドレスバーに「cmd」と入力して Enter を押します。
2. 開いたターミナルで次を実行します。
   .\FluxBoundDesigner.exe
3. 表示されたメッセージ（エラー内容）を開発担当者へ共有してください。
"@ | Set-Content -Path $readmePath -Encoding UTF8

Write-Host ""
Write-Host "Build completed successfully."
Write-Host "Output: dist\FluxBoundDesigner\FluxBoundDesigner.exe"
