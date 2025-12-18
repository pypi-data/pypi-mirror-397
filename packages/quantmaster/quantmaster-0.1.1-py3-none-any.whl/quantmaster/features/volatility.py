from __future__ import annotations

import numpy as np
import pandas as pd

from quantmaster.features.utils import get_price_series, validate_columns, validate_positive_int


def realized_variance(
    data: pd.DataFrame | pd.Series,
    *,
    price_col: str = "close",
    log_returns: bool = True,
) -> pd.Series:
    price = get_price_series(data, price_col=price_col).astype(float)

    if log_returns:
        rets = np.log(price).diff()
    else:
        rets = price.pct_change()

    rv = rets.pow(2)
    rv.name = "rv"
    return rv


def har_rv(
    data: pd.DataFrame | pd.Series,
    *,
    price_col: str = "close",
    weekly_window: int = 5,
    monthly_window: int = 22,
    prefix: str = "har_rv",
) -> pd.DataFrame:
    weekly_window = validate_positive_int(weekly_window, name="weekly_window")
    monthly_window = validate_positive_int(monthly_window, name="monthly_window")

    rv = realized_variance(data, price_col=price_col)

    out = pd.DataFrame(index=rv.index)
    out[f"{prefix}_d"] = rv
    out[f"{prefix}_w"] = rv.rolling(weekly_window).mean()
    out[f"{prefix}_m"] = rv.rolling(monthly_window).mean()
    return out


def har_rv_forecast(
    data: pd.DataFrame | pd.Series,
    *,
    price_col: str = "close",
    horizon: int = 1,
    estimation_window: int = 100,
    weekly_window: int = 5,
    monthly_window: int = 22,
    log_rv: bool = True,
) -> pd.Series:
    horizon = validate_positive_int(horizon, name="horizon")
    estimation_window = validate_positive_int(estimation_window, name="estimation_window")
    weekly_window = validate_positive_int(weekly_window, name="weekly_window")
    monthly_window = validate_positive_int(monthly_window, name="monthly_window")

    rv = realized_variance(data, price_col=price_col)
    rv = rv.astype(float)

    if log_rv:
        base = np.log(rv.where(rv > 0))
    else:
        base = rv

    x_d = base
    x_w = base.rolling(weekly_window).mean()
    x_m = base.rolling(monthly_window).mean()

    y = base.shift(-horizon)

    x = np.column_stack(
        [
            x_d.to_numpy(dtype=float),
            x_w.to_numpy(dtype=float),
            x_m.to_numpy(dtype=float),
        ]
    )
    y_arr = y.to_numpy(dtype=float)

    n = len(rv)
    out_arr = np.full(n, np.nan, dtype=float)

    for i in range(n):
        train_end = i - horizon
        if train_end < 0:
            continue

        train_start = train_end - estimation_window + 1
        if train_start < 0:
            continue

        x_win = x[train_start : train_end + 1]
        y_win = y_arr[train_start : train_end + 1]

        mask = np.isfinite(y_win)
        mask &= np.isfinite(x_win).all(axis=1)

        if mask.sum() < 4:
            continue

        a = np.column_stack([np.ones(mask.sum(), dtype=float), x_win[mask]])
        beta, *_ = np.linalg.lstsq(a, y_win[mask], rcond=None)

        x_i = x[i]
        if not np.isfinite(x_i).all():
            continue

        out_arr[i] = float(beta[0] + np.dot(beta[1:], x_i))

    out = pd.Series(out_arr, index=rv.index)
    out.name = f"har_rv_forecast_{horizon}_{estimation_window}"
    return out


def yang_zhang_volatility(
    data: pd.DataFrame,
    *,
    window: int = 20,
    open_col: str = "open",
    high_col: str = "high",
    low_col: str = "low",
    close_col: str = "close",
) -> pd.Series:
    window = validate_positive_int(window, name="window")
    if window < 2:
        raise ValueError(f"window must be >= 2, got {window}")

    validate_columns(data, required=(open_col, high_col, low_col, close_col))

    o = pd.to_numeric(data[open_col], errors="coerce").astype(float)
    h = pd.to_numeric(data[high_col], errors="coerce").astype(float)
    l = pd.to_numeric(data[low_col], errors="coerce").astype(float)
    c = pd.to_numeric(data[close_col], errors="coerce").astype(float)

    o = o.where(o > 0)
    h = h.where(h > 0)
    l = l.where(l > 0)
    c = c.where(c > 0)

    prev_c = c.shift(1)

    o_ret = np.log(o / prev_c)
    c_ret = np.log(c / o)

    sigma_o2 = o_ret.rolling(window).var(ddof=1)
    sigma_c2 = c_ret.rolling(window).var(ddof=1)

    log_ho = np.log(h / o)
    log_hc = np.log(h / c)
    log_lo = np.log(l / o)
    log_lc = np.log(l / c)
    rs = log_ho * log_hc + log_lo * log_lc
    sigma_rs2 = rs.rolling(window).mean()

    k = 0.34 / (1.34 + (window + 1) / (window - 1))
    yz_var = sigma_o2 + k * sigma_c2 + (1.0 - k) * sigma_rs2

    out = np.sqrt(yz_var)
    out.name = f"yang_zhang_volatility_{window}"
    return out
