# データ分析 Streamlit アプリ仕様書

## 1. 目的
`F.S.Flux` と `Ele.Flow` の関係を回帰分析し、95%予測区間と  
`Min_Ele_Flow` / `Max_Ele_Flow` との交点を可視化する。

## 2. スコープ
- Phase 1: Notebookでロジック検証
- Phase 2: StreamlitでUI実装
- Phase 3: PyInstallerで配布可能な実行形式を作成

## 3. 入力仕様
- 必須列: `F.S.Flux`, `Ele.Flow`
- 3行以上
- 欠損値なし
- 数値として解釈可能

## 4. 解析仕様
- 手法: OLS回帰（`statsmodels`）
- 出力:
  - 回帰式 `y = ax + b`
  - 決定係数 `R^2`
  - `min_intersection`, `max_intersection`
- 予測区間: 95%

## 5. 可視化仕様（Plotly）
- 観測点（散布図）
- 回帰直線（表示x範囲全域）
- 95%予測区間（表示x範囲全域）
- 交点縦線: 赤破線、注釈なし、凡例なし
- Ele.Flow上下限: 青実線、凡例名 `Ele.Flow上下限`
- 交点マーカー: 赤、大きめ、凡例なし
- 軸範囲: データ・交点・上下限を含む範囲の外側10%
- y軸表記: `k`省略なし（生の数値）

## 6. UI仕様（Streamlit）
- 日本語UI
- 上から下へのステップ導線
  1. テンプレートCSVダウンロード
  2. CSVアップロード（直下にプレビュー表示）
  3. `Min_Ele_Flow` / `Max_Ele_Flow` 入力
  4. `解析実行`
- 実行時に進捗バーを0%→100%で表示

## 7. テスト仕様
- フレームワーク: `pytest`
- 入力検証と数値検証を実施
- 現在の結果: `6 passed`

## 8. 配布仕様
- PyInstaller `--onedir` を採用
- エントリーポイント: `run_streamlit_app.py`
- 実行ファイル: `dist/FluxBoundDesigner/FluxBoundDesigner.exe`
- 配布アーカイブ: `dist/FluxBoundDesigner_win64_20260212_001837.zip`

---

## 更新履歴（2026-02-12）
- Step 6（配布準備）完了
- 配布・起動確認・ドキュメント整備を実施
