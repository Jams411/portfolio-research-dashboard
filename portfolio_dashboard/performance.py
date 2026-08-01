"""Return calculations and portfolio performance statistics."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .config import TRADING_DAYS


def simple_returns(prices: pd.Series | pd.DataFrame) -> pd.Series | pd.DataFrame:
    """Calculate simple daily returns without forward-filling missing prices."""
    return prices.pct_change(fill_method=None).iloc[1:]


def portfolio_returns(asset_returns: pd.DataFrame, weights: pd.Series) -> pd.Series:
    """Calculate constant-weight daily portfolio returns on complete rows."""
    if set(asset_returns.columns) != set(weights.index):
        raise ValueError("Weight labels must exactly match return columns.")
    if asset_returns.isna().any().any():
        raise ValueError("Asset returns contain missing observations after alignment.")
    return asset_returns.loc[:, weights.index].mul(weights, axis=1).sum(axis=1).rename("Portfolio")


def total_return(returns: pd.Series) -> float:
    return float((1.0 + returns.dropna()).prod() - 1.0)


def cagr(returns: pd.Series, periods_per_year: int = TRADING_DAYS) -> float:
    clean = returns.dropna()
    if clean.empty or (1 + clean).prod() <= 0:
        return float("nan")
    return float((1 + clean).prod() ** (periods_per_year / len(clean)) - 1)


def annualized_arithmetic_return(
    returns: pd.Series, periods_per_year: int = TRADING_DAYS
) -> float:
    """Annualize the sample arithmetic mean return.

    This is the historical expected-return convention used by mean-variance
    construction and risk-adjusted performance ratios. It is deliberately
    distinct from CAGR, which measures realized compound growth.
    """
    clean = returns.dropna()
    return float(clean.mean() * periods_per_year) if not clean.empty else float("nan")


def annualized_volatility(returns: pd.Series, periods_per_year: int = TRADING_DAYS) -> float:
    return float(returns.dropna().std(ddof=1) * np.sqrt(periods_per_year))


def annualized_variance(returns: pd.Series, periods_per_year: int = TRADING_DAYS) -> float:
    """Annualized sample variance of periodic returns."""
    return float(returns.dropna().var(ddof=1) * periods_per_year)


def portfolio_expected_return(
    asset_returns: pd.DataFrame, weights: pd.Series, periods_per_year: int = TRADING_DAYS
) -> float:
    """Historical arithmetic annualized return ``w'μ`` for labeled assets."""
    return annualized_arithmetic_return(portfolio_returns(asset_returns, weights), periods_per_year)


def portfolio_variance(
    asset_returns: pd.DataFrame, weights: pd.Series, periods_per_year: int = TRADING_DAYS
) -> float:
    """Annualized covariance-matrix variance ``w'Σw`` for labeled assets."""
    if set(asset_returns.columns) != set(weights.index):
        raise ValueError("Weight labels must exactly match return columns.")
    cov = asset_returns.loc[:, weights.index].cov() * periods_per_year
    return float(weights @ cov @ weights)


def sharpe_from_statistics(expected_return: float, volatility: float, risk_free_rate: float = 0.0) -> float:
    """Return Sharpe from annualized arithmetic return and volatility inputs."""
    return float((expected_return - risk_free_rate) / volatility) if volatility > 0 else float("nan")


def sharpe_ratio(
    returns: pd.Series, risk_free_rate: float = 0.0, periods_per_year: int = TRADING_DAYS
) -> float:
    """Arithmetic annualized excess return divided by annualized volatility."""
    clean = returns.dropna()
    vol = annualized_volatility(clean, periods_per_year)
    expected = annualized_arithmetic_return(clean, periods_per_year)
    return sharpe_from_statistics(expected, vol, risk_free_rate)


def sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
    """Annualized arithmetic excess return divided by target downside deviation.

    The annual risk-free rate is converted to an equivalent daily minimum
    acceptable return. Downside deviation includes every observation, with
    returns above the target contributing zero downside risk.
    """
    clean = returns.dropna()
    if clean.empty or risk_free_rate <= -1:
        return float("nan")
    daily_target = (1.0 + risk_free_rate) ** (1.0 / TRADING_DAYS) - 1.0
    shortfall = np.minimum(clean.to_numpy() - daily_target, 0.0)
    downside = float(np.sqrt(np.mean(shortfall ** 2)) * np.sqrt(TRADING_DAYS))
    expected = annualized_arithmetic_return(clean)
    return float((expected - risk_free_rate) / downside) if downside > 0 else float("nan")


def drawdown_series(returns: pd.Series) -> pd.Series:
    """Drawdown from the running peak, including initial wealth of 1.0."""
    wealth = (1 + returns.fillna(0)).cumprod()
    running_peak = wealth.cummax().clip(lower=1.0)
    return wealth / running_peak - 1


def max_drawdown(returns: pd.Series) -> float:
    return float(drawdown_series(returns).min())


def performance_metrics(returns: pd.Series, risk_free_rate: float = 0.0) -> dict[str, float]:
    """Return the standard performance scorecard for a daily return series."""
    clean = returns.dropna()
    ann_return, max_dd = cagr(clean), max_drawdown(clean)
    return {
        "Total Return": total_return(clean),
        "Historical Arithmetic Annualized Return": annualized_arithmetic_return(clean),
        "CAGR": ann_return,
        "Annualized Variance": annualized_variance(clean),
        "Annualized Volatility": annualized_volatility(clean),
        "Sharpe Ratio": sharpe_ratio(clean, risk_free_rate),
        "Sortino Ratio": sortino_ratio(clean, risk_free_rate),
        "Maximum Drawdown": max_dd,
        "Calmar Ratio": ann_return / abs(max_dd) if max_dd < 0 else float("nan"),
        "Best Daily Return": float(clean.max()), "Worst Daily Return": float(clean.min()),
        "Positive-Day Percentage": float((clean > 0).mean()),
    }


def monthly_returns(returns: pd.Series) -> pd.DataFrame:
    monthly = (1 + returns).resample("ME").prod() - 1
    table = monthly.to_frame("return")
    table["Year"], table["Month"] = table.index.year, table.index.strftime("%b")
    return table.pivot(index="Year", columns="Month", values="return").reindex(
        columns=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    )
