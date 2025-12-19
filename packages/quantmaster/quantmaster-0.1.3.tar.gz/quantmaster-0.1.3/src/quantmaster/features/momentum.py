from __future__ import annotations

import numpy as np
import pandas as pd

from quantmaster.features.utils import get_price_series, validate_positive_int


def rsi(
    data: pd.DataFrame | pd.Series,
    *,
    window: int = 14,
    price_col: str = "close",
) -> pd.Series:
    window = validate_positive_int(window, name="window")

    price = get_price_series(data, price_col=price_col).astype(float)

    delta = price.diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)

    avg_gain = gain.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()
    avg_loss = loss.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()

    rs = avg_gain / avg_loss
    out = 100 - (100 / (1 + rs))

    out = out.where(avg_loss != 0, 100.0)
    out = out.where(avg_gain != 0, 0.0)

    out.name = f"rsi_{window}"
    return out


def time_series_momentum(
    data: pd.DataFrame | pd.Series,
    *,
    lookback: int = 252,
    volatility_window: int = 60,
    price_col: str = "close",
) -> pd.Series:
    lookback = validate_positive_int(lookback, name="lookback")
    volatility_window = validate_positive_int(volatility_window, name="volatility_window")

    price = get_price_series(data, price_col=price_col).astype(float)
    price = price.where(price > 0)

    log_p = np.log(price)
    r_total = log_p.diff(lookback)

    daily = log_p.diff()
    sigma = daily.rolling(volatility_window).std(ddof=1)

    out = r_total / sigma.where(sigma > 0)
    out.name = f"time_series_momentum_{lookback}_{volatility_window}"
    return out


def chande_momentum_oscillator(
    data: pd.DataFrame | pd.Series,
    *,
    window: int = 14,
    price_col: str = "close",
) -> pd.Series:
    window = validate_positive_int(window, name="window")

    price = get_price_series(data, price_col=price_col).astype(float)
    delta = price.diff()

    gain = delta.clip(lower=0.0)
    loss = (-delta).clip(lower=0.0)

    sum_gain = gain.rolling(window).sum()
    sum_loss = loss.rolling(window).sum()

    denom = sum_gain + sum_loss
    out = 100.0 * (sum_gain - sum_loss) / denom.where(denom > 0)
    out = out.clip(lower=-100.0, upper=100.0)
    out.name = f"chande_momentum_oscillator_{window}"
    return out
