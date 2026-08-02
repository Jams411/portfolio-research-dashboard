"""Input validation and adjusted market-data retrieval."""

from __future__ import annotations

from datetime import date, datetime
from dataclasses import dataclass
from typing import Sequence

import numpy as np
import pandas as pd
import yfinance as yf

from .config import BENCHMARK_TICKER_ALIASES, MIN_OBSERVATIONS, WEIGHT_TOLERANCE


class InputError(ValueError):
    """Raised when an input cannot support a defensible analysis."""


class MarketDataError(RuntimeError):
    """Raised when requested market data are unavailable or incomplete."""


@dataclass(frozen=True)
class TickerResolution:
    """User-facing and provider-native symbols for one benchmark input."""

    display_symbol: str
    provider_symbol: str

    @property
    def was_mapped(self) -> bool:
        return self.display_symbol != self.provider_symbol

    @property
    def notice(self) -> str | None:
        if not self.was_mapped or self.display_symbol == "SPX":
            return None
        return f"{self.display_symbol} was mapped to Yahoo Finance symbol {self.provider_symbol}."


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


def resolve_benchmark_ticker(symbol: str) -> TickerResolution:
    """Resolve only an explicit benchmark alias; never guess equity symbols."""
    display = str(symbol).strip().upper()
    if not display:
        raise InputError("Enter exactly one benchmark ticker.")
    return TickerResolution(display, BENCHMARK_TICKER_ALIASES.get(display, display))


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


def parse_weight_input(
    tickers: Sequence[str], value: str, *, equal_weight: bool = False
) -> tuple[pd.Series, bool]:
    """Return validated portfolio weights from a UI percentage string or equal mode.

    Equal-weight mode deliberately ignores ``value`` and constructs decimal weights
    directly. Manual values may be percentage points (``50,35,15``) or decimals
    (``0.50,0.35,0.15``); conversion to decimals occurs exactly once in
    :func:`validate_weights`.
    """
    if not tickers:
        raise InputError("Enter at least one ticker symbol.")
    if equal_weight:
        return pd.Series(1.0 / len(tickers), index=list(tickers), dtype=float), False
    try:
        raw_weights = [float(item.strip()) for item in value.split(",") if item.strip()]
    except (AttributeError, ValueError) as exc:
        raise InputError("Weights must be comma-separated numeric values.") from exc
    return validate_weights(tickers, raw_weights)


def extract_adjusted_prices(raw: pd.DataFrame, tickers: Sequence[str]) -> pd.DataFrame:
    """Extract adjusted prices safely from either yfinance column layout."""
    if raw is None or raw.empty:
        raise MarketDataError(
            "The market-data provider returned no rows. "
            "Try a Yahoo Finance symbol such as ^GSPC for the S&P 500."
        )
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
        raise MarketDataError(
            "No usable history for: " + ", ".join(missing)
            + ". Check the symbols and date range. "
            "Try a Yahoo Finance symbol such as ^GSPC for the S&P 500."
        )
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
