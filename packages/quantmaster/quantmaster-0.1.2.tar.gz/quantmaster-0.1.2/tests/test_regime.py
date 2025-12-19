from __future__ import annotations

import numpy as np
import pandas as pd

from quantmaster.features.regime import (
    cusum_statistic,
    market_efficiency_index,
    runs_test_statistic,
    variance_ratio,
)
from tests.helpers import assert_no_lookahead


def test_regime_module_importable() -> None:
    import quantmaster.features.regime as regime

    assert regime is not None


def _sample_close_df(*, n: int = 200) -> pd.DataFrame:
    idx = pd.date_range("2024-01-01", periods=n, freq="D")
    close = pd.Series(100.0 + np.cumsum(np.linspace(-0.1, 0.2, n)), index=idx)
    return pd.DataFrame({"close": close}, index=idx)


def test_cusum_statistic_shape_name_and_no_lookahead() -> None:
    df = _sample_close_df(n=240)
    out = cusum_statistic(df, window=60)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "cusum_statistic_60"

    valid = out.dropna()
    assert np.isfinite(valid).all()

    assert_no_lookahead(feature_fn=cusum_statistic, data=df, t=120, feature_kwargs={"window": 60})


def test_variance_ratio_shape_name_and_no_lookahead() -> None:
    df = _sample_close_df(n=260)
    out = variance_ratio(df, window=120, holding_period=5)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "variance_ratio_120_5"

    valid = out.dropna()
    assert np.isfinite(valid).all()

    assert_no_lookahead(
        feature_fn=variance_ratio,
        data=df,
        t=140,
        feature_kwargs={"window": 120, "holding_period": 5},
    )


def test_market_efficiency_index_shape_name_and_no_lookahead() -> None:
    df = _sample_close_df(n=220)
    out = market_efficiency_index(df, window=60, holding_period=5)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "market_efficiency_index_60_5"

    valid = out.dropna()
    assert np.isfinite(valid).all()

    assert_no_lookahead(
        feature_fn=market_efficiency_index,
        data=df,
        t=120,
        feature_kwargs={"window": 60, "holding_period": 5},
    )


def test_runs_test_statistic_shape_name_and_no_lookahead() -> None:
    df = _sample_close_df(n=220)
    out = runs_test_statistic(df, window=60)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "runs_test_statistic_60"

    valid = out.dropna()
    assert np.isfinite(valid).all()

    assert_no_lookahead(feature_fn=runs_test_statistic, data=df, t=120, feature_kwargs={"window": 60})
