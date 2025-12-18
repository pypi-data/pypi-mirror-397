from __future__ import annotations

import numpy as np
import pandas as pd

from quantmaster.features.utils import get_price_series, validate_positive_int


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
    d: float = 0.5,
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

    max_allowed_lags = len(x) - 1
    max_lags_eff = max_allowed_lags if max_lags is None else min(max_lags, max_allowed_lags)

    weights = _fracdiff_weights(d, thresh=thresh, max_lags=max_lags_eff)
    k = len(weights) - 1

    y = np.convolve(x.to_numpy(dtype=float), weights, mode="full")[: len(x)]
    if k > 0:
        y[:k] = np.nan

    out = pd.Series(y, index=x.index)
    out.name = out_name
    return out


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
