"""Deterministic research diagnostics built from PortfolioLens analytics."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .performance import performance_metrics, portfolio_returns
from .stress import custom_shock


def _validate_weights(weights: pd.Series, columns: pd.Index) -> pd.Series:
    if set(weights.index) != set(columns):
        raise ValueError("Weight labels must exactly match asset-return columns.")
    aligned = weights.reindex(columns).astype(float)
    if not np.isfinite(aligned.to_numpy()).all():
        raise ValueError("Weights must be finite.")
    if (aligned < 0).any() or not np.isclose(aligned.sum(), 1.0, atol=1e-6):
        raise ValueError("Weights must be nonnegative and sum to 100%.")
    return aligned


def portfolio_comparison(
    asset_returns: pd.DataFrame,
    allocations: pd.DataFrame,
    current_weights: pd.Series,
    risk_free_rate: float = 0.0,
) -> pd.DataFrame:
    """Compare allocation methods under the existing constant-weight model."""
    current = _validate_weights(current_weights, asset_returns.columns)
    rows: dict[str, dict[str, float]] = {}
    for name in allocations.columns:
        weights = _validate_weights(allocations[name], asset_returns.columns)
        metrics = performance_metrics(portfolio_returns(asset_returns, weights), risk_free_rate)
        rows[str(name)] = {
            "Arithmetic Return": metrics["Historical Arithmetic Annualized Return"],
            "CAGR": metrics["CAGR"],
            "Annualized Volatility": metrics["Annualized Volatility"],
            "Sharpe Ratio": metrics["Sharpe Ratio"],
            "Maximum Drawdown": metrics["Maximum Drawdown"],
            "Effective Holdings": float(1 / weights.pow(2).sum()),
            "Largest Weight": float(weights.max()),
            "Weight Distance from Current": float(0.5 * (weights - current).abs().sum()),
        }
    return pd.DataFrame.from_dict(rows, orient="index").rename_axis("Portfolio")


def portfolio_health_score(
    performance: dict[str, float],
    benchmark: dict[str, float],
    weights: pd.Series,
    cvar_95: float,
) -> tuple[float, float, pd.DataFrame]:
    """Return a transparent 0–100 historical diagnostic and component table.

    Available components are rescaled to 100. The score is descriptive and
    intentionally does not represent suitability, forecast return, or advice.
    """
    effective = float(1 / weights.pow(2).sum())
    n_assets = len(weights)
    definitions = [
        ("Diversification", 25.0, effective / n_assets if n_assets else np.nan,
         effective, "effective holdings / holding count"),
        ("Risk-adjusted return", 25.0,
         (performance.get("Sharpe Ratio", np.nan) + 1.0) / 3.0,
         performance.get("Sharpe Ratio", np.nan), "Sharpe mapped from -1 (0%) to 2 (100%)"),
        ("Drawdown resilience", 20.0,
         1.0 - abs(performance.get("Maximum Drawdown", np.nan)) / 0.50,
         performance.get("Maximum Drawdown", np.nan), "1 - |maximum drawdown| / 50%"),
        ("Tail resilience", 15.0, 1.0 - cvar_95 / 0.10,
         cvar_95, "1 - daily 95% CVaR / 10%"),
        ("Benchmark efficiency", 15.0,
         (benchmark.get("Information Ratio", np.nan) + 1.0) / 2.0,
         benchmark.get("Information Ratio", np.nan), "information ratio mapped from -1 (0%) to 1 (100%)"),
    ]
    rows = []
    for component, weight, raw, value, rule in definitions:
        available = bool(np.isfinite(raw) and np.isfinite(value))
        normalized = float(np.clip(raw, 0.0, 1.0)) if available else np.nan
        rows.append({
            "Component": component, "Weight": weight / 100, "Metric Value": value,
            "Normalized Result": normalized, "Points": normalized * weight if available else np.nan,
            "Rule": rule, "Available": available,
        })
    table = pd.DataFrame(rows).set_index("Component")
    available_weight = float(table.loc[table["Available"], "Weight"].sum())
    score = float(table["Points"].sum() / available_weight) if available_weight > 0 else float("nan")
    return score, available_weight, table


def what_if_analysis(
    asset_returns: pd.DataFrame,
    current_weights: pd.Series,
    scenario_weights: pd.Series,
    shocks: pd.Series,
    portfolio_value: float,
    risk_free_rate: float = 0.0,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, float | str]]:
    """Compare current and hypothetical weights and apply explicit shocks."""
    current = _validate_weights(current_weights, asset_returns.columns)
    scenario = _validate_weights(scenario_weights, asset_returns.columns)
    comparison = portfolio_comparison(
        asset_returns,
        pd.DataFrame({"Current": current, "What-if": scenario}),
        current,
        risk_free_rate,
    )
    comparison.loc["Change"] = comparison.loc["What-if"] - comparison.loc["Current"]
    shock_table, shock_summary = custom_shock(scenario, shocks, portfolio_value)
    return comparison, shock_table, shock_summary


def deterministic_insights(
    performance: dict[str, float],
    benchmark: dict[str, float],
    weights: pd.Series,
    volatility_contributions: pd.Series,
    cvar_95: float,
) -> pd.DataFrame:
    """Generate rules-based observations with explicit metric evidence."""
    rows: list[dict[str, object]] = []

    def add(category: str, observation: str, metric: str, value: float, rule: str) -> None:
        rows.append({"Category": category, "Observation": observation, "Metric": metric,
                     "Value": value, "Rule": rule})

    sharpe = performance.get("Sharpe Ratio", np.nan)
    if np.isfinite(sharpe):
        text = "Historical excess return was positive per unit of total volatility." if sharpe > 0 else "Historical excess return was nonpositive per unit of total volatility."
        add("Performance", text, "Sharpe Ratio", sharpe, "positive if Sharpe > 0; nonpositive otherwise")
    excess = benchmark.get("Excess Return", np.nan)
    if np.isfinite(excess):
        relation = "exceeded" if excess > 0 else "trailed" if excess < 0 else "matched"
        add("Benchmark", f"The portfolio {relation} the benchmark over the selected period.",
            "Excess Return", excess, "sign of cumulative portfolio minus benchmark return")
    drawdown = performance.get("Maximum Drawdown", np.nan)
    if np.isfinite(drawdown):
        severity = "exceeded 20%" if drawdown <= -0.20 else "remained below 20%"
        add("Risk", f"The largest historical peak-to-trough decline {severity}.",
            "Maximum Drawdown", drawdown, "20% descriptive drawdown threshold")
    largest_weight = float(weights.max())
    effective = float(1 / weights.pow(2).sum())
    concentration = "at least 40%" if largest_weight >= 0.40 else "below 40%"
    add("Diversification", f"The largest position was {concentration}; effective holdings were {effective:.2f}.",
        "Largest Weight", largest_weight, "40% descriptive concentration threshold")
    beta = benchmark.get("Beta", np.nan)
    if np.isfinite(beta):
        exposure = "above" if beta > 1.10 else "below" if beta < 0.90 else "near"
        add("Market exposure", f"Historical benchmark sensitivity was {exposure} one.",
            "Beta", beta, "above 1.10, below 0.90, otherwise near one")
    idiosyncratic = benchmark.get("Idiosyncratic Risk Share", np.nan)
    if np.isfinite(idiosyncratic):
        source = "more than half" if idiosyncratic > 0.50 else "no more than half"
        add("Risk decomposition", f"Idiosyncratic variation represented {source} of modeled variance.",
            "Idiosyncratic Risk Share", idiosyncratic, "greater than 50% of single-index model variance")
    total_volatility = performance.get("Annualized Volatility", np.nan)
    if np.isfinite(total_volatility) and total_volatility > 0 and not volatility_contributions.empty:
        ticker = str(volatility_contributions.idxmax())
        share = float(volatility_contributions.loc[ticker] / total_volatility)
        add("Risk contribution", f"{ticker} was the largest Euler volatility contributor.",
            f"{ticker} Volatility Contribution Share", share, "largest component contribution / portfolio volatility")
    if np.isfinite(cvar_95):
        add("Tail risk", "Historical CVaR summarizes the average observed return in the empirical 5% tail.",
            "Historical CVaR (95%)", cvar_95, "nonnegative empirical daily loss magnitude")
    return pd.DataFrame(rows)
