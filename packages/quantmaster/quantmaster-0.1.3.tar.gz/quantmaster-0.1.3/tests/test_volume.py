import numpy as np
import pandas as pd

from quantmaster.features.volume import (
    close_location_value,
    order_flow_imbalance,
    price_volume_correlation,
    rvol,
    tick_imbalance_proxy,
    volume_volatility_ratio,
    volume_weighted_close_location,
)
from tests.helpers import assert_no_lookahead


def test_rvol_shape_and_name() -> None:
    idx = pd.date_range("2024-01-01", periods=60, freq="D")
    df = pd.DataFrame(
        {
            "open": range(1, 61),
            "high": range(2, 62),
            "low": range(0, 60),
            "close": range(1, 61),
            "volume": [100] * 60,
        },
        index=idx,
    )

    out = rvol(df, window=30)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "rvol_30"

    valid = out.dropna()
    assert np.isfinite(valid).all()


def test_rvol_constant_volume_is_zero_after_warmup() -> None:
    idx = pd.date_range("2024-01-01", periods=60, freq="D")
    df = pd.DataFrame({"volume": [100] * 60}, index=idx)

    out = rvol(df, window=30)

    valid = out.dropna()
    assert np.isclose(valid, 0.0).all()


def _sample_ohlcv_df(*, n: int = 120) -> pd.DataFrame:
    idx = pd.date_range("2024-01-01", periods=n, freq="D")
    close = pd.Series(100.0 + np.cumsum(np.sin(np.linspace(0, 12, n)) * 0.2), index=idx)
    open_ = close.shift(1).fillna(close.iloc[0])
    high = pd.concat([open_, close], axis=1).max(axis=1) + 0.1
    low = pd.concat([open_, close], axis=1).min(axis=1) - 0.1
    volume = pd.Series(1000.0 + (np.cos(np.linspace(0, 12, n)) * 50.0), index=idx)
    volume = volume.clip(lower=1.0)
    return pd.DataFrame({"open": open_, "high": high, "low": low, "close": close, "volume": volume}, index=idx)


def test_price_volume_correlation_shape_name_and_no_lookahead() -> None:
    df = _sample_ohlcv_df(n=160)
    out = price_volume_correlation(df, window=20)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "price_volume_correlation_20"

    valid = out.dropna()
    assert np.isfinite(valid).all()
    assert (valid >= -1.0 - 1e-12).all()
    assert (valid <= 1.0 + 1e-12).all()

    assert_no_lookahead(feature_fn=price_volume_correlation, data=df, t=80, feature_kwargs={"window": 20})


def test_volume_volatility_ratio_shape_name_and_no_lookahead() -> None:
    df = _sample_ohlcv_df(n=160)
    out = volume_volatility_ratio(df, window=20)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "volume_volatility_ratio_20"

    valid = out.dropna()
    assert np.isfinite(valid).all()

    assert_no_lookahead(feature_fn=volume_volatility_ratio, data=df, t=80, feature_kwargs={"window": 20})


def test_close_location_value_bounds_and_no_lookahead() -> None:
    df = _sample_ohlcv_df(n=100)
    out = close_location_value(df)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "close_location_value"

    valid = out.dropna()
    assert np.isfinite(valid).all()
    assert (valid >= -1.0 - 1e-12).all()
    assert (valid <= 1.0 + 1e-12).all()

    assert_no_lookahead(feature_fn=close_location_value, data=df, t=60, feature_kwargs={})


def test_tick_imbalance_proxy_bounds_and_no_lookahead() -> None:
    df = _sample_ohlcv_df(n=160)
    out = tick_imbalance_proxy(df, window=20)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "tick_imbalance_proxy_20"

    valid = out.dropna()
    assert np.isfinite(valid).all()
    assert (valid >= -1.0 - 1e-12).all()
    assert (valid <= 1.0 + 1e-12).all()

    assert_no_lookahead(feature_fn=tick_imbalance_proxy, data=df, t=80, feature_kwargs={"window": 20})


def test_volume_weighted_close_location_bounds_and_no_lookahead() -> None:
    df = _sample_ohlcv_df(n=160)
    out = volume_weighted_close_location(df, window=20)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "volume_weighted_close_location_20"

    valid = out.dropna()
    assert np.isfinite(valid).all()
    assert (valid >= -1.0 - 1e-12).all()
    assert (valid <= 1.0 + 1e-12).all()

    assert_no_lookahead(feature_fn=volume_weighted_close_location, data=df, t=80, feature_kwargs={"window": 20})


def test_order_flow_imbalance_bounds_and_no_lookahead() -> None:
    df = _sample_ohlcv_df(n=160)
    out = order_flow_imbalance(df, window=20)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "order_flow_imbalance_20"

    valid = out.dropna()
    assert np.isfinite(valid).all()
    assert (valid >= -1.0 - 1e-12).all()
    assert (valid <= 1.0 + 1e-12).all()

    assert_no_lookahead(feature_fn=order_flow_imbalance, data=df, t=80, feature_kwargs={"window": 20})
