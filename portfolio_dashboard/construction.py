"""Long-only portfolio allocation methods."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import linprog, minimize

from .config import TRADING_DAYS
from .performance import sharpe_from_statistics

WEIGHT_TOLERANCE = 1e-7
RETURN_TOLERANCE = 1e-7


def annualized_optimizer_inputs(returns: pd.DataFrame) -> tuple[pd.Series, pd.DataFrame]:
    """Return aligned arithmetic means and sample covariance in annual units."""
    if returns.empty or len(returns) < 2 or returns.shape[1] == 0:
        raise RuntimeError("Optimization requires at least two return observations.")
    if not np.isfinite(returns.to_numpy()).all():
        raise RuntimeError("Optimization inputs must be finite and complete.")
    expected = returns.mean() * TRADING_DAYS
    covariance = returns.cov() * TRADING_DAYS
    if not np.isfinite(expected.to_numpy()).all() or not np.isfinite(covariance.to_numpy()).all():
        raise RuntimeError("Optimization estimates are not finite.")
    return expected, covariance


def optimizer_statistics(
    returns: pd.DataFrame, weights: pd.Series, risk_free_rate: float = 0.0
) -> dict[str, float]:
    """Historical arithmetic optimizer inputs evaluated at labeled weights."""
    aligned = weights.reindex(returns.columns)
    if aligned.isna().any():
        raise ValueError("Weight labels must match return columns.")
    expected_returns, covariance = annualized_optimizer_inputs(returns)
    expected = float(aligned @ expected_returns)
    variance = float(aligned @ covariance @ aligned)
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
    expected_series, covariance = annualized_optimizer_inputs(returns)
    cov = covariance.to_numpy()
    expected = expected_series.to_numpy()
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
    cleaned = np.where(np.abs(result.x) < WEIGHT_TOLERANCE, 0.0, result.x)
    cleaned = np.where(np.abs(cleaned - 1.0) < WEIGHT_TOLERANCE, 1.0, cleaned)
    cleaned = np.clip(cleaned, 0, 1)
    cleaned = cleaned / cleaned.sum()
    if abs(cleaned.sum() - 1.0) > WEIGHT_TOLERANCE or cleaned.min() < -WEIGHT_TOLERANCE:
        raise RuntimeError("Optimization result violates long-only weight constraints.")
    if target_return is not None and abs(float(cleaned @ expected) - target_return) > RETURN_TOLERANCE:
        raise RuntimeError("Optimization result violates the target-return constraint.")
    return pd.Series(cleaned, index=returns.columns)


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
    returns: pd.DataFrame, risk_free_rate: float = 0.0, points: int = 50,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Generate the long-only upper efficient branch, including tangency."""
    if points < 2:
        raise ValueError("Efficient frontier requires at least two points.")
    gmv = minimum_variance_weights(returns)
    gmv_return = optimizer_statistics(returns, gmv, risk_free_rate)["Optimizer Expected Return"]
    tangency = maximum_sharpe_weights(returns, risk_free_rate)
    tangency_return = optimizer_statistics(returns, tangency, risk_free_rate)["Optimizer Expected Return"]
    expected, _ = annualized_optimizer_inputs(returns)
    maximum_return = float(expected.max())
    base_targets = np.linspace(gmv_return, maximum_return, points)
    targets = np.unique(np.append(base_targets, np.clip(tangency_return, gmv_return, maximum_return)))
    targets.sort()
    rows: list[dict[str, float]] = []
    weights: dict[str, pd.Series] = {}
    failed_points = 0
    for target_return in targets:
        try:
            if np.isclose(target_return, gmv_return, atol=RETURN_TOLERANCE):
                candidate = gmv
            elif np.isclose(target_return, tangency_return, atol=RETURN_TOLERANCE):
                candidate = tangency
            else:
                candidate = target_return_weights(returns, float(target_return))
        except (ValueError, RuntimeError):
            failed_points += 1
            continue
        stats = optimizer_statistics(returns, candidate, risk_free_rate)
        if rows and stats["Optimizer Expected Return"] <= rows[-1]["Optimizer Expected Return"] + RETURN_TOLERANCE:
            continue
        if rows and stats["Optimizer Volatility"] < rows[-1]["Optimizer Volatility"] - WEIGHT_TOLERANCE:
            continue
        label = f"Frontier {len(rows) + 1}"
        rows.append({"Portfolio": label, "Target Return": float(target_return), **stats})
        weights[label] = candidate
    if not rows:
        raise RuntimeError("No feasible efficient-frontier points were produced.")
    frontier = pd.DataFrame(rows).set_index("Portfolio")
    frontier.attrs["Failed Points"] = failed_points
    return frontier, pd.DataFrame(weights)


def capital_allocation_line(
    tangency_statistics: dict[str, float], risk_free_rate: float, points: int = 20,
) -> pd.DataFrame:
    """Non-leveraged CAL from the risk-free asset to the constrained tangency portfolio."""
    if points < 2:
        raise ValueError("Capital Allocation Line requires at least two points.")
    volatility = tangency_statistics["Optimizer Volatility"]
    expected = tangency_statistics["Optimizer Expected Return"]
    if not np.isfinite([volatility, expected, risk_free_rate]).all() or volatility <= 0:
        raise ValueError("Tangency statistics must contain finite return and positive volatility.")
    sharpe = sharpe_from_statistics(expected, volatility, risk_free_rate)
    risky_weight = np.linspace(0.0, 1.0, points)
    return pd.DataFrame({
        "Risky Portfolio Weight": risky_weight,
        "Expected Return": risk_free_rate + risky_weight * volatility * sharpe,
        "Volatility": risky_weight * volatility,
        "Sharpe Ratio": np.where(risky_weight > 0, sharpe, np.nan),
    })


def optimization_diagnostics(
    returns: pd.DataFrame,
    weights: pd.Series,
    risk_free_rate: float,
    *,
    target_return: float | None = None,
    frontier: pd.DataFrame | None = None,
    tangency_statistics: dict[str, float] | None = None,
) -> dict[str, float | int | str | bool]:
    """Return auditable estimation, constraint, and reconciliation diagnostics."""
    expected, covariance = annualized_optimizer_inputs(returns)
    aligned = weights.reindex(expected.index)
    if aligned.isna().any():
        raise ValueError("Diagnostic weight labels must match return columns.")
    statistics = optimizer_statistics(returns, aligned, risk_free_rate)
    target_residual = (
        abs(statistics["Optimizer Expected Return"] - target_return)
        if target_return is not None else float("nan")
    )
    frontier_distance = float("nan")
    cal_residual = float("nan")
    if tangency_statistics is not None:
        if frontier is not None and not frontier.empty:
            distances = np.hypot(
                frontier["Optimizer Expected Return"] - tangency_statistics["Optimizer Expected Return"],
                frontier["Optimizer Volatility"] - tangency_statistics["Optimizer Volatility"],
            )
            frontier_distance = float(distances.min())
        line = capital_allocation_line(tangency_statistics, risk_free_rate, points=2)
        cal_residual = abs(
            float(line.iloc[-1]["Expected Return"])
            - tangency_statistics["Optimizer Expected Return"]
        )
    return {
        "Expected-return estimation": "Daily simple-return arithmetic mean × 252",
        "Covariance estimation": "Aligned daily sample covariance (n−1) × 252",
        "Annualization factor": TRADING_DAYS,
        "Observations": len(returns),
        "Optimizer success": not frontier.attrs.get("Failed Points", 0) if frontier is not None else True,
        "Failed frontier points": frontier.attrs.get("Failed Points", 0) if frontier is not None else 0,
        "Weight-sum residual": abs(float(aligned.sum()) - 1.0),
        "Lower-bound breach": max(-float(aligned.min()), 0.0),
        "Upper-bound breach": max(float(aligned.max()) - 1.0, 0.0),
        "Minimum weight": float(aligned.min()),
        "Maximum weight": float(aligned.max()),
        "Target-return residual": target_residual,
        "Tangency/frontier distance": frontier_distance,
        "CAL tangency residual": cal_residual,
        "Covariance condition number": float(np.linalg.cond(covariance.to_numpy())),
        "Covariance stabilization": "None",
    }


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
    """Select a lending-only complete portfolio using quadratic utility.

    The unconstrained mean-variance solution is
    ``y* = (E[r_T] - r_f) / (A sigma_T^2)``. PortfolioLens applies its
    existing non-leveraged product boundary by clipping ``y*`` to ``[0, 1]``
    and reports whether that boundary changed the unconstrained solution.
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
