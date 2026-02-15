# Flux規格提案くん

Streamlit app for regression analysis of F.S.Flux vs Ele.Flow, visualizing regression line, 95% prediction interval, and intersections with Ele.Flow bounds.

## 動作環境
- Windows 10/11
- Python 3.12 以上（推奨）

## セットアップ
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## プロジェクト構成
- `app.py` - Streamlit アプリケーション本体
- `src/` - 解析ロジック
- `tests/` - テストコード
- `tools/` - ビルドスクリプト (`build.ps1`, `verify_build.ps1`)
- `notebooks/` - プロトタイプノートブック
- `docs/development/` - 開発ドキュメント
- `docs/distribution/` - 配布・ビルド手順書

## ローカル実行
```powershell
streamlit run app.py
```

## 入力CSV仕様
- 必須列: `F.S.Flux`, `Ele.Flow`
- 3行以上必要
- 欠損値なし
- 数値として解釈可能な値のみ

## 配布ビルド（PyInstaller / onedir）

**推奨**: ビルドスクリプトを使用
```powershell
.\tools\build.ps1
```

**手動ビルド**（必要時のみ）:
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

出力先:
- `dist\AppStart\AppStart.exe`

## 配布物の起動
```powershell
.\dist\AppStart\AppStart.exe
```
起動後、ブラウザで `http://localhost:8501` を開いて利用します。

## 起動確認チェックリスト
1. トップ画面が表示される
2. `sample_data.csv` をアップロードできる
3. `解析実行` で進捗バーが 0% → 100% で進む
4. 回帰式・R^2・交点（min/max）が表示される
5. グラフに観測点、回帰直線、95%予測区間、赤破線交点、青実線Ele.Flow上下限が表示される
