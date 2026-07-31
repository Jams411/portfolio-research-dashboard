"""Deterministic unit and integration tests for financial calculations."""
import numpy as np
import pandas as pd
import pytest

from portfolio_dashboard.construction import inverse_volatility_weights, maximum_sharpe_weights, minimum_variance_weights
from portfolio_dashboard.data import InputError, MarketDataError, align_prices, extract_adjusted_prices, parse_tickers, validate_weights
from portfolio_dashboard.performance import (annualized_volatility, cagr, drawdown_series, max_drawdown,
    performance_metrics, portfolio_returns, sharpe_ratio, simple_returns, sortino_ratio)
from portfolio_dashboard.pipeline import run_analysis
from portfolio_dashboard.rebalancing import rebalancing_plan
from portfolio_dashboard.risk import beta, historical_cvar, historical_var, information_ratio, tracking_error, volatility_contributions
from portfolio_dashboard.strategy import momentum_backtest
from portfolio_dashboard.stress import custom_shock, historical_stress

@pytest.fixture
def returns() -> pd.DataFrame:
    index = pd.bdate_range("2020-01-01", periods=300)
    x = np.arange(300)
    return pd.DataFrame({"A": 0.0005 + 0.008 * np.sin(x / 9), "B": 0.0002 + 0.004 * np.cos(x / 13)}, index=index)

def test_ticker_and_weight_validation():
    assert parse_tickers(" aapl, MSFT, aapl ") == ["AAPL", "MSFT"]
    weights, changed = validate_weights(["A", "B"], [60, 40])
    assert weights.sum() == pytest.approx(1); assert not changed
    normalized, changed = validate_weights(["A", "B"], [0.5002, 0.5002])
    assert normalized.sum() == pytest.approx(1); assert changed
    with pytest.raises(InputError): validate_weights(["A"], [-1])
    with pytest.raises(InputError): validate_weights(["A", "B"], [1])

def test_simple_and_portfolio_returns():
    prices = pd.DataFrame({"A": [100, 110, 99], "B": [100, 100, 110]})
    result = simple_returns(prices)
    assert result.iloc[0].tolist() == pytest.approx([.1, 0])
    p = portfolio_returns(result, pd.Series({"A": .6, "B": .4}))
    assert p.iloc[0] == pytest.approx(.06)

def test_missing_data_policy():
    prices = pd.DataFrame({"A": [1, 2, np.nan, 4], "B": [1, np.nan, 3, 4]})
    aligned = align_prices(prices, ["A", "B"], min_observations=2)
    assert len(aligned) == 2 and not aligned.isna().any().any()
    with pytest.raises(MarketDataError): align_prices(prices, ["A", "C"], min_observations=1)

def test_extract_single_and_multiindex_prices():
    raw = pd.DataFrame({"Adj Close": [10, 11], "Close": [9, 10]})
    assert list(extract_adjusted_prices(raw, ["A"]).columns) == ["A"]
    columns = pd.MultiIndex.from_product([["Adj Close", "Close"], ["A", "B"]])
    multi = pd.DataFrame(np.arange(8).reshape(2, 4), columns=columns)
    assert list(extract_adjusted_prices(multi, ["A", "B"]).columns) == ["A", "B"]

def test_performance_formulas():
    r = pd.Series([.01, -.02, .03, .01])
    expected_cagr = (np.prod(1 + r) ** (252 / 4)) - 1
    assert cagr(r) == pytest.approx(expected_cagr)
    assert annualized_volatility(r) == pytest.approx(r.std(ddof=1) * np.sqrt(252))
    assert sharpe_ratio(r, .02) == pytest.approx((expected_cagr - .02) / annualized_volatility(r))
    assert np.isfinite(sortino_ratio(pd.Series([.01, -.01, .02, -.03, .01])))
    dd = drawdown_series(pd.Series([.1, -.2, .1]))
    assert max_drawdown(pd.Series([.1, -.2, .1])) == pytest.approx(dd.min())

def test_var_cvar_beta_and_relative_metrics():
    benchmark = pd.Series([-.03, -.02, -.01, 0, .01, .02])
    portfolio = benchmark * 1.5
    assert historical_var(portfolio, .95) > 0
    assert historical_cvar(portfolio, .95) >= historical_var(portfolio, .95)
    assert beta(portfolio, benchmark) == pytest.approx(1.5)
    assert tracking_error(portfolio, benchmark) > 0
    assert np.isfinite(information_ratio(portfolio + .001, benchmark))

def test_risk_contributions_reconcile(returns):
    weights = pd.Series({"A": .6, "B": .4})
    contribution = volatility_contributions(returns, weights)
    portfolio_vol = np.sqrt(float(weights @ (returns.cov() * 252) @ weights))
    assert contribution.sum() == pytest.approx(portfolio_vol)

def test_allocation_methods_and_constraints(returns):
    inverse = inverse_volatility_weights(returns)
    assert inverse.sum() == pytest.approx(1); assert (inverse >= 0).all()
    assert inverse["B"] > inverse["A"]
    for weights in (minimum_variance_weights(returns), maximum_sharpe_weights(returns)):
        assert weights.sum() == pytest.approx(1, abs=1e-6)
        assert ((weights >= 0) & (weights <= 1)).all()

def test_rebalancing_reconciles():
    plan = rebalancing_plan(pd.Series({"A": .7, "B": .3}), pd.Series({"A": .5, "B": .5}), 100_000)
    assert plan["Estimated Buy / Sell"].sum() == pytest.approx(0)
    assert plan.set_index("Ticker").loc["A", "Action"] == "Sell"
    assert plan.set_index("Ticker").loc["B", "Action"] == "Buy"

def test_strategy_signal_lag_and_transaction_costs():
    prices = pd.Series([10, 11, 12, 13, 12, 11, 14, 15], index=pd.bdate_range("2024-01-01", periods=8))
    free, _ = momentum_backtest(prices, 2, 3, 0)
    costly, metrics = momentum_backtest(prices, 2, 3, .01)
    expected = free["Signal"].shift(1).fillna(0)
    pd.testing.assert_series_equal(free["Position"], expected, check_names=False)
    assert (costly["Strategy Return"] <= free["Strategy Return"] + 1e-15).all()
    assert metrics["Number of Trades"] == int((costly["Turnover"] > 0).sum())

def test_custom_and_historical_stress():
    weights = pd.Series({"A": .6, "B": .4}); shocks = pd.Series({"A": -.2, "B": -.1})
    table, summary = custom_shock(weights, shocks, 1000)
    assert summary["Estimated Portfolio Impact"] == pytest.approx(-.16)
    assert summary["After Value"] == pytest.approx(840)
    dates = pd.bdate_range("2019-01-01", "2023-01-01")
    prices = pd.DataFrame({"A": np.linspace(100, 150, len(dates)), "B": np.linspace(100, 120, len(dates))}, index=dates)
    result = historical_stress(prices, weights, prices["A"])
    assert set(result["Scenario"]) == {"COVID-19 market decline", "2022 equity and rate shock"}
    assert result["Complete"].all()

def test_main_pipeline_integration(returns):
    prices = 100 * (1 + returns).cumprod()
    benchmark_returns = .7 * returns["A"] + .3 * returns["B"]
    benchmark_prices = 100 * (1 + benchmark_returns).cumprod()
    weights = pd.Series({"A": .6, "B": .4})
    result = run_analysis(prices, benchmark_prices, weights, .02)
    assert result.performance["Total Return"] == pytest.approx((1 + result.portfolio_returns).prod() - 1)
    assert result.return_contributions.sum() == pytest.approx(result.performance["Total Return"])
    assert result.volatility_contributions.sum() == pytest.approx(result.performance["Annualized Volatility"])
    assert set(["Current", "Equal Weight", "Inverse Volatility"]).issubset(result.allocations.columns)
