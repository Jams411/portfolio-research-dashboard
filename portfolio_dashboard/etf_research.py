"""Deterministic ETF research, holdings look-through, and security screening tools."""
from __future__ import annotations

from io import BytesIO
from itertools import combinations

import numpy as np
import pandas as pd

from .config import TRADING_DAYS
from .performance import drawdown_series


HOLDINGS_COLUMNS = ("ETF", "Security", "Holding Weight")


def etf_research_metrics(
    returns: pd.DataFrame,
    risk_free_rate: float = 0.0,
    periods_per_year: int = TRADING_DAYS,
) -> pd.DataFrame:
    """Calculate comparable historical arithmetic risk/return metrics by security."""
    if returns.empty:
        return pd.DataFrame(columns=[
            "Observations", "Historical Arithmetic Return", "Volatility", "Sharpe Ratio",
            "Cumulative Return", "Maximum Drawdown",
        ])
    rows: dict[str, dict[str, float]] = {}
    for symbol in returns.columns:
        series = returns[symbol].dropna()
        observations = len(series)
        annual_return = float(series.mean() * periods_per_year) if observations else np.nan
        volatility = float(series.std(ddof=1) * np.sqrt(periods_per_year)) if observations >= 2 else np.nan
        rows[str(symbol)] = {
            "Observations": float(observations),
            "Historical Arithmetic Return": annual_return,
            "Volatility": volatility,
            "Sharpe Ratio": (
                (annual_return - risk_free_rate) / volatility
                if np.isfinite(volatility) and volatility > 0 else np.nan
            ),
            "Cumulative Return": float((1.0 + series).prod() - 1.0) if observations else np.nan,
            "Maximum Drawdown": float(drawdown_series(series).min()) if observations else np.nan,
        }
    return pd.DataFrame.from_dict(rows, orient="index").rename_axis("Symbol")


def filter_etf_research(
    metrics: pd.DataFrame,
    min_observations: int = 60,
    min_sharpe: float = 0.5,
    max_volatility: float = 0.25,
) -> pd.DataFrame:
    """Apply explicit, reproducible history, Sharpe, and volatility filters."""
    required = {"Observations", "Sharpe Ratio", "Volatility"}
    missing = required.difference(metrics.columns)
    if missing:
        raise ValueError(f"ETF metrics are missing columns: {', '.join(sorted(missing))}.")
    mask = (
        (metrics["Observations"] >= min_observations)
        & (metrics["Sharpe Ratio"] >= min_sharpe)
        & (metrics["Volatility"] <= max_volatility)
    )
    return metrics.loc[mask].sort_values(["Sharpe Ratio", "Volatility"], ascending=[False, True])


def parse_holdings_csv(content: bytes) -> pd.DataFrame:
    """Parse and validate a local holdings CSV without any network dependency."""
    if not content:
        raise ValueError("The holdings file is empty.")
    try:
        frame = pd.read_csv(BytesIO(content))
    except Exception as exc:  # pandas supplies the useful parser detail
        raise ValueError(f"The holdings CSV could not be parsed: {exc}") from exc
    return normalize_holdings(frame)


def normalize_holdings(frame: pd.DataFrame) -> pd.DataFrame:
    """Normalize tickers, weight units, and duplicate ETF/security rows.

    Decimal and percentage weights are accepted. Each ETF may sum to less than 100%
    when a source omits cash or minor holdings, but totals above 100% are rejected.
    """
    missing = set(HOLDINGS_COLUMNS).difference(frame.columns)
    if missing:
        raise ValueError(f"Holdings data are missing columns: {', '.join(sorted(missing))}.")
    clean = frame.loc[:, HOLDINGS_COLUMNS].copy()
    clean["ETF"] = clean["ETF"].astype(str).str.strip().str.upper()
    clean["Security"] = clean["Security"].astype(str).str.strip().str.upper()
    clean["Holding Weight"] = pd.to_numeric(clean["Holding Weight"], errors="coerce")
    invalid = (
        clean["ETF"].isin(["", "NAN"]) | clean["Security"].isin(["", "NAN"])
        | clean["Holding Weight"].isna() | (clean["Holding Weight"] < 0)
    )
    if invalid.any():
        raise ValueError("Holdings rows require non-empty ETF/security labels and non-negative numeric weights.")
    if clean.empty:
        raise ValueError("The holdings table contains no rows.")
    if clean["Holding Weight"].max() > 1.0:
        clean["Holding Weight"] = clean["Holding Weight"] / 100.0
    clean = clean.groupby(["ETF", "Security"], as_index=False, sort=True)["Holding Weight"].sum()
    totals = clean.groupby("ETF")["Holding Weight"].sum()
    breached = totals[totals > 1.000001]
    if not breached.empty:
        labels = ", ".join(f"{symbol} ({value:.2%})" for symbol, value in breached.items())
        raise ValueError(f"Holding weights exceed 100% for: {labels}.")
    return clean


def holdings_coverage(holdings: pd.DataFrame) -> pd.DataFrame:
    """Summarize disclosed holding weight and security count by ETF."""
    return holdings.groupby("ETF").agg(
        **{"Disclosed Weight": ("Holding Weight", "sum"), "Securities": ("Security", "nunique")}
    )


def consolidated_security_exposure(
    holdings: pd.DataFrame,
    etf_allocations: pd.Series,
) -> pd.DataFrame:
    """Look through ETF allocations to aggregate underlying security exposure."""
    allocations = etf_allocations.copy().astype(float)
    allocations.index = allocations.index.astype(str).str.strip().str.upper()
    if (allocations < 0).any() or allocations.sum() <= 0:
        raise ValueError("ETF allocations must be non-negative and have a positive total.")
    allocations = allocations / allocations.sum()
    merged = holdings.merge(allocations.rename("ETF Allocation"), left_on="ETF", right_index=True, how="left")
    merged["ETF Allocation"] = merged["ETF Allocation"].fillna(0.0)
    merged["Portfolio Exposure"] = merged["ETF Allocation"] * merged["Holding Weight"]
    return (
        merged.groupby("Security", as_index=True)["Portfolio Exposure"].sum()
        .sort_values(ascending=False).to_frame()
    )


def etf_overlap(holdings: pd.DataFrame) -> pd.DataFrame:
    """Return pairwise constituent and weight-overlap diagnostics."""
    rows = []
    indexed = {name: group.set_index("Security")["Holding Weight"] for name, group in holdings.groupby("ETF")}
    for left, right in combinations(sorted(indexed), 2):
        left_weights, right_weights = indexed[left], indexed[right]
        securities = left_weights.index.union(right_weights.index)
        shared = left_weights.index.intersection(right_weights.index)
        rows.append({
            "ETF 1": left,
            "ETF 2": right,
            "Shared Securities": len(shared),
            "Constituent Jaccard": len(shared) / len(securities) if len(securities) else np.nan,
            "Weighted Overlap": float(np.minimum(
                left_weights.reindex(securities, fill_value=0.0),
                right_weights.reindex(securities, fill_value=0.0),
            ).sum()),
        })
    return pd.DataFrame(rows, columns=["ETF 1", "ETF 2", "Shared Securities", "Constituent Jaccard", "Weighted Overlap"])


def rank_security_candidates(
    regression_table: pd.DataFrame,
    minimum_alpha: float = 0.0,
    maximum_p_value: float = 0.10,
    minimum_observations: int = 60,
) -> pd.DataFrame:
    """Rank statistically screened historical alpha diagnostics without a trade label."""
    required = {"Regression Alpha", "Alpha p-Value", "Regression Observations", "Residual Volatility"}
    missing = required.difference(regression_table.columns)
    if missing:
        raise ValueError(f"Regression results are missing columns: {', '.join(sorted(missing))}.")
    result = regression_table.copy()
    result["Passes Screen"] = (
        (result["Regression Alpha"] > minimum_alpha)
        & (result["Alpha p-Value"] <= maximum_p_value)
        & (result["Regression Observations"] >= minimum_observations)
    )
    result["Alpha / Residual Variance"] = result["Regression Alpha"] / result["Residual Volatility"].pow(2)
    result.loc[result["Residual Volatility"] <= 0, "Alpha / Residual Variance"] = np.nan
    return result.sort_values(
        ["Passes Screen", "Regression Alpha", "Alpha p-Value"], ascending=[False, False, True]
    )
