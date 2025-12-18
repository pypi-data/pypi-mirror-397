import numpy as np
import pandas as pd

from quantmaster.features.statistical import fracdiff, hurst_dfa, ornstein_uhlenbeck


def test_fracdiff_shape_and_name() -> None:
    idx = pd.date_range("2024-01-01", periods=60, freq="D")
    df = pd.DataFrame({"close": range(1, 61)}, index=idx)

    out = fracdiff(df, d=0.5)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "fracdiff_0.5"

    valid = out.dropna()
    assert np.isfinite(valid).all()


def test_fracdiff_d0_is_identity() -> None:
    idx = pd.date_range("2024-01-01", periods=20, freq="D")
    df = pd.DataFrame({"close": range(1, 21)}, index=idx)

    out = fracdiff(df, d=0.0)

    expected = pd.Series(df["close"].astype(float), index=df.index, name="fracdiff_0")
    pd.testing.assert_series_equal(out, expected)


def test_fracdiff_d1_matches_first_difference() -> None:
    idx = pd.date_range("2024-01-01", periods=20, freq="D")
    df = pd.DataFrame({"close": range(1, 21)}, index=idx)

    out = fracdiff(df, d=1.0)

    assert out.name == "fracdiff_1"
    assert pd.isna(out.iloc[0])
    assert np.isclose(out.iloc[1:].to_numpy(dtype=float), 1.0).all()


def test_fracdiff_max_lags_controls_warmup_nans() -> None:
    idx = pd.date_range("2024-01-01", periods=20, freq="D")
    df = pd.DataFrame({"close": range(1, 21)}, index=idx)

    out = fracdiff(df, d=0.5, max_lags=3, thresh=1e-12)

    assert out.iloc[:3].isna().all()
    assert out.iloc[3:].notna().any()


def test_hurst_dfa_shape_and_index() -> None:
    idx = pd.date_range("2024-01-01", periods=300, freq="D")
    df = pd.DataFrame({"close": range(1, 301)}, index=idx)

    out = hurst_dfa(df, window=60)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "hurst_dfa_60"
    assert out.notna().any()


def test_ornstein_uhlenbeck_shape_and_columns() -> None:
    idx = pd.date_range("2024-01-01", periods=400, freq="D")
    df = pd.DataFrame({"close": range(1, 401)}, index=idx)

    out = ornstein_uhlenbeck(df, window=120, detrend_window=20)

    assert isinstance(out, pd.DataFrame)
    assert out.index.equals(df.index)
    assert list(out.columns) == [
        "ou_phi_120",
        "ou_kappa_120",
        "ou_theta_120",
        "ou_sigma_120",
        "ou_sigma_eq_120",
        "ou_halflife_120",
        "ou_zscore_120",
    ]
    assert out.notna().any().any()
