# Repository Guidelines

## プロジェクト構成
- `app.py`: Streamlit UI本体（CSVアップロード、条件入力、解析実行、結果表示）
- `src/analysis.py`: 解析ロジック（バリデーション、OLS回帰、予測区間、グラフ生成）
- `tests/test_analysis.py`: `pytest` のテスト
- `analysis_prototype.ipynb`: 仕様確認用Notebook
- `sample_data.csv`: 動作確認用サンプルデータ
- `run_streamlit_app.py`: PyInstaller配布用ランチャー

## 開発コマンド
- `python -m venv .venv` / `.\\.venv\\Scripts\\Activate.ps1`: 仮想環境の作成・有効化
- `pip install -r requirements.txt`: 依存関係のインストール
- `streamlit run app.py`: ローカル起動
- `.\\.venv\\Scripts\\python -m pytest -q`: テスト実行
- `.\\.venv\\Scripts\\python -m py_compile app.py src\\analysis.py`: 構文チェック

## コーディング規約
- Pythonは4スペースインデント、PEP 8準拠
- 命名規約: 変数/関数は`snake_case`、クラスは`PascalCase`
- 解析ロジックは`src/analysis.py`に集約し、`app.py`はUI制御に集中させる
- 例外メッセージは原因が分かる具体的な文言にする

## テスト方針
- フレームワークは`pytest`
- テスト命名: `tests/test_*.py`、関数は`test_*`
- 入力検証（列不足・欠損・型不正・行数不足）と数値結果を必ず検証する
- PR前に`pytest`と`sample_data.csv`での手動確認を行う

## ドキュメントと文字コード
- `.md` は **UTF-8** で作成・保存する
- 文字化け回避のため、PowerShellで表示確認する際は `chcp 65001` を実行する
- 文字コードが混在しないよう、既存Markdownの追記・更新時もUTF-8を維持する

## コミットとPR
- コミットメッセージは命令形で簡潔に記述する
- PRには「変更概要」「検証手順」「検証結果」を記載する
- UI変更がある場合はスクリーンショットを添付する
