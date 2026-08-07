"""Deterministic end-to-end PortfolioLens research workflow."""

import numpy as np
import pandas as pd
import pytest

from portfolio_dashboard.asset_pricing import capm_security_table, security_market_line
from portfolio_dashboard.construction import (
    constrained_portfolio_weights, constraint_validation_summary, efficient_frontier,
    optimizer_statistics, target_return_weights,
)
from portfolio_dashboard.performance import portfolio_returns
from portfolio_dashboard.etf_research import etf_research_metrics, rank_security_candidates
from portfolio_dashboard.pipeline import run_analysis
from portfolio_dashboard.rebalancing import compare_rebalancing_policies, rebalancing_plan
from portfolio_dashboard.reporting import generate_html_report, research_summary
from portfolio_dashboard.research import (
    deterministic_insights, portfolio_comparison, portfolio_health_score,
)
from portfolio_dashboard.risk import historical_cvar, historical_var, security_single_index_table
from portfolio_dashboard.strategy import momentum_backtest
from portfolio_dashboard.stress import custom_shock


def metric_frame(values: dict[str, float]) -> pd.DataFrame:
    return pd.DataFrame({"Value": values})


def test_complete_four_etf_research_workflow():
    tickers = ["SPY", "QQQ", "TLT", "GLD"]
    weights = pd.Series({"SPY": .40, "QQQ": .25, "TLT": .20, "GLD": .15})
    index = pd.bdate_range("2020-01-02", periods=900)
    x = np.arange(len(index), dtype=float)
    market = .00035 + .006 * np.sin(x / 17) + .002 * np.cos(x / 43)
    return_frame = pd.DataFrame({
        "SPY": market + .0010 * np.sin(x / 7),
        "QQQ": .00015 + 1.20 * market + .0015 * np.cos(x / 11),
        "TLT": .00010 - .25 * market + .0020 * np.sin(x / 19),
        "GLD": .00012 + .10 * market + .0025 * np.cos(x / 23),
    }, index=index)
    prices = 100 * (1 + return_frame).cumprod()
    benchmark_returns = pd.Series(.00020 + .95 * market, index=index, name="SPX")
    benchmark_prices = 100 * (1 + benchmark_returns).cumprod()

    analysis = run_analysis(prices, benchmark_prices, weights, .04)
    assert set(analysis.asset_returns.columns) == set(tickers)
    assert analysis.return_contributions.sum() == pytest.approx(analysis.performance["Total Return"])
    assert analysis.volatility_contributions.sum() == pytest.approx(analysis.performance["Annualized Volatility"])
    assert np.isfinite(analysis.benchmark["Jensen's Alpha"])
    assert analysis.benchmark["Information Ratio"] == pytest.approx(
        analysis.benchmark["Annualized Active Return"] / analysis.benchmark["Tracking Error"]
    )

    frontier, frontier_weights = efficient_frontier(analysis.asset_returns, .04, 15)
    target = float(frontier.iloc[7]["Optimizer Expected Return"])
    target_weights = target_return_weights(analysis.asset_returns, target)
    assert optimizer_statistics(analysis.asset_returns, target_weights, .04)["Optimizer Expected Return"] == pytest.approx(target)

    groups = pd.Series({"SPY": "Equity", "QQQ": "Equity", "TLT": "Defensive", "GLD": "Defensive"})
    minimum = pd.Series(0.0, index=tickers)
    maximum = pd.Series(1.0, index=tickers)
    constrained = constrained_portfolio_weights(
        analysis.asset_returns, "Minimum Variance", minimum_weights=minimum,
        maximum_weights=maximum, groups=groups, group_caps={"Equity": .70},
    )
    validation = constraint_validation_summary(
        constrained, minimum, maximum, groups, {"Equity": .70},
    )
    assert validation["Pass"].all()

    policy_summary, policy_histories, policy_trades = compare_rebalancing_policies(
        asset_returns=analysis.asset_returns,
        target_weights=weights,
        initial_value=100_000,
        transaction_cost_rate=.001,
        threshold=.05,
        risk_free_rate=.04,
        benchmark_returns=benchmark_returns,
    )
    assert policy_summary.loc["Buy and Hold", "Rebalancing Dates"] == 0
    assert policy_summary.loc["Monthly", "Transaction Costs"] > 0
    assert not policy_trades["Quarterly"].empty
    assert {
        "Annualized Active Return", "Mean Absolute Periodic Difference",
        "Tracking Error", "Information Ratio",
    } <= set(policy_summary.columns)

    strategy_data, strategy_metrics = momentum_backtest(
        analysis.prices["SPY"], 20, 60, .001, .04,
    )
    assert strategy_data["Strategy Growth"].notna().any()
    shocks = pd.Series({"SPY": -.12, "QQQ": -.18, "TLT": .04, "GLD": .06})
    shock_table, shock_summary = custom_shock(weights, shocks, 100_000)
    assert shock_table["Portfolio Impact"].sum() == pytest.approx(shock_summary["Estimated Portfolio Impact"])

    cvar = historical_cvar(analysis.portfolio_returns)
    score, coverage, health = portfolio_health_score(
        analysis.performance, analysis.benchmark, weights, cvar,
    )
    comparisons = portfolio_comparison(analysis.asset_returns, analysis.allocations, weights, .04)
    insights = deterministic_insights(
        analysis.performance, analysis.benchmark, weights,
        analysis.volatility_contributions, cvar,
    )
    summary = research_summary(
        analysis.performance, analysis.benchmark, weights, analysis.return_contributions,
        analysis.volatility_contributions, strategy_metrics, shock_summary,
    )
    security_table = security_single_index_table(analysis.asset_returns, benchmark_returns, .04)
    capm_table = capm_security_table(analysis.asset_returns, benchmark_returns, risk_free_rate=.04)
    etf_table = etf_research_metrics(analysis.asset_returns, .04)
    security_screen = rank_security_candidates(security_table)
    evaluation_table = pd.DataFrame({"Portfolio": analysis.performance, "Benchmark-relative": analysis.benchmark})
    report = generate_html_report(
        title="PortfolioLens Investment Research Report", tickers=tickers, weights=weights,
        start=analysis.prices.index.min().date(), end=analysis.prices.index.max().date(),
        summary=summary, performance=metric_frame(analysis.performance),
        risk=metric_frame({"Historical VaR (95%)": historical_var(analysis.portfolio_returns),
                           "Historical CVaR (95%)": cvar}),
        benchmark=metric_frame(analysis.benchmark),
        attribution=pd.concat([analysis.return_contributions, analysis.volatility_contributions], axis=1),
        allocations=analysis.allocations,
        rebalancing=rebalancing_plan(weights, analysis.allocations["Equal Weight"], 100_000),
        rebalancing_method="Equal Weight", strategy=metric_frame(strategy_metrics), stress=shock_table,
        benchmark_ticker="SPX", risk_free_rate=.04, initial_value=100_000,
        health_score=score, health_coverage=coverage, health_components=health,
        comparison=comparisons, insights=insights, efficient_frontier=frontier,
        optimized_allocations=frontier_weights, rebalancing_policies=policy_summary,
        rebalancing_history=policy_histories["Quarterly"],
        constrained_allocation=constrained.rename("Constrained Weight").to_frame(),
        constraint_validation=validation, transaction_cost_rate=.001,
        rebalancing_threshold=.05, selected_rebalancing_policy="Quarterly",
        strategy_short_window=20, strategy_long_window=60,
        security_analysis=security_table, asset_pricing=capm_table,
        performance_evaluation=evaluation_table, etf_research=etf_table,
        security_screen=security_screen,
    )

    sml = security_market_line([-0.5, 0.0, 1.0, 1.5], .04, benchmark_returns.mean() * 252)
    assert capm_table.index.tolist() == ["SPY", "QQQ", "TLT", "GLD"]
    assert capm_table["Observations"].eq(len(analysis.asset_returns)).all()
    assert sml.loc[sml["Beta"].eq(0), "CAPM Required Return"].iloc[0] == pytest.approx(.04)
    html = report.decode()
    assert len(report) > 10_000
    assert "Fixed income —" not in html
    for section in (
        "Portfolio inputs", "Benchmark comparison", "Efficient frontier",
        "Optimized allocations", "Rebalancing policy comparison",
        "Momentum-strategy results", "Stress-test results", "Limitations and disclaimer",
        "Performance evaluation", "Single-index security analysis", "CAPM and asset pricing",
        "ETF universe research", "Security candidate screen",
    ):
        assert section in html
