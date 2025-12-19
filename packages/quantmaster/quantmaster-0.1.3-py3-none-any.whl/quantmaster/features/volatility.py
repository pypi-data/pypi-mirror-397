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


def parkinson_volatility(
    data: pd.DataFrame,
    *,
    window: int = 20,
    high_col: str = "high",
    low_col: str = "low",
) -> pd.Series:
    window = validate_positive_int(window, name="window")
    validate_columns(data, required=(high_col, low_col))

    h = pd.to_numeric(data[high_col], errors="coerce").astype(float)
    l = pd.to_numeric(data[low_col], errors="coerce").astype(float)

    h = h.where(h > 0)
    l = l.where(l > 0)

    log_hl = np.log(h / l)
    var = log_hl.pow(2).rolling(window).mean() / (4.0 * np.log(2.0))

    out = np.sqrt(var.clip(lower=0.0))
    out.name = f"parkinson_volatility_{window}"
    return out


def garman_klass_volatility(
    data: pd.DataFrame,
    *,
    window: int = 20,
    open_col: str = "open",
    high_col: str = "high",
    low_col: str = "low",
    close_col: str = "close",
) -> pd.Series:
    window = validate_positive_int(window, name="window")
    validate_columns(data, required=(open_col, high_col, low_col, close_col))

    o = pd.to_numeric(data[open_col], errors="coerce").astype(float)
    h = pd.to_numeric(data[high_col], errors="coerce").astype(float)
    l = pd.to_numeric(data[low_col], errors="coerce").astype(float)
    c = pd.to_numeric(data[close_col], errors="coerce").astype(float)

    o = o.where(o > 0)
    h = h.where(h > 0)
    l = l.where(l > 0)
    c = c.where(c > 0)

    log_hl = np.log(h / l)
    log_co = np.log(c / o)
    gk_var = 0.5 * log_hl.pow(2) - (2.0 * np.log(2.0) - 1.0) * log_co.pow(2)
    var = gk_var.rolling(window).mean()

    out = np.sqrt(var.clip(lower=0.0))
    out.name = f"garman_klass_volatility_{window}"
    return out


def rogers_satchell_volatility(
    data: pd.DataFrame,
    *,
    window: int = 20,
    open_col: str = "open",
    high_col: str = "high",
    low_col: str = "low",
    close_col: str = "close",
) -> pd.Series:
    window = validate_positive_int(window, name="window")
    validate_columns(data, required=(open_col, high_col, low_col, close_col))

    o = pd.to_numeric(data[open_col], errors="coerce").astype(float)
    h = pd.to_numeric(data[high_col], errors="coerce").astype(float)
    l = pd.to_numeric(data[low_col], errors="coerce").astype(float)
    c = pd.to_numeric(data[close_col], errors="coerce").astype(float)

    o = o.where(o > 0)
    h = h.where(h > 0)
    l = l.where(l > 0)
    c = c.where(c > 0)

    log_hc = np.log(h / c)
    log_ho = np.log(h / o)
    log_lc = np.log(l / c)
    log_lo = np.log(l / o)
    rs_var = log_hc * log_ho + log_lc * log_lo
    var = rs_var.rolling(window).mean()

    out = np.sqrt(var.clip(lower=0.0))
    out.name = f"rogers_satchell_volatility_{window}"
    return out


def intraday_range(
    data: pd.DataFrame,
    *,
    window: int = 20,
    high_col: str = "high",
    low_col: str = "low",
) -> pd.Series:
    window = validate_positive_int(window, name="window")
    validate_columns(data, required=(high_col, low_col))

    h = pd.to_numeric(data[high_col], errors="coerce").astype(float)
    l = pd.to_numeric(data[low_col], errors="coerce").astype(float)

    h = h.where(h > 0)
    l = l.where(l > 0)

    out = np.log(h / l).rolling(window).mean()
    out.name = f"intraday_range_{window}"
    return out


def volatility_ratio(
    data: pd.DataFrame,
    *,
    window: int = 14,
    high_col: str = "high",
    low_col: str = "low",
    close_col: str = "close",
) -> pd.Series:
    window = validate_positive_int(window, name="window")
    validate_columns(data, required=(high_col, low_col, close_col))

    h = pd.to_numeric(data[high_col], errors="coerce").astype(float)
    l = pd.to_numeric(data[low_col], errors="coerce").astype(float)
    c = pd.to_numeric(data[close_col], errors="coerce").astype(float)

    prev_c = c.shift(1)
    tr_1 = h - l
    tr_2 = (h - prev_c).abs()
    tr_3 = (l - prev_c).abs()
    tr = pd.concat([tr_1, tr_2, tr_3], axis=1).max(axis=1)

    atr = tr.rolling(window).mean()
    out = tr / atr.where(atr > 0)
    out.name = f"volatility_ratio_{window}"
    return out


def bipower_variation(
    data: pd.DataFrame | pd.Series,
    *,
    price_col: str = "close",
    log_returns: bool = True,
) -> pd.Series:
    price = get_price_series(data, price_col=price_col).astype(float)
    price = price.where(price > 0)

    if log_returns:
        rets = np.log(price).diff()
    else:
        rets = price.pct_change()

    abs_r = rets.abs()
    out = (np.pi / 2.0) * abs_r * abs_r.shift(1)
    out.name = "bv"
    return out


def jump_variation(
    data: pd.DataFrame | pd.Series,
    *,
    price_col: str = "close",
    log_returns: bool = True,
) -> pd.Series:
    rv = realized_variance(data, price_col=price_col, log_returns=log_returns).astype(float)
    bv = bipower_variation(data, price_col=price_col, log_returns=log_returns).astype(float)

    out = (rv - bv).clip(lower=0.0)
    out.name = "jv"
    return out


def realized_semivariance(
    data: pd.DataFrame | pd.Series,
    *,
    price_col: str = "close",
    log_returns: bool = True,
) -> pd.DataFrame:
    price = get_price_series(data, price_col=price_col).astype(float)
    price = price.where(price > 0)

    if log_returns:
        rets = np.log(price).diff()
    else:
        rets = price.pct_change()

    sq = rets.pow(2)
    pos = sq.where(rets > 0, 0.0)
    neg = sq.where(rets < 0, 0.0)

    out = pd.DataFrame(index=price.index)
    out["rsv_pos"] = pos
    out["rsv_neg"] = neg
    return out


def signed_jump_variation(
    data: pd.DataFrame | pd.Series,
    *,
    price_col: str = "close",
    log_returns: bool = True,
) -> pd.DataFrame:
    rsv = realized_semivariance(data, price_col=price_col, log_returns=log_returns)
    bv = bipower_variation(data, price_col=price_col, log_returns=log_returns).astype(float)

    half_bv = bv / 2.0
    pos = (rsv["rsv_pos"].astype(float) - half_bv).clip(lower=0.0)
    neg = (rsv["rsv_neg"].astype(float) - half_bv).clip(lower=0.0)

    out = pd.DataFrame(index=rsv.index)
    out["signed_jump_pos"] = pos
    out["signed_jump_neg"] = neg
    return out


def minrv(
    data: pd.DataFrame | pd.Series,
    *,
    price_col: str = "close",
    log_returns: bool = True,
) -> pd.Series:
    price = get_price_series(data, price_col=price_col).astype(float)
    price = price.where(price > 0)

    if log_returns:
        rets = np.log(price).diff()
    else:
        rets = price.pct_change()

    abs_r = rets.abs()
    m = np.minimum(abs_r, abs_r.shift(1))
    out = (np.pi / (np.pi - 2.0)) * m.pow(2)
    out.name = "minrv"
    return out


def medrv(
    data: pd.DataFrame | pd.Series,
    *,
    price_col: str = "close",
    log_returns: bool = True,
) -> pd.Series:
    price = get_price_series(data, price_col=price_col).astype(float)
    price = price.where(price > 0)

    if log_returns:
        rets = np.log(price).diff()
    else:
        rets = price.pct_change()

    abs_r = rets.abs()
    med3 = abs_r.rolling(3).median()
    const = np.pi / (6.0 - 4.0 * np.sqrt(3.0) + np.pi)
    out = const * med3.pow(2)
    out.name = "medrv"
    return out


def realized_quarticity(
    data: pd.DataFrame | pd.Series,
    *,
    price_col: str = "close",
    log_returns: bool = True,
) -> pd.Series:
    price = get_price_series(data, price_col=price_col).astype(float)
    price = price.where(price > 0)

    if log_returns:
        rets = np.log(price).diff()
    else:
        rets = price.pct_change()

    out = rets.pow(4)
    out.name = "rq"
    return out


def harq_adjustment(
    data: pd.DataFrame | pd.Series,
    *,
    price_col: str = "close",
    window: int = 22,
    log_returns: bool = True,
) -> pd.Series:
    window = validate_positive_int(window, name="window")

    rv = realized_variance(data, price_col=price_col, log_returns=log_returns).astype(float)
    rq = realized_quarticity(data, price_col=price_col, log_returns=log_returns).astype(float)

    mean_rq = rq.rolling(window).mean()
    mean_rv = rv.rolling(window).mean()

    out = mean_rq / mean_rv.pow(2)
    out.name = f"harq_adjustment_{window}"
    return out


def shar_components(
    data: pd.DataFrame | pd.Series,
    *,
    price_col: str = "close",
    weekly_window: int = 5,
    monthly_window: int = 22,
    log_returns: bool = True,
) -> pd.DataFrame:
    weekly_window = validate_positive_int(weekly_window, name="weekly_window")
    monthly_window = validate_positive_int(monthly_window, name="monthly_window")

    rsv = realized_semivariance(data, price_col=price_col, log_returns=log_returns)
    pos = rsv["rsv_pos"].astype(float)
    neg = rsv["rsv_neg"].astype(float)

    out = pd.DataFrame(index=rsv.index)
    out["rsv_pos_d"] = pos
    out["rsv_neg_d"] = neg
    out["rsv_pos_w"] = pos.rolling(weekly_window).mean()
    out["rsv_neg_w"] = neg.rolling(weekly_window).mean()
    out["rsv_pos_m"] = pos.rolling(monthly_window).mean()
    out["rsv_neg_m"] = neg.rolling(monthly_window).mean()
    return out


def realized_roughness(
    data: pd.DataFrame | pd.Series,
    *,
    window: int = 60,
    lags: list[int] = [1, 2, 5, 10],
    price_col: str = "close",
) -> pd.Series:
    window = validate_positive_int(window, name="window")
    if not isinstance(lags, list) or not lags:
        raise TypeError("lags must be a non-empty list[int]")
    if not all(isinstance(l, int) for l in lags):
        raise TypeError("lags must be a list[int]")
    if not all(l > 0 for l in lags):
        raise ValueError("lags must contain only positive integers")

    lags_sorted = sorted(set(lags))
    x = np.log(np.asarray(lags_sorted, dtype=float))
    x_mat = np.column_stack([np.ones(len(x), dtype=float), x])

    rv = realized_variance(data, price_col=price_col).astype(float)
    log_rv = np.log(rv.where(rv > 0))

    roll_means: list[pd.Series] = []
    for lag in lags_sorted:
        d2 = (log_rv - log_rv.shift(lag)).pow(2)
        roll_means.append(d2.rolling(window).mean())

    means_df = pd.concat(roll_means, axis=1)
    means_df.columns = [str(l) for l in lags_sorted]

    n = len(means_df)
    out_arr = np.full(n, np.nan, dtype=float)

    for i in range(n):
        y = means_df.iloc[i].to_numpy(dtype=float)
        if not np.isfinite(y).all():
            continue
        if not (y > 0).all():
            continue

        y_log = np.log(y)
        beta, *_ = np.linalg.lstsq(x_mat, y_log, rcond=None)
        out_arr[i] = float(beta[1] / 2.0)

    out = pd.Series(out_arr, index=means_df.index)
    out.name = f"realized_roughness_{window}"
    return out


def log_volatility_increment(
    data: pd.DataFrame | pd.Series,
    *,
    window: int = 20,
    lag: int = 1,
    price_col: str = "close",
) -> pd.Series:
    window = validate_positive_int(window, name="window")
    lag = validate_positive_int(lag, name="lag")

    rv = realized_variance(data, price_col=price_col).astype(float)
    smoothed = rv.rolling(window).mean()

    log_v = np.log(smoothed.where(smoothed > 0))
    out = log_v - log_v.shift(lag)
    out.name = f"log_volatility_increment_{window}_{lag}"
    return out
