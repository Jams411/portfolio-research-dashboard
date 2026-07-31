"""Display and report formatting shared by presentation layers."""
import math

PERCENT_METRICS = {
    "Total Return", "Buy & Hold Total Return", "CAGR", "Annualized Volatility",
    "Maximum Drawdown", "Best Daily Return", "Worst Daily Return",
    "Positive-Day Percentage", "Positive Active-Day Rate", "Portfolio Return",
    "Benchmark Return", "Excess Return", "Tracking Error", "Relative Drawdown",
    "Time in Market", "Turnover", "Historical VaR (95%)", "Historical CVaR (95%)",
}
COUNT_METRICS = {"Position Changes", "Warm-up Observations"}

def pct(value: float, decimals: int = 2) -> str:
    return "N/A" if value is None or not math.isfinite(float(value)) else f"{float(value):.{decimals}%}"

def ratio(value: float, decimals: int = 2) -> str:
    return "N/A" if value is None or not math.isfinite(float(value)) else f"{float(value):.{decimals}f}"

def money(value: float) -> str:
    return "N/A" if value is None or not math.isfinite(float(value)) else f"${float(value):,.2f}"


def metric_value(name: str, value: float) -> str:
    """Format a named metric with its financial unit, preserving ratios as ratios."""
    if name in PERCENT_METRICS:
        return pct(value)
    if name in COUNT_METRICS:
        return "N/A" if value is None or not math.isfinite(float(value)) else f"{int(value):,}"
    return ratio(value)
