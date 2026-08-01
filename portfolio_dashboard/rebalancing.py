"""Practical target-allocation trade calculations."""

import numpy as np
import pandas as pd

from .performance import performance_metrics


def rebalancing_plan(current: pd.Series, target: pd.Series, portfolio_value: float, hold_threshold: float = 0.0) -> pd.DataFrame:
    """Build a self-financing buy/sell plan before transaction costs.

    ``hold_threshold`` is opt-in. When supplied, it changes only the action label;
    the estimated amount remains the exact target-allocation gap for transparency.
    """
    if portfolio_value <= 0 or set(current.index) != set(target.index):
        raise ValueError("Portfolio value must be positive and weight labels must match.")
    frame = pd.DataFrame({"Current Weight": current, "Target Weight": target[current.index]})
    frame["Weight Change"] = frame["Target Weight"] - frame["Current Weight"]
    frame["Current Dollar Allocation"] = frame["Current Weight"] * portfolio_value
    frame["Target Dollar Allocation"] = frame["Target Weight"] * portfolio_value
    frame["Estimated Buy / Sell"] = frame["Target Dollar Allocation"] - frame["Current Dollar Allocation"]
    frame["Action"] = np.where(frame["Weight Change"].abs() <= hold_threshold, "Hold",
                               np.where(frame["Weight Change"] > 0, "Buy", "Sell"))
    return frame.rename_axis("Ticker").reset_index()


def _is_period_end(index: pd.DatetimeIndex, position: int, policy: str) -> bool:
    if position >= len(index) - 1:
        return False
    frequency = {"Monthly": "M", "Quarterly": "Q", "Annual": "Y"}[policy]
    return index[position].to_period(frequency) != index[position + 1].to_period(frequency)


def simulate_rebalancing(
    asset_returns: pd.DataFrame,
    target_weights: pd.Series,
    initial_value: float,
    policy: str,
    transaction_cost_rate: float = 0.0,
    threshold: float = 0.05,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Simulate buy-and-hold, periodic, or threshold rebalancing."""
    allowed = {"Buy and Hold", "Monthly", "Quarterly", "Annual", "Threshold"}
    if policy not in allowed:
        raise ValueError(f"Policy must be one of: {', '.join(sorted(allowed))}.")
    if initial_value <= 0 or transaction_cost_rate < 0 or threshold < 0:
        raise ValueError("Value must be positive and cost/threshold assumptions nonnegative.")
    if not isinstance(asset_returns.index, pd.DatetimeIndex) or not asset_returns.index.is_monotonic_increasing:
        raise ValueError("Rebalancing returns require a sorted DatetimeIndex.")
    if asset_returns.empty or asset_returns.isna().any().any() or not np.isfinite(asset_returns.to_numpy()).all():
        raise ValueError("Rebalancing returns must be finite, complete, and nonempty.")
    if (asset_returns <= -1).any().any():
        raise ValueError("Asset returns must be greater than -100%.")
    weights = target_weights.reindex(asset_returns.columns).astype(float)
    if weights.isna().any() or (weights < 0).any() or not np.isclose(weights.sum(), 1, atol=1e-6):
        raise ValueError("Target weights must match assets, be nonnegative, and sum to 100%.")

    holdings = weights * initial_value
    prior_value = float(initial_value)
    daily_rows: list[dict[str, object]] = []
    trades: list[dict[str, object]] = []
    for position, (date, returns) in enumerate(asset_returns.iterrows()):
        holdings = holdings * (1 + returns)
        gross_value = float(holdings.sum())
        before_weights = holdings / gross_value
        drift = before_weights - weights
        trigger = (
            policy in {"Monthly", "Quarterly", "Annual"}
            and _is_period_end(asset_returns.index, position, policy)
        ) or (policy == "Threshold" and float(drift.abs().max()) >= threshold)
        turnover = 0.0
        cost = 0.0
        if trigger:
            pre_cost_target = weights * gross_value
            trade_values = pre_cost_target - holdings
            gross_traded = float(trade_values.abs().sum())
            turnover = float(0.5 * gross_traded / gross_value)
            cost = float(gross_traded * transaction_cost_rate)
            holdings = weights * (gross_value - cost)
            for ticker in weights.index:
                trades.append({
                    "Date": date, "Policy": policy, "Ticker": ticker,
                    "Before Weight": float(before_weights[ticker]),
                    "Target Weight": float(weights[ticker]), "After Weight": float(weights[ticker]),
                    "Trade Before Cost": float(trade_values[ticker]),
                    "Estimated Transaction Cost": (
                        float(cost * abs(trade_values[ticker]) / gross_traded) if gross_traded > 0 else 0.0
                    ),
                    "Drift Before Trade": float(drift[ticker]),
                })
        end_value = float(holdings.sum())
        end_weights = holdings / end_value
        daily_rows.append({
            "Date": date, "Portfolio Value": end_value, "Gross Value Before Trade": gross_value,
            "Daily Return": end_value / prior_value - 1, "Turnover": turnover,
            "Transaction Costs": cost, "Maximum Drift": float((end_weights - weights).abs().max()),
            "Rebalanced": bool(trigger),
        })
        prior_value = end_value
    daily = pd.DataFrame(daily_rows).set_index("Date")
    trade_columns = [
        "Date", "Policy", "Ticker", "Before Weight", "Target Weight", "After Weight",
        "Trade Before Cost", "Estimated Transaction Cost", "Drift Before Trade",
    ]
    return daily, pd.DataFrame(trades, columns=trade_columns)


def compare_rebalancing_policies(
    asset_returns: pd.DataFrame,
    target_weights: pd.Series,
    initial_value: float,
    transaction_cost_rate: float = 0.0,
    threshold: float = 0.05,
    risk_free_rate: float = 0.0,
) -> tuple[pd.DataFrame, dict[str, pd.DataFrame], dict[str, pd.DataFrame]]:
    """Evaluate supported policies on a common path and assumptions."""
    histories: dict[str, pd.DataFrame] = {}
    trades: dict[str, pd.DataFrame] = {}
    rows: dict[str, dict[str, float]] = {}
    for policy in ("Buy and Hold", "Monthly", "Quarterly", "Annual", "Threshold"):
        daily, trade_history = simulate_rebalancing(
            asset_returns, target_weights, initial_value, policy, transaction_cost_rate, threshold,
        )
        histories[policy], trades[policy] = daily, trade_history
        metrics = performance_metrics(daily["Daily Return"], risk_free_rate)
        rows[policy] = {
            "Total Return": metrics["Total Return"], "CAGR": metrics["CAGR"],
            "Annualized Volatility": metrics["Annualized Volatility"],
            "Sharpe Ratio": metrics["Sharpe Ratio"], "Maximum Drawdown": metrics["Maximum Drawdown"],
            "Total Turnover": float(daily["Turnover"].sum()),
            "Transaction Costs": float(daily["Transaction Costs"].sum()),
            "Rebalancing Dates": float(daily["Rebalanced"].sum()),
            "Ending Maximum Drift": float(daily["Maximum Drift"].iloc[-1]),
        }
    return pd.DataFrame.from_dict(rows, orient="index").rename_axis("Policy"), histories, trades
