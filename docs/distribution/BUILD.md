# Flux規格提案くん ビルド手順書

このドキュメントは、Flux規格提案くん を Windows 環境でビルドし、配布可能な実行ファイル（`.exe`）を作成するための手順をまとめたものです。
日常運用では `tools\build.ps1` を実行すれば必要な処理が一括で実行されるようにしています。

## 1. 前提条件
- Windows 10/11
- PowerShell
- Python（プロジェクトで利用しているバージョン）
- プロジェクトルートに `requirements.txt` が存在すること
- `tools\` フォルダに `build.ps1`、`verify_build.ps1` が存在すること

## 2. 通常のビルド手順（推奨）
まずは仮想環境を作成し、依存関係をインストールします。  
すでに `.venv` がある場合は、`Activate.ps1` から実行してください。

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
.\tools\build.ps1
```

`tools\build.ps1` は以下を自動で実行します。
1. `pytest` によるテスト実行
2. 構文チェック（`py_compile`）
3. 既存の `build/`・`dist/`・`AppStart.spec` の削除
4. PyInstaller による onedir ビルド
5. `tools\verify_build.ps1` による成果物検証
6. `dist\AppStart\README.txt` の生成

## 3. ビルド成果物の確認
ビルド成功後は、最低限次のファイルが存在することを確認してください。

- `dist\AppStart\AppStart.exe`
- `dist\AppStart\_internal\app.py`
- `dist\AppStart\_internal\src\analysis.py`
- `dist\AppStart\_internal\sample_data.csv`

手動で検証する場合は、次を実行します。

```powershell
.\tools\verify_build.ps1
```

## 4. 実行確認
作成したアプリは次のコマンドで起動します。

```powershell
.\dist\AppStart\AppStart.exe
```

起動後、ブラウザで以下にアクセスして画面表示を確認します。
- `http://localhost:8501`

初回起動時は表示まで 10 秒以上かかる場合があります。これは PyInstaller 版では比較的よくある挙動です。

## 5. 会社PCでの運用（GitHub ZIP 展開後）
`dist/` と `build/` は通常 `.gitignore` 対象です。  
そのため、GitHub からダウンロードした ZIP を会社PCで展開した直後は、`dist\AppStart` が存在しない前提で運用してください。

つまり、会社PCでは **`.\tools\build.ps1` の実行が必須** です。

### 5.1 会社PCでの最小手順
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
.\tools\build.ps1
```

### 5.2 同僚へ渡すファイル
同僚に渡すときは、ソース一式ではなく次を渡してください。
- `dist\AppStart` フォルダ一式（ZIP化して送付）

同僚側の基本操作は以下です。
1. ZIP を展開
2. `AppStart.exe` を実行
3. 必要に応じて `http://localhost:8501` を開く

## 6. 今後の改良時の運用
今後コードを更新する場合も手順は同じです。
変更後に `.\tools\build.ps1` を再実行すれば、テスト・クリーン・ビルド・検証まで一貫して実施できます。

## 7. 手動ビルドコマンド（必要時のみ）
通常は `tools\build.ps1` を使うため、以下は調査や切り分けが必要な場合のみ使用してください。

```powershell
.\.venv\Scripts\python -m PyInstaller `
  --noconfirm `
  --clean `
  --onedir `
  --name AppStart `
  --add-data "app.py;." `
  --add-data "src;src" `
  --add-data "sample_data.csv;." `
  --collect-all streamlit `
  --collect-all plotly `
  --collect-all statsmodels `
  --collect-all pandas `
  --collect-all numpy `
  run_streamlit_app.py
```

## 8. トラブルシューティング
### 8.1 ブラウザが 3000 番など別ポートを開く
- `run_streamlit_app.py` で以下が明示されているか確認
- `--server.port 8501`
- `--browser.serverPort 8501`
- `--browser.serverAddress localhost`

### 8.2 `ERR_CONNECTION_REFUSED` が出る
- EXE をターミナルから起動してログを確認
- 8501 ポートが他プロセスに使用されていないか確認

```powershell
Get-NetTCPConnection -LocalPort 8501 -ErrorAction SilentlyContinue
```

### 8.3 `localhost` で 404 が出る
- 同梱ファイル不足が主因のことが多い
- `app.py` と `src` が `--add-data` で含まれているか確認
- `.\tools\verify_build.ps1` で必須ファイルを確認

### 8.4 ビルド成功表示なのに EXE がすぐ終了する
一度クリーンして再ビルドしてください。

```powershell
Remove-Item -Recurse -Force build, dist, AppStart.spec
.\tools\build.ps1
```



