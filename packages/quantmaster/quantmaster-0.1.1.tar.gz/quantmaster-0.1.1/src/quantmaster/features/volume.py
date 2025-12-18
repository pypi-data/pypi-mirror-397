from __future__ import annotations

import numpy as np
import pandas as pd

from quantmaster.features.utils import validate_columns, validate_positive_int


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
