from __future__ import annotations

import numpy as np
import pandas as pd

from quantmaster.features.microstructure import (
    amihud_illiquidity,
    corwin_schultz_spread,
    relative_spread_proxy,
    roll_spread,
)
from tests.helpers import assert_no_lookahead


def test_microstructure_module_importable() -> None:
    import quantmaster.features.microstructure as microstructure

    assert microstructure is not None


def test_amihud_illiquidity_shape_name_and_no_lookahead() -> None:
    idx = pd.date_range("2024-01-01", periods=80, freq="D")
    close = pd.Series(np.linspace(100, 120, len(idx)), index=idx)
    volume = pd.Series([1000] * len(idx), index=idx)
    df = pd.DataFrame({"close": close, "volume": volume}, index=idx)

    out = amihud_illiquidity(df, window=20)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "amihud_illiquidity_20"

    valid = out.dropna()
    assert np.isfinite(valid).all()

    assert_no_lookahead(feature_fn=amihud_illiquidity, data=df, t=30, feature_kwargs={"window": 20})


def test_roll_spread_shape_name_and_no_lookahead() -> None:
    idx = pd.date_range("2024-01-01", periods=120, freq="D")
    close = pd.Series(np.linspace(100, 130, len(idx)), index=idx)
    df = pd.DataFrame({"close": close}, index=idx)

    out = roll_spread(df, window=30)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "roll_spread_30"

    valid = out.dropna()
    assert np.isfinite(valid).all()
    assert (valid >= 0).all()

    assert_no_lookahead(feature_fn=roll_spread, data=df, t=40, feature_kwargs={"window": 30})


def test_corwin_schultz_spread_shape_name_and_no_lookahead() -> None:
    idx = pd.date_range("2024-01-01", periods=120, freq="D")
    close = pd.Series(np.linspace(100, 130, len(idx)), index=idx)
    high = close * 1.01
    low = close * 0.99
    df = pd.DataFrame({"high": high, "low": low, "close": close}, index=idx)

    out = corwin_schultz_spread(df, window=10)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "corwin_schultz_spread_10"

    valid = out.dropna()
    assert np.isfinite(valid).all()
    assert (valid >= 0).all()

    assert_no_lookahead(feature_fn=corwin_schultz_spread, data=df, t=40, feature_kwargs={"window": 10})


def test_relative_spread_proxy_shape_name_and_no_lookahead() -> None:
    idx = pd.date_range("2024-01-01", periods=120, freq="D")
    close = pd.Series(np.linspace(100, 130, len(idx)), index=idx)
    open_ = close.shift(1).fillna(close.iloc[0])
    high = np.maximum(open_, close) * 1.01
    low = np.minimum(open_, close) * 0.99
    df = pd.DataFrame({"open": open_, "high": high, "low": low, "close": close}, index=idx)

    out = relative_spread_proxy(df, window=14)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "relative_spread_proxy_14"

    valid = out.dropna()
    assert np.isfinite(valid).all()
    assert (valid >= 0).all()

    assert_no_lookahead(feature_fn=relative_spread_proxy, data=df, t=40, feature_kwargs={"window": 14})
