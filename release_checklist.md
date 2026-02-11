# 配布前チェックリスト

## ビルド前

- `.venv` を有効化済み
- `pip install -r requirements.txt` 実行済み
- `python -m pytest -q` が成功

## ビルド

- `python -m PyInstaller --onedir --name EleFlowAnalyzer ... run_streamlit_app.py` が成功
- `dist\EleFlowAnalyzer\EleFlowAnalyzer.exe` が生成される

## 配布物の確認

- `EleFlowAnalyzer.exe` 起動でアプリが開く
- `sample_data.csv` で解析実行できる
- 進捗バーが 0% -> 100% で動く
- グラフ表示が Notebook と一致する
