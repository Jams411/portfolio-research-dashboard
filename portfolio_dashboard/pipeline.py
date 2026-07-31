"""One reusable analytics pipeline shared by the UI and integration tests."""
from dataclasses import dataclass
import pandas as pd
from .construction import allocation_methods
from .performance import performance_metrics, portfolio_returns, simple_returns
from .risk import benchmark_metrics, return_contributions, volatility_contributions

@dataclass(frozen=True)
class Analysis:
    prices: pd.DataFrame
    benchmark_prices: pd.Series
    asset_returns: pd.DataFrame
    portfolio_returns: pd.Series
    benchmark_returns: pd.Series
    performance: dict[str, float]
    benchmark: dict[str, float]
    return_contributions: pd.Series
    volatility_contributions: pd.Series
    allocations: pd.DataFrame
    allocation_warnings: list[str]

def run_analysis(prices: pd.DataFrame, benchmark_prices: pd.Series, weights: pd.Series, risk_free_rate: float = 0.0) -> Analysis:
    """Run the validated main analytics path on already aligned prices."""
    combined = prices.join(benchmark_prices.rename("Benchmark"), how="inner").dropna()
    if len(combined) < 3:
        raise ValueError("Insufficient common portfolio and benchmark history.")
    clean_prices, clean_benchmark = combined[prices.columns], combined["Benchmark"]
    asset_returns = simple_returns(clean_prices)
    benchmark_returns = simple_returns(clean_benchmark)
    portfolio = portfolio_returns(asset_returns, weights)
    allocations, warnings = allocation_methods(asset_returns, weights, risk_free_rate)
    return Analysis(clean_prices, clean_benchmark, asset_returns, portfolio, benchmark_returns,
                    performance_metrics(portfolio, risk_free_rate), benchmark_metrics(portfolio, benchmark_returns),
                    return_contributions(asset_returns, weights), volatility_contributions(asset_returns, weights),
                    allocations, warnings)
