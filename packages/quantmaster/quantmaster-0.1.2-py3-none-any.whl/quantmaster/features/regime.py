from __future__ import annotations

import numpy as np
import pandas as pd

from quantmaster.features.utils import get_price_series, validate_positive_int


def cusum_statistic(
    data: pd.DataFrame | pd.Series,
    *,
    window: int = 60,
    price_col: str = "close",
) -> pd.Series:
    window = validate_positive_int(window, name="window")

    price = get_price_series(data, price_col=price_col).astype(float)
    price = price.where(price > 0)
    rets = np.log(price).diff()

    mu = rets.rolling(window).mean()
    sigma = rets.rolling(window).std(ddof=1)

    z = (rets - mu) / sigma.where(sigma > 0)
    out = z.rolling(window).sum()
    out.name = f"cusum_statistic_{window}"
    return out


def variance_ratio(
    data: pd.DataFrame | pd.Series,
    *,
    window: int = 120,
    holding_period: int = 5,
    price_col: str = "close",
) -> pd.Series:
    window = validate_positive_int(window, name="window")
    holding_period = validate_positive_int(holding_period, name="holding_period")

    price = get_price_series(data, price_col=price_col).astype(float)
    price = price.where(price > 0)
    r1 = np.log(price).diff()
    rq = np.log(price).diff(holding_period)

    var_1 = r1.rolling(window).var(ddof=1)
    var_q = rq.rolling(window).var(ddof=1)

    denom = float(holding_period) * var_1
    out = var_q / denom.where(denom != 0)
    out.name = f"variance_ratio_{window}_{holding_period}"
    return out


def market_efficiency_index(
    data: pd.DataFrame | pd.Series,
    *,
    window: int = 60,
    holding_period: int = 5,
    price_col: str = "close",
) -> pd.Series:
    window = validate_positive_int(window, name="window")
    holding_period = validate_positive_int(holding_period, name="holding_period")

    price = get_price_series(data, price_col=price_col).astype(float)
    price = price.where(price > 0)
    rets = np.log(price).diff()

    ac1 = rets.rolling(window).corr(rets.shift(1))
    vr = variance_ratio(data, window=window, holding_period=holding_period, price_col=price_col)

    out = 1.0 - ac1.abs() - 0.5 * (vr - 1.0).abs()
    out.name = f"market_efficiency_index_{window}_{holding_period}"
    return out


def _runs_z_statistic(x: np.ndarray) -> float:
    x = x[np.isfinite(x)]
    if x.size < 2:
        return float("nan")

    n1 = int(np.sum(x > 0))
    n2 = int(np.sum(x < 0))
    n = n1 + n2
    if n < 2 or n1 == 0 or n2 == 0:
        return float("nan")

    runs = int(1 + np.sum(x[1:] != x[:-1]))

    mu = (2.0 * n1 * n2) / n + 1.0
    numer = 2.0 * n1 * n2 * (2.0 * n1 * n2 - n1 - n2)
    denom = float(n * n * (n - 1))
    if denom <= 0.0:
        return float("nan")

    var = numer / denom
    if var <= 0.0:
        return float("nan")

    return float((runs - mu) / np.sqrt(var))


def runs_test_statistic(
    data: pd.DataFrame | pd.Series,
    *,
    window: int = 60,
    price_col: str = "close",
) -> pd.Series:
    window = validate_positive_int(window, name="window")

    price = get_price_series(data, price_col=price_col).astype(float)
    price = price.where(price > 0)
    rets = np.log(price).diff()

    signs = np.sign(rets)
    signs = signs.replace(0.0, np.nan)

    out = signs.rolling(window).apply(_runs_z_statistic, raw=True)
    out.name = f"runs_test_statistic_{window}"
    return out
