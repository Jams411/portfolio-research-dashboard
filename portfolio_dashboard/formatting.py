"""Display and report formatting shared by presentation layers."""
import math

PERCENT_METRICS = {
    "Total Return", "Buy & Hold Total Return", "Historical Arithmetic Annualized Return",
    "CAGR", "Annualized Volatility",
    "Maximum Drawdown", "Best Daily Return", "Worst Daily Return",
    "Positive-Day Percentage", "Positive Active-Day Rate", "Portfolio Return",
    "Benchmark Return", "Excess Return", "Tracking Error", "Relative Drawdown",
    "Annualized Active Return",
    "Regression Alpha", "Residual Volatility", "Systematic Risk Share",
    "Idiosyncratic Risk Share", "CAPM Required Return", "Jensen's Alpha", "Treynor Ratio",
    "CML Required Return at Portfolio Risk", "Selectivity", "Diversification Effect",
    "Net Selectivity", "Overall Performance",
    "Time in Market", "Turnover", "Historical VaR (95%)", "Historical CVaR (95%)",
}
COUNT_METRICS = {
    "Position Changes", "Warm-up Observations", "Regression Observations",
    "Rebalancing Dates",
}

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
    if name in {"Annualized Variance", "Systematic Variance", "Idiosyncratic Variance"}:
        return ratio(value, 4)
    if name in COUNT_METRICS:
        return "N/A" if value is None or not math.isfinite(float(value)) else f"{int(value):,}"
    return ratio(value)
