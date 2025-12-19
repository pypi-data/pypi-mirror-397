from __future__ import annotations

import numpy as np
import pandas as pd

from quantmaster.features.utils import get_price_series, validate_columns, validate_positive_int


def trend_intensity(
    data: pd.DataFrame | pd.Series,
    *,
    window: int = 20,
    price_col: str = "close",
) -> pd.Series:
    window = validate_positive_int(window, name="window")

    price = get_price_series(data, price_col=price_col).astype(float)
    price = price.where(price > 0)
    rets = np.log(price).diff()

    num = rets.rolling(window).sum().abs()
    denom = rets.abs().rolling(window).sum()

    out = num / denom.where(denom > 0)
    out.name = f"trend_intensity_{window}"
    return out


def kaufman_efficiency_ratio(
    data: pd.DataFrame | pd.Series,
    *,
    window: int = 10,
    price_col: str = "close",
) -> pd.Series:
    window = validate_positive_int(window, name="window")

    price = get_price_series(data, price_col=price_col).astype(float)

    change = (price - price.shift(window)).abs()
    volatility = price.diff().abs().rolling(window).sum()

    out = change / volatility.where(volatility > 0)
    out.name = f"kaufman_efficiency_ratio_{window}"
    return out


def price_acceleration(
    data: pd.DataFrame | pd.Series,
    *,
    window: int = 20,
    price_col: str = "close",
) -> pd.Series:
    window = validate_positive_int(window, name="window")

    price = get_price_series(data, price_col=price_col).astype(float)
    price = price.where(price > 0)
    rets = np.log(price).diff()

    out = (rets - rets.shift(window)) / float(window)
    out.name = f"price_acceleration_{window}"
    return out


def trend_strength_indicator(
    data: pd.DataFrame | pd.Series,
    *,
    windows: list[int] = [21, 63, 126, 252],
    price_col: str = "close",
) -> pd.Series:
    if not isinstance(windows, list) or not windows:
        raise TypeError("windows must be a non-empty list[int]")
    if not all(isinstance(w, int) for w in windows):
        raise TypeError("windows must be a list[int]")
    if not all(w > 0 for w in windows):
        raise ValueError("windows must contain only positive integers")

    uniq = sorted(set(windows))

    price = get_price_series(data, price_col=price_col).astype(float)
    price = price.where(price > 0)
    log_p = np.log(price)

    daily = log_p.diff()
    signals: list[pd.Series] = []
    for w in uniq:
        w = validate_positive_int(w, name="window")
        r = log_p.diff(w)
        sigma = daily.rolling(w).std(ddof=1) * np.sqrt(float(w))
        scaled = r / sigma.where(sigma > 0)
        s = np.sign(r) * scaled.abs().clip(upper=2.0)
        signals.append(s)

    df = pd.concat(signals, axis=1)
    out = df.mean(axis=1)
    out.name = "trend_strength_indicator_" + "_".join(str(w) for w in uniq)
    return out


def trend_strength_autocorr(
    data: pd.DataFrame | pd.Series,
    *,
    window: int = 60,
    lag: int = 1,
    price_col: str = "close",
) -> pd.Series:
    window = validate_positive_int(window, name="window")
    lag = validate_positive_int(lag, name="lag")

    price = get_price_series(data, price_col=price_col).astype(float)
    price = price.where(price > 0)
    rets = np.log(price).diff()

    out = rets.rolling(window).corr(rets.shift(lag))
    out.name = f"trend_strength_autocorr_{window}_{lag}"
    return out


def bar_range_position(
    data: pd.DataFrame,
    *,
    open_col: str = "open",
    high_col: str = "high",
    low_col: str = "low",
    close_col: str = "close",
) -> pd.Series:
    validate_columns(data, required=[open_col, high_col, low_col, close_col])

    o = pd.to_numeric(data[open_col], errors="coerce").astype(float)
    h = pd.to_numeric(data[high_col], errors="coerce").astype(float)
    l = pd.to_numeric(data[low_col], errors="coerce").astype(float)
    c = pd.to_numeric(data[close_col], errors="coerce").astype(float)

    rng = h - l
    out = (c - l) / rng.where(rng != 0)
    out = out.where(rng != 0, 0.5)
    out = out.clip(lower=0.0, upper=1.0)
    out.name = "bar_range_position"
    return out


def body_to_range_ratio(
    data: pd.DataFrame,
    *,
    open_col: str = "open",
    high_col: str = "high",
    low_col: str = "low",
    close_col: str = "close",
) -> pd.Series:
    validate_columns(data, required=[open_col, high_col, low_col, close_col])

    o = pd.to_numeric(data[open_col], errors="coerce").astype(float)
    h = pd.to_numeric(data[high_col], errors="coerce").astype(float)
    l = pd.to_numeric(data[low_col], errors="coerce").astype(float)
    c = pd.to_numeric(data[close_col], errors="coerce").astype(float)

    rng = h - l
    out = (c - o).abs() / rng.where(rng != 0)
    out = out.where(rng != 0, 0.0)
    out = out.clip(lower=0.0, upper=1.0)
    out.name = "body_to_range_ratio"
    return out


def upper_shadow_ratio(
    data: pd.DataFrame,
    *,
    open_col: str = "open",
    high_col: str = "high",
    low_col: str = "low",
    close_col: str = "close",
) -> pd.Series:
    validate_columns(data, required=[open_col, high_col, low_col, close_col])

    o = pd.to_numeric(data[open_col], errors="coerce").astype(float)
    h = pd.to_numeric(data[high_col], errors="coerce").astype(float)
    l = pd.to_numeric(data[low_col], errors="coerce").astype(float)
    c = pd.to_numeric(data[close_col], errors="coerce").astype(float)

    rng = h - l
    top_body = np.maximum(o, c)
    out = (h - top_body) / rng.where(rng != 0)
    out = out.where(rng != 0, 0.0)
    out = out.clip(lower=0.0, upper=1.0)
    out.name = "upper_shadow_ratio"
    return out


def lower_shadow_ratio(
    data: pd.DataFrame,
    *,
    open_col: str = "open",
    high_col: str = "high",
    low_col: str = "low",
    close_col: str = "close",
) -> pd.Series:
    validate_columns(data, required=[open_col, high_col, low_col, close_col])

    o = pd.to_numeric(data[open_col], errors="coerce").astype(float)
    h = pd.to_numeric(data[high_col], errors="coerce").astype(float)
    l = pd.to_numeric(data[low_col], errors="coerce").astype(float)
    c = pd.to_numeric(data[close_col], errors="coerce").astype(float)

    rng = h - l
    bot_body = np.minimum(o, c)
    out = (bot_body - l) / rng.where(rng != 0)
    out = out.where(rng != 0, 0.0)
    out = out.clip(lower=0.0, upper=1.0)
    out.name = "lower_shadow_ratio"
    return out
