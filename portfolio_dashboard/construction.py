"""Long-only portfolio allocation methods."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from .config import TRADING_DAYS


def equal_weights(columns: list[str] | pd.Index) -> pd.Series:
    return pd.Series(1 / len(columns), index=columns, name="Equal Weight")


def inverse_volatility_weights(returns: pd.DataFrame) -> pd.Series:
    vol = returns.std(ddof=1) * np.sqrt(TRADING_DAYS)
    if (vol <= 0).any() or vol.isna().any():
        raise ValueError("Inverse-volatility weights require positive finite volatility for every asset.")
    inverse = 1 / vol
    return (inverse / inverse.sum()).rename("Inverse Volatility")


def _optimize(returns: pd.DataFrame, objective: str, risk_free_rate: float = 0.0) -> pd.Series:
    cov = returns.cov().to_numpy() * TRADING_DAYS
    expected = returns.mean().to_numpy() * TRADING_DAYS
    n = len(returns.columns)
    if n == 1:
        return pd.Series([1.0], index=returns.columns)
    def portfolio_vol(w: np.ndarray) -> float:
        return float(np.sqrt(max(w @ cov @ w, 0)))
    def target(w: np.ndarray) -> float:
        vol = portfolio_vol(w)
        if objective == "min_variance":
            return vol ** 2
        return -float((w @ expected - risk_free_rate) / vol) if vol > 0 else 1e9
    result = minimize(target, np.repeat(1 / n, n), method="SLSQP", bounds=[(0, 1)] * n,
                      constraints={"type": "eq", "fun": lambda w: w.sum() - 1},
                      options={"maxiter": 1000, "ftol": 1e-12})
    if not result.success or not np.isfinite(result.x).all() or abs(result.x.sum() - 1) > 1e-6:
        raise RuntimeError(f"Optimization did not converge: {result.message}")
    cleaned = np.clip(result.x, 0, 1)
    return pd.Series(cleaned / cleaned.sum(), index=returns.columns)


def minimum_variance_weights(returns: pd.DataFrame) -> pd.Series:
    return _optimize(returns, "min_variance").rename("Minimum Variance")


def maximum_sharpe_weights(returns: pd.DataFrame, risk_free_rate: float = 0.0) -> pd.Series:
    return _optimize(returns, "max_sharpe", risk_free_rate).rename("Maximum Sharpe")


def allocation_methods(returns: pd.DataFrame, current: pd.Series, risk_free_rate: float) -> tuple[pd.DataFrame, list[str]]:
    methods = {"Current": current, "Equal Weight": equal_weights(returns.columns),
               "Inverse Volatility": inverse_volatility_weights(returns)}
    warnings: list[str] = []
    for label, function in (("Minimum Variance", minimum_variance_weights),
                            ("Maximum Sharpe", lambda r: maximum_sharpe_weights(r, risk_free_rate))):
        try:
            methods[label] = function(returns)
        except RuntimeError as exc:
            warnings.append(f"{label} unavailable: {exc}")
    return pd.DataFrame(methods), warnings
