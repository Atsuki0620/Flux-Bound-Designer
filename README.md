# Spec-Finder

Ele.Flow 回帰分析を行う Streamlit アプリです。  
CSVを読み込み、回帰直線・95%予測区間・Ele.Flow上下限・交点を可視化します。

## 動作環境
- Windows 10/11
- Python 3.12 以上（推奨）

## セットアップ
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

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
- `dist\EleFlowAnalyzer\EleFlowAnalyzer.exe`

## 配布物の起動
```powershell
.\dist\EleFlowAnalyzer\EleFlowAnalyzer.exe
```
起動後、ブラウザで `http://localhost:8501` を開いて利用します。

## 起動確認チェックリスト
1. トップ画面が表示される
2. `sample_data.csv` をアップロードできる
3. `解析実行` で進捗バーが 0% → 100% で進む
4. 回帰式・R^2・交点（min/max）が表示される
5. グラフに観測点、回帰直線、95%予測区間、赤破線交点、青実線Ele.Flow上下限が表示される
