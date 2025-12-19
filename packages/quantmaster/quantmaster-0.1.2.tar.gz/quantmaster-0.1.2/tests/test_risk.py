from __future__ import annotations

import numpy as np
import pandas as pd

from quantmaster.features.risk import (
    expected_shortfall,
    max_drawdown_duration,
    tail_risk_measure,
    value_at_risk_historical,
)
from tests.helpers import assert_no_lookahead


def test_risk_module_importable() -> None:
    import quantmaster.features.risk as risk

    assert risk is not None


def _sample_close_df(*, n: int = 260) -> pd.DataFrame:
    idx = pd.date_range("2024-01-01", periods=n, freq="D")
    noise = np.sin(np.linspace(0, 12, n)) * 0.2
    close = pd.Series(100.0 + np.cumsum(noise), index=idx)
    return pd.DataFrame({"close": close}, index=idx)


def test_value_at_risk_historical_shape_name_and_no_lookahead() -> None:
    df = _sample_close_df(n=240)
    out = value_at_risk_historical(df, window=30, confidence=0.95)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "value_at_risk_historical_30_0.95"

    valid = out.dropna()
    assert np.isfinite(valid).all()
    assert (valid >= 0).all()

    assert_no_lookahead(
        feature_fn=value_at_risk_historical,
        data=df,
        t=80,
        feature_kwargs={"window": 30, "confidence": 0.95},
    )


def test_expected_shortfall_shape_name_and_no_lookahead() -> None:
    df = _sample_close_df(n=240)
    out = expected_shortfall(df, window=30, confidence=0.95)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "expected_shortfall_30_0.95"

    valid = out.dropna()
    assert np.isfinite(valid).all()
    assert (valid >= 0).all()

    assert_no_lookahead(
        feature_fn=expected_shortfall,
        data=df,
        t=80,
        feature_kwargs={"window": 30, "confidence": 0.95},
    )


def test_tail_risk_measure_shape_name_and_no_lookahead() -> None:
    df = _sample_close_df(n=240)
    out = tail_risk_measure(df, window=60, quantile=0.05)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "tail_risk_measure_60_0.05"

    valid = out.dropna()
    assert np.isfinite(valid).all()

    assert_no_lookahead(
        feature_fn=tail_risk_measure,
        data=df,
        t=120,
        feature_kwargs={"window": 60, "quantile": 0.05},
    )


def test_max_drawdown_duration_shape_name_and_no_lookahead() -> None:
    df = _sample_close_df(n=260)
    out = max_drawdown_duration(df, window=60)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "max_drawdown_duration_60"

    valid = out.dropna()
    assert np.isfinite(valid).all()
    assert (valid >= 0).all()
    assert (valid <= 60).all()

    assert_no_lookahead(
        feature_fn=max_drawdown_duration,
        data=df,
        t=140,
        feature_kwargs={"window": 60},
    )
