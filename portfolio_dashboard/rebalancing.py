"""Practical target-allocation trade calculations."""

import numpy as np
import pandas as pd


def rebalancing_plan(current: pd.Series, target: pd.Series, portfolio_value: float, hold_threshold: float = 0.005) -> pd.DataFrame:
    """Build a self-financing buy/sell plan before transaction costs."""
    if portfolio_value <= 0 or set(current.index) != set(target.index):
        raise ValueError("Portfolio value must be positive and weight labels must match.")
    frame = pd.DataFrame({"Current Weight": current, "Target Weight": target[current.index]})
    frame["Weight Change"] = frame["Target Weight"] - frame["Current Weight"]
    frame["Current Dollar Allocation"] = frame["Current Weight"] * portfolio_value
    frame["Target Dollar Allocation"] = frame["Target Weight"] * portfolio_value
    frame["Estimated Buy / Sell"] = frame["Target Dollar Allocation"] - frame["Current Dollar Allocation"]
    frame["Action"] = np.where(frame["Weight Change"].abs() < hold_threshold, "Hold",
                               np.where(frame["Weight Change"] > 0, "Buy", "Sell"))
    return frame.rename_axis("Ticker").reset_index()
