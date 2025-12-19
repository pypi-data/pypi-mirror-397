from __future__ import annotations

import numpy as np
import pandas as pd

from quantmaster.features.utils import get_price_series, validate_positive_int


def value_at_risk_historical(
    data: pd.DataFrame | pd.Series,
    *,
    window: int = 252,
    confidence: float = 0.95,
    price_col: str = "close",
    log_returns: bool = True,
) -> pd.Series:
    window = validate_positive_int(window, name="window")
    try:
        confidence = float(confidence)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"confidence must be float, got {type(confidence).__name__}") from exc
    if not (0.0 < confidence < 1.0):
        raise ValueError(f"confidence must be between 0 and 1, got {confidence}")

    price = get_price_series(data, price_col=price_col).astype(float)
    price = price.where(price > 0)

    if log_returns:
        rets = np.log(price).diff()
    else:
        rets = price.pct_change()

    alpha = 1.0 - confidence
    q = rets.rolling(window).quantile(alpha)
    out = (-q).clip(lower=0.0)
    out.name = f"value_at_risk_historical_{window}_{confidence:g}"
    return out


def _expected_shortfall_window(x: np.ndarray, *, alpha: float) -> float:
    x = x[np.isfinite(x)]
    if x.size < 2:
        return float("nan")
    q = float(np.quantile(x, alpha))
    tail = x[x <= q]
    if tail.size == 0:
        return float("nan")
    return float(-np.mean(tail))


def expected_shortfall(
    data: pd.DataFrame | pd.Series,
    *,
    window: int = 252,
    confidence: float = 0.95,
    price_col: str = "close",
    log_returns: bool = True,
) -> pd.Series:
    window = validate_positive_int(window, name="window")
    try:
        confidence = float(confidence)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"confidence must be float, got {type(confidence).__name__}") from exc
    if not (0.0 < confidence < 1.0):
        raise ValueError(f"confidence must be between 0 and 1, got {confidence}")

    price = get_price_series(data, price_col=price_col).astype(float)
    price = price.where(price > 0)

    if log_returns:
        rets = np.log(price).diff()
    else:
        rets = price.pct_change()

    alpha = 1.0 - confidence
    out = rets.rolling(window).apply(lambda x: _expected_shortfall_window(x, alpha=alpha), raw=True)
    out = out.clip(lower=0.0)
    out.name = f"expected_shortfall_{window}_{confidence:g}"
    return out


def _tail_risk_measure_window(x: np.ndarray, *, quantile: float) -> float:
    x = x[np.isfinite(x)]
    if x.size < 2:
        return float("nan")
    q = float(np.quantile(x, quantile))
    if q == 0.0 or not np.isfinite(q):
        return float("nan")
    tail = x[x <= q]
    if tail.size == 0:
        return float("nan")
    tail_mean = float(np.mean(tail))
    return float(tail_mean / q)


def tail_risk_measure(
    data: pd.DataFrame | pd.Series,
    *,
    window: int = 60,
    quantile: float = 0.05,
    price_col: str = "close",
    log_returns: bool = True,
) -> pd.Series:
    window = validate_positive_int(window, name="window")
    try:
        quantile = float(quantile)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"quantile must be float, got {type(quantile).__name__}") from exc
    if not (0.0 < quantile < 1.0):
        raise ValueError(f"quantile must be between 0 and 1, got {quantile}")

    price = get_price_series(data, price_col=price_col).astype(float)
    price = price.where(price > 0)

    if log_returns:
        rets = np.log(price).diff()
    else:
        rets = price.pct_change()

    out = rets.rolling(window).apply(lambda x: _tail_risk_measure_window(x, quantile=quantile), raw=True)
    out.name = f"tail_risk_measure_{window}_{quantile:g}"
    return out


def _max_consecutive_true(mask: np.ndarray) -> int:
    best = 0
    cur = 0
    for v in mask.tolist():
        if v:
            cur += 1
            if cur > best:
                best = cur
        else:
            cur = 0
    return best


def _max_drawdown_duration_window(x: np.ndarray) -> float:
    x = x[np.isfinite(x)]
    if x.size < 2:
        return float("nan")
    peaks = np.maximum.accumulate(x)
    dd = x / peaks - 1.0
    underwater = dd < 0.0
    return float(_max_consecutive_true(underwater))


def max_drawdown_duration(
    data: pd.DataFrame | pd.Series,
    *,
    window: int = 252,
    price_col: str = "close",
) -> pd.Series:
    window = validate_positive_int(window, name="window")

    price = get_price_series(data, price_col=price_col).astype(float)
    price = price.where(price > 0)

    out = price.rolling(window).apply(_max_drawdown_duration_window, raw=True)
    out.name = f"max_drawdown_duration_{window}"
    return out
