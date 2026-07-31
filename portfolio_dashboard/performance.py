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


def annualized_volatility(returns: pd.Series, periods_per_year: int = TRADING_DAYS) -> float:
    return float(returns.dropna().std(ddof=1) * np.sqrt(periods_per_year))


def sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
    clean = returns.dropna()
    vol = annualized_volatility(clean)
    return float((cagr(clean) - risk_free_rate) / vol) if vol > 0 else float("nan")


def sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
    """Annualized excess CAGR divided by target downside deviation.

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
    return float((cagr(clean) - risk_free_rate) / downside) if downside > 0 else float("nan")


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
        "Total Return": total_return(clean), "CAGR": ann_return,
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
