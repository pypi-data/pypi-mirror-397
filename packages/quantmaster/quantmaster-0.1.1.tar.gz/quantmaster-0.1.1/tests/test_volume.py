import numpy as np
import pandas as pd

from quantmaster.features.volume import rvol


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
