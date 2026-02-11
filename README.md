# Spec-Finder

Ele.Flow 回帰分析を行う Streamlit アプリです。  
CSV を読み込み、回帰直線・95%予測区間・Ele.Flow 上下限・交点を可視化します。

## 動作環境

- Windows 10/11
- Python 3.12 推奨

## セットアップ

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 開発時の起動

```powershell
streamlit run app.py
```

## 入力CSV仕様

- 必須列: `F.S.Flux`, `Ele.Flow`
- 3行以上必要
- 欠損値なし
- 数値として解釈可能な値のみ

## 配布ビルド（PyInstaller / onedir）

以下をプロジェクト直下で実行します。

```powershell
.\.venv\Scripts\python -m PyInstaller `
  --noconfirm `
  --clean `
  --onedir `
  --name EleFlowAnalyzer `
  --collect-all streamlit `
  --collect-all plotly `
  --collect-all statsmodels `
  --collect-all pandas `
  --collect-all numpy `
  run_streamlit_app.py
```

出力先:

- 実行ファイル: `dist\EleFlowAnalyzer\EleFlowAnalyzer.exe`

## 配布物の起動

```powershell
.\dist\EleFlowAnalyzer\EleFlowAnalyzer.exe
```

起動後、ブラウザで `http://localhost:8501` を開いて利用します。

## 起動確認チェックリスト

1. アプリのトップ画面が表示される
2. `sample_data.csv` をアップロードできる
3. `解析実行` で進捗バーが 0% から 100% まで進む
4. 回帰式・R^2・交点（min/max）が表示される
5. グラフに以下が表示される
   - 観測点
   - 回帰直線
   - 95%予測区間
   - 赤破線の交点縦線
   - 青実線の Ele.Flow 上下限
