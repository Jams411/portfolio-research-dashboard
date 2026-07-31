"""Benchmark risk, attribution, and concentration analytics."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .config import TRADING_DAYS


def historical_var(returns: pd.Series, confidence: float = 0.95) -> float:
    """Positive loss threshold from the empirical lower-tail quantile."""
    return float(-returns.dropna().quantile(1 - confidence))


def historical_cvar(returns: pd.Series, confidence: float = 0.95) -> float:
    clean = returns.dropna()
    cutoff = clean.quantile(1 - confidence)
    tail = clean[clean <= cutoff]
    return float(-tail.mean()) if not tail.empty else float("nan")


def beta(portfolio: pd.Series, benchmark: pd.Series) -> float:
    joined = pd.concat([portfolio, benchmark], axis=1).dropna()
    variance = joined.iloc[:, 1].var(ddof=1)
    return float(joined.cov().iloc[0, 1] / variance) if variance > 0 else float("nan")


def tracking_error(portfolio: pd.Series, benchmark: pd.Series) -> float:
    active = pd.concat([portfolio, benchmark], axis=1).dropna().diff(axis=1).iloc[:, 1] * -1
    return float(active.std(ddof=1) * np.sqrt(TRADING_DAYS))


def information_ratio(portfolio: pd.Series, benchmark: pd.Series) -> float:
    joined = pd.concat([portfolio, benchmark], axis=1).dropna()
    active = joined.iloc[:, 0] - joined.iloc[:, 1]
    te = active.std(ddof=1) * np.sqrt(TRADING_DAYS)
    return float(active.mean() * TRADING_DAYS / te) if te > 0 else float("nan")


def volatility_contributions(asset_returns: pd.DataFrame, weights: pd.Series) -> pd.Series:
    """Euler contributions to annualized portfolio volatility.

    For covariance matrix Σ and weights w, component contribution is
    w_i(Σw)_i / sqrt(w'Σw). Contributions sum to portfolio volatility.
    """
    cov = asset_returns.loc[:, weights.index].cov() * TRADING_DAYS
    portfolio_variance = float(weights @ cov @ weights)
    if portfolio_variance <= 0:
        return pd.Series(0.0, index=weights.index, name="Volatility Contribution")
    sigma = np.sqrt(portfolio_variance)
    return (weights * (cov @ weights) / sigma).rename("Volatility Contribution")


def return_contributions(asset_returns: pd.DataFrame, weights: pd.Series) -> pd.Series:
    """Arithmetic contribution to cumulative portfolio return; exactly reconciles."""
    daily = asset_returns.loc[:, weights.index].mul(weights, axis=1)
    portfolio = daily.sum(axis=1)
    growth_before = (1 + portfolio).cumprod().shift(1, fill_value=1.0)
    return daily.mul(growth_before, axis=0).sum().rename("Total Return Contribution")


def benchmark_metrics(portfolio: pd.Series, benchmark: pd.Series) -> dict[str, float]:
    joined = pd.concat([portfolio, benchmark], axis=1).dropna()
    p, b = joined.iloc[:, 0], joined.iloc[:, 1]
    p_total, b_total = (1 + p).prod() - 1, (1 + b).prod() - 1
    relative = (1 + p).cumprod() / (1 + b).cumprod()
    return {
        "Portfolio Return": float(p_total), "Benchmark Return": float(b_total),
        "Excess Return": float(p_total - b_total), "Tracking Error": tracking_error(p, b),
        "Information Ratio": information_ratio(p, b), "Beta": beta(p, b),
        "Correlation": float(p.corr(b)),
        "Relative Drawdown": float((relative / relative.cummax() - 1).min()),
    }
