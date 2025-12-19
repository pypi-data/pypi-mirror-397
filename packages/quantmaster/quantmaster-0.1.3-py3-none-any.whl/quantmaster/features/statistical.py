from __future__ import annotations

import numpy as np
import pandas as pd

from quantmaster.features.utils import get_price_series, validate_columns, validate_positive_int


def _fracdiff_weights(d: float, *, thresh: float, max_lags: int) -> np.ndarray:
    weights: list[float] = [1.0]

    if max_lags < 1:
        return np.asarray(weights, dtype=float)

    w_prev = 1.0
    for k in range(1, max_lags + 1):
        w_k = -w_prev * (d - k + 1) / k
        if abs(w_k) < thresh:
            break
        weights.append(w_k)
        w_prev = w_k

    return np.asarray(weights, dtype=float)


def fracdiff(
    data: pd.DataFrame | pd.Series,
    *,
    d: float = 0.4,
    thresh: float = 1e-5,
    max_lags: int | None = None,
    price_col: str = "close",
) -> pd.Series:
    try:
        d = float(d)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"d must be float, got {type(d).__name__}") from exc

    if not (0.0 <= d <= 1.0):
        raise ValueError(f"d must be between 0 and 1 (inclusive), got {d}")

    try:
        thresh = float(thresh)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"thresh must be float, got {type(thresh).__name__}") from exc

    if thresh <= 0:
        raise ValueError(f"thresh must be > 0, got {thresh}")

    if max_lags is not None:
        max_lags = validate_positive_int(max_lags, name="max_lags")

    x = get_price_series(data, price_col=price_col).astype(float)

    out_name = f"fracdiff_{d:g}"

    if len(x) < 2:
        out = pd.Series(np.nan, index=x.index, name=out_name, dtype=float)
        if d == 0.0:
            out = x.astype(float).copy()
            out.name = out_name
        return out

    x_arr = x.to_numpy(dtype=float)
    finite = np.isfinite(x_arr)

    y = np.full(x_arr.shape[0], np.nan, dtype=float)

    if finite.any():
        idxs = np.flatnonzero(finite)
        start = int(idxs[0])
        prev = int(idxs[0])
        for i in idxs[1:]:
            i = int(i)
            if i != prev + 1:
                _apply_fracdiff_segment(y, x_arr, start=start, end=prev + 1, d=d, thresh=thresh, max_lags=max_lags)
                start = i
            prev = i
        _apply_fracdiff_segment(y, x_arr, start=start, end=prev + 1, d=d, thresh=thresh, max_lags=max_lags)

    out = pd.Series(y, index=x.index)
    out.name = out_name
    return out


def _apply_fracdiff_segment(
    y: np.ndarray,
    x: np.ndarray,
    *,
    start: int,
    end: int,
    d: float,
    thresh: float,
    max_lags: int | None,
) -> None:
    seg = x[start:end]
    if seg.size < 2:
        return

    max_allowed_lags = int(seg.size - 1)
    max_lags_eff = max_allowed_lags if max_lags is None else min(int(max_lags), max_allowed_lags)

    weights = _fracdiff_weights(d, thresh=thresh, max_lags=max_lags_eff)
    k = len(weights) - 1

    seg_y = np.convolve(seg, weights, mode="full")[: seg.size]
    if k > 0:
        seg_y[:k] = np.nan
    y[start:end] = seg_y


def hurst_dfa(
    data: pd.DataFrame | pd.Series,
    *,
    window: int = 240,
    price_col: str = "close",
    min_scale: int = 4,
    max_scale: int | None = None,
    n_scales: int = 10,
    log_price: bool = True,
) -> pd.Series:
    window = validate_positive_int(window, name="window")
    min_scale = validate_positive_int(min_scale, name="min_scale")
    n_scales = validate_positive_int(n_scales, name="n_scales")

    if window < 8:
        raise ValueError(f"window must be >= 8, got {window}")

    if max_scale is None:
        max_scale_eff = max(min_scale, window // 4)
    else:
        max_scale_eff = validate_positive_int(max_scale, name="max_scale")

    max_scale_eff = min(max_scale_eff, window // 2)
    if max_scale_eff < min_scale:
        raise ValueError(f"max_scale must be >= min_scale, got max_scale={max_scale_eff}, min_scale={min_scale}")

    x = get_price_series(data, price_col=price_col).astype(float)
    if log_price:
        x = np.log(x.where(x > 0))

    out = pd.Series(np.nan, index=x.index, dtype=float)
    out.name = f"hurst_dfa_{window}"

    if len(x) < window:
        return out

    scales = np.unique(
        np.floor(
            np.logspace(
                np.log10(float(min_scale)),
                np.log10(float(max_scale_eff)),
                int(n_scales),
            )
        ).astype(int)
    )
    scales = scales[(scales >= min_scale) & (scales <= max_scale_eff)]
    if scales.size < 2:
        return out

    x_arr = x.to_numpy(dtype=float)
    windows = np.lib.stride_tricks.sliding_window_view(x_arr, window_shape=window)

    mean_win = np.nanmean(windows, axis=1, keepdims=True)
    prof = np.nancumsum(windows - mean_win, axis=1)

    log_s = np.log(scales.astype(float))
    f_mat = np.full((prof.shape[0], scales.size), np.nan, dtype=float)

    for j, s in enumerate(scales.tolist()):
        m = window // int(s)
        if m < 2:
            continue

        y = prof[:, : m * s].reshape(prof.shape[0], m, s)

        t = np.arange(s, dtype=float)
        t_mean = t.mean()
        t_centered = t - t_mean
        denom = float(np.sum(t_centered**2))
        if denom == 0.0:
            continue

        y_mean = np.nanmean(y, axis=2, keepdims=True)
        slope = np.nansum(t_centered[None, None, :] * (y - y_mean), axis=2, keepdims=True) / denom
        intercept = y_mean - slope * t_mean

        trend = slope * t[None, None, :] + intercept
        res = y - trend
        f_mat[:, j] = np.sqrt(np.nanmean(res**2, axis=(1, 2)))

    log_f = np.log(f_mat)
    valid_scale = np.isfinite(log_s)
    valid_scale &= np.isfinite(log_f).all(axis=0)

    if valid_scale.sum() < 2:
        return out

    xs = log_s[valid_scale]
    ys = log_f[:, valid_scale]

    x_mean = xs.mean()
    x_centered = xs - x_mean
    x_var = float(np.sum(x_centered**2))
    if x_var == 0.0:
        return out

    y_mean = ys.mean(axis=1, keepdims=True)
    cov = np.sum((ys - y_mean) * x_centered[None, :], axis=1)
    hurst = cov / x_var

    out.iloc[window - 1 :] = hurst
    return out


def ornstein_uhlenbeck(
    data: pd.DataFrame | pd.Series,
    *,
    window: int = 240,
    detrend_window: int = 48,
    price_col: str = "close",
) -> pd.DataFrame:
    window = validate_positive_int(window, name="window")
    detrend_window = validate_positive_int(detrend_window, name="detrend_window")

    if window < 8:
        raise ValueError(f"window must be >= 8, got {window}")

    price = get_price_series(data, price_col=price_col).astype(float)
    log_p = np.log(price.where(price > 0))
    x = log_p - log_p.rolling(detrend_window).mean()

    out = pd.DataFrame(index=price.index)
    out[f"ou_phi_{window}"] = np.nan
    out[f"ou_kappa_{window}"] = np.nan
    out[f"ou_theta_{window}"] = np.nan
    out[f"ou_sigma_{window}"] = np.nan
    out[f"ou_sigma_eq_{window}"] = np.nan
    out[f"ou_halflife_{window}"] = np.nan
    out[f"ou_zscore_{window}"] = np.nan

    if len(x) < window:
        return out

    x_arr = x.to_numpy(dtype=float)
    windows = np.lib.stride_tricks.sliding_window_view(x_arr, window_shape=window)

    x_prev = windows[:, :-1]
    y = windows[:, 1:]
    mask = np.isfinite(x_prev) & np.isfinite(y)

    x_prev_m = np.where(mask, x_prev, np.nan)
    y_m = np.where(mask, y, np.nan)

    n_eff = np.sum(mask, axis=1)
    min_obs = max(10, (window - 1) // 2)
    valid_n = n_eff >= min_obs

    mean_x = np.nanmean(x_prev_m, axis=1)
    mean_y = np.nanmean(y_m, axis=1)

    x_c = x_prev - mean_x[:, None]
    y_c = y - mean_y[:, None]

    cov_xy = np.nanmean(np.where(mask, x_c * y_c, np.nan), axis=1)
    var_x = np.nanmean(np.where(mask, x_c * x_c, np.nan), axis=1)

    phi = cov_xy / var_x
    phi = np.where(valid_n & np.isfinite(phi), phi, np.nan)

    c = mean_y - phi * mean_x

    phi_valid = (phi > 0.0) & (phi < 1.0)
    kappa = np.where(phi_valid, -np.log(phi), np.nan)

    theta = np.where(phi_valid, c / (1.0 - phi), np.nan)

    pred = c[:, None] + phi[:, None] * x_prev
    resid = np.where(mask, y - pred, np.nan)
    resid_var = np.nanmean(resid * resid, axis=1)

    one_minus_phi2 = 1.0 - phi * phi
    sigma_eq2 = np.where(phi_valid & (one_minus_phi2 > 0.0), resid_var / one_minus_phi2, np.nan)
    sigma_eq = np.sqrt(sigma_eq2)
    sigma = np.where(phi_valid & np.isfinite(kappa), sigma_eq * np.sqrt(2.0 * kappa), np.nan)

    halflife = np.where(phi_valid & (kappa > 0.0), np.log(2.0) / kappa, np.nan)

    x_t = windows[:, -1]
    zscore = np.where(phi_valid & (sigma_eq > 0.0), (x_t - theta) / sigma_eq, np.nan)

    start = window - 1
    out.iloc[start:, out.columns.get_loc(f"ou_phi_{window}")] = phi
    out.iloc[start:, out.columns.get_loc(f"ou_kappa_{window}")] = kappa
    out.iloc[start:, out.columns.get_loc(f"ou_theta_{window}")] = theta
    out.iloc[start:, out.columns.get_loc(f"ou_sigma_{window}")] = sigma
    out.iloc[start:, out.columns.get_loc(f"ou_sigma_eq_{window}")] = sigma_eq
    out.iloc[start:, out.columns.get_loc(f"ou_halflife_{window}")] = halflife
    out.iloc[start:, out.columns.get_loc(f"ou_zscore_{window}")] = zscore

    return out


def _beta_from_windows(x: np.ndarray, y: np.ndarray) -> float:
    mask = np.isfinite(x) & np.isfinite(y)
    if mask.sum() < 2:
        return float("nan")

    x_m = x[mask]
    y_m = y[mask]

    x_mean = float(x_m.mean())
    y_mean = float(y_m.mean())
    x_c = x_m - x_mean
    y_c = y_m - y_mean

    denom = float(np.sum(y_c * y_c))
    if denom == 0.0:
        return float("nan")

    return float(np.sum(x_c * y_c) / denom)


def rolling_beta(
    data: pd.DataFrame | pd.Series,
    benchmark: pd.Series,
    *,
    window: int = 60,
    price_col: str = "close",
    log_returns: bool = True,
) -> pd.Series:
    window = validate_positive_int(window, name="window")

    asset_price = get_price_series(data, price_col=price_col).astype(float)
    bench_price = pd.to_numeric(benchmark, errors="coerce").astype(float)

    if log_returns:
        r_asset = np.log(asset_price.where(asset_price > 0)).diff()
        r_bench = np.log(bench_price.where(bench_price > 0)).diff()
    else:
        r_asset = asset_price.pct_change()
        r_bench = bench_price.pct_change()

    df = pd.concat([r_asset.rename("asset"), r_bench.rename("bench")], axis=1)
    out = pd.Series(np.nan, index=df.index, dtype=float)
    out.name = f"rolling_beta_{window}"

    if len(df) < window:
        return out

    x = df["asset"].to_numpy(dtype=float)
    y = df["bench"].to_numpy(dtype=float)

    xw = np.lib.stride_tricks.sliding_window_view(x, window_shape=window)
    yw = np.lib.stride_tricks.sliding_window_view(y, window_shape=window)

    beta_arr = np.full(xw.shape[0], np.nan, dtype=float)
    for i in range(xw.shape[0]):
        beta_arr[i] = _beta_from_windows(xw[i], yw[i])

    out.iloc[window - 1 :] = beta_arr
    return out


def downside_beta(
    data: pd.DataFrame | pd.Series,
    benchmark: pd.Series,
    *,
    window: int = 60,
    price_col: str = "close",
    log_returns: bool = True,
) -> pd.Series:
    window = validate_positive_int(window, name="window")

    asset_price = get_price_series(data, price_col=price_col).astype(float)
    bench_price = pd.to_numeric(benchmark, errors="coerce").astype(float)

    if log_returns:
        r_asset = np.log(asset_price.where(asset_price > 0)).diff()
        r_bench = np.log(bench_price.where(bench_price > 0)).diff()
    else:
        r_asset = asset_price.pct_change()
        r_bench = bench_price.pct_change()

    df = pd.concat([r_asset.rename("asset"), r_bench.rename("bench")], axis=1)
    out = pd.Series(np.nan, index=df.index, dtype=float)
    out.name = f"downside_beta_{window}"

    if len(df) < window:
        return out

    x = df["asset"].to_numpy(dtype=float)
    y = df["bench"].to_numpy(dtype=float)

    xw = np.lib.stride_tricks.sliding_window_view(x, window_shape=window)
    yw = np.lib.stride_tricks.sliding_window_view(y, window_shape=window)

    beta_arr = np.full(xw.shape[0], np.nan, dtype=float)
    for i in range(xw.shape[0]):
        mask = np.isfinite(xw[i]) & np.isfinite(yw[i]) & (yw[i] < 0.0)
        if mask.sum() < 2:
            continue
        beta_arr[i] = _beta_from_windows(xw[i][mask], yw[i][mask])

    out.iloc[window - 1 :] = beta_arr
    return out


def information_discreteness(
    data: pd.DataFrame | pd.Series,
    *,
    window: int = 20,
    price_col: str = "close",
    log_returns: bool = True,
) -> pd.Series:
    window = validate_positive_int(window, name="window")

    price = get_price_series(data, price_col=price_col).astype(float)
    price = price.where(price > 0)

    if log_returns:
        rets = np.log(price).diff()
    else:
        rets = price.pct_change()

    out = pd.Series(np.nan, index=price.index, dtype=float)
    out.name = f"information_discreteness_{window}"

    if len(rets) < window:
        return out

    r = rets.to_numpy(dtype=float)
    rw = np.lib.stride_tricks.sliding_window_view(r, window_shape=window)

    id_arr = np.full(rw.shape[0], np.nan, dtype=float)
    for i in range(rw.shape[0]):
        w = rw[i]
        w = w[np.isfinite(w)]
        if w.size < 2:
            continue

        r_total = float(np.sum(w))
        s_total = float(np.sign(r_total))
        if s_total == 0.0:
            id_arr[i] = 0.0
            continue

        s = np.sign(w)
        s = s[s != 0.0]
        if s.size == 0:
            continue

        same = float(np.mean(s == s_total))
        opp = float(np.mean(s == -s_total))
        id_arr[i] = s_total * (same - opp)

    out.iloc[window - 1 :] = id_arr
    return out


def realized_skewness(
    data: pd.DataFrame | pd.Series,
    *,
    window: int = 20,
    price_col: str = "close",
    log_returns: bool = True,
) -> pd.Series:
    window = validate_positive_int(window, name="window")

    price = get_price_series(data, price_col=price_col).astype(float)
    price = price.where(price > 0)

    if log_returns:
        r = np.log(price).diff()
    else:
        r = price.pct_change()

    m2 = r.pow(2).rolling(window).sum()
    m3 = r.pow(3).rolling(window).sum()

    denom = m2.pow(1.5)
    out = np.sqrt(float(window)) * m3 / denom.where(denom > 0)
    out.name = f"realized_skewness_{window}"
    return out


def realized_kurtosis(
    data: pd.DataFrame | pd.Series,
    *,
    window: int = 20,
    price_col: str = "close",
    log_returns: bool = True,
) -> pd.Series:
    window = validate_positive_int(window, name="window")

    price = get_price_series(data, price_col=price_col).astype(float)
    price = price.where(price > 0)

    if log_returns:
        r = np.log(price).diff()
    else:
        r = price.pct_change()

    m2 = r.pow(2).rolling(window).sum()
    m4 = r.pow(4).rolling(window).sum()

    denom = m2.pow(2)
    out = float(window) * m4 / denom.where(denom > 0)
    out.name = f"realized_kurtosis_{window}"
    return out


def _rolling_corr_1d(x: np.ndarray, y: np.ndarray) -> float:
    mask = np.isfinite(x) & np.isfinite(y)
    if mask.sum() < 2:
        return float("nan")
    x_m = x[mask]
    y_m = y[mask]
    x_c = x_m - float(x_m.mean())
    y_c = y_m - float(y_m.mean())
    denom = float(np.sqrt(np.sum(x_c * x_c) * np.sum(y_c * y_c)))
    if denom == 0.0:
        return float("nan")
    return float(np.sum(x_c * y_c) / denom)


def return_autocorrelation(
    data: pd.DataFrame | pd.Series,
    *,
    window: int = 60,
    lag: int = 1,
    price_col: str = "close",
    log_returns: bool = True,
) -> pd.Series:
    window = validate_positive_int(window, name="window")
    lag = validate_positive_int(lag, name="lag")
    if lag >= window:
        raise ValueError(f"lag must be < window, got lag={lag} window={window}")

    price = get_price_series(data, price_col=price_col).astype(float)
    price = price.where(price > 0)

    if log_returns:
        r = np.log(price).diff()
    else:
        r = price.pct_change()

    def _fn(w: np.ndarray) -> float:
        a = w[lag:]
        b = w[:-lag]
        return _rolling_corr_1d(a, b)

    out = r.rolling(window).apply(_fn, raw=True)
    out.name = f"return_autocorrelation_{window}_{lag}"
    return out


def absolute_return_autocorrelation(
    data: pd.DataFrame | pd.Series,
    *,
    window: int = 60,
    lag: int = 1,
    price_col: str = "close",
    log_returns: bool = True,
) -> pd.Series:
    window = validate_positive_int(window, name="window")
    lag = validate_positive_int(lag, name="lag")
    if lag >= window:
        raise ValueError(f"lag must be < window, got lag={lag} window={window}")

    price = get_price_series(data, price_col=price_col).astype(float)
    price = price.where(price > 0)

    if log_returns:
        r = np.log(price).diff().abs()
    else:
        r = price.pct_change().abs()

    def _fn(w: np.ndarray) -> float:
        a = w[lag:]
        b = w[:-lag]
        return _rolling_corr_1d(a, b)

    out = r.rolling(window).apply(_fn, raw=True)
    out.name = f"absolute_return_autocorrelation_{window}_{lag}"
    return out


def _generalized_hurst_exponent_1d(x: np.ndarray, *, q: float, max_lag: int) -> float:
    x = x[np.isfinite(x)]
    if x.size < max_lag + 2:
        return float("nan")

    taus = np.arange(1, max_lag + 1, dtype=int)
    moments = np.empty_like(taus, dtype=float)
    for i, tau in enumerate(taus):
        d = np.abs(x[tau:] - x[:-tau])
        if d.size < 2:
            moments[i] = np.nan
        else:
            moments[i] = float(np.mean(d**q))

    mask = np.isfinite(moments) & (moments > 0)
    if mask.sum() < 2:
        return float("nan")

    log_tau = np.log(taus[mask].astype(float))
    log_m = np.log(moments[mask])
    slope = float(np.polyfit(log_tau, log_m, 1)[0])
    return float(slope / q)


def generalized_hurst_exponent(
    data: pd.DataFrame | pd.Series,
    *,
    window: int = 100,
    q: float = 2.0,
    max_lag: int = 20,
    price_col: str = "close",
) -> pd.Series:
    window = validate_positive_int(window, name="window")
    max_lag = validate_positive_int(max_lag, name="max_lag")
    try:
        q = float(q)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"q must be float, got {type(q).__name__}") from exc
    if q <= 0:
        raise ValueError(f"q must be > 0, got {q}")
    if max_lag >= window:
        raise ValueError(f"max_lag must be < window, got max_lag={max_lag} window={window}")

    price = get_price_series(data, price_col=price_col).astype(float)
    price = price.where(price > 0)
    x = np.log(price)

    out = pd.Series(np.nan, index=price.index, dtype=float)
    out.name = f"generalized_hurst_exponent_{window}_{q:g}_{max_lag}"

    if len(x) < window:
        return out

    arr = x.to_numpy(dtype=float)
    windows = np.lib.stride_tricks.sliding_window_view(arr, window_shape=window)
    vals = np.full(windows.shape[0], np.nan, dtype=float)
    for i in range(windows.shape[0]):
        vals[i] = _generalized_hurst_exponent_1d(windows[i], q=q, max_lag=max_lag)

    out.iloc[window - 1 :] = vals
    return out


def _fractal_dimension_mincover_1d(x: np.ndarray, *, max_scale: int) -> float:
    x = x[np.isfinite(x)]
    n = x.size
    if n < 4:
        return float("nan")

    max_scale_eff = min(int(max_scale), max(2, n // 2))
    if max_scale_eff < 2:
        return float("nan")

    scales = np.arange(1, max_scale_eff + 1, dtype=int)
    a = np.empty_like(scales, dtype=float)
    for i, k in enumerate(scales):
        m = n // k
        if m < 1:
            a[i] = np.nan
            continue
        x_use = x[: m * k]
        blocks = x_use.reshape(m, k)
        rng = blocks.max(axis=1) - blocks.min(axis=1)
        a_k = float(np.sum(rng))
        a[i] = a_k

    mask = np.isfinite(a) & (a > 0) & (scales > 0)
    if mask.sum() < 2:
        return float("nan")

    log_s = np.log(scales[mask].astype(float))
    log_a = np.log(a[mask])
    slope = float(np.polyfit(log_s, log_a, 1)[0])
    return float(2.0 - slope)


def fractal_dimension_mincover(
    data: pd.DataFrame | pd.Series,
    *,
    window: int = 100,
    max_scale: int = 10,
    price_col: str = "close",
) -> pd.Series:
    window = validate_positive_int(window, name="window")
    max_scale = validate_positive_int(max_scale, name="max_scale")

    price = get_price_series(data, price_col=price_col).astype(float)
    price = price.where(price > 0)
    x = np.log(price)

    out = pd.Series(np.nan, index=price.index, dtype=float)
    out.name = f"fractal_dimension_mincover_{window}_{max_scale}"

    if len(x) < window:
        return out

    arr = x.to_numpy(dtype=float)
    windows = np.lib.stride_tricks.sliding_window_view(arr, window_shape=window)
    vals = np.full(windows.shape[0], np.nan, dtype=float)
    for i in range(windows.shape[0]):
        vals[i] = _fractal_dimension_mincover_1d(windows[i], max_scale=max_scale)

    out.iloc[window - 1 :] = vals
    return out


def _ols_slope(x: np.ndarray, y: np.ndarray) -> float:
    mask = np.isfinite(x) & np.isfinite(y)
    if mask.sum() < 2:
        return float("nan")
    x_m = x[mask]
    y_m = y[mask]
    x_c = x_m - float(x_m.mean())
    y_c = y_m - float(y_m.mean())
    denom = float(np.sum(x_c * x_c))
    if denom == 0.0:
        return float("nan")
    return float(np.sum(x_c * y_c) / denom)


def mean_reversion_half_life(
    data: pd.DataFrame | pd.Series,
    *,
    window: int = 60,
    price_col: str = "close",
) -> pd.Series:
    window = validate_positive_int(window, name="window")

    price = get_price_series(data, price_col=price_col).astype(float)
    price = price.where(price > 0)

    out = pd.Series(np.nan, index=price.index, dtype=float)
    out.name = f"mean_reversion_half_life_{window}"

    if len(price) < window:
        return out

    p = np.log(price).to_numpy(dtype=float)
    pw = np.lib.stride_tricks.sliding_window_view(p, window_shape=window)

    hl = np.full(pw.shape[0], np.nan, dtype=float)
    for i in range(pw.shape[0]):
        w = pw[i]
        x = w[:-1]
        y = np.diff(w)
        lam = _ols_slope(x, y)
        if not np.isfinite(lam) or lam >= 0.0:
            continue
        hl[i] = float(-np.log(2.0) / lam)

    out.iloc[window - 1 :] = hl
    return out


def spread_zscore(
    data: pd.DataFrame,
    benchmark: pd.Series,
    *,
    window: int = 60,
    price_col: str = "close",
    log_prices: bool = True,
) -> pd.Series:
    window = validate_positive_int(window, name="window")

    asset_price = get_price_series(data, price_col=price_col).astype(float)
    bench_price = pd.to_numeric(benchmark, errors="coerce").astype(float)

    asset_price = asset_price.where(asset_price > 0)
    bench_price = bench_price.where(bench_price > 0)

    df = pd.concat([asset_price.rename("asset"), bench_price.rename("bench")], axis=1)

    out = pd.Series(np.nan, index=df.index, dtype=float)
    out.name = f"spread_zscore_{window}"

    if len(df) < window:
        return out

    if log_prices:
        x = np.log(df["asset"]).to_numpy(dtype=float)
        y = np.log(df["bench"]).to_numpy(dtype=float)
    else:
        x = df["asset"].to_numpy(dtype=float)
        y = df["bench"].to_numpy(dtype=float)

    xw = np.lib.stride_tricks.sliding_window_view(x, window_shape=window)
    yw = np.lib.stride_tricks.sliding_window_view(y, window_shape=window)

    beta = np.full(xw.shape[0], np.nan, dtype=float)
    for i in range(xw.shape[0]):
        beta[i] = _beta_from_windows(xw[i], yw[i])

    spread = x - np.concatenate([np.full(window - 1, np.nan, dtype=float), beta]) * y

    spread_s = pd.Series(spread, index=df.index)
    mu = spread_s.rolling(window).mean()
    sigma = spread_s.rolling(window).std(ddof=1)
    out = (spread_s - mu) / sigma.where(sigma > 0)
    out.name = f"spread_zscore_{window}"
    return out


def path_signature_features(
    data: pd.DataFrame,
    *,
    depth: int = 2,
    window: int = 20,
    open_col: str = "open",
    high_col: str = "high",
    low_col: str = "low",
    close_col: str = "close",
    volume_col: str = "volume",
    log_transform: bool = True,
) -> pd.DataFrame:
    try:
        import iisignature  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "path_signature_features requires optional dependency 'iisignature'. "
            "Install it with `pip install iisignature`."
        ) from exc

    depth = validate_positive_int(depth, name="depth")
    window = validate_positive_int(window, name="window")

    cols = [open_col, high_col, low_col, close_col, volume_col]
    validate_columns(data, required=cols)

    x = data[cols].apply(pd.to_numeric, errors="coerce").astype(float)
    if log_transform:
        x = x.where(x > 0)
        x = np.log(x)

    x_arr = x.to_numpy(dtype=float)
    n, d = x_arr.shape

    sig_len = int(iisignature.siglength(d, depth))
    col_names = [f"path_sig_{depth}_{k}" for k in range(sig_len)]

    out = pd.DataFrame(np.nan, index=data.index, columns=col_names, dtype=float)
    if n < window:
        return out

    windows = np.lib.stride_tricks.sliding_window_view(x_arr, window_shape=window, axis=0)

    sig_mat = np.full((windows.shape[0], sig_len), np.nan, dtype=float)
    for i in range(windows.shape[0]):
        w = windows[i]
        if not np.isfinite(w).all():
            continue

        w0 = w - w[0:1]
        try:
            sig = np.asarray(iisignature.sig(w0, depth), dtype=float)
        except Exception:
            continue

        if sig.shape[0] != sig_len:
            continue
        sig_mat[i] = sig

    start = window - 1
    out.iloc[start:, :] = sig_mat
    return out


def _validate_positive_int_local(value: int, *, name: str) -> int:
    return validate_positive_int(value, name=name)


def _validate_r(r: float) -> float:
    try:
        r = float(r)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"r must be float, got {type(r).__name__}") from exc
    if r <= 0:
        raise ValueError(f"r must be > 0, got {r}")
    return r


def _validate_m(m: int) -> int:
    if not isinstance(m, int):
        raise TypeError(f"m must be int, got {type(m).__name__}")
    if m < 1:
        raise ValueError(f"m must be >= 1, got {m}")
    return m


def _count_matches_upper(emb: np.ndarray, tol: float) -> int:
    k = emb.shape[0]
    if k < 2:
        return 0

    cnt = 0
    for i in range(k - 1):
        dist = np.max(np.abs(emb[i + 1 :] - emb[i]), axis=1)
        cnt += int(np.sum(dist <= tol))
    return cnt


def _sample_entropy_1d(x: np.ndarray, *, m: int, tol: float) -> float:
    n = x.size
    if n < m + 2:
        return float("nan")

    if not np.isfinite(x).all():
        return float("nan")

    emb_m = np.lib.stride_tricks.sliding_window_view(x, window_shape=m)
    emb_m1 = np.lib.stride_tricks.sliding_window_view(x, window_shape=m + 1)

    b = _count_matches_upper(emb_m, tol)
    a = _count_matches_upper(emb_m1, tol)

    if b <= 0 or a <= 0:
        return float("nan")

    return float(-np.log(a / b))


def _approximate_entropy_1d(x: np.ndarray, *, m: int, tol: float) -> float:
    n = x.size
    if n < m + 2:
        return float("nan")

    if not np.isfinite(x).all():
        return float("nan")

    emb_m = np.lib.stride_tricks.sliding_window_view(x, window_shape=m)
    emb_m1 = np.lib.stride_tricks.sliding_window_view(x, window_shape=m + 1)

    k_m = emb_m.shape[0]
    k_m1 = emb_m1.shape[0]

    c_m = np.empty(k_m, dtype=float)
    for i in range(k_m):
        dist = np.max(np.abs(emb_m - emb_m[i]), axis=1)
        c_m[i] = np.sum(dist <= tol) / float(k_m)

    c_m1 = np.empty(k_m1, dtype=float)
    for i in range(k_m1):
        dist = np.max(np.abs(emb_m1 - emb_m1[i]), axis=1)
        c_m1[i] = np.sum(dist <= tol) / float(k_m1)

    if not (c_m > 0).all() or not (c_m1 > 0).all():
        return float("nan")

    phi_m = float(np.mean(np.log(c_m)))
    phi_m1 = float(np.mean(np.log(c_m1)))
    return phi_m - phi_m1


def _permutation_entropy_1d(x: np.ndarray, *, order: int, delay: int) -> float:
    n = x.size
    span = (order - 1) * delay + 1
    if n < span:
        return float("nan")
    if not np.isfinite(x).all():
        return float("nan")

    windows = np.lib.stride_tricks.sliding_window_view(x, window_shape=span)
    emb = windows[:, ::delay]

    ranks = np.argsort(np.argsort(emb, axis=1, kind="mergesort"), axis=1, kind="mergesort")

    base = int(order)
    weights = (base ** np.arange(order, dtype=np.int64)).astype(np.int64)
    codes = (ranks.astype(np.int64) * weights[None, :]).sum(axis=1)

    _, counts = np.unique(codes, return_counts=True)
    p = counts.astype(float) / float(counts.sum())
    return float(-np.sum(p * np.log(p)))


def _cross_sample_entropy_1d(x1: np.ndarray, x2: np.ndarray, *, m: int, tol: float) -> float:
    if x1.size != x2.size:
        return float("nan")
    n = x1.size
    if n < m + 2:
        return float("nan")
    if not np.isfinite(x1).all() or not np.isfinite(x2).all():
        return float("nan")

    emb1_m = np.lib.stride_tricks.sliding_window_view(x1, window_shape=m)
    emb2_m = np.lib.stride_tricks.sliding_window_view(x2, window_shape=m)
    emb1_m1 = np.lib.stride_tricks.sliding_window_view(x1, window_shape=m + 1)
    emb2_m1 = np.lib.stride_tricks.sliding_window_view(x2, window_shape=m + 1)

    b = 0
    for i in range(emb1_m.shape[0]):
        dist = np.max(np.abs(emb2_m - emb1_m[i]), axis=1)
        b += int(np.sum(dist <= tol))

    a = 0
    for i in range(emb1_m1.shape[0]):
        dist = np.max(np.abs(emb2_m1 - emb1_m1[i]), axis=1)
        a += int(np.sum(dist <= tol))

    if b <= 0 or a <= 0:
        return float("nan")

    return float(-np.log(a / b))


def sample_entropy(
    data: pd.DataFrame | pd.Series,
    *,
    window: int = 100,
    m: int = 2,
    r: float = 0.2,
    price_col: str = "close",
) -> pd.Series:
    window = _validate_positive_int_local(window, name="window")
    m = _validate_m(m)
    r = _validate_r(r)

    x = get_price_series(data, price_col=price_col).astype(float)
    out = pd.Series(np.nan, index=x.index, dtype=float)
    out.name = f"sample_entropy_{window}"

    if len(x) < window:
        return out

    x_arr = x.to_numpy(dtype=float)
    for i in range(window - 1, len(x_arr)):
        win = x_arr[i - window + 1 : i + 1]
        if not np.isfinite(win).all():
            continue
        tol = r * float(np.std(win))
        out.iat[i] = _sample_entropy_1d(win, m=m, tol=tol)

    return out


def approximate_entropy(
    data: pd.DataFrame | pd.Series,
    *,
    window: int = 100,
    m: int = 2,
    r: float = 0.2,
    price_col: str = "close",
) -> pd.Series:
    window = _validate_positive_int_local(window, name="window")
    m = _validate_m(m)
    r = _validate_r(r)

    x = get_price_series(data, price_col=price_col).astype(float)
    out = pd.Series(np.nan, index=x.index, dtype=float)
    out.name = f"approximate_entropy_{window}"

    if len(x) < window:
        return out

    x_arr = x.to_numpy(dtype=float)
    for i in range(window - 1, len(x_arr)):
        win = x_arr[i - window + 1 : i + 1]
        if not np.isfinite(win).all():
            continue
        tol = r * float(np.std(win))
        out.iat[i] = _approximate_entropy_1d(win, m=m, tol=tol)

    return out


def permutation_entropy(
    data: pd.DataFrame | pd.Series,
    *,
    window: int = 100,
    order: int = 3,
    delay: int = 1,
    price_col: str = "close",
) -> pd.Series:
    window = _validate_positive_int_local(window, name="window")
    order = _validate_positive_int_local(order, name="order")
    delay = _validate_positive_int_local(delay, name="delay")
    if order < 2:
        raise ValueError(f"order must be >= 2, got {order}")
    if order > 8:
        raise ValueError(f"order must be <= 8, got {order}")

    x = get_price_series(data, price_col=price_col).astype(float)
    out = pd.Series(np.nan, index=x.index, dtype=float)
    out.name = f"permutation_entropy_{window}_{order}_{delay}"

    if len(x) < window:
        return out

    x_arr = x.to_numpy(dtype=float)
    for i in range(window - 1, len(x_arr)):
        win = x_arr[i - window + 1 : i + 1]
        out.iat[i] = _permutation_entropy_1d(win, order=order, delay=delay)

    return out


def cross_sample_entropy(
    data1: pd.Series,
    data2: pd.Series,
    *,
    window: int = 100,
    m: int = 2,
    r: float = 0.2,
) -> pd.Series:
    window = _validate_positive_int_local(window, name="window")
    m = _validate_m(m)
    r = _validate_r(r)

    s1 = pd.to_numeric(data1, errors="coerce").astype(float)
    s2 = pd.to_numeric(data2, errors="coerce").astype(float)

    df = pd.concat([s1.rename("x"), s2.rename("y")], axis=1)

    out = pd.Series(np.nan, index=df.index, dtype=float)
    out.name = f"cross_sample_entropy_{window}"

    if len(df) < window:
        return out

    x1 = df["x"].to_numpy(dtype=float)
    x2 = df["y"].to_numpy(dtype=float)

    for i in range(window - 1, len(df)):
        w1 = x1[i - window + 1 : i + 1]
        w2 = x2[i - window + 1 : i + 1]
        if not np.isfinite(w1).all() or not np.isfinite(w2).all():
            continue
        std = float(np.std(np.concatenate([w1, w2])))
        if not np.isfinite(std):
            continue
        tol = r * std
        out.iat[i] = _cross_sample_entropy_1d(w1, w2, m=m, tol=tol)

    return out
