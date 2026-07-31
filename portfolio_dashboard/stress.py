"""Custom shock and fixed historical-window stress calculations."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .config import HISTORICAL_STRESS_PERIODS
from .performance import portfolio_returns, simple_returns


def custom_shock(weights: pd.Series, shocks: pd.Series, portfolio_value: float) -> tuple[pd.DataFrame, dict[str, float | str]]:
    """Apply user-specified instantaneous asset shocks with no rebalancing."""
    if portfolio_value <= 0:
        raise ValueError("Portfolio value must be positive.")
    if set(shocks.index) != set(weights.index):
        raise ValueError("Every holding must have exactly one explicit shock.")
    if not np.isfinite(weights.to_numpy()).all() or not np.isfinite(shocks.to_numpy()).all():
        raise ValueError("Weights and shocks must be finite.")
    if (weights < 0).any() or not np.isclose(weights.sum(), 1.0, atol=1e-6):
        raise ValueError("Stress-test weights must be nonnegative and sum to 100%.")
    shocks = shocks.reindex(weights.index)
    impact = weights * shocks
    table = pd.DataFrame({"Weight": weights, "Shock": shocks, "Portfolio Impact": impact,
                          "Dollar Impact": impact * portfolio_value})
    total = float(impact.sum())
    largest_loss = str(table["Dollar Impact"].idxmin()) if table["Dollar Impact"].min() < 0 else "No loss contributors"
    summary = {"Estimated Portfolio Impact": total, "Before Value": portfolio_value,
               "After Value": portfolio_value * (1 + total),
               "Largest Loss Contributor": largest_loss}
    return table, summary


def historical_stress(prices: pd.DataFrame, weights: pd.Series, benchmark_prices: pd.Series) -> pd.DataFrame:
    """Evaluate only stress windows fully covered by the selected common history."""
    rows: list[dict[str, object]] = []
    first = max(prices.index.min(), benchmark_prices.index.min())
    last = min(prices.index.max(), benchmark_prices.index.max())
    for name, (start, end) in HISTORICAL_STRESS_PERIODS.items():
        start_ts, end_ts = pd.Timestamp(start), pd.Timestamp(end)
        if first > start_ts or last < end_ts:
            continue
        combined = prices.loc[start_ts:end_ts].join(benchmark_prices.rename("Benchmark"), how="inner").dropna()
        if len(combined) < 2:
            continue
        asset_returns = simple_returns(combined[prices.columns])
        portfolio = portfolio_returns(asset_returns, weights)
        benchmark = simple_returns(combined["Benchmark"])
        rows.append({"Scenario": name, "Configured Start": start, "Configured End": end,
                     "Actual Start": combined.index[0].date().isoformat(),
                     "Actual End": combined.index[-1].date().isoformat(),
                     "Portfolio Return": float((1 + portfolio).prod() - 1),
                     "Benchmark Return": float((1 + benchmark).prod() - 1),
                     "Complete": True})
    return pd.DataFrame(rows)
