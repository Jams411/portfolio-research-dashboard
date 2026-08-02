"""Portfolio and manager performance-evaluation calculations."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .config import TRADING_DAYS


def fama_selectivity_decomposition(
    portfolio_return: float,
    benchmark_return: float,
    risk_free_rate: float,
    portfolio_volatility: float,
    benchmark_volatility: float,
    portfolio_beta: float,
) -> dict[str, float]:
    """Decompose performance into Fama selectivity and diversification effects.

    All inputs use one annual arithmetic convention. The source model defines:

    * overall performance = ``R_p - R_f``;
    * CAPM required return = ``R_f + beta_p(R_m - R_f)``;
    * CML required return = ``R_f + (R_m - R_f)(sigma_p / sigma_m)``;
    * selectivity = ``R_p - CAPM required return``;
    * diversification effect = ``CML required return - CAPM required return``;
    * net selectivity = ``selectivity - diversification effect``.
    """
    inputs = np.asarray(
        [portfolio_return, benchmark_return, risk_free_rate, portfolio_volatility,
         benchmark_volatility, portfolio_beta],
        dtype=float,
    )
    if not np.isfinite(inputs).all():
        raise ValueError("Fama evaluation inputs must be finite.")
    if portfolio_volatility < 0 or benchmark_volatility <= 0:
        raise ValueError("Portfolio volatility cannot be negative and benchmark volatility must be positive.")

    market_premium = benchmark_return - risk_free_rate
    capm_required = risk_free_rate + portfolio_beta * market_premium
    cml_required = risk_free_rate + market_premium * portfolio_volatility / benchmark_volatility
    selectivity = portfolio_return - capm_required
    diversification = cml_required - capm_required
    net_selectivity = selectivity - diversification
    return {
        "Overall Performance": portfolio_return - risk_free_rate,
        "CAPM Required Return": capm_required,
        "CML Required Return at Portfolio Risk": cml_required,
        "Selectivity": selectivity,
        "Diversification Effect": diversification,
        "Net Selectivity": net_selectivity,
    }


def allocation_selection_attribution(
    benchmark_weights: pd.Series,
    benchmark_returns: pd.Series,
    portfolio_weights: pd.Series,
    portfolio_returns: pd.Series,
) -> dict[str, float]:
    """Reproduce the source's category allocation/selection convention.

    Allocation is ``sum((w_p-w_b)(r_b-R_b))``. Selection uses portfolio
    weights, ``sum(w_p(r_p-r_b))``, so it includes the conventional interaction
    term and is deliberately not labeled as pure Brinson selection.
    """
    labels = benchmark_weights.index
    if any(not labels.equals(series.index) for series in (
        benchmark_returns, portfolio_weights, portfolio_returns,
    )):
        raise ValueError("Attribution inputs must have identical ordered labels.")
    values = np.concatenate([
        benchmark_weights.to_numpy(dtype=float), benchmark_returns.to_numpy(dtype=float),
        portfolio_weights.to_numpy(dtype=float), portfolio_returns.to_numpy(dtype=float),
    ])
    if len(labels) == 0 or not np.isfinite(values).all():
        raise ValueError("Attribution inputs must be nonempty and finite.")
    if not np.isclose(benchmark_weights.sum(), 1.0) or not np.isclose(portfolio_weights.sum(), 1.0):
        raise ValueError("Benchmark and portfolio weights must each sum to one.")

    benchmark_total = float(benchmark_weights @ benchmark_returns)
    portfolio_total = float(portfolio_weights @ portfolio_returns)
    allocation = float((portfolio_weights - benchmark_weights) @ (benchmark_returns - benchmark_total))
    selection_including_interaction = float(portfolio_weights @ (portfolio_returns - benchmark_returns))
    active = portfolio_total - benchmark_total
    return {
        "Benchmark Return": benchmark_total,
        "Portfolio Return": portfolio_total,
        "Active Return": active,
        "Allocation Effect": allocation,
        "Selection Effect Including Interaction": selection_including_interaction,
        "Reconciliation Residual": active - allocation - selection_including_interaction,
    }


def modified_dietz_return(
    beginning_value: float,
    ending_value: float,
    cash_flows: pd.Series,
    elapsed_fractions: pd.Series,
) -> float:
    """Return the Modified Dietz period return for external cash flows.

    ``elapsed_fractions`` is the fraction of the period elapsed when each
    contribution occurs. A midpoint contribution therefore has value ``0.5``.
    """
    if not cash_flows.index.equals(elapsed_fractions.index):
        raise ValueError("Cash flows and timing fractions must have identical labels.")
    values = np.asarray([beginning_value, ending_value, *cash_flows, *elapsed_fractions], dtype=float)
    if not np.isfinite(values).all() or beginning_value <= 0:
        raise ValueError("Values and cash flows must be finite, with positive beginning value.")
    if ((elapsed_fractions < 0) | (elapsed_fractions > 1)).any():
        raise ValueError("Elapsed cash-flow fractions must be between zero and one.")
    denominator = beginning_value + float(((1.0 - elapsed_fractions) * cash_flows).sum())
    if np.isclose(denominator, 0.0):
        return float("nan")
    return float((ending_value - beginning_value - cash_flows.sum()) / denominator)


def time_weighted_return(period_returns: pd.Series) -> float:
    """Compound subperiod returns into a cumulative time-weighted return."""
    clean = period_returns.dropna()
    if clean.empty or (clean <= -1.0).any():
        return float("nan")
    return float((1.0 + clean).prod() - 1.0)


def rolling_performance_evaluation(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
    risk_free_rate: float = 0.0,
    window: int = 63,
    periods_per_year: int = TRADING_DAYS,
) -> pd.DataFrame:
    """Calculate rolling Sharpe, tracking error and Information Ratio."""
    if window < 3 or periods_per_year <= 0:
        raise ValueError("Window must be at least three and periods per year must be positive.")
    joined = pd.concat([
        portfolio_returns.rename("Portfolio"), benchmark_returns.rename("Benchmark")
    ], axis=1).dropna()
    active = joined["Portfolio"] - joined["Benchmark"]
    portfolio_return = joined["Portfolio"].rolling(window).mean() * periods_per_year
    portfolio_volatility = joined["Portfolio"].rolling(window).std(ddof=1) * np.sqrt(periods_per_year)
    active_return = active.rolling(window).mean() * periods_per_year
    tracking_error = active.rolling(window).std(ddof=1) * np.sqrt(periods_per_year)
    result = pd.DataFrame({
        "Rolling Sharpe Ratio": (portfolio_return - risk_free_rate) / portfolio_volatility,
        "Rolling Annualized Active Return": active_return,
        "Rolling Tracking Error": tracking_error,
        "Rolling Information Ratio": active_return / tracking_error,
    })
    return result.replace([np.inf, -np.inf], np.nan).dropna(how="all")
