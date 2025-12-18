import pandas as pd

from quantmaster.features.volatility import har_rv, har_rv_forecast, realized_variance, yang_zhang_volatility


def test_realized_variance_shape() -> None:
    idx = pd.date_range("2024-01-01", periods=50, freq="D")
    df = pd.DataFrame({"close": range(1, 51)}, index=idx)

    rv = realized_variance(df)

    assert isinstance(rv, pd.Series)
    assert rv.index.equals(df.index)
    assert rv.name == "rv"


def test_har_rv_columns_and_index() -> None:
    idx = pd.date_range("2024-01-01", periods=50, freq="D")
    df = pd.DataFrame({"close": range(1, 51)}, index=idx)

    out = har_rv(df, weekly_window=5, monthly_window=22)

    assert isinstance(out, pd.DataFrame)
    assert out.index.equals(df.index)
    assert list(out.columns) == ["har_rv_d", "har_rv_w", "har_rv_m"]


def test_har_rv_forecast_shape_and_name() -> None:
    idx = pd.date_range("2024-01-01", periods=200, freq="D")
    price = pd.Series(range(1, 201), index=idx, dtype=float)
    df = pd.DataFrame({"close": price}, index=idx)

    out = har_rv_forecast(df, horizon=1, estimation_window=100, weekly_window=5, monthly_window=22)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "har_rv_forecast_1_100"

    assert out.notna().any()


def test_yang_zhang_volatility_shape_and_index() -> None:
    idx = pd.date_range("2024-01-01", periods=50, freq="D")
    df = pd.DataFrame(
        {
            "open": range(1, 51),
            "high": range(2, 52),
            "low": range(0, 50),
            "close": range(1, 51),
            "volume": [100] * 50,
        },
        index=idx,
    )

    out = yang_zhang_volatility(df, window=10)

    assert out.index.equals(df.index)
    assert out.name is not None
