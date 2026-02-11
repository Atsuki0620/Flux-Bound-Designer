import io
import time

import pandas as pd
import streamlit as st

from src.analysis import analyze_dataframe, build_figure, validate_dataframe


st.set_page_config(page_title="Ele.Flow 回帰分析ツール", layout="wide")


def build_template_csv_bytes() -> bytes:
    template = pd.DataFrame(
        {
            "F.S.Flux": [1.0, 2.0, 3.0, 4.0, 5.0],
            "Ele.Flow": [10.5, 20.3, 30.1, 40.8, 50.2],
        }
    )
    return template.to_csv(index=False).encode("utf-8-sig")


def read_uploaded_csv(file_obj) -> pd.DataFrame:
    raw = file_obj.getvalue()
    # UTF-8 is the standard; utf-8-sig also accepts BOM-prefixed UTF-8 safely.
    return pd.read_csv(io.BytesIO(raw), encoding="utf-8-sig")


def update_progress(progress_bar, status_box, value: int, message: str) -> None:
    progress_bar.progress(value)
    status_box.info(f"進捗: {value}% - {message}")


st.title("Ele.Flow 回帰分析ツール")
st.caption("CSVをアップロードすると、回帰直線・予測区間・Ele.Flow上下限との交点を可視化します。")

template_bytes = build_template_csv_bytes()

st.subheader("ステップ1: CSVテンプレートをダウンロード")
st.write("ステップ1: CSVテンプレートをダウンロードして、F.S.Flux と Ele.Flow の2列でデータを準備してください。")
st.download_button(
    label="テンプレートCSVをダウンロード",
    data=template_bytes,
    file_name="template_fsflux_eleflow.csv",
    mime="text/csv",
    use_container_width=True,
)

st.subheader("ステップ2: CSVをアップロード")
st.write("ステップ2: 作成したCSVファイルをアップロードしてください。")
uploaded_file = st.file_uploader(
    "解析に使うCSVファイルを選択してください",
    type=["csv"],
    label_visibility="visible",
)

if uploaded_file is not None:
    try:
        preview_df = read_uploaded_csv(uploaded_file)
        st.subheader("アップロード済みデータ")
        st.dataframe(preview_df, use_container_width=True, height=200)
    except Exception as exc:
        st.error(f"CSVの読み込みに失敗しました: {exc}")

st.subheader("ステップ3: 解析条件を入力")
st.write("ステップ3: Min_Ele_Flow（下限）と Max_Ele_Flow（上限）を入力してください。")
input_col1, input_col2, input_col3 = st.columns([1, 1, 1.2])
with input_col1:
    min_ele_flow = st.number_input("Min_Ele_Flow（下限）", value=8800.0, step=0.1)
with input_col2:
    max_ele_flow = st.number_input("Max_Ele_Flow（上限）", value=13200.0, step=0.1)
with input_col3:
    st.write("")
    st.write("")
    run_clicked = st.button("解析実行", type="primary", use_container_width=True)

if run_clicked:
    if uploaded_file is None:
        st.error("先にCSVファイルをアップロードしてください。")
    elif min_ele_flow >= max_ele_flow:
        st.error("Min_Ele_Flow は Max_Ele_Flow より小さい値にしてください。")
    else:
        progress_bar = st.progress(0)
        status_box = st.empty()
        try:
            update_progress(progress_bar, status_box, 0, "開始しました")
            time.sleep(0.08)

            update_progress(progress_bar, status_box, 20, "CSVを読み込み中")
            df = read_uploaded_csv(uploaded_file)
            time.sleep(0.08)

            update_progress(progress_bar, status_box, 40, "データを検証中")
            validated_df = validate_dataframe(df)
            time.sleep(0.08)

            update_progress(progress_bar, status_box, 65, "回帰分析を実行中")
            result, pred_summary, fitted_values = analyze_dataframe(
                validated_df,
                min_ele_flow=min_ele_flow,
                max_ele_flow=max_ele_flow,
            )
            time.sleep(0.08)

            update_progress(progress_bar, status_box, 85, "グラフを作成中")
            fig = build_figure(
                validated_df,
                pred_summary,
                fitted_values,
                result,
                min_ele_flow=min_ele_flow,
                max_ele_flow=max_ele_flow,
            )
            time.sleep(0.08)

            update_progress(progress_bar, status_box, 100, "完了")
            st.success("解析が完了しました。")
            st.subheader("解析結果")
            st.write(f"回帰式: y = {result.slope:.3f}x {result.intercept:+.3f}")
            st.write(f"決定係数 R^2: {result.r_squared:.3f}")
            st.write(f"min_intersection: {result.min_intersection:.3f}")
            st.write(f"max_intersection: {result.max_intersection:.3f}")
            st.plotly_chart(fig, use_container_width=True)
        except Exception as exc:
            status_box.empty()
            progress_bar.empty()
            st.error(f"解析に失敗しました: {exc}")
