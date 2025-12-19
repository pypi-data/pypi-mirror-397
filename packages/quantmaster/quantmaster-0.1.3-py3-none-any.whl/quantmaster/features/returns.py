from __future__ import annotations

import numpy as np
import pandas as pd

from quantmaster.features.utils import validate_columns


def overnight_gap(
    data: pd.DataFrame,
    *,
    open_col: str = "open",
    close_col: str = "close",
) -> pd.Series:
    validate_columns(data, required=(open_col, close_col))

    o = pd.to_numeric(data[open_col], errors="coerce").astype(float)
    c = pd.to_numeric(data[close_col], errors="coerce").astype(float)

    o = o.where(o > 0)
    c = c.where(c > 0)
    prev_c = c.shift(1)

    out = np.log(o / prev_c)
    out.name = "overnight_gap"
    return out


def intraday_return(
    data: pd.DataFrame,
    *,
    open_col: str = "open",
    close_col: str = "close",
) -> pd.Series:
    validate_columns(data, required=(open_col, close_col))

    o = pd.to_numeric(data[open_col], errors="coerce").astype(float)
    c = pd.to_numeric(data[close_col], errors="coerce").astype(float)

    o = o.where(o > 0)
    c = c.where(c > 0)

    out = np.log(c / o)
    out.name = "intraday_return"
    return out
