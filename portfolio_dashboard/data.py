"""Input validation and adjusted market-data retrieval."""

from __future__ import annotations

from datetime import date, datetime
from typing import Sequence

import numpy as np
import pandas as pd
import yfinance as yf

from .config import MIN_OBSERVATIONS, WEIGHT_TOLERANCE


class InputError(ValueError):
    """Raised when an input cannot support a defensible analysis."""


class MarketDataError(RuntimeError):
    """Raised when requested market data are unavailable or incomplete."""


def parse_tickers(value: str | Sequence[str]) -> list[str]:
    """Normalize comma-separated symbols, preserving order and removing duplicates."""
    raw = value.split(",") if isinstance(value, str) else list(value or [])
    result: list[str] = []
    for item in raw:
        symbol = str(item).strip().upper()
        if symbol and symbol not in result:
            result.append(symbol)
    if not result:
        raise InputError("Enter at least one ticker symbol.")
    return result


def validate_dates(start: date | datetime | str, end: date | datetime | str) -> tuple[pd.Timestamp, pd.Timestamp]:
    """Return validated timestamps with start strictly before end."""
    try:
        start_ts, end_ts = pd.Timestamp(start), pd.Timestamp(end)
    except (TypeError, ValueError) as exc:
        raise InputError("Start and end dates must be valid dates.") from exc
    if pd.isna(start_ts) or pd.isna(end_ts) or start_ts >= end_ts:
        raise InputError("Start date must be earlier than end date.")
    return start_ts, end_ts


def validate_weights(
    tickers: Sequence[str], weights: Sequence[float], *, normalize: bool = False
) -> tuple[pd.Series, bool]:
    """Validate long-only weights and optionally normalize an approximate total.

    Returns the weight Series and whether normalization was applied. Values may be
    supplied as percentages (for example 60, 40) or decimals (0.6, 0.4).
    """
    if len(weights) != len(tickers):
        raise InputError(f"Enter exactly {len(tickers)} weights, one for each ticker.")
    try:
        series = pd.Series(weights, index=list(tickers), dtype=float)
    except (TypeError, ValueError) as exc:
        raise InputError("Weights must be numeric.") from exc
    if not np.isfinite(series).all() or (series < 0).any():
        raise InputError("Weights must be finite and nonnegative.")
    total = float(series.sum())
    if total > 1.5:
        series = series / 100.0
        total /= 100.0
    if total <= 0:
        raise InputError("At least one weight must be positive.")
    difference = abs(total - 1.0)
    if difference <= WEIGHT_TOLERANCE:
        normalized = difference > 1e-12
        return series / total, normalized
    if normalize:
        return series / total, True
    raise InputError(f"Weights sum to {total:.2%}; they must sum to approximately 100%.")


def extract_adjusted_prices(raw: pd.DataFrame, tickers: Sequence[str]) -> pd.DataFrame:
    """Extract adjusted prices safely from either yfinance column layout."""
    if raw is None or raw.empty:
        raise MarketDataError("The market-data provider returned no rows.")
    if isinstance(raw.columns, pd.MultiIndex):
        for field in ("Adj Close", "Close"):
            for level in range(raw.columns.nlevels):
                if field in raw.columns.get_level_values(level):
                    prices = raw.xs(field, axis=1, level=level, drop_level=True)
                    break
            else:
                continue
            break
        else:
            raise MarketDataError("Downloaded data contain no adjusted or close prices.")
        if isinstance(prices, pd.Series):
            prices = prices.to_frame(name=tickers[0])
    else:
        field = "Adj Close" if "Adj Close" in raw.columns else "Close" if "Close" in raw.columns else None
        if field is None:
            raise MarketDataError("Downloaded data contain no adjusted or close prices.")
        prices = raw[[field]].rename(columns={field: tickers[0]})
    prices.columns = [str(c).upper() for c in prices.columns]
    return prices


def align_prices(prices: pd.DataFrame, tickers: Sequence[str], min_observations: int = MIN_OBSERVATIONS) -> pd.DataFrame:
    """Align assets on complete common dates without filling or inventing prices."""
    missing = [ticker for ticker in tickers if ticker not in prices.columns or prices[ticker].dropna().empty]
    if missing:
        raise MarketDataError("No usable history for: " + ", ".join(missing) + ". Check the symbols and date range.")
    aligned = prices.loc[:, list(tickers)].sort_index().replace([np.inf, -np.inf], np.nan).dropna(how="any")
    if len(aligned) < min_observations:
        raise MarketDataError(
            f"Only {len(aligned)} common price observations are available; at least {min_observations} are required."
        )
    return aligned.astype(float)


def download_prices(tickers: Sequence[str], start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    """Download and align adjusted prices; fail if any requested asset is missing."""
    try:
        raw = yf.download(list(tickers), start=start, end=end, auto_adjust=False, progress=False, threads=True)
    except Exception as exc:
        raise MarketDataError(f"Market-data download failed: {exc}") from exc
    return align_prices(extract_adjusted_prices(raw, tickers), tickers)
