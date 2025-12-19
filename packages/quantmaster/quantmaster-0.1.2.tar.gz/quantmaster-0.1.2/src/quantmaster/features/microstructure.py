from __future__ import annotations

import numpy as np
import pandas as pd

from quantmaster.features.utils import get_price_series, validate_columns, validate_positive_int


def amihud_illiquidity(
    data: pd.DataFrame | pd.Series,
    *,
    window: int = 20,
    price_col: str = "close",
    volume_col: str = "volume",
    log_returns: bool = True,
) -> pd.Series:
    window = validate_positive_int(window, name="window")

    if isinstance(data, pd.Series):
        raise TypeError("amihud_illiquidity requires a DataFrame with price and volume")

    validate_columns(data, required=(price_col, volume_col))

    price = get_price_series(data, price_col=price_col).astype(float)
    volume = pd.to_numeric(data[volume_col], errors="coerce").astype(float)

    price = price.where(price > 0)
    volume = volume.where(volume > 0)

    if log_returns:
        rets = np.log(price).diff()
    else:
        rets = price.pct_change()

    dollar_volume = price * volume
    ratio = rets.abs() / dollar_volume
    ratio = ratio.where(dollar_volume > 0)

    out = ratio.rolling(window).mean()
    out.name = f"amihud_illiquidity_{window}"
    return out


def roll_spread(
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

    cov = rets.rolling(window).cov(rets.shift(1))
    spread = 2.0 * np.sqrt((-cov).clip(lower=0.0))
    spread = spread.where(np.isfinite(cov))

    spread.name = f"roll_spread_{window}"
    return spread


def corwin_schultz_spread(
    data: pd.DataFrame,
    *,
    window: int = 20,
    high_col: str = "high",
    low_col: str = "low",
    close_col: str = "close",
) -> pd.Series:
    window = validate_positive_int(window, name="window")
    validate_columns(data, required=(high_col, low_col, close_col))

    h = pd.to_numeric(data[high_col], errors="coerce").astype(float)
    l = pd.to_numeric(data[low_col], errors="coerce").astype(float)
    c = pd.to_numeric(data[close_col], errors="coerce").astype(float)

    h = h.where(h > 0)
    l = l.where(l > 0)
    c = c.where(c > 0)

    prev_c = c.shift(1)

    gap_up = l - prev_c
    gap_down = h - prev_c

    high_adj = h.copy()
    low_adj = l.copy()

    high_adj = np.where(gap_up > 0, h - gap_up, high_adj)
    low_adj = np.where(gap_up > 0, l - gap_up, low_adj)
    high_adj = np.where(gap_down < 0, h - gap_down, high_adj)
    low_adj = np.where(gap_down < 0, l - gap_down, low_adj)

    high_adj = pd.Series(high_adj, index=data.index, dtype=float)
    low_adj = pd.Series(low_adj, index=data.index, dtype=float)
    high_adj = high_adj.where(high_adj > 0)
    low_adj = low_adj.where(low_adj > 0)

    high_2d = h.rolling(2).max()
    low_2d = l.rolling(2).min()

    beta = np.log(high_adj / low_adj).pow(2) + np.log(high_adj.shift(1) / low_adj.shift(1)).pow(2)
    gamma = np.log(high_2d / low_2d).pow(2)

    k = 3.0 - 2.0 * np.sqrt(2.0)
    alpha = ((np.sqrt(2.0 * beta) - np.sqrt(beta)) / k) - np.sqrt(gamma / k)
    alpha = alpha.clip(lower=0.0)

    spread_daily = (2.0 * (np.exp(alpha) - 1.0)) / (1.0 + np.exp(alpha))

    out = spread_daily if window == 1 else spread_daily.rolling(window).mean()
    out.name = f"corwin_schultz_spread_{window}"
    return out


def relative_spread_proxy(
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

    term = (h - c) * (h - o) + (l - c) * (l - o)
    term_mean = term.rolling(window).mean()

    spread_abs = 2.0 * np.sqrt(term_mean.clip(lower=0.0))
    out = spread_abs / c
    out = out.where(c > 0)

    out.name = f"relative_spread_proxy_{window}"
    return out
