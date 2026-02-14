from dataclasses import dataclass

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import statsmodels.api as sm


REQUIRED_COLUMNS = ["F.S.Flux", "Ele.Flow"]


@dataclass(frozen=True)
class AnalysisResult:
    slope: float
    intercept: float
    r_squared: float
    min_intersection: float
    max_intersection: float


def load_and_validate_csv(file_path: str, encoding: str = "utf-8") -> pd.DataFrame:
    df = pd.read_csv(file_path, encoding=encoding)
    return validate_dataframe(df)


def validate_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    validated = df.copy()

    if len(validated) < 3:
        raise ValueError("At least 3 rows are required for analysis.")

    if validated[REQUIRED_COLUMNS].isnull().any().any():
        raise ValueError("Missing values found in required columns.")

    for col in REQUIRED_COLUMNS:
        validated[col] = pd.to_numeric(validated[col], errors="raise")

    return validated


def analyze_dataframe(
    df: pd.DataFrame,
    min_ele_flow: float,
    max_ele_flow: float,
    prediction_interval_pct: float = 95.0,
) -> tuple[AnalysisResult, pd.DataFrame, np.ndarray]:
    validated = validate_dataframe(df)
    if not (0.0 < float(prediction_interval_pct) < 100.0):
        raise ValueError("prediction_interval_pct must be between 0 and 100.")

    x = validated["F.S.Flux"].astype(float)
    y = validated["Ele.Flow"].astype(float)
    x_with_const = sm.add_constant(x)

    model = sm.OLS(y, x_with_const).fit()
    alpha = 1.0 - float(prediction_interval_pct) / 100.0
    pred_summary = model.get_prediction(x_with_const).summary_frame(alpha=alpha)

    slope = float(model.params["F.S.Flux"])
    intercept = float(model.params["const"])
    r_squared = float(model.rsquared)

    lower_fit = np.polyfit(x.to_numpy(), pred_summary["obs_ci_lower"].to_numpy(), deg=1)
    upper_fit = np.polyfit(x.to_numpy(), pred_summary["obs_ci_upper"].to_numpy(), deg=1)
    a_lower, b_lower = float(lower_fit[0]), float(lower_fit[1])
    a_upper, b_upper = float(upper_fit[0]), float(upper_fit[1])

    if abs(a_lower) < 1e-12:
        raise ZeroDivisionError("Lower CI fitted slope is too close to zero.")
    if abs(a_upper) < 1e-12:
        raise ZeroDivisionError("Upper CI fitted slope is too close to zero.")

    min_intersection = (float(min_ele_flow) - b_lower) / a_lower
    max_intersection = (float(max_ele_flow) - b_upper) / a_upper

    result = AnalysisResult(
        slope=slope,
        intercept=intercept,
        r_squared=r_squared,
        min_intersection=float(min_intersection),
        max_intersection=float(max_intersection),
    )
    return result, pred_summary, model.fittedvalues.to_numpy()


def build_figure(
    df: pd.DataFrame,
    pred_summary: pd.DataFrame,
    fitted_values: np.ndarray,
    result: AnalysisResult,
    min_ele_flow: float,
    max_ele_flow: float,
    prediction_interval_pct: float = 95.0,
) -> go.Figure:
    x = df["F.S.Flux"].astype(float)
    y = df["Ele.Flow"].astype(float)
    x_candidates = np.array([x.min(), x.max(), result.min_intersection, result.max_intersection], dtype=float)
    y_candidates = np.array([y.min(), y.max(), float(min_ele_flow), float(max_ele_flow)], dtype=float)

    x_min = float(np.min(x_candidates))
    x_max = float(np.max(x_candidates))
    y_min = float(np.min(y_candidates))
    y_max = float(np.max(y_candidates))

    x_pad = (x_max - x_min) * 0.1
    y_pad = (y_max - y_min) * 0.1
    if x_pad == 0.0:
        x_pad = max(abs(x_min) * 0.1, 1.0)
    if y_pad == 0.0:
        y_pad = max(abs(y_min) * 0.1, 1.0)

    x_plot_min = x_min - x_pad
    x_plot_max = x_max + x_pad
    y_plot_min = y_min - y_pad
    y_plot_max = y_max + y_pad

    x_line = np.linspace(x_plot_min, x_plot_max, 200)
    reg_line = result.slope * x_line + result.intercept
    lower_fit = np.polyfit(x.to_numpy(), pred_summary["obs_ci_lower"].to_numpy(), deg=1)
    upper_fit = np.polyfit(x.to_numpy(), pred_summary["obs_ci_upper"].to_numpy(), deg=1)
    ci_lower_line = lower_fit[0] * x_line + lower_fit[1]
    ci_upper_line = upper_fit[0] * x_line + upper_fit[1]

    obs_ci_upper = pred_summary["obs_ci_upper"].to_numpy()
    obs_ci_lower = pred_summary["obs_ci_lower"].to_numpy()
    in_interval_mask = (y.to_numpy() <= obs_ci_upper) & (y.to_numpy() >= obs_ci_lower)
    out_interval_mask = ~in_interval_mask

    marker_y = y_plot_min + (y_plot_max - y_plot_min) * 0.04
    marker_label_y = y_plot_min + (y_plot_max - y_plot_min) * 0.09

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x[in_interval_mask],
            y=y[in_interval_mask],
            mode="markers",
            name="予測区間内",
            marker=dict(size=8, color="rgba(0, 90, 180, 0.8)"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=x[out_interval_mask],
            y=y[out_interval_mask],
            mode="markers",
            name="予測区間外",
            marker=dict(size=8, color="rgba(198, 40, 40, 0.85)"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=x_line,
            y=reg_line,
            mode="lines",
            line=dict(color="#1f77b4", width=3),
            name="回帰直線",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=x_line,
            y=ci_upper_line,
            mode="lines",
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=x_line,
            y=ci_lower_line,
            mode="lines",
            line=dict(width=0),
            fill="tonexty",
            fillcolor="rgba(31, 119, 180, 0.25)",
            name=f"{float(prediction_interval_pct):g}% 予測区間",
        )
    )

    fig.add_hline(y=float(max_ele_flow), line_dash="dash", line_color="#c62828", line_width=2)
    fig.add_hline(y=float(min_ele_flow), line_dash="dash", line_color="#c62828", line_width=2)
    fig.add_annotation(
        x=x_plot_max,
        y=float(max_ele_flow),
        text="上限",
        showarrow=False,
        xanchor="left",
        font=dict(color="#c62828"),
    )
    fig.add_annotation(
        x=x_plot_max,
        y=float(min_ele_flow),
        text="下限",
        showarrow=False,
        xanchor="left",
        font=dict(color="#c62828"),
    )

    if np.isfinite(result.min_intersection) and np.isfinite(result.max_intersection):
        fig.add_vline(x=result.min_intersection, line_dash="dot", line_color="#2e7d32", line_width=1)
        fig.add_vline(x=result.max_intersection, line_dash="dot", line_color="#2e7d32", line_width=1)
        fig.add_trace(
            go.Scatter(
                x=[result.min_intersection, result.max_intersection],
                y=[marker_y, marker_y],
                mode="lines+markers",
                line=dict(color="#2e7d32", width=12),
                marker=dict(size=10, color="#2e7d32"),
                name="平膜Flux範囲",
            )
        )
        fig.add_annotation(
            x=(result.min_intersection + result.max_intersection) / 2.0,
            y=marker_label_y,
            text=f"範囲: {result.min_intersection:.2f} - {result.max_intersection:.2f}",
            showarrow=False,
            font=dict(color="#1b5e20"),
        )
    else:
        fig.add_annotation(
            x=(x_plot_min + x_plot_max) / 2.0,
            y=marker_label_y,
            text="この条件では範囲がありません",
            showarrow=False,
            font=dict(color="#b71c1c"),
        )

    fig.update_layout(
        xaxis_title="F.S.Flux",
        yaxis_title="Ele.Flow",
        template="plotly_white",
        height=560,
        font=dict(size=18),
        legend=dict(font=dict(size=16)),
    )
    fig.update_xaxes(range=[x_plot_min, x_plot_max])
    fig.update_yaxes(
        range=[y_plot_min, y_plot_max],
        tickformat=",.0f",
        separatethousands=True,
        exponentformat="none",
        tickfont=dict(size=15),
    )
    return fig
