"""CAPM and assumption-based factor-pricing calculations."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .config import TRADING_DAYS
from .performance import annualized_arithmetic_return
from .risk import single_index_regression_diagnostics


def capm_required_return(beta: float, risk_free_rate: float, market_return: float) -> float:
    """Return CAPM required return in the same annual units as the inputs."""
    values = np.asarray([beta, risk_free_rate, market_return], dtype=float)
    if not np.isfinite(values).all():
        raise ValueError("CAPM inputs must be finite.")
    return float(risk_free_rate + beta * (market_return - risk_free_rate))


def capm_alpha(
    actual_return: float, beta: float, risk_free_rate: float, market_return: float
) -> float:
    """Actual arithmetic return less the CAPM required return."""
    if not np.isfinite(actual_return):
        raise ValueError("Actual return must be finite.")
    return float(actual_return - capm_required_return(beta, risk_free_rate, market_return))


def security_market_line(
    betas: pd.Series | np.ndarray | list[float],
    risk_free_rate: float,
    market_return: float,
) -> pd.DataFrame:
    """Return sorted Security Market Line coordinates."""
    beta_values = pd.Series(betas, dtype=float, name="Beta")
    if beta_values.empty or not np.isfinite(beta_values).all():
        raise ValueError("Security Market Line betas must be nonempty and finite.")
    result = pd.DataFrame({"Beta": beta_values})
    result["CAPM Required Return"] = result["Beta"].map(
        lambda value: capm_required_return(value, risk_free_rate, market_return)
    )
    return result.sort_values("Beta").reset_index(drop=True)


def capm_security_table(
    asset_returns: pd.DataFrame,
    benchmark_returns: pd.Series,
    risk_free_rate: float = 0.0,
    periods_per_year: int = TRADING_DAYS,
) -> pd.DataFrame:
    """Compare realized arithmetic returns with CAPM required returns."""
    if asset_returns.empty:
        raise ValueError("CAPM security analysis requires at least one security.")
    aligned_market = benchmark_returns.dropna()
    if len(aligned_market) < 3:
        raise ValueError("CAPM security analysis requires at least three benchmark observations.")
    rows: dict[str, dict[str, float | str]] = {}
    for security in asset_returns.columns:
        metrics, observations = single_index_regression_diagnostics(
            asset_returns[security], benchmark_returns, risk_free_rate, periods_per_year
        )
        actual_return = annualized_arithmetic_return(
            observations["Security Return"], periods_per_year
        )
        market_return = annualized_arithmetic_return(
            observations["Benchmark Return"], periods_per_year
        )
        required = capm_required_return(
            metrics["Beta"], risk_free_rate, market_return
        )
        alpha_value = actual_return - required
        rows[str(security)] = {
            "Beta": metrics["Beta"],
            "Historical Arithmetic Return": actual_return,
            "CAPM Required Return": required,
            "Jensen's Alpha": alpha_value,
            "R-Squared": metrics["R-Squared"],
            "Residual Volatility": metrics["Residual Volatility"],
            "Position vs SML": "Above" if alpha_value > 0 else "Below" if alpha_value < 0 else "On",
            "Observations": metrics["Regression Observations"],
        }
    return pd.DataFrame.from_dict(rows, orient="index").rename_axis("Security")


def factor_expected_return(
    base_return: float,
    exposures: pd.Series,
    factor_premia: pd.Series,
) -> tuple[float, pd.DataFrame]:
    """Return assumption-based linear factor expected return and contributions.

    This is a pricing framework, not a factor-estimation routine. Exposures and
    premia must be supplied in matching decimal-return units.
    """
    exposures = pd.Series(exposures, dtype=float)
    factor_premia = pd.Series(factor_premia, dtype=float)
    if exposures.index.has_duplicates or factor_premia.index.has_duplicates:
        raise ValueError("Factor names must be unique.")
    if set(exposures.index) != set(factor_premia.index) or exposures.empty:
        raise ValueError("Factor exposures and premia must have matching nonempty factors.")
    factor_premia = factor_premia.reindex(exposures.index)
    values = np.r_[float(base_return), exposures.to_numpy(), factor_premia.to_numpy()]
    if not np.isfinite(values).all():
        raise ValueError("Factor-model inputs must be finite.")
    contributions = exposures * factor_premia
    table = pd.DataFrame({
        "Exposure": exposures,
        "Factor Premium": factor_premia,
        "Expected Return Contribution": contributions,
    })
    return float(base_return + contributions.sum()), table
