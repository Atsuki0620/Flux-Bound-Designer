import io
import time
from statistics import NormalDist

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.analysis import analyze_dataframe, build_figure, validate_dataframe


st.set_page_config(page_title="Flux Bound Designer", layout="wide")


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


def draw_section_divider() -> None:
    st.markdown(
        "<hr style='border:0; border-top:1px solid #e7e7e7; margin:0.8rem 0 1.2rem 0;'>",
        unsafe_allow_html=True,
    )


def get_confidence_comment(confidence_pct: float) -> str:
    if confidence_pct >= 99.0:
        return "安全重視の設定です。帯が太くなり、F.S.Flux 範囲はかなり狭くなります。"
    if confidence_pct >= 95.0:
        return "バランス型の設定です。実務でよく使われる安全側の目安です。"
    if confidence_pct >= 90.0:
        return "やや攻めた設定です。範囲は広がりやすい一方で取りこぼしリスクは上がります。"
    return "攻めた設定です。帯は細くなりますが、ばらつきの取りこぼしリスクが高まります。"


def build_prediction_interval_simulation_figure(confidence_pct: float) -> tuple[go.Figure, int, int]:
    # Simulation constants for an intuitive manufacturing example.
    lsl = 9200.0
    usl = 12600.0
    slope = 4700.0
    intercept = 5000.0
    x_min, x_max = 0.8, 1.8
    x_plot_min, x_plot_max = 0.8, 1.8
    x_center = (x_min + x_max) / 2.0
    base_sigma = 240.0
    sigma_variation = 45.0

    # Load pre-generated perfect simulation data (seed 634, quantile method)
    # This data achieves ±1 accuracy for all prediction levels 50-99%
    try:
        sim_data = pd.read_csv("simulation_data_perfect.csv")
        x_obs = sim_data["x"].to_numpy()
        y_obs = sim_data["y"].to_numpy()
    except FileNotFoundError:
        # Fallback: generate on-the-fly if CSV doesn't exist
        from statistics import NormalDist
        rng = np.random.default_rng(634)
        x_obs = np.linspace(x_min, x_max, 100)
        sigma_obs = base_sigma + sigma_variation * ((x_obs - x_center) ** 2)

        random_order = rng.permutation(100)
        ranks = np.argsort(random_order)
        standardized_residuals = np.array([NormalDist().inv_cdf((ranks[i] + 0.5) / 100.0) for i in range(100)])
        residuals = standardized_residuals * sigma_obs
        y_obs = slope * x_obs + intercept + residuals

    x_line = np.linspace(x_plot_min, x_plot_max, 320)
    y_line = slope * x_line + intercept

    z = NormalDist().inv_cdf(0.5 + float(confidence_pct) / 200.0)
    pred_sigma = base_sigma + sigma_variation * ((x_line - x_center) ** 2)
    band_half = z * pred_sigma
    pi_upper = y_line + band_half
    pi_lower = y_line - band_half

    obs_pi_upper = np.interp(x_obs, x_line, pi_upper)
    obs_pi_lower = np.interp(x_obs, x_line, pi_lower)
    in_interval_mask = (y_obs <= obs_pi_upper) & (y_obs >= obs_pi_lower)
    in_count = int(np.count_nonzero(in_interval_mask))
    out_count = int(x_obs.size - in_count)

    valid_mask = (pi_upper <= usl) & (pi_lower >= lsl)
    has_valid = bool(np.any(valid_mask))
    if has_valid:
        x_recommended = x_line[valid_mask]
        rec_x_min = float(x_recommended.min())
        rec_x_max = float(x_recommended.max())
    else:
        rec_x_min = rec_x_max = None

    marker_y = 8120.0

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x_obs[in_interval_mask],
            y=y_obs[in_interval_mask],
            mode="markers",
            marker=dict(color="rgba(0, 90, 180, 0.8)", size=7),
            name="予測区間内",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=x_obs[~in_interval_mask],
            y=y_obs[~in_interval_mask],
            mode="markers",
            marker=dict(color="rgba(198, 40, 40, 0.85)", size=7),
            name="予測区間外",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=x_line,
            y=y_line,
            mode="lines",
            line=dict(color="#1f77b4", width=3),
            name="回帰直線",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=x_line,
            y=pi_upper,
            mode="lines",
            line=dict(width=0),
            hoverinfo="skip",
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=x_line,
            y=pi_lower,
            mode="lines",
            fill="tonexty",
            fillcolor="rgba(31, 119, 180, 0.25)",
            line=dict(width=0),
            name=f"{confidence_pct:.1f}% 予測区間",
        )
    )
    fig.add_hline(y=usl, line_dash="dash", line_color="#c62828", line_width=2)
    fig.add_hline(y=lsl, line_dash="dash", line_color="#c62828", line_width=2)
    fig.add_annotation(x=x_plot_max, y=usl, text="上限", showarrow=False, xanchor="left", font=dict(color="#c62828"))
    fig.add_annotation(x=x_plot_max, y=lsl, text="下限", showarrow=False, xanchor="left", font=dict(color="#c62828"))

    if has_valid:
        fig.add_vline(x=rec_x_min, line_dash="dot", line_color="#2e7d32", line_width=1)
        fig.add_vline(x=rec_x_max, line_dash="dot", line_color="#2e7d32", line_width=1)
        fig.add_trace(
            go.Scatter(
                x=[rec_x_min, rec_x_max],
                y=[marker_y, marker_y],
                mode="lines+markers",
                line=dict(color="#2e7d32", width=12),
                marker=dict(size=10, color="#2e7d32"),
                name="平膜Flux範囲",
            )
        )
        fig.add_annotation(
            x=(rec_x_min + rec_x_max) / 2.0,
            y=8380.0,
            text=f"範囲: {rec_x_min:.2f} - {rec_x_max:.2f}",
            showarrow=False,
            font=dict(color="#1b5e20"),
        )
    else:
        fig.add_annotation(
            x=(x_min + x_max) / 2.0,
            y=8380.0,
            text="この条件では範囲がありません",
            showarrow=False,
            font=dict(color="#b71c1c"),
        )

    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0.0),
    )
    fig.update_xaxes(title="F.S.Flux", range=[x_plot_min, x_plot_max])
    fig.update_yaxes(title="Ele.Flow", range=[8000.0, 14000.0], tickformat=",.0f")
    return fig, in_count, out_count


st.title("📈 Flux Bound Designer")
st.markdown(
    "<p style='font-size:1.08rem; color:#111111; margin-top:-0.25rem;'>"
    "実測データのバラツキから将来の変動を考慮し、エレメント規格を満たせる平膜の範囲を算出します。"
    "</p>",
    unsafe_allow_html=True,
)

with st.expander("【説明】平膜Flux範囲の算出方法"):
    left_col, right_col = st.columns([1, 2])
    with left_col:
        # 概念説明
        st.markdown(
            "本ツールは実測データから回帰直線と予測区間を算出し、"
            "エレメント規格（下限・上限）を満たす平膜Flux範囲を導出します。"
            "予測区間は将来のばらつきを考慮した範囲を示し、"
            "予測水準（%）が高いほど安全側の設定となりますが範囲は狭くなります。"
            "下記のスライダーで予測水準を変更すると、グラフ上の範囲がどう変化するかシミュレーションできます。"
        )

        # 区切り線
        st.markdown("---")

        # スライダー
        sim_confidence_pct = st.slider(
            "予測水準（%）",
            min_value=50,
            max_value=99,
            value=95,
            step=1,
        )

        # グラフ作成
        sim_fig, sim_in_count, sim_out_count = build_prediction_interval_simulation_figure(sim_confidence_pct)
        total_count = sim_in_count + sim_out_count

        st.markdown(f'<span style="color: rgba(0, 90, 180, 0.8);">予測区間内 ●: {sim_in_count} 点</span>', unsafe_allow_html=True)
        st.markdown(f'<span style="color: rgba(198, 40, 40, 0.85);">予測区間外 ●: {sim_out_count} 点</span>', unsafe_allow_html=True)
        st.write(f"区間内の比率: {sim_in_count / total_count * 100:.1f}%")

    with right_col:
        st.plotly_chart(
            sim_fig,
            use_container_width=True,
        )

template_bytes = build_template_csv_bytes()
draw_section_divider()

st.subheader("📥 ステップ1")
st.write("CSVテンプレートをダウンロードして、F.S.Flux と Ele.Flow の2列でデータを準備してください。")
st.download_button(
    label="📄 テンプレートCSVをダウンロード",
    data=template_bytes,
    file_name="template_fsflux_eleflow.csv",
    mime="text/csv",
    use_container_width=True,
)
draw_section_divider()

st.subheader("📂 ステップ2")
st.write("作成したCSVファイルをアップロードしてください。")
uploaded_file = st.file_uploader(
    "ドラッグ&ドロップ、またはクリックしてファイルを選択",
    type=["csv"],
    label_visibility="visible",
)

if uploaded_file is not None:
    try:
        preview_df = read_uploaded_csv(uploaded_file)
        st.subheader("🗂️ アップロード済みデータ")
        st.dataframe(preview_df, use_container_width=True, height=200)
    except Exception as exc:
        st.error(f"CSVの読み込みに失敗しました: {exc}")
draw_section_divider()

st.subheader("🎯 ステップ3")
st.write("分析条件を設定してください。")
input_col1, input_col2, input_col3, input_col4, input_col5 = st.columns([1, 1, 1.8, 1.1, 1.0])
with input_col1:
    min_ele_flow = st.number_input("エレメントFlow下限", value=8800.0, step=0.1)
with input_col2:
    max_ele_flow = st.number_input("エレメントFlow上限", value=13200.0, step=0.1)
with input_col3:
    prediction_interval_option = st.radio(
        "予測水準（%）",
        options=["68%", "90%", "95%", "99.7%", "カスタム"],
        index=2,
        horizontal=True,
    )
with input_col4:
    custom_prediction_interval_pct = st.number_input(
        "カスタム予測水準（%）",
        min_value=0.1,
        max_value=99.9,
        value=95.0,
        step=0.1,
        format="%.1f",
        disabled=prediction_interval_option != "カスタム",
    )
with input_col5:
    st.write("")
    st.write("")
    run_clicked = st.button("🚀 分析実行", type="primary", use_container_width=True)

if prediction_interval_option == "カスタム":
    prediction_interval_pct = float(custom_prediction_interval_pct)
else:
    prediction_interval_pct = float(prediction_interval_option.replace("%", ""))

st.markdown(
    """
    <style>
    div[data-testid="stButton"] > button {
        background-color: #0b6e4f;
        color: #ffffff;
        border: 1px solid #09553d;
        font-size: 1.15rem;
        font-weight: 700;
    }
    div[data-testid="stButton"] > button:hover {
        background-color: #09553d;
        color: #ffffff;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

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
                prediction_interval_pct=prediction_interval_pct,
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
                prediction_interval_pct=prediction_interval_pct,
            )
            time.sleep(0.08)

            update_progress(progress_bar, status_box, 100, "完了")
            st.success("分析が完了しました。")
            st.subheader("✅ 分析結果")
            result_col_left, result_col_right = st.columns([1, 2])
            with result_col_left:
                st.write(f"回帰式: y = {result.slope:.3f}x {result.intercept:+.3f}")
                st.write(f"決定係数 R^2: {result.r_squared:.3f}")
                st.write(f"予測区間: {prediction_interval_pct:g}%")
                st.write(f"平膜Flux範囲: {result.min_intersection:.3f} ～ {result.max_intersection:.3f}")
            with result_col_right:
                st.plotly_chart(fig, use_container_width=True)
        except Exception as exc:
            status_box.empty()
            progress_bar.empty()
            st.error(f"分析に失敗しました: {exc}")
