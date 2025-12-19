import numpy as np
import pandas as pd
import pytest

from tests.helpers import assert_no_lookahead

from quantmaster.features.statistical import (
    absolute_return_autocorrelation,
    approximate_entropy,
    cross_sample_entropy,
    fractal_dimension_mincover,
    fracdiff,
    generalized_hurst_exponent,
    hurst_dfa,
    information_discreteness,
    downside_beta,
    mean_reversion_half_life,
    ornstein_uhlenbeck,
    path_signature_features,
    permutation_entropy,
    realized_kurtosis,
    realized_skewness,
    return_autocorrelation,
    rolling_beta,
    spread_zscore,
    sample_entropy,
)


def test_fracdiff_shape_and_name() -> None:
    idx = pd.date_range("2024-01-01", periods=60, freq="D")
    df = pd.DataFrame({"close": range(1, 61)}, index=idx)

    out = fracdiff(df)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "fracdiff_0.4"

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

    out = fracdiff(df, d=0.4, max_lags=3, thresh=1e-12)

    assert out.iloc[:3].isna().all()
    assert out.iloc[3:].notna().any()


def test_fracdiff_handles_internal_nans_by_segment() -> None:
    idx = pd.date_range("2024-01-01", periods=50, freq="D")
    close = pd.Series(np.arange(1, 51, dtype=float), index=idx)
    close.iloc[10:15] = np.nan
    df = pd.DataFrame({"close": close}, index=idx)

    out = fracdiff(df, d=0.4, max_lags=3, thresh=1e-12)

    # Gap stays NaN
    assert out.iloc[10:15].isna().all()
    # After the gap, the segment should recover (not remain all-NaN)
    assert out.iloc[18:].notna().any()


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


def test_sample_entropy_shape_name_and_no_lookahead() -> None:
    idx = pd.date_range("2024-01-01", periods=120, freq="D")
    df = pd.DataFrame({"close": np.linspace(1.0, 2.0, len(idx))}, index=idx)

    out = sample_entropy(df, window=30, m=2, r=0.2)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "sample_entropy_30"
    assert out.notna().any()

    assert_no_lookahead(
        feature_fn=sample_entropy,
        data=df,
        t=60,
        feature_kwargs={"window": 30, "m": 2, "r": 0.2},
    )


def test_approximate_entropy_shape_name_and_no_lookahead() -> None:
    idx = pd.date_range("2024-01-01", periods=120, freq="D")
    df = pd.DataFrame({"close": np.linspace(1.0, 2.0, len(idx))}, index=idx)

    out = approximate_entropy(df, window=30, m=2, r=0.2)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "approximate_entropy_30"
    assert out.notna().any()

    assert_no_lookahead(
        feature_fn=approximate_entropy,
        data=df,
        t=60,
        feature_kwargs={"window": 30, "m": 2, "r": 0.2},
    )


def test_permutation_entropy_shape_name_and_no_lookahead() -> None:
    idx = pd.date_range("2024-01-01", periods=120, freq="D")
    df = pd.DataFrame({"close": np.linspace(1.0, 2.0, len(idx))}, index=idx)

    out = permutation_entropy(df, window=40, order=3, delay=1)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "permutation_entropy_40_3_1"
    assert out.notna().any()

    assert_no_lookahead(
        feature_fn=permutation_entropy,
        data=df,
        t=60,
        feature_kwargs={"window": 40, "order": 3, "delay": 1},
    )


def test_cross_sample_entropy_shape_name_and_no_lookahead() -> None:
    idx = pd.date_range("2024-01-01", periods=120, freq="D")
    df = pd.DataFrame(
        {
            "x": np.linspace(1.0, 2.0, len(idx)),
            "y": np.linspace(1.1, 2.1, len(idx)),
        },
        index=idx,
    )

    def _fn(d: pd.DataFrame, *, window: int, m: int, r: float) -> pd.Series:
        return cross_sample_entropy(d["x"], d["y"], window=window, m=m, r=r)

    out = _fn(df, window=30, m=2, r=0.2)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "cross_sample_entropy_30"
    assert out.notna().any()

    assert_no_lookahead(
        feature_fn=_fn,
        data=df,
        t=60,
        feature_kwargs={"window": 30, "m": 2, "r": 0.2},
    )


def test_rolling_beta_shape_name_and_no_lookahead() -> None:
    idx = pd.date_range("2024-01-01", periods=260, freq="D")
    asset = pd.Series(100.0 + np.cumsum(np.sin(np.linspace(0, 10, len(idx))) * 0.2), index=idx)
    bench = pd.Series(200.0 + np.cumsum(np.cos(np.linspace(0, 10, len(idx))) * 0.1), index=idx)
    df = pd.DataFrame({"asset": asset, "bench": bench}, index=idx)

    def _fn(d: pd.DataFrame, *, window: int) -> pd.Series:
        return rolling_beta(d["asset"], d["bench"], window=window)

    out = _fn(df, window=60)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "rolling_beta_60"

    valid = out.dropna()
    assert np.isfinite(valid).all()

    assert_no_lookahead(feature_fn=_fn, data=df, t=120, feature_kwargs={"window": 60})


def test_path_signature_features_shape_and_no_lookahead() -> None:
    iisignature = pytest.importorskip("iisignature")

    idx = pd.date_range("2024-01-01", periods=120, freq="D")
    df = pd.DataFrame(
        {
            "open": 100.0 + np.linspace(0, 2, len(idx)),
            "high": 101.0 + np.linspace(0, 2, len(idx)),
            "low": 99.0 + np.linspace(0, 2, len(idx)),
            "close": 100.5 + np.linspace(0, 2, len(idx)),
            "volume": 1000.0 + np.linspace(0, 10, len(idx)),
        },
        index=idx,
    )

    depth = 2
    window = 20
    sig_len = int(iisignature.siglength(5, depth))

    out = path_signature_features(df, depth=depth, window=window)

    assert isinstance(out, pd.DataFrame)
    assert out.index.equals(df.index)
    assert out.shape == (len(df), sig_len)
    assert list(out.columns) == [f"path_sig_{depth}_{k}" for k in range(sig_len)]

    valid = out.dropna()
    assert np.isfinite(valid.to_numpy(dtype=float)).all()

    assert_no_lookahead(
        feature_fn=path_signature_features,
        data=df,
        t=60,
        feature_kwargs={"depth": depth, "window": window},
    )


def test_downside_beta_shape_name_and_no_lookahead() -> None:
    idx = pd.date_range("2024-01-01", periods=260, freq="D")
    asset = pd.Series(100.0 + np.cumsum(np.sin(np.linspace(0, 12, len(idx))) * 0.2), index=idx)
    bench = pd.Series(200.0 + np.cumsum(np.cos(np.linspace(0, 12, len(idx))) * 0.2), index=idx)
    df = pd.DataFrame({"asset": asset, "bench": bench}, index=idx)

    def _fn(d: pd.DataFrame, *, window: int) -> pd.Series:
        return downside_beta(d["asset"], d["bench"], window=window)

    out = _fn(df, window=60)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "downside_beta_60"

    valid = out.dropna()
    assert np.isfinite(valid).all()

    assert_no_lookahead(feature_fn=_fn, data=df, t=120, feature_kwargs={"window": 60})


def test_information_discreteness_shape_name_and_no_lookahead() -> None:
    idx = pd.date_range("2024-01-01", periods=120, freq="D")
    close = pd.Series(100.0 + np.cumsum(np.linspace(-0.2, 0.4, len(idx))), index=idx)
    df = pd.DataFrame({"close": close}, index=idx)

    out = information_discreteness(df, window=20)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "information_discreteness_20"

    valid = out.dropna()
    assert np.isfinite(valid).all()
    assert (valid >= -1.0 - 1e-12).all()
    assert (valid <= 1.0 + 1e-12).all()

    assert_no_lookahead(feature_fn=information_discreteness, data=df, t=60, feature_kwargs={"window": 20})


def test_realized_skewness_shape_name_and_no_lookahead() -> None:
    idx = pd.date_range("2024-01-01", periods=160, freq="D")
    close = pd.Series(100.0 + np.cumsum(np.linspace(-0.2, 0.4, len(idx))), index=idx)
    df = pd.DataFrame({"close": close}, index=idx)

    out = realized_skewness(df, window=20)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "realized_skewness_20"

    valid = out.dropna()
    assert np.isfinite(valid).all()

    assert_no_lookahead(feature_fn=realized_skewness, data=df, t=80, feature_kwargs={"window": 20})


def test_realized_kurtosis_shape_name_and_no_lookahead() -> None:
    idx = pd.date_range("2024-01-01", periods=160, freq="D")
    close = pd.Series(100.0 + np.cumsum(np.linspace(-0.2, 0.4, len(idx))), index=idx)
    df = pd.DataFrame({"close": close}, index=idx)

    out = realized_kurtosis(df, window=20)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "realized_kurtosis_20"

    valid = out.dropna()
    assert np.isfinite(valid).all()

    assert_no_lookahead(feature_fn=realized_kurtosis, data=df, t=80, feature_kwargs={"window": 20})


def test_return_autocorrelation_shape_name_and_no_lookahead() -> None:
    idx = pd.date_range("2024-01-01", periods=260, freq="D")
    close = pd.Series(100.0 + np.cumsum(np.sin(np.linspace(0, 14, len(idx))) * 0.2), index=idx)
    df = pd.DataFrame({"close": close}, index=idx)

    out = return_autocorrelation(df, window=60, lag=1)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "return_autocorrelation_60_1"

    valid = out.dropna()
    assert np.isfinite(valid).all()
    assert (valid >= -1.0 - 1e-12).all()
    assert (valid <= 1.0 + 1e-12).all()

    assert_no_lookahead(
        feature_fn=return_autocorrelation,
        data=df,
        t=120,
        feature_kwargs={"window": 60, "lag": 1},
    )


def test_absolute_return_autocorrelation_shape_name_and_no_lookahead() -> None:
    idx = pd.date_range("2024-01-01", periods=260, freq="D")
    close = pd.Series(100.0 + np.cumsum(np.sin(np.linspace(0, 14, len(idx))) * 0.2), index=idx)
    df = pd.DataFrame({"close": close}, index=idx)

    out = absolute_return_autocorrelation(df, window=60, lag=1)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "absolute_return_autocorrelation_60_1"

    valid = out.dropna()
    assert np.isfinite(valid).all()
    assert (valid >= -1.0 - 1e-12).all()
    assert (valid <= 1.0 + 1e-12).all()

    assert_no_lookahead(
        feature_fn=absolute_return_autocorrelation,
        data=df,
        t=120,
        feature_kwargs={"window": 60, "lag": 1},
    )


def test_generalized_hurst_exponent_shape_name_and_no_lookahead() -> None:
    idx = pd.date_range("2024-01-01", periods=260, freq="D")
    close = pd.Series(100.0 + np.cumsum(np.sin(np.linspace(0, 20, len(idx))) * 0.3), index=idx)
    df = pd.DataFrame({"close": close}, index=idx)

    out = generalized_hurst_exponent(df, window=100, q=2.0, max_lag=10)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "generalized_hurst_exponent_100_2_10"

    valid = out.dropna()
    assert np.isfinite(valid).all()

    assert_no_lookahead(
        feature_fn=generalized_hurst_exponent,
        data=df,
        t=150,
        feature_kwargs={"window": 100, "q": 2.0, "max_lag": 10},
    )


def test_fractal_dimension_mincover_shape_name_and_no_lookahead() -> None:
    idx = pd.date_range("2024-01-01", periods=260, freq="D")
    close = pd.Series(100.0 + np.cumsum(np.sin(np.linspace(0, 20, len(idx))) * 0.3), index=idx)
    df = pd.DataFrame({"close": close}, index=idx)

    out = fractal_dimension_mincover(df, window=100, max_scale=10)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "fractal_dimension_mincover_100_10"

    valid = out.dropna()
    assert np.isfinite(valid).all()
    assert (valid > 0).all()

    assert_no_lookahead(
        feature_fn=fractal_dimension_mincover,
        data=df,
        t=150,
        feature_kwargs={"window": 100, "max_scale": 10},
    )


def test_mean_reversion_half_life_shape_name_and_no_lookahead() -> None:
    idx = pd.date_range("2024-01-01", periods=260, freq="D")
    close = pd.Series(100.0 + np.cumsum(np.sin(np.linspace(0, 20, len(idx))) * 0.3), index=idx)
    df = pd.DataFrame({"close": close}, index=idx)

    out = mean_reversion_half_life(df, window=60)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "mean_reversion_half_life_60"

    valid = out.dropna()
    assert np.isfinite(valid).all()
    assert (valid > 0).all()

    assert_no_lookahead(
        feature_fn=mean_reversion_half_life,
        data=df,
        t=120,
        feature_kwargs={"window": 60},
    )


def test_spread_zscore_shape_name_and_no_lookahead() -> None:
    idx = pd.date_range("2024-01-01", periods=260, freq="D")
    asset = pd.Series(100.0 + np.cumsum(np.sin(np.linspace(0, 16, len(idx))) * 0.25), index=idx)
    bench = pd.Series(200.0 + np.cumsum(np.cos(np.linspace(0, 16, len(idx))) * 0.2), index=idx)
    df = pd.DataFrame({"close": asset, "bench": bench}, index=idx)

    def _fn(d: pd.DataFrame, *, window: int) -> pd.Series:
        return spread_zscore(d, d["bench"], window=window)

    out = _fn(df, window=60)

    assert isinstance(out, pd.Series)
    assert out.index.equals(df.index)
    assert out.name == "spread_zscore_60"

    valid = out.dropna()
    assert np.isfinite(valid).all()

    assert_no_lookahead(feature_fn=_fn, data=df, t=120, feature_kwargs={"window": 60})
