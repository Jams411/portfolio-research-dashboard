"""Long-only portfolio allocation methods."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from .config import TRADING_DAYS
from .performance import sharpe_from_statistics


def optimizer_statistics(
    returns: pd.DataFrame, weights: pd.Series, risk_free_rate: float = 0.0
) -> dict[str, float]:
    """Historical arithmetic optimizer inputs evaluated at labeled weights."""
    aligned = weights.reindex(returns.columns)
    if aligned.isna().any():
        raise ValueError("Weight labels must match return columns.")
    expected = float(aligned @ (returns.mean() * TRADING_DAYS))
    variance = float(aligned @ (returns.cov() * TRADING_DAYS) @ aligned)
    volatility = float(np.sqrt(max(variance, 0.0)))
    return {
        "Optimizer Expected Return": expected,
        "Optimizer Volatility": volatility,
        "Optimizer Sharpe": sharpe_from_statistics(expected, volatility, risk_free_rate),
    }


def equal_weights(columns: list[str] | pd.Index) -> pd.Series:
    return pd.Series(1 / len(columns), index=columns, name="Equal Weight")


def inverse_volatility_weights(returns: pd.DataFrame) -> pd.Series:
    vol = returns.std(ddof=1) * np.sqrt(TRADING_DAYS)
    if (vol <= 0).any() or vol.isna().any():
        raise ValueError("Inverse-volatility weights require positive finite volatility for every asset.")
    inverse = 1 / vol
    return (inverse / inverse.sum()).rename("Inverse Volatility")


def _optimize(
    returns: pd.DataFrame, objective: str, risk_free_rate: float = 0.0,
    target_return: float | None = None,
) -> pd.Series:
    if returns.empty or len(returns) < 2 or returns.shape[1] == 0:
        raise RuntimeError("Optimization requires at least two return observations.")
    if not np.isfinite(returns.to_numpy()).all():
        raise RuntimeError("Optimization inputs must be finite and complete.")
    cov = returns.cov().to_numpy() * TRADING_DAYS
    expected = returns.mean().to_numpy() * TRADING_DAYS
    if not np.isfinite(cov).all() or not np.isfinite(expected).all():
        raise RuntimeError("Optimization estimates are not finite.")
    n = len(returns.columns)
    if n == 1:
        return pd.Series([1.0], index=returns.columns)
    if objective == "max_sharpe" and np.max(np.diag(cov)) <= np.finfo(float).eps:
        raise RuntimeError("Maximum-Sharpe optimization requires positive volatility.")
    def portfolio_vol(w: np.ndarray) -> float:
        return float(np.sqrt(max(w @ cov @ w, 0)))
    def target(w: np.ndarray) -> float:
        vol = portfolio_vol(w)
        if objective == "min_variance":
            return vol ** 2
        return -sharpe_from_statistics(float(w @ expected), vol, risk_free_rate) if vol > 0 else 1e9
    constraints: list[dict[str, object]] = [{"type": "eq", "fun": lambda w: w.sum() - 1}]
    if target_return is not None:
        minimum, maximum = float(expected.min()), float(expected.max())
        if target_return < minimum - 1e-10 or target_return > maximum + 1e-10:
            raise ValueError(
                f"Target return {target_return:.2%} is outside the long-only feasible range "
                f"{minimum:.2%} to {maximum:.2%}."
            )
        constraints.append({"type": "eq", "fun": lambda w: float(w @ expected - target_return)})
    result = minimize(target, np.repeat(1 / n, n), method="SLSQP", bounds=[(0, 1)] * n,
                      constraints=constraints,
                      options={"maxiter": 1000, "ftol": 1e-12})
    if not result.success or not np.isfinite(result.x).all() or abs(result.x.sum() - 1) > 1e-6:
        raise RuntimeError(f"Optimization did not converge: {result.message}")
    cleaned = np.clip(result.x, 0, 1)
    return pd.Series(cleaned / cleaned.sum(), index=returns.columns)


def minimum_variance_weights(returns: pd.DataFrame) -> pd.Series:
    return _optimize(returns, "min_variance").rename("Minimum Variance")


def maximum_sharpe_weights(returns: pd.DataFrame, risk_free_rate: float = 0.0) -> pd.Series:
    return _optimize(returns, "max_sharpe", risk_free_rate).rename("Maximum Sharpe")


def target_return_weights(returns: pd.DataFrame, target_return: float) -> pd.Series:
    """Minimum-variance long-only weights for an arithmetic annual target."""
    return _optimize(returns, "min_variance", target_return=target_return).rename("Target Return")


def efficient_frontier(
    returns: pd.DataFrame, risk_free_rate: float = 0.0, points: int = 25,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Generate the long-only upper efficient branch from GMV to max return."""
    if points < 2:
        raise ValueError("Efficient frontier requires at least two points.")
    gmv = minimum_variance_weights(returns)
    gmv_return = optimizer_statistics(returns, gmv, risk_free_rate)["Optimizer Expected Return"]
    maximum_return = float((returns.mean() * TRADING_DAYS).max())
    targets = np.linspace(gmv_return, maximum_return, points)
    rows: list[dict[str, float]] = []
    weights: dict[str, pd.Series] = {}
    for index, target_return in enumerate(targets):
        candidate = gmv if index == 0 else target_return_weights(returns, float(target_return))
        stats = optimizer_statistics(returns, candidate, risk_free_rate)
        label = f"Frontier {index + 1}"
        rows.append({"Portfolio": label, "Target Return": float(target_return), **stats})
        weights[label] = candidate
    return pd.DataFrame(rows).set_index("Portfolio"), pd.DataFrame(weights)


def capital_allocation_line(
    tangency_statistics: dict[str, float], risk_free_rate: float, points: int = 20,
) -> pd.DataFrame:
    """Non-leveraged CAL from the risk-free asset to the constrained tangency portfolio."""
    if points < 2:
        raise ValueError("Capital Allocation Line requires at least two points.")
    volatility = tangency_statistics["Optimizer Volatility"]
    sharpe = tangency_statistics["Optimizer Sharpe"]
    if not np.isfinite(volatility) or volatility <= 0 or not np.isfinite(sharpe):
        raise ValueError("Tangency statistics must contain positive volatility and finite Sharpe.")
    risky_weight = np.linspace(0.0, 1.0, points)
    return pd.DataFrame({
        "Risky Portfolio Weight": risky_weight,
        "Expected Return": risk_free_rate + risky_weight * volatility * sharpe,
        "Volatility": risky_weight * volatility,
    })


def allocation_methods(returns: pd.DataFrame, current: pd.Series, risk_free_rate: float) -> tuple[pd.DataFrame, list[str]]:
    methods = {"Current": current, "Equal Weight": equal_weights(returns.columns)}
    warnings: list[str] = []
    for label, function in (("Inverse Volatility", inverse_volatility_weights),
                            ("Minimum Variance", minimum_variance_weights),
                            ("Maximum Sharpe", lambda r: maximum_sharpe_weights(r, risk_free_rate))):
        try:
            methods[label] = function(returns)
        except (ValueError, RuntimeError) as exc:
            warnings.append(f"{label} unavailable: {exc}")
    return pd.DataFrame(methods), warnings
