import math

import pandas as pd
import pytest

from src.analysis import analyze_dataframe, build_figure, validate_dataframe


def make_valid_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "F.S.Flux": [1.0, 2.0, 3.0, 4.0, 5.0],
            "Ele.Flow": [10.5, 20.3, 30.1, 40.8, 50.2],
        }
    )


def test_validate_dataframe_success() -> None:
    df = make_valid_df()
    out = validate_dataframe(df)
    assert list(out.columns) == ["F.S.Flux", "Ele.Flow"]
    assert len(out) == 5


def test_validate_dataframe_missing_column() -> None:
    df = pd.DataFrame({"F.S.Flux": [1.0, 2.0, 3.0]})
    with pytest.raises(ValueError, match="Missing required columns"):
        validate_dataframe(df)


def test_validate_dataframe_too_few_rows() -> None:
    df = pd.DataFrame({"F.S.Flux": [1.0, 2.0], "Ele.Flow": [10.0, 20.0]})
    with pytest.raises(ValueError, match="At least 3 rows"):
        validate_dataframe(df)


def test_validate_dataframe_missing_values() -> None:
    df = pd.DataFrame({"F.S.Flux": [1.0, None, 3.0], "Ele.Flow": [10.0, 20.0, 30.0]})
    with pytest.raises(ValueError, match="Missing values"):
        validate_dataframe(df)


def test_validate_dataframe_non_numeric() -> None:
    df = pd.DataFrame({"F.S.Flux": [1.0, 2.0, 3.0], "Ele.Flow": [10.0, "x", 30.0]})
    with pytest.raises(ValueError):
        validate_dataframe(df)


def test_analyze_dataframe_expected_values() -> None:
    df = make_valid_df()
    result, pred_summary, fitted = analyze_dataframe(df, min_ele_flow=15.0, max_ele_flow=45.0)

    assert math.isclose(result.slope, 9.99, rel_tol=1e-8, abs_tol=1e-8)
    assert math.isclose(result.intercept, 0.41, rel_tol=1e-8, abs_tol=1e-8)
    assert math.isclose(result.r_squared, 0.9996924796756111, rel_tol=1e-10, abs_tol=1e-10)
    assert math.isclose(result.min_intersection, 1.5808252639534688, rel_tol=1e-10, abs_tol=1e-10)
    assert math.isclose(result.max_intersection, 4.343098659970456, rel_tol=1e-10, abs_tol=1e-10)
    assert len(pred_summary) == len(df)
    assert len(fitted) == len(df)


def test_analyze_dataframe_prediction_interval_width_changes() -> None:
    df = make_valid_df()
    _, pred_68, _ = analyze_dataframe(df, min_ele_flow=15.0, max_ele_flow=45.0, prediction_interval_pct=68.0)
    _, pred_997, _ = analyze_dataframe(df, min_ele_flow=15.0, max_ele_flow=45.0, prediction_interval_pct=99.7)

    width_68 = (pred_68["obs_ci_upper"] - pred_68["obs_ci_lower"]).mean()
    width_997 = (pred_997["obs_ci_upper"] - pred_997["obs_ci_lower"]).mean()
    assert width_997 > width_68


@pytest.mark.parametrize("pct", [0.0, 100.0, -1.0, 120.0])
def test_analyze_dataframe_prediction_interval_pct_out_of_range(pct: float) -> None:
    df = make_valid_df()
    with pytest.raises(ValueError, match="prediction_interval_pct"):
        analyze_dataframe(df, min_ele_flow=15.0, max_ele_flow=45.0, prediction_interval_pct=pct)


def test_build_figure_uses_simulation_aligned_styles() -> None:
    df = make_valid_df()
    result, pred_summary, fitted = analyze_dataframe(df, min_ele_flow=15.0, max_ele_flow=45.0, prediction_interval_pct=95.0)
    fig = build_figure(
        df,
        pred_summary,
        fitted,
        result,
        min_ele_flow=15.0,
        max_ele_flow=45.0,
        prediction_interval_pct=95.0,
    )

    trace_names = [trace.name for trace in fig.data if trace.name]
    assert "予測区間内" in trace_names
    assert "予測区間外" in trace_names
    assert "回帰直線" in trace_names
    assert "95% 予測区間" in trace_names
    assert "平膜Flux範囲" in trace_names

    shapes = list(fig.layout.shapes or [])
    red_dash_horizontal = [
        s
        for s in shapes
        if s.line.color == "#c62828" and s.line.dash == "dash" and s.y0 == s.y1
    ]
    green_dot_vertical = [
        s
        for s in shapes
        if s.line.color == "#2e7d32" and s.line.dash == "dot" and s.x0 == s.x1
    ]
    assert len(red_dash_horizontal) == 2
    assert len(green_dot_vertical) == 2

    annotation_texts = [a.text for a in (fig.layout.annotations or [])]
    assert "上限" in annotation_texts
    assert "下限" in annotation_texts
    assert any(text.startswith("範囲:") for text in annotation_texts if text)
