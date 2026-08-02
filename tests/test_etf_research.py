"""Deterministic tests for the ETF research and look-through pipeline."""
import numpy as np
import pandas as pd
import pytest

from portfolio_dashboard.etf_research import (
    consolidated_security_exposure, etf_overlap, etf_research_metrics,
    filter_etf_research, holdings_coverage, normalize_holdings,
    parse_holdings_csv, rank_security_candidates,
)
from portfolio_dashboard.construction import maximum_sharpe_weights, optimizer_statistics


def test_etf_metrics_and_explicit_filter_rules():
    returns = pd.DataFrame({
        "STEADY": [.001, .002, .0015, .0025, .001] * 20,
        "VOLATILE": [.08, -.08, .07, -.07, .01] * 20,
    })
    metrics = etf_research_metrics(returns, risk_free_rate=.01, periods_per_year=12)
    assert list(metrics.index) == ["STEADY", "VOLATILE"]
    assert metrics.loc["STEADY", "Historical Arithmetic Return"] == pytest.approx(returns["STEADY"].mean() * 12)
    assert metrics.loc["STEADY", "Volatility"] == pytest.approx(returns["STEADY"].std(ddof=1) * np.sqrt(12))
    selected = filter_etf_research(metrics, min_observations=60, min_sharpe=0, max_volatility=.10)
    assert list(selected.index) == ["STEADY"]
    with pytest.raises(ValueError, match="missing columns"):
        filter_etf_research(pd.DataFrame({"Volatility": [.1]}))


def test_holdings_normalization_aggregates_duplicates_and_preserves_coverage():
    raw = pd.DataFrame({
        "ETF": [" spy ", "SPY", "qqq", "QQQ"],
        "Security": ["aapl", "AAPL", "AAPL", "MSFT"],
        "Holding Weight": [3.0, 2.0, 4.0, 5.0],
    })
    result = normalize_holdings(raw)
    assert result.query("ETF == 'SPY' and Security == 'AAPL'")["Holding Weight"].iloc[0] == pytest.approx(.05)
    coverage = holdings_coverage(result)
    assert coverage.loc["SPY", "Disclosed Weight"] == pytest.approx(.05)
    assert coverage.loc["QQQ", "Securities"] == 2


def test_holdings_schema_empty_and_invalid_totals_fail_clearly():
    with pytest.raises(ValueError, match="missing columns"):
        normalize_holdings(pd.DataFrame({"ETF": ["SPY"]}))
    with pytest.raises(ValueError, match="empty"):
        parse_holdings_csv(b"")
    with pytest.raises(ValueError, match="exceed 100%"):
        normalize_holdings(pd.DataFrame({
            "ETF": ["SPY", "SPY"], "Security": ["A", "B"], "Holding Weight": [.7, .6]
        }))


def test_weighted_exposure_and_overlap_reconcile():
    holdings = normalize_holdings(pd.DataFrame({
        "ETF": ["ETF1", "ETF1", "ETF2", "ETF2"],
        "Security": ["A", "B", "A", "C"],
        "Holding Weight": [.60, .40, .25, .75],
    }))
    exposure = consolidated_security_exposure(holdings, pd.Series({"ETF1": .4, "ETF2": .6}))
    assert exposure.loc["A", "Portfolio Exposure"] == pytest.approx(.39)
    assert exposure.loc["B", "Portfolio Exposure"] == pytest.approx(.16)
    assert exposure.loc["C", "Portfolio Exposure"] == pytest.approx(.45)
    assert exposure["Portfolio Exposure"].sum() == pytest.approx(1.0)
    overlap = etf_overlap(holdings).iloc[0]
    assert overlap["Shared Securities"] == 1
    assert overlap["Constituent Jaccard"] == pytest.approx(1 / 3)
    assert overlap["Weighted Overlap"] == pytest.approx(.25)


def test_security_screen_ranking_and_zero_residual_edge_case():
    regression = pd.DataFrame({
        "Regression Alpha": [.03, .02, -.01],
        "Alpha p-Value": [.04, .20, .01],
        "Regression Observations": [100, 100, 100],
        "Residual Volatility": [.10, .0, .12],
        "Beta": [1.0, .8, 1.2],
        "R-Squared": [.7, .5, .8],
    }, index=["PASS", "NOT_SIGNIFICANT", "NEGATIVE"])
    ranked = rank_security_candidates(regression)
    assert ranked.index[0] == "PASS"
    assert bool(ranked.loc["PASS", "Passes Screen"])
    assert not bool(ranked.loc["NOT_SIGNIFICANT", "Passes Screen"])
    assert np.isnan(ranked.loc["NOT_SIGNIFICANT", "Alpha / Residual Variance"])


def test_holdings_csv_export_round_trip_is_consistent():
    original = pd.DataFrame({
        "ETF": ["SPY", "QQQ"], "Security": ["AAPL", "MSFT"], "Holding Weight": [.1, .2]
    })
    parsed = parse_holdings_csv(original.to_csv(index=False).encode())
    reparsed = parse_holdings_csv(parsed.to_csv(index=False).encode())
    pd.testing.assert_frame_equal(parsed, reparsed)


def test_end_to_end_research_pipeline_with_fixed_local_data():
    returns = pd.DataFrame({
        "ETF1": [.003, -.001, .004, .002, .001] * 20,
        "ETF2": [.002, .001, -.001, .003, .002] * 20,
    })
    metrics = etf_research_metrics(returns, risk_free_rate=0.0, periods_per_year=12)
    selected = filter_etf_research(metrics, 60, 0.0, 1.0)
    assert set(selected.index) == {"ETF1", "ETF2"}
    holdings = parse_holdings_csv(
        b"ETF,Security,Holding Weight\nETF1,A,60\nETF1,B,40\nETF2,A,20\nETF2,C,80\n"
    )
    exposure = consolidated_security_exposure(holdings, pd.Series({"ETF1": .55, "ETF2": .45}))
    assert exposure["Portfolio Exposure"].sum() == pytest.approx(1.0)
    assert exposure.index[0] == "A"
    regression = pd.DataFrame({
        "Regression Alpha": [.04, .01], "Alpha p-Value": [.01, .25],
        "Regression Observations": [100, 100], "Residual Volatility": [.10, .12],
    }, index=["A", "B"])
    ranked = rank_security_candidates(regression)
    assert ranked.index[0] == "A" and ranked.loc["A", "Passes Screen"]
    candidate_returns = returns.rename(columns={"ETF1": "A", "ETF2": "B"})
    optimized = maximum_sharpe_weights(candidate_returns, risk_free_rate=0.0)
    stats = optimizer_statistics(candidate_returns, optimized, 0.0)
    assert optimized.sum() == pytest.approx(1.0)
    assert (optimized >= 0).all() and (optimized <= 1).all()
    assert np.isfinite(stats["Optimizer Expected Return"])
