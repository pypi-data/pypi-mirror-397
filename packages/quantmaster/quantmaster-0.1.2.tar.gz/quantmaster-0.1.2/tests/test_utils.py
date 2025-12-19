from __future__ import annotations

import numpy as np
import pandas as pd

from quantmaster.features.utils import create_all


def _make_ohlcv(n: int = 120) -> pd.DataFrame:
    idx = pd.date_range("2024-01-01", periods=n, freq="D")
    close = 100.0 + np.cumsum(np.sin(np.linspace(0, 10, n)) * 0.2)
    df = pd.DataFrame(
        {
            "open": close + 0.1,
            "high": close + 0.5,
            "low": close - 0.5,
            "close": close,
            "volume": 1000.0 + np.linspace(0, 10, n),
        },
        index=idx,
    )
    return df


def test_create_all_adds_some_features_and_preserves_index() -> None:
    df = _make_ohlcv(200)
    out = create_all(df)

    assert isinstance(out, pd.DataFrame)
    assert out.index.equals(df.index)
    assert set(df.columns).issubset(out.columns)

    # Should add at least a couple of well-known series-based features.
    assert "rsi_14" in out.columns
    assert "trend_intensity_20" in out.columns


def test_create_all_does_not_overwrite_existing_columns_by_default() -> None:
    df = _make_ohlcv(200)
    df["rsi_14"] = 123.0

    out = create_all(df)
    assert (out["rsi_14"] == 123.0).all()


def test_create_all_overwrite_true_recomputes() -> None:
    df = _make_ohlcv(200)
    df["rsi_14"] = 123.0

    out = create_all(df, overwrite=True)
    assert not (out["rsi_14"] == 123.0).all()


def test_create_all_can_include_subset() -> None:
    df = _make_ohlcv(200)
    out = create_all(df, include=["rsi", "har_rv"])

    assert "rsi_14" in out.columns
    assert "har_rv_d" in out.columns


def test_create_all_inplace_true_mutates_original_df() -> None:
    df = _make_ohlcv(200)
    out = create_all(df, inplace=True)

    assert out is df
    assert "rsi_14" in df.columns
