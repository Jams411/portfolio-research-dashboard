"""Long-only portfolio allocation methods."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import linprog, minimize

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
    minimum_weights: pd.Series | None = None,
    maximum_weights: pd.Series | None = None,
    groups: pd.Series | None = None,
    group_caps: dict[str, float] | None = None,
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
    minimum = pd.Series(0.0, index=returns.columns) if minimum_weights is None else minimum_weights.reindex(returns.columns)
    maximum = pd.Series(1.0, index=returns.columns) if maximum_weights is None else maximum_weights.reindex(returns.columns)
    if minimum.isna().any() or maximum.isna().any() or (minimum < 0).any() or (maximum > 1).any():
        raise ValueError("Asset bounds must be finite values between 0% and 100%.")
    if (minimum > maximum).any():
        raise ValueError("Each minimum asset weight must be at or below its maximum.")
    if minimum.sum() > 1 + 1e-10 or maximum.sum() < 1 - 1e-10:
        raise ValueError("Asset bounds cannot satisfy the 100% sum constraint.")
    caps = group_caps or {}
    group_labels = pd.Series("", index=returns.columns) if groups is None else groups.reindex(returns.columns).fillna("").astype(str)
    unknown = set(caps) - set(group_labels[group_labels.ne("")])
    if unknown or any(not np.isfinite(cap) or cap < 0 or cap > 1 for cap in caps.values()):
        raise ValueError("Group caps must reference defined groups and fall between 0% and 100%.")
    def portfolio_vol(w: np.ndarray) -> float:
        return float(np.sqrt(max(w @ cov @ w, 0)))
    def target(w: np.ndarray) -> float:
        vol = portfolio_vol(w)
        if objective == "min_variance":
            return vol ** 2
        return -sharpe_from_statistics(float(w @ expected), vol, risk_free_rate) if vol > 0 else 1e9
    constraints: list[dict[str, object]] = [{"type": "eq", "fun": lambda w: w.sum() - 1}]
    a_eq = [np.ones(n)]
    b_eq = [1.0]
    if target_return is not None:
        feasible_minimum, feasible_maximum = float(expected.min()), float(expected.max())
        if target_return < feasible_minimum - 1e-10 or target_return > feasible_maximum + 1e-10:
            raise ValueError(
                f"Target return {target_return:.2%} is outside the long-only feasible range "
                f"{feasible_minimum:.2%} to {feasible_maximum:.2%}."
            )
        constraints.append({"type": "eq", "fun": lambda w: float(w @ expected - target_return)})
        a_eq.append(expected)
        b_eq.append(target_return)
    a_ub: list[np.ndarray] = []
    b_ub: list[float] = []
    for group, cap in caps.items():
        mask = (group_labels == group).to_numpy(dtype=float)
        constraints.append({"type": "ineq", "fun": lambda w, m=mask, c=cap: float(c - w @ m)})
        a_ub.append(mask)
        b_ub.append(cap)
    bounds = list(zip(minimum.to_numpy(dtype=float), maximum.to_numpy(dtype=float)))
    feasible = linprog(
        np.zeros(n), A_ub=np.array(a_ub) if a_ub else None,
        b_ub=np.array(b_ub) if b_ub else None, A_eq=np.array(a_eq), b_eq=np.array(b_eq),
        bounds=bounds, method="highs",
    )
    if not feasible.success:
        raise ValueError(f"Allocation constraints are infeasible: {feasible.message}")
    result = minimize(target, feasible.x, method="SLSQP", bounds=bounds,
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


def constrained_portfolio_weights(
    returns: pd.DataFrame,
    objective: str,
    risk_free_rate: float = 0.0,
    target_return: float | None = None,
    minimum_weights: pd.Series | None = None,
    maximum_weights: pd.Series | None = None,
    groups: pd.Series | None = None,
    group_caps: dict[str, float] | None = None,
) -> pd.Series:
    """Optimize under explicit user-defined long-only allocation constraints."""
    if objective not in {"Minimum Variance", "Maximum Sharpe", "Target Return"}:
        raise ValueError("Unknown constrained optimization objective.")
    if objective == "Target Return" and target_return is None:
        raise ValueError("Target Return objective requires an arithmetic annual target.")
    internal = "max_sharpe" if objective == "Maximum Sharpe" else "min_variance"
    result = _optimize(
        returns, internal, risk_free_rate,
        target_return if objective == "Target Return" else None,
        minimum_weights, maximum_weights, groups, group_caps,
    )
    return result.rename(f"Constrained {objective}")


def constraint_validation_summary(
    weights: pd.Series,
    minimum_weights: pd.Series,
    maximum_weights: pd.Series,
    groups: pd.Series | None = None,
    group_caps: dict[str, float] | None = None,
) -> pd.DataFrame:
    """Report each explicit allocation constraint, result, and breach."""
    aligned = weights.index
    minimum = minimum_weights.reindex(aligned)
    maximum = maximum_weights.reindex(aligned)
    rows: list[dict[str, object]] = []
    total = float(weights.sum())
    rows.append({"Constraint": "Weights sum to 100%", "Result": total, "Limit": 1.0,
                 "Pass": bool(np.isclose(total, 1, atol=1e-6)), "Breach": abs(total - 1),
                 "Affected Asset": "Portfolio"})
    for ticker in aligned:
        below = max(float(minimum[ticker] - weights[ticker]), 0.0)
        above = max(float(weights[ticker] - maximum[ticker]), 0.0)
        rows.extend([
            {"Constraint": "Minimum asset weight", "Result": float(weights[ticker]),
             "Limit": float(minimum[ticker]), "Pass": below <= 1e-6, "Breach": below,
             "Affected Asset": ticker},
            {"Constraint": "Maximum asset weight", "Result": float(weights[ticker]),
             "Limit": float(maximum[ticker]), "Pass": above <= 1e-6, "Breach": above,
             "Affected Asset": ticker},
        ])
    labels = pd.Series("", index=aligned) if groups is None else groups.reindex(aligned).fillna("")
    for group, cap in (group_caps or {}).items():
        result = float(weights[labels == group].sum())
        breach = max(result - cap, 0.0)
        rows.append({"Constraint": f"Group cap: {group}", "Result": result, "Limit": cap,
                     "Pass": breach <= 1e-6, "Breach": breach,
                     "Affected Asset": ", ".join(map(str, weights.index[labels == group]))})
    return pd.DataFrame(rows)


def parse_group_caps(value: str) -> dict[str, float]:
    """Parse explicit ``Group:percentage`` pairs from the UI."""
    if not value.strip():
        return {}
    caps: dict[str, float] = {}
    try:
        for item in value.split(","):
            name, percent = item.split(":", maxsplit=1)
            clean_name = name.strip()
            if not clean_name or clean_name in caps:
                raise ValueError
            caps[clean_name] = float(percent.strip()) / 100
    except (TypeError, ValueError) as exc:
        raise ValueError("Group caps must use unique Group:percent pairs, for example Growth:60.") from exc
    return caps


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


def complete_portfolio_statistics(
    tangency_statistics: dict[str, float], risk_free_rate: float, risky_weight: float,
) -> dict[str, float]:
    """Combine the tangency portfolio with the risk-free asset without leverage.

    ``E[r_c] = r_f + y(E[r_T]-r_f)`` and ``sigma_c = y sigma_T`` for
    ``0 <= y <= 1``. Workbook 2 also illustrates borrowing for ``y > 1``;
    PortfolioLens intentionally keeps that case educational-only.
    """
    expected = tangency_statistics.get("Optimizer Expected Return", float("nan"))
    volatility = tangency_statistics.get("Optimizer Volatility", float("nan"))
    if not np.isfinite([expected, volatility, risk_free_rate, risky_weight]).all():
        raise ValueError("Complete-portfolio inputs must be finite.")
    if volatility <= 0:
        raise ValueError("The risky portfolio must have positive volatility.")
    if risky_weight < 0 or risky_weight > 1:
        raise ValueError("Risky allocation must be between 0% and 100% without leverage.")
    complete_expected = risk_free_rate + risky_weight * (expected - risk_free_rate)
    complete_volatility = risky_weight * volatility
    complete_sharpe = (
        (complete_expected - risk_free_rate) / complete_volatility
        if complete_volatility > 0 else float("nan")
    )
    return {
        "Risky Portfolio Weight": float(risky_weight),
        "Risk-Free Asset Weight": float(1.0 - risky_weight),
        "Optimizer Expected Return": float(complete_expected),
        "Optimizer Volatility": float(complete_volatility),
        "Optimizer Sharpe": float(complete_sharpe),
    }


def quadratic_utility(expected_return: float, volatility: float, risk_aversion: float) -> float:
    """Return mean-variance utility ``U = E[r] - 0.5 A sigma^2``."""
    if not np.isfinite([expected_return, volatility, risk_aversion]).all():
        raise ValueError("Utility inputs must be finite.")
    if volatility < 0:
        raise ValueError("Volatility cannot be negative.")
    if risk_aversion <= 0:
        raise ValueError("Risk aversion must be positive.")
    return float(expected_return - 0.5 * risk_aversion * volatility ** 2)


def utility_optimal_complete_portfolio(
    tangency_statistics: dict[str, float], risk_free_rate: float, risk_aversion: float,
) -> dict[str, float | bool]:
    """Select a lending-only complete portfolio using Workbook 3 utility.

    The unconstrained classroom solution is
    ``y* = (E[r_T] - r_f) / (A sigma_T^2)``. PortfolioLens applies its
    existing non-leveraged product boundary by clipping ``y*`` to ``[0, 1]``
    and reports whether that boundary changed the classroom solution.
    """
    expected = tangency_statistics.get("Optimizer Expected Return", float("nan"))
    volatility = tangency_statistics.get("Optimizer Volatility", float("nan"))
    if not np.isfinite([expected, volatility, risk_free_rate, risk_aversion]).all():
        raise ValueError("Utility-allocation inputs must be finite.")
    if volatility <= 0:
        raise ValueError("The risky portfolio must have positive volatility.")
    if risk_aversion <= 0:
        raise ValueError("Risk aversion must be positive.")
    unconstrained_weight = (expected - risk_free_rate) / (risk_aversion * volatility ** 2)
    applied_weight = float(np.clip(unconstrained_weight, 0.0, 1.0))
    complete = complete_portfolio_statistics(tangency_statistics, risk_free_rate, applied_weight)
    return {
        **complete,
        "Risk Aversion": float(risk_aversion),
        "Unconstrained Risky Portfolio Weight": float(unconstrained_weight),
        "Allocation Constraint Binding": not np.isclose(unconstrained_weight, applied_weight),
        "Quadratic Utility": quadratic_utility(
            complete["Optimizer Expected Return"], complete["Optimizer Volatility"], risk_aversion,
        ),
    }


def complete_portfolio_weights(tangency_weights: pd.Series, risky_weight: float) -> pd.Series:
    """Return risky-asset and risk-free weights for a non-leveraged complete portfolio."""
    if tangency_weights.empty or not np.isfinite(tangency_weights.to_numpy()).all():
        raise ValueError("Tangency weights must be finite and nonempty.")
    if not np.isclose(tangency_weights.sum(), 1.0, atol=1e-6):
        raise ValueError("Tangency weights must sum to one.")
    if (tangency_weights < -1e-10).any():
        raise ValueError("PortfolioLens complete portfolios require long-only tangency weights.")
    if not np.isfinite(risky_weight) or risky_weight < 0 or risky_weight > 1:
        raise ValueError("Risky allocation must be between 0% and 100% without leverage.")
    result = (tangency_weights * risky_weight).rename("Complete Portfolio Weight")
    result.loc["Risk-free asset"] = 1.0 - risky_weight
    return result


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
