"""Benchmark risk, attribution, and concentration analytics."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .config import TRADING_DAYS
from .performance import annualized_arithmetic_return


def historical_var(returns: pd.Series, confidence: float = 0.95) -> float:
    """Positive loss threshold from the empirical lower-tail quantile."""
    if not 0 < confidence < 1:
        raise ValueError("Confidence must be between 0 and 1.")
    clean = returns.dropna()
    if clean.empty:
        return float("nan")
    return max(0.0, float(-clean.quantile(1 - confidence)))


def historical_cvar(returns: pd.Series, confidence: float = 0.95) -> float:
    if not 0 < confidence < 1:
        raise ValueError("Confidence must be between 0 and 1.")
    clean = returns.dropna()
    if clean.empty:
        return float("nan")
    cutoff = clean.quantile(1 - confidence)
    tail = clean[clean <= cutoff]
    return max(0.0, float(-tail.mean())) if not tail.empty else float("nan")


def beta(portfolio: pd.Series, benchmark: pd.Series) -> float:
    joined = pd.concat([portfolio, benchmark], axis=1).dropna()
    variance = joined.iloc[:, 1].var(ddof=1)
    return float(joined.cov().iloc[0, 1] / variance) if variance > 0 else float("nan")


def single_index_regression(
    portfolio: pd.Series,
    benchmark: pd.Series,
    risk_free_rate: float = 0.0,
    periods_per_year: int = TRADING_DAYS,
) -> dict[str, float]:
    """OLS regression of portfolio excess returns on benchmark excess returns.

    The annual risk-free rate is divided by the number of periods so the
    arithmetic annualization of the fitted intercept reconciles exactly with
    Jensen's alpha calculated from annualized arithmetic returns.
    """
    joined = pd.concat([portfolio, benchmark], axis=1).dropna()
    if len(joined) < 3:
        raise ValueError("Single-index regression requires at least three aligned observations.")
    if periods_per_year <= 0:
        raise ValueError("Periods per year must be positive.")

    periodic_risk_free = risk_free_rate / periods_per_year
    y = joined.iloc[:, 0] - periodic_risk_free
    x = joined.iloc[:, 1] - periodic_risk_free
    x_variance = float(x.var(ddof=1))
    if not np.isfinite(x_variance) or x_variance <= 0:
        raise ValueError("Benchmark excess returns must have positive sample variance.")

    slope = float(x.cov(y) / x_variance)
    intercept = float(y.mean() - slope * x.mean())
    residuals = y - (intercept + slope * x)
    systematic_variance = float(slope**2 * x_variance * periods_per_year)
    idiosyncratic_variance = float(residuals.var(ddof=1) * periods_per_year)
    total_model_variance = systematic_variance + idiosyncratic_variance
    total_sum_squares = float((y - y.mean()).pow(2).sum())
    residual_volatility = float(residuals.std(ddof=2) * np.sqrt(periods_per_year))
    portfolio_expected_return = annualized_arithmetic_return(joined.iloc[:, 0], periods_per_year)
    benchmark_expected_return = annualized_arithmetic_return(joined.iloc[:, 1], periods_per_year)
    capm_required_return = float(risk_free_rate + slope * (benchmark_expected_return - risk_free_rate))
    jensen_alpha = float(portfolio_expected_return - capm_required_return)
    treynor = float((portfolio_expected_return - risk_free_rate) / slope) if not np.isclose(slope, 0.0) else float("nan")

    return {
        "Regression Alpha": float(intercept * periods_per_year),
        "Beta": slope,
        "R-Squared": float(1 - residuals.pow(2).sum() / total_sum_squares) if total_sum_squares > 0 else float("nan"),
        "Residual Volatility": residual_volatility,
        "Systematic Variance": systematic_variance,
        "Idiosyncratic Variance": idiosyncratic_variance,
        "Systematic Risk Share": float(systematic_variance / total_model_variance) if total_model_variance > 0 else float("nan"),
        "Idiosyncratic Risk Share": float(idiosyncratic_variance / total_model_variance) if total_model_variance > 0 else float("nan"),
        "CAPM Required Return": capm_required_return,
        "Jensen's Alpha": jensen_alpha,
        "Treynor Ratio": treynor,
        "Regression Observations": float(len(joined)),
    }


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


def benchmark_metrics(
    portfolio: pd.Series, benchmark: pd.Series, risk_free_rate: float = 0.0
) -> dict[str, float]:
    joined = pd.concat([portfolio, benchmark], axis=1).dropna()
    p, b = joined.iloc[:, 0], joined.iloc[:, 1]
    p_total, b_total = (1 + p).prod() - 1, (1 + b).prod() - 1
    annualized_active_return = float((p - b).mean() * TRADING_DAYS)
    relative = (1 + p).cumprod() / (1 + b).cumprod()
    relative_peak = relative.cummax().clip(lower=1.0)
    metrics = {
        "Portfolio Return": float(p_total), "Benchmark Return": float(b_total),
        "Excess Return": float(p_total - b_total),
        "Annualized Active Return": annualized_active_return,
        "Tracking Error": tracking_error(p, b),
        "Information Ratio": information_ratio(p, b), "Beta": beta(p, b),
        "Correlation": float(p.corr(b)),
        "Relative Drawdown": float((relative / relative_peak - 1).min()),
    }
    try:
        metrics.update(single_index_regression(p, b, risk_free_rate))
    except ValueError:
        metrics.update({
            "Regression Alpha": float("nan"), "R-Squared": float("nan"),
            "Residual Volatility": float("nan"), "Systematic Variance": float("nan"),
            "Idiosyncratic Variance": float("nan"), "Systematic Risk Share": float("nan"),
            "Idiosyncratic Risk Share": float("nan"), "CAPM Required Return": float("nan"),
            "Jensen's Alpha": float("nan"), "Treynor Ratio": float("nan"),
            "Regression Observations": float(len(joined)),
        })
    return metrics
