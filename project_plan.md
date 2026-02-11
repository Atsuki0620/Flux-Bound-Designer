# Data Analysis App Project Plan

## 1. 要件固定（半日）
- 内容: `data_analysis_app_specification.md` の機能要件・入出力・エラー条件を確定し、曖昧点を洗い出す
- 成果物: 要件チェックリスト（MVP/将来対応の切り分け）
- 完了条件: 「まず作る範囲」が合意されている

## 2. プロトタイプ解析（Phase 1: Notebook）（1日）
- 内容: `analysis_prototype.ipynb` でCSV読込、バリデーション、OLS回帰、95%予測区間、交点計算を実装
- 成果物: 再現可能なNotebook、サンプルCSVでの実行結果
- 完了条件: 手計算/期待値と主要指標（傾き・切片・R²・交点）が一致

## 3. コアロジックのモジュール化（0.5〜1日）
- 内容: Notebookの計算部分を `src/analysis.py` などに分離し、Streamlitから再利用可能にする
- 成果物: 純粋関数ベースの解析モジュール
- 完了条件: UIなしで関数単体実行できる（入出力が固定）

## 4. Streamlitアプリ実装（Phase 2）（1〜2日）
- 内容: `app.py` にテンプレDL、CSVアップロード、データ検証、Plotly可視化、結果表示を実装
- 成果物: ローカル実行可能なUI（`streamlit run app.py`）
- 完了条件: 正常系/異常系（列不足、欠損、行不足）で期待通りの表示

## 5. テスト・品質担保（1日）
- 内容: 解析ロジックの単体テスト、主要UIフローの手動テスト、境界値テスト（3行、100行）
- 成果物: `tests/`、テスト結果ログ、既知制約メモ
- 完了条件: 重要ロジックが自動テストで担保され、回帰を検知できる

## 6. 配布準備（Phase 3: exe化）（0.5〜1日）
- 内容: `requirements.txt` 固定、PyInstaller設定（`--onedir`優先検討）、起動確認手順を整備
- 成果物: 配布物（exe/フォルダ）、README運用手順
- 完了条件: 別環境で起動確認できる


---

## ?????2026-02-12 00:21?

- Streamlit UI?????????UI??????????0-100%??????????
- ?????????PyInstaller `--onedir` ???????
- ??????????: `dist/EleFlowAnalyzer_win64_20260212_001837.zip`
- ???????: `dist/EleFlowAnalyzer/EleFlowAnalyzer.exe` ???? `http://localhost:8501` ??????
- ?????????????: `README.md`, `release_checklist.md`?
