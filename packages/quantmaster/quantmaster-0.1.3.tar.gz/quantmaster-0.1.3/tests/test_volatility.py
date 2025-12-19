import numpy as np
import pandas as pd

from tests.helpers import assert_no_lookahead

from quantmaster.features.volatility import (
    bipower_variation,
    harq_adjustment,
    garman_klass_volatility,
    har_rv,
    har_rv_forecast,
    intraday_range,
    jump_variation,
    medrv,
    minrv,
    parkinson_volatility,
    realized_quarticity,
    realized_roughness,
    realized_semivariance,
    realized_variance,
    rogers_satchell_volatility,
    log_volatility_increment,
    shar_components,
    signed_jump_variation,
    volatility_ratio,
    yang_zhang_volatility,
)


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


def test_bipower_variation_shape_name_and_no_lookahead() -> None:
    idx = pd.date_range("2024-01-01", periods=120, freq="D")
    price = pd.Series(np.linspace(100, 130, len(idx)), index=idx, dtype=float)

    out = bipower_variation(price)

    assert isinstance(out, pd.Series)
    assert out.index.equals(price.index)
    assert out.name == "bv"

    assert_no_lookahead(feature_fn=bipower_variation, data=price.to_frame("close"), t=40)


def test_jump_variation_shape_name_and_no_lookahead() -> None:
    idx = pd.date_range("2024-01-01", periods=120, freq="D")
    df = pd.DataFrame({"close": np.linspace(100, 130, len(idx))}, index=idx)

    out = jump_variation(df)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "jv"

    valid = out.dropna()
    assert (valid >= 0).all()

    assert_no_lookahead(feature_fn=jump_variation, data=df, t=40)


def test_realized_semivariance_shape_and_no_lookahead() -> None:
    idx = pd.date_range("2024-01-01", periods=120, freq="D")
    price = pd.Series(np.linspace(100, 130, len(idx)), index=idx, dtype=float)
    df = pd.DataFrame({"close": price}, index=idx)

    out = realized_semivariance(df)

    assert isinstance(out, pd.DataFrame)
    assert out.index.equals(df.index)
    assert list(out.columns) == ["rsv_pos", "rsv_neg"]

    assert_no_lookahead(feature_fn=realized_semivariance, data=df, t=40)


def test_signed_jump_variation_shape_and_no_lookahead() -> None:
    idx = pd.date_range("2024-01-01", periods=120, freq="D")
    price = pd.Series(np.linspace(100, 130, len(idx)), index=idx, dtype=float)
    df = pd.DataFrame({"close": price}, index=idx)

    out = signed_jump_variation(df)

    assert isinstance(out, pd.DataFrame)
    assert out.index.equals(df.index)
    assert list(out.columns) == ["signed_jump_pos", "signed_jump_neg"]

    valid = out.dropna()
    assert (valid >= 0).all().all()

    assert_no_lookahead(feature_fn=signed_jump_variation, data=df, t=40)


def test_minrv_shape_name_and_no_lookahead() -> None:
    idx = pd.date_range("2024-01-01", periods=120, freq="D")
    df = pd.DataFrame({"close": np.linspace(100, 130, len(idx))}, index=idx)

    out = minrv(df)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "minrv"

    valid = out.dropna()
    assert (valid >= 0).all()

    assert_no_lookahead(feature_fn=minrv, data=df, t=40)


def test_medrv_shape_name_and_no_lookahead() -> None:
    idx = pd.date_range("2024-01-01", periods=120, freq="D")
    df = pd.DataFrame({"close": np.linspace(100, 130, len(idx))}, index=idx)

    out = medrv(df)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "medrv"

    valid = out.dropna()
    assert (valid >= 0).all()

    assert_no_lookahead(feature_fn=medrv, data=df, t=40)


def test_realized_quarticity_shape_name_and_no_lookahead() -> None:
    idx = pd.date_range("2024-01-01", periods=120, freq="D")
    df = pd.DataFrame({"close": np.linspace(100, 130, len(idx))}, index=idx)

    out = realized_quarticity(df)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "rq"

    valid = out.dropna()
    assert (valid >= 0).all()

    assert_no_lookahead(feature_fn=realized_quarticity, data=df, t=40)


def test_harq_adjustment_shape_name_and_no_lookahead() -> None:
    idx = pd.date_range("2024-01-01", periods=200, freq="D")
    df = pd.DataFrame({"close": np.linspace(100, 160, len(idx))}, index=idx)

    out = harq_adjustment(df, window=22)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "harq_adjustment_22"

    assert_no_lookahead(feature_fn=harq_adjustment, data=df, t=80, feature_kwargs={"window": 22})


def test_shar_components_columns_and_no_lookahead() -> None:
    idx = pd.date_range("2024-01-01", periods=200, freq="D")
    df = pd.DataFrame({"close": np.linspace(100, 160, len(idx))}, index=idx)

    out = shar_components(df, weekly_window=5, monthly_window=22)

    assert isinstance(out, pd.DataFrame)
    assert out.index.equals(df.index)
    assert list(out.columns) == [
        "rsv_pos_d",
        "rsv_neg_d",
        "rsv_pos_w",
        "rsv_neg_w",
        "rsv_pos_m",
        "rsv_neg_m",
    ]

    assert_no_lookahead(
        feature_fn=shar_components,
        data=df,
        t=80,
        feature_kwargs={"weekly_window": 5, "monthly_window": 22},
    )


def test_realized_roughness_shape_name_and_no_lookahead() -> None:
    idx = pd.date_range("2024-01-01", periods=260, freq="D")
    df = pd.DataFrame({"close": np.linspace(100, 180, len(idx))}, index=idx)

    out = realized_roughness(df, window=60, lags=[1, 2, 5, 10])

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "realized_roughness_60"

    assert out.notna().any()

    assert_no_lookahead(
        feature_fn=realized_roughness,
        data=df,
        t=120,
        feature_kwargs={"window": 60, "lags": [1, 2, 5, 10]},
    )


def test_log_volatility_increment_shape_name_and_no_lookahead() -> None:
    idx = pd.date_range("2024-01-01", periods=260, freq="D")
    df = pd.DataFrame({"close": np.linspace(100, 180, len(idx))}, index=idx)

    out = log_volatility_increment(df, window=20, lag=2)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "log_volatility_increment_20_2"

    assert out.notna().any()

    assert_no_lookahead(
        feature_fn=log_volatility_increment,
        data=df,
        t=120,
        feature_kwargs={"window": 20, "lag": 2},
    )


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


def test_parkinson_volatility_shape_name_and_no_lookahead() -> None:
    idx = pd.date_range("2024-01-01", periods=80, freq="D")
    df = pd.DataFrame(
        {
            "high": range(2, 82),
            "low": range(1, 81),
        },
        index=idx,
    )

    out = parkinson_volatility(df, window=10)
    assert out.index.equals(df.index)
    assert out.name == "parkinson_volatility_10"

    assert_no_lookahead(feature_fn=parkinson_volatility, data=df, t=30, feature_kwargs={"window": 10})


def test_garman_klass_volatility_shape_name_and_no_lookahead() -> None:
    idx = pd.date_range("2024-01-01", periods=80, freq="D")
    df = pd.DataFrame(
        {
            "open": range(1, 81),
            "high": range(2, 82),
            "low": range(1, 81),
            "close": range(1, 81),
        },
        index=idx,
    )

    out = garman_klass_volatility(df, window=10)
    assert out.index.equals(df.index)
    assert out.name == "garman_klass_volatility_10"

    assert_no_lookahead(feature_fn=garman_klass_volatility, data=df, t=30, feature_kwargs={"window": 10})


def test_rogers_satchell_volatility_shape_name_and_no_lookahead() -> None:
    idx = pd.date_range("2024-01-01", periods=80, freq="D")
    df = pd.DataFrame(
        {
            "open": range(1, 81),
            "high": range(2, 82),
            "low": range(1, 81),
            "close": range(1, 81),
        },
        index=idx,
    )

    out = rogers_satchell_volatility(df, window=10)
    assert out.index.equals(df.index)
    assert out.name == "rogers_satchell_volatility_10"

    assert_no_lookahead(feature_fn=rogers_satchell_volatility, data=df, t=30, feature_kwargs={"window": 10})


def test_intraday_range_shape_name_and_no_lookahead() -> None:
    idx = pd.date_range("2024-01-01", periods=80, freq="D")
    df = pd.DataFrame(
        {
            "high": range(2, 82),
            "low": range(1, 81),
        },
        index=idx,
    )

    out = intraday_range(df, window=10)
    assert out.index.equals(df.index)
    assert out.name == "intraday_range_10"

    assert_no_lookahead(feature_fn=intraday_range, data=df, t=30, feature_kwargs={"window": 10})


def test_volatility_ratio_shape_name_and_no_lookahead() -> None:
    idx = pd.date_range("2024-01-01", periods=80, freq="D")
    close = pd.Series(range(10, 90), index=idx, dtype=float)
    high = close + 1.0
    low = close - 1.0
    df = pd.DataFrame({"high": high, "low": low, "close": close}, index=idx)

    out = volatility_ratio(df, window=14)
    assert out.index.equals(df.index)
    assert out.name == "volatility_ratio_14"

    assert_no_lookahead(feature_fn=volatility_ratio, data=df, t=30, feature_kwargs={"window": 14})
