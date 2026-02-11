import math

import pandas as pd
import pytest

from src.analysis import analyze_dataframe, validate_dataframe


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
