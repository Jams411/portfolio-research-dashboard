"""Custom shock and fixed historical-window stress calculations."""

from __future__ import annotations

import pandas as pd

from .config import HISTORICAL_STRESS_PERIODS


def custom_shock(weights: pd.Series, shocks: pd.Series, portfolio_value: float) -> tuple[pd.DataFrame, dict[str, float | str]]:
    """Apply user-specified instantaneous asset shocks with no rebalancing."""
    shocks = shocks.reindex(weights.index).fillna(0.0)
    impact = weights * shocks
    table = pd.DataFrame({"Weight": weights, "Shock": shocks, "Portfolio Impact": impact,
                          "Dollar Impact": impact * portfolio_value})
    total = float(impact.sum())
    summary = {"Estimated Portfolio Impact": total, "Before Value": portfolio_value,
               "After Value": portfolio_value * (1 + total),
               "Largest Loss Contributor": str(table["Dollar Impact"].idxmin())}
    return table, summary


def historical_stress(prices: pd.DataFrame, weights: pd.Series, benchmark_prices: pd.Series) -> pd.DataFrame:
    """Evaluate only stress windows fully covered by the selected common history."""
    rows: list[dict[str, object]] = []
    first, last = prices.index.min(), prices.index.max()
    for name, (start, end) in HISTORICAL_STRESS_PERIODS.items():
        start_ts, end_ts = pd.Timestamp(start), pd.Timestamp(end)
        if first > start_ts or last < end_ts:
            continue
        window = prices.loc[start_ts:end_ts]
        benchmark = benchmark_prices.loc[start_ts:end_ts]
        if len(window) < 2 or len(benchmark) < 2:
            continue
        asset_changes = window.iloc[-1] / window.iloc[0] - 1
        rows.append({"Scenario": name, "Start": start, "End": end,
                     "Portfolio Return": float(asset_changes @ weights),
                     "Benchmark Return": float(benchmark.iloc[-1] / benchmark.iloc[0] - 1),
                     "Complete": True})
    return pd.DataFrame(rows)
