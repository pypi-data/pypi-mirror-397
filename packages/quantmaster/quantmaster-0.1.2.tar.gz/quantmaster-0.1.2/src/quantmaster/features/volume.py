from __future__ import annotations

import numpy as np
import pandas as pd

from quantmaster.features.utils import get_price_series, validate_columns, validate_positive_int


def rvol(
    data: pd.DataFrame | pd.Series,
    *,
    window: int = 30,
    volume_col: str = "volume",
) -> pd.Series:
    window = validate_positive_int(window, name="window")

    if isinstance(data, pd.Series):
        volume = pd.to_numeric(data, errors="coerce").astype(float)
    else:
        validate_columns(data, required=[volume_col])
        volume = pd.to_numeric(data[volume_col], errors="coerce").astype(float)

    rolling_mean = volume.rolling(window).mean()
    ratio = (volume / rolling_mean).where((volume > 0) & (rolling_mean > 0))

    out = np.log(ratio)
    out.name = f"rvol_{window}"
    return out


def price_volume_correlation(
    data: pd.DataFrame,
    *,
    window: int = 20,
    price_col: str = "close",
    volume_col: str = "volume",
    log_returns: bool = True,
) -> pd.Series:
    window = validate_positive_int(window, name="window")
    validate_columns(data, required=[price_col, volume_col])

    price = get_price_series(data, price_col=price_col).astype(float)
    volume = pd.to_numeric(data[volume_col], errors="coerce").astype(float)

    price = price.where(price > 0)
    volume = volume.where(volume > 0)

    if log_returns:
        rets = np.log(price).diff()
    else:
        rets = price.pct_change()

    vol_level = np.log(volume)
    out = rets.rolling(window).corr(vol_level)
    out.name = f"price_volume_correlation_{window}"
    return out


def volume_volatility_ratio(
    data: pd.DataFrame,
    *,
    window: int = 20,
    price_col: str = "close",
    volume_col: str = "volume",
    log_returns: bool = True,
) -> pd.Series:
    window = validate_positive_int(window, name="window")
    validate_columns(data, required=[price_col, volume_col])

    price = get_price_series(data, price_col=price_col).astype(float)
    volume = pd.to_numeric(data[volume_col], errors="coerce").astype(float)

    price = price.where(price > 0)
    volume = volume.where(volume > 0)

    if log_returns:
        rets = np.log(price).diff()
    else:
        rets = price.pct_change()

    vol = rets.rolling(window).std(ddof=1)
    vol_mean = volume.rolling(window).mean()

    ratio = (vol_mean / vol).where((vol_mean > 0) & (vol > 0))
    out = np.log(ratio)
    out.name = f"volume_volatility_ratio_{window}"
    return out


def close_location_value(
    data: pd.DataFrame,
    *,
    high_col: str = "high",
    low_col: str = "low",
    close_col: str = "close",
) -> pd.Series:
    validate_columns(data, required=[high_col, low_col, close_col])

    high = pd.to_numeric(data[high_col], errors="coerce").astype(float)
    low = pd.to_numeric(data[low_col], errors="coerce").astype(float)
    close = pd.to_numeric(data[close_col], errors="coerce").astype(float)

    denom = (high - low).where((high - low) != 0)
    out = ((close - low) - (high - close)) / denom
    out = out.clip(lower=-1.0, upper=1.0)
    out.name = "close_location_value"
    return out


def tick_imbalance_proxy(
    data: pd.DataFrame,
    *,
    window: int = 20,
    price_col: str = "close",
    log_returns: bool = True,
) -> pd.Series:
    window = validate_positive_int(window, name="window")
    validate_columns(data, required=[price_col])

    price = get_price_series(data, price_col=price_col).astype(float)
    price = price.where(price > 0)

    if log_returns:
        rets = np.log(price).diff()
    else:
        rets = price.pct_change()

    s = np.sign(rets)
    s = s.where(s != 0.0)
    out = s.rolling(window).mean()
    out = out.clip(lower=-1.0, upper=1.0)
    out.name = f"tick_imbalance_proxy_{window}"
    return out


def volume_weighted_close_location(
    data: pd.DataFrame,
    *,
    window: int = 20,
    high_col: str = "high",
    low_col: str = "low",
    close_col: str = "close",
    volume_col: str = "volume",
) -> pd.Series:
    window = validate_positive_int(window, name="window")
    validate_columns(data, required=[high_col, low_col, close_col, volume_col])

    clv = close_location_value(data, high_col=high_col, low_col=low_col, close_col=close_col)
    volume = pd.to_numeric(data[volume_col], errors="coerce").astype(float)
    volume = volume.where(volume > 0)

    num = (clv * volume).rolling(window).sum()
    den = volume.rolling(window).sum()
    out = (num / den.where(den > 0)).clip(lower=-1.0, upper=1.0)
    out.name = f"volume_weighted_close_location_{window}"
    return out


def order_flow_imbalance(
    data: pd.DataFrame,
    *,
    window: int = 20,
    price_col: str = "close",
    volume_col: str = "volume",
    log_returns: bool = True,
) -> pd.Series:
    window = validate_positive_int(window, name="window")
    validate_columns(data, required=[price_col, volume_col])

    price = get_price_series(data, price_col=price_col).astype(float)
    volume = pd.to_numeric(data[volume_col], errors="coerce").astype(float)

    price = price.where(price > 0)
    volume = volume.where(volume > 0)

    if log_returns:
        rets = np.log(price).diff()
    else:
        rets = price.pct_change()

    s = np.sign(rets)
    s = s.where(s != 0.0, 0.0)

    buy_sell = (volume * s).rolling(window).sum()
    total = volume.rolling(window).sum()
    out = (buy_sell / total.where(total > 0)).clip(lower=-1.0, upper=1.0)
    out.name = f"order_flow_imbalance_{window}"
    return out
