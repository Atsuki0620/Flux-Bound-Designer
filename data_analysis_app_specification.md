# 📘 データ分析Streamlitアプリ 実装仕様書

## 1. プロジェクト概要

### 目的
F.S.FluxとEle.Flowの相関分析を行い、95%予測区間と規格限界の交点を算出するStreamlitアプリを開発し、exe化して配布する。

### 開発フロー
```
Phase 1: Jupyter Notebookで分析ロジック確立・合意
Phase 2: Streamlitアプリ化 & ローカルUI確認・調整
Phase 3: PyInstallerでexe化
```

---

## 2. 技術スタック

```python
# 必須ライブラリ
pandas >= 1.5.0
numpy >= 1.23.0
plotly >= 5.14.0
statsmodels >= 0.14.0
streamlit >= 1.28.0
pyinstaller >= 5.13.0  # exe化時
```

---

## 3. 機能仕様

### 3.1 テンプレートCSVダウンロード機能

**仕様**
- カラム: `F.S.Flux`, `Ele.Flow`
- 5行のサンプルデータ付き
- データ型: float

**サンプルデータ例**
```csv
F.S.Flux,Ele.Flow
1.0,10.5
2.0,20.3
3.0,30.1
4.0,40.8
5.0,50.2
```

**実装ポイント**
- Streamlitの`st.download_button`でCSV生成
- UTF-8 BOM付きで保存（Excel互換）

---

### 3.2 CSVアップロード & バリデーション

**処理フロー**
```
1. CSVアップロード (st.file_uploader)
2. DataFrame読み込み (pd.read_csv)
3. DataFrame表示 (st.dataframe)
4. データクリーニング
   - 欠損値のある行を自動削除
   - 削除した行数を表示
5. データ件数チェック
   - 3点未満 → エラー表示して処理中止
   - 3点以上 → 分析続行
```

**エラーメッセージ例**
```
❌ エラー: データ点数が不足しています
有効なデータ: 2点
最低必要点数: 3点
欠損値のある行を削除しましたが、データが不足しています。
```

---

### 3.3 散布図描画（Plotly）

**要素**
1. **散布図**: X軸=F.S.Flux, Y軸=Ele.Flow
2. **規格線**: y=上限（オレンジ）、y=下限（オレンジ）← ユーザー入力
3. **線形回帰線**
4. **95%予測区間**: 上側・下側
5. **交点**: 赤いマーカー + 赤い縦線（x=交点）

**初期設定**
- デフォルト設定で作成
- Phase 1（ipynb）で見た目を確認・調整
- Phase 2（Streamlit）でUI上で最終調整

**凡例**
- Phase 1で試行して決定（おまかせ）

---

### 3.4 線形回帰 & 予測区間計算

**使用ライブラリ**: `statsmodels.api`

**計算内容**
```python
import statsmodels.api as sm

# 線形回帰
X = df['F.S.Flux']
y = df['Ele.Flow']
X_with_const = sm.add_constant(X)
model = sm.OLS(y, X_with_const).fit()

# 予測区間（95%）
predictions = model.get_prediction(X_with_const)
pred_summary = predictions.summary_frame(alpha=0.05)
# pred_summary['obs_ci_lower'] → 下側予測区間
# pred_summary['obs_ci_upper'] → 上側予測区間
```

**表示項目**
- R²（決定係数）
- 回帰式: `y = {slope:.4f}x + {intercept:.4f}`

---

### 3.5 交点計算アルゴリズム

**目的**
- 下側予測区間とy=下限の交点 → `min_Intersection point`
- 上側予測区間とy=上限の交点 → `max_Intersection point`

**計算方法**
```python
# 予測区間は直線ではないが、線形近似で交点を求める
# または、予測区間の直線（y = ax + b形式）を求めて交点計算

# 下側予測区間: y_lower = a_lower * x + b_lower
# y_lower = 下限 を解く
# min_Intersection = (下限 - b_lower) / a_lower

# 上側予測区間: y_upper = a_upper * x + b_upper
# y_upper = 上限 を解く
# max_Intersection = (上限 - b_upper) / a_upper
```

**注意点**
- 予測区間は非線形の可能性があるため、Phase 1で確認
- 必要に応じて多項式近似や補間を検討

---

### 3.6 結果表示UI

**表示内容**
```
📊 分析結果

回帰式: y = 10.123x + 2.456
R² = 0.987

🔴 交点情報
- min_Intersection point (下側予測区間 ∩ 下限): X = 3.45
- max_Intersection point (上側予測区間 ∩ 上限): X = 8.92
```

**グラフ上での可視化**
- 赤いマーカー（scatter）で交点を明示
- 赤い縦線（`x=交点`）をプロット

---

## 4. データ構造定義

### 4.1 CSVフォーマット
```
F.S.Flux,Ele.Flow
<float>,<float>
<float>,<float>
...
```

### 4.2 DataFrame構造
```python
df = pd.DataFrame({
    'F.S.Flux': [float, ...],
    'Ele.Flow': [float, ...]
})
```

### 4.3 計算結果
```python
results = {
    'slope': float,           # 傾き
    'intercept': float,       # 切片
    'r_squared': float,       # R²
    'min_intersection': float,  # 下側交点
    'max_intersection': float   # 上側交点
}
```

---

## 5. UI/UXフロー（Streamlit）

### 画面レイアウト案
```
========================================
📈 F.S.Flux vs Ele.Flow 分析ツール
========================================

【Step 1】テンプレートダウンロード
[Download CSV Template] ボタン

【Step 2】データアップロード
[Browse files] ← CSVアップロード

【Step 3】規格限界設定
上限: [____] 
下限: [____]
[分析実行] ボタン

========================================
📊 結果表示
----------------------------------------
- DataFrame表示（アップロード後）
- 散布図（Plotly）
- 統計情報（R², 回帰式）
- 交点情報（テキスト表示）
========================================
```

---

## 6. 実装段階

### Phase 1: Jupyter Notebook（分析ロジック確立）

**ファイル**: `analysis_prototype.ipynb`

**実装内容**
1. サンプルCSVの生成
2. データ読み込み・クリーニング
3. statsmodelsで線形回帰 & 予測区間
4. Plotlyで散布図作成
5. 交点計算ロジック
6. 凡例・グラフスタイル調整

**成果物**
- 動作確認済みのコード
- 最終的なグラフデザイン

---

### Phase 2: Streamlitアプリ化

**ファイル**: `app.py`

**実装内容**
1. ipynbのコードをStreamlit形式に移植
2. UIコンポーネント実装
   - ファイルアップローダー
   - 数値入力（上限・下限）
   - ボタン配置
3. ローカルで起動確認
   ```bash
   streamlit run app.py
   ```
4. UI調整（レイアウト、色、サイズ等）

---

### Phase 3: exe化

**ツール**: PyInstaller

**手順**
```bash
# 1. 仮想環境作成
python -m venv venv
venv\Scripts\activate

# 2. 必要ライブラリインストール
pip install -r requirements.txt

# 3. exe化
pyinstaller --onefile --add-data "venv/Lib/site-packages/streamlit;streamlit" app.py

# または、specファイル作成して調整
pyi-makespec --onefile app.py
# app.specを編集後
pyinstaller app.spec
```

**注意点**
- Streamlitのexe化は`--onefile`だと問題が出る場合あり
- `--onedir`推奨（フォルダ形式）
- `.streamlit/config.toml`も含める

**代替案**
- **Nuitka**: より軽量・高速なexeが可能
- **Docker**: exe不要でDocker Desktop上で実行

---

## 7. テストケース

### 正常系
| テスト項目 | 入力 | 期待結果 |
|-----------|------|---------|
| 正常データ | 5点の有効データ | 散布図・交点が正しく表示 |
| 大量データ | 100点 | 処理完了 |

### 異常系
| テスト項目 | 入力 | 期待結果 |
|-----------|------|---------|
| 欠損値あり | 10点中3点に欠損 | 欠損削除後、7点で分析 |
| 不足データ | 2点のみ | エラー表示 |
| カラム名誤り | F.S.Flux → Flux | エラー表示 |
| 非数値データ | 文字列混入 | 該当行削除 or エラー |

---

## 8. 補足事項

### 予測区間の直線近似について
statsmodelsの予測区間は厳密には曲線ですが、データ範囲内では直線近似で問題ない場合が多いです。Phase 1で確認し、必要に応じて以下を検討：
- `numpy.polyfit`で予測区間を線形近似
- 補間（`scipy.interpolate`）で交点を数値的に求める

### exe化のファイルサイズ
- 想定サイズ: 200-500MB
- 同僚への配布方法: 共有フォルダ or USBメモリ

---

## 9. 次のアクション

1. **Phase 1開始**: Jupyter Notebookで分析ロジック実装
2. 実装後、グラフデザインと凡例を確認・調整
3. 合意後、Phase 2（Streamlitアプリ化）へ進む

**このドキュメントをCoding Agentに渡して実装を依頼してください！**


---

## ?????2026-02-12 00:21?

### Step 6??????????
- PyInstaller `--onedir` ???????????? `dist/EleFlowAnalyzer` ????
- ??????????: `dist/EleFlowAnalyzer_win64_20260212_001837.zip`?
- ??????????????? `run_streamlit_app.py` ????
- ?????????????????? `README.md` ? `release_checklist.md` ?????

### ????
- ???????: `6 passed`
- ??????: `EleFlowAnalyzer.exe` ?? Streamlit ??????localhost?????
