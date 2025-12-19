from __future__ import annotations

import inspect
import warnings
from collections.abc import Iterable

import pandas as pd

DEFAULT_OHLCV_COLUMNS: tuple[str, ...] = ("open", "high", "low", "close", "volume")

DEFAULT_CREATE_ALL_EXCLUDE: set[str] = {"create_all", "har_rv_forecast"}


def validate_positive_int(value: int, *, name: str) -> int:
    if not isinstance(value, int):
        raise TypeError(f"{name} must be int, got {type(value).__name__}")
    if value < 1:
        raise ValueError(f"{name} must be >= 1, got {value}")
    return value


def validate_non_negative_int(value: int, *, name: str) -> int:
    if not isinstance(value, int):
        raise TypeError(f"{name} must be int, got {type(value).__name__}")
    if value < 0:
        raise ValueError(f"{name} must be >= 0, got {value}")
    return value


def validate_columns(data: pd.DataFrame, *, required: Iterable[str]) -> None:
    missing = [c for c in required if c not in data.columns]
    if missing:
        raise KeyError(f"Missing required columns: {missing}")


def validate_ohlcv(data: pd.DataFrame, *, required: Iterable[str] = DEFAULT_OHLCV_COLUMNS) -> None:
    validate_columns(data, required=required)


def get_price_series(data: pd.DataFrame | pd.Series, *, price_col: str = "close") -> pd.Series:
    if isinstance(data, pd.Series):
        series = data
    else:
        if price_col not in data.columns:
            raise KeyError(f"Column '{price_col}' not found in DataFrame")
        series = data[price_col]

    return pd.to_numeric(series, errors="coerce")


def create_all(
    data: pd.DataFrame,
    *,
    benchmark: pd.Series | None = None,
    inplace: bool = False,
    overwrite: bool = False,
    include: Iterable[str] | None = None,
    exclude: Iterable[str] | None = None,
    errors: str = "ignore",
) -> pd.DataFrame:
    if not isinstance(data, pd.DataFrame):
        raise TypeError(f"data must be a pandas.DataFrame, got {type(data).__name__}")
    if errors not in {"ignore", "warn", "raise"}:
        raise ValueError(f"errors must be one of 'ignore', 'warn', 'raise', got {errors!r}")

    if inplace:
        out_df = data
    else:
        out_df = data.copy()

    include_set = set(include) if include is not None else None
    exclude_set = set(exclude) if exclude is not None else set()
    exclude_set |= DEFAULT_CREATE_ALL_EXCLUDE

    from quantmaster import features as _features

    names = [n for n in getattr(_features, "__all__", []) if isinstance(n, str)]

    for name in names:
        if include_set is not None and name not in include_set:
            continue
        if name in exclude_set:
            continue

        fn = getattr(_features, name, None)
        if not callable(fn):
            continue

        try:
            sig = inspect.signature(fn)
        except (TypeError, ValueError):
            continue

        params = sig.parameters
        kwargs: dict[str, object] = {}
        if "benchmark" in params:
            p = params["benchmark"]
            if benchmark is None and p.default is inspect._empty:
                continue
            if benchmark is not None:
                kwargs["benchmark"] = benchmark

        try:
            res = fn(out_df, **kwargs)
        except Exception as exc:
            if errors == "raise":
                raise
            if errors == "warn":
                warnings.warn(f"create_all skipped '{name}': {exc}", RuntimeWarning)
            continue

        if isinstance(res, pd.Series):
            col = res.name or name
            if (not overwrite) and (col in out_df.columns):
                continue
            out_df[col] = res
            continue

        if isinstance(res, pd.DataFrame):
            for c in res.columns:
                if (not overwrite) and (c in out_df.columns):
                    continue
                out_df[c] = res[c]
            continue

        if errors == "raise":
            raise TypeError(f"Feature '{name}' returned unsupported type {type(res).__name__}")
        if errors == "warn":
            warnings.warn(
                f"create_all skipped '{name}': unsupported return type {type(res).__name__}",
                RuntimeWarning,
            )

    return out_df
