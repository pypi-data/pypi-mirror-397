from __future__ import annotations

import numpy as np
import pandas as pd

from quantmaster.features.returns import intraday_return, overnight_gap
from tests.helpers import assert_no_lookahead


def test_returns_module_importable() -> None:
    import quantmaster.features.returns as returns

    assert returns is not None


def test_overnight_gap_shape_name_and_no_lookahead() -> None:
    idx = pd.date_range("2024-01-01", periods=80, freq="D")
    close = pd.Series(100.0 + np.cumsum(np.linspace(-0.1, 0.2, len(idx))), index=idx)
    open_ = close.shift(1).fillna(close.iloc[0])
    df = pd.DataFrame({"open": open_, "close": close}, index=idx)

    out = overnight_gap(df)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "overnight_gap"

    valid = out.dropna()
    assert np.isfinite(valid).all()

    assert_no_lookahead(feature_fn=overnight_gap, data=df, t=30)


def test_intraday_return_shape_name_and_no_lookahead() -> None:
    idx = pd.date_range("2024-01-01", periods=80, freq="D")
    open_ = pd.Series(100.0 + np.cumsum(np.linspace(-0.1, 0.2, len(idx))), index=idx)
    close = open_ * 1.001
    df = pd.DataFrame({"open": open_, "close": close}, index=idx)

    out = intraday_return(df)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "intraday_return"

    valid = out.dropna()
    assert np.isfinite(valid).all()

    assert_no_lookahead(feature_fn=intraday_return, data=df, t=30)
