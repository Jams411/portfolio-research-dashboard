"""Deterministic fixed-income pricing, risk, portfolio, scenario, and selection tests."""
from datetime import date

import numpy as np
import pandas as pd
import pytest

import portfolio_dashboard.fixed_income as fi
from portfolio_dashboard.bond_portfolio import (
    analyze_bond_portfolio,
    construct_bond_portfolio,
    filter_and_rank_bonds,
    portfolio_rate_scenario,
)
from portfolio_dashboard.fixed_income import (
    BondTerms,
    accrued_interest,
    bond_risk_metrics,
    cash_flow_schedule,
    clean_price,
    current_yield,
    dirty_price,
    duration_convexity_price_change,
    duration_price_change,
    yield_shock_analysis,
    yield_to_maturity,
)


SETTLEMENT = date(2026, 1, 1)


def terms(years=5, coupon=0.05, frequency=2, settlement=SETTLEMENT, day_count="Actual/Actual"):
    return BondTerms(1000, coupon, frequency, settlement, date(2026 + years, 1, 1), day_count)


def sample_holdings() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Bond": "Bond A", "Quantity": 10, "Face Value": 1000, "Coupon Rate": 0.04,
                "Frequency": 2, "Settlement": SETTLEMENT, "Maturity": date(2031, 1, 1),
                "YTM": 0.05, "Clean Price": np.nan, "Day Count": "Actual/Actual",
                "Issuer": "Issuer A", "Sector": "Government", "Credit Quality": "AA",
                "Callable": "No", "Tax Status": "Taxable",
            },
            {
                "Bond": "Bond B", "Quantity": 5, "Face Value": 1000, "Coupon Rate": 0.06,
                "Frequency": 2, "Settlement": SETTLEMENT, "Maturity": date(2036, 1, 1),
                "YTM": 0.055, "Clean Price": np.nan, "Day Count": "Actual/Actual",
                "Issuer": "Issuer B", "Sector": "Corporate", "Credit Quality": "A",
                "Callable": "No", "Tax Status": "Taxable",
            },
        ]
    )


@pytest.mark.parametrize("frequency", [1, 2, 4, 12])
def test_par_bond_and_supported_coupon_frequencies(frequency):
    bond = terms(coupon=0.05, frequency=frequency)
    assert dirty_price(bond, 0.05) == pytest.approx(1000.0, abs=1e-8)
    assert clean_price(bond, 0.05) == pytest.approx(1000.0, abs=1e-8)
    assert len(cash_flow_schedule(bond)) == 5 * frequency


def test_premium_discount_and_zero_coupon_pricing():
    bond = terms(coupon=0.05)
    assert clean_price(bond, 0.04) > 1000
    assert clean_price(bond, 0.06) < 1000
    zero = terms(coupon=0.0)
    expected = 1000 / (1 + 0.06 / 2) ** 10
    assert dirty_price(zero, 0.06) == pytest.approx(expected)
    assert current_yield(zero, expected) == 0
    assert len(cash_flow_schedule(zero)) == 1


def test_clean_dirty_price_and_accrued_interest_actual_actual():
    bond = BondTerms(1000, 0.06, 2, date(2026, 4, 1), date(2031, 1, 1))
    accrued = accrued_interest(bond)
    expected_fraction = 90 / 181
    assert accrued == pytest.approx(30 * expected_fraction)
    assert dirty_price(bond, 0.05) - clean_price(bond, 0.05) == pytest.approx(accrued)


def test_30_360_accrued_interest():
    bond = BondTerms(1000, 0.06, 2, date(2026, 4, 1), date(2031, 1, 1), "30/360")
    assert accrued_interest(bond) == pytest.approx(15.0)


def test_current_yield_and_ytm_recovery():
    bond = terms(coupon=0.04)
    price = clean_price(bond, 0.0525)
    assert current_yield(bond, price) == pytest.approx(40 / price)
    assert yield_to_maturity(bond, price) == pytest.approx(0.0525, abs=1e-10)


@pytest.mark.parametrize("price", [0, -10, np.nan])
def test_invalid_market_prices_fail(price):
    with pytest.raises(ValueError, match="positive"):
        yield_to_maturity(terms(), price)


def test_impossible_yield_and_solver_failure(monkeypatch):
    with pytest.raises(ValueError, match="discount factor"):
        dirty_price(terms(), -2.0)
    with pytest.raises(ValueError, match="bracketed"):
        yield_to_maturity(terms(), 1000, lower=0.20, upper=0.30)
    monkeypatch.setattr(fi, "brentq", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError()))
    with pytest.raises(ValueError, match="did not converge"):
        yield_to_maturity(terms(), 1000)


def test_duration_units_sign_dollar_duration_and_dv01():
    metrics = bond_risk_metrics(terms(coupon=0.04), 0.05)
    assert 0 < metrics["Modified Duration"] < metrics["Macaulay Duration"] < 5
    assert metrics["Dollar Duration"] == pytest.approx(
        metrics["Modified Duration"] * metrics["Dirty Price"]
    )
    assert metrics["DV01"] == pytest.approx(metrics["Dollar Duration"] * 0.0001)
    assert duration_price_change(metrics["Modified Duration"], 0.01) < 0


def test_zero_coupon_duration():
    metrics = bond_risk_metrics(terms(coupon=0.0), 0.05)
    assert metrics["Macaulay Duration"] == pytest.approx(5.0)
    assert metrics["Modified Duration"] == pytest.approx(5 / 1.025)


def test_convexity_and_approximation_improvement():
    bond = terms(years=10, coupon=0.05)
    metrics = bond_risk_metrics(bond, 0.055)
    scenario = yield_shock_analysis(bond, 0.055, 100)
    assert metrics["Convexity"] > 0
    assert abs(scenario["Duration + Convexity Error"]) < abs(scenario["Duration-only Error"])
    assert scenario["Full Repriced Price"] == pytest.approx(dirty_price(bond, 0.065))
    assert scenario["Approximation Error"] == pytest.approx(
        scenario["Duration + Convexity Change"] - scenario["Full Repricing Change"]
    )


@pytest.mark.parametrize("shock", [-200, -100, -50, 0, 50, 100, 200, 500])
def test_positive_negative_zero_and_large_scenarios(shock):
    result = yield_shock_analysis(terms(), 0.05, shock)
    assert result["Shock (bps)"] == shock
    if shock == 0:
        assert result["Full Repricing Change"] == pytest.approx(0)
        assert result["Approximation Error"] == pytest.approx(0)
    elif shock > 0:
        assert result["Full Repricing Change"] < 0
    else:
        assert result["Full Repricing Change"] > 0


def test_portfolio_weights_values_and_contributions_reconcile():
    analysis = analyze_bond_portfolio(sample_holdings())
    holdings, summary = analysis.holdings, analysis.summary
    assert holdings["Portfolio Weight"].sum() == pytest.approx(1)
    assert holdings["Market Value"].sum() == pytest.approx(summary["Total Market Value"])
    assert holdings["Duration Contribution"].sum() == pytest.approx(summary["Portfolio Modified Duration"])
    assert holdings["DV01 Contribution"].sum() == pytest.approx(summary["Portfolio DV01"])
    assert holdings["Convexity Contribution"].sum() == pytest.approx(summary["Portfolio Convexity"])
    expected_mac = (holdings["Portfolio Weight"] * holdings["Macaulay Duration"]).sum()
    assert summary["Portfolio Macaulay Duration"] == pytest.approx(expected_mac)


@pytest.mark.parametrize("shock", [-100, 0, 100, 500])
def test_portfolio_scenario_contributions_reconcile(shock):
    detail, summary = portfolio_rate_scenario(analyze_bond_portfolio(sample_holdings()), shock)
    assert detail["Full Repricing Impact"].sum() == pytest.approx(summary["Full Repricing Impact"])
    assert detail["Portfolio Impact Contribution"].sum() == pytest.approx(summary["Contribution Total"])
    assert detail["Full Repriced Value"].sum() == pytest.approx(summary["Full Repriced Portfolio Value"])


def test_selection_filters_and_ranking_are_transparent():
    universe = sample_holdings()
    ranked, formula = filter_and_rank_bonds(
        universe,
        filters={"min_ytm": 0.051, "sector": "Corporate", "max_duration": 9},
        criterion="Highest yield per unit of duration",
    )
    assert ranked["Bond"].tolist() == ["Bond B"]
    assert formula == "Yield to Maturity / Modified Duration; rank descending."
    all_ranked, _ = filter_and_rank_bonds(universe, criterion="Lowest duration")
    assert all_ranked["Modified Duration"].is_monotonic_increasing


def test_selection_target_fit_missing_data_duplicates_and_classifications():
    universe = sample_holdings()
    ranked, formula = filter_and_rank_bonds(universe, criterion="Duration-target fit", target_duration=6)
    assert "Duration Gap" in ranked and "Absolute modified-duration gap" in formula
    with pytest.raises(ValueError, match="target maturity"):
        filter_and_rank_bonds(universe, criterion="Maturity fit")
    duplicate = pd.concat([universe, universe.iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="Duplicate"):
        filter_and_rank_bonds(duplicate)
    with pytest.raises(ValueError, match="explicitly supplied"):
        filter_and_rank_bonds(universe.drop(columns="Credit Quality"), filters={"credit_quality": "AA"})
    invalid = universe.copy()
    invalid.loc[0, "Issuer"] = ""
    with pytest.raises(ValueError, match="explicitly supplied"):
        filter_and_rank_bonds(invalid, filters={"issuer": "Issuer B"})


def test_target_duration_caps_yield_floor_and_duration_band_construction():
    candidates, _ = filter_and_rank_bonds(sample_holdings(), criterion="Highest YTM")
    target = float(candidates["Modified Duration"].mean())
    weights, summary, validation = construct_bond_portfolio(
        candidates,
        target_duration=target,
        min_position=0.10,
        max_position=0.90,
        issuer_cap=0.90,
        credit_quality_cap=0.90,
        sector_cap=0.90,
        yield_floor=0.05,
        duration_ceiling=target + 0.01,
    )
    assert weights.sum() == pytest.approx(1)
    assert summary["Modified Duration"] == pytest.approx(target)
    assert summary["Weighted YTM"] >= 0.05
    assert set(validation["Constraint"]) == {"Weights sum to one", "Target duration"}
    weights2, summary2, _ = construct_bond_portfolio(
        candidates, duration_band=(target - 0.1, target + 0.1), max_position=0.9
    )
    assert weights2.sum() == pytest.approx(1)
    assert target - 0.1 <= summary2["Modified Duration"] <= target + 0.1


def test_maturity_bucket_construction_and_invalid_constraints():
    candidates, _ = filter_and_rank_bonds(sample_holdings(), criterion="Highest YTM")
    weights, _, _ = construct_bond_portfolio(
        candidates,
        maturity_buckets={"Intermediate": (0, 7, 0.5), "Long": (7, 30, 0.5)},
    )
    assert weights.loc["Bond A"] == pytest.approx(0.5)
    assert weights.loc["Bond B"] == pytest.approx(0.5)
    with pytest.raises(ValueError, match="cannot support"):
        construct_bond_portfolio(candidates, max_position=0.4)


def test_required_end_to_end_two_bond_case():
    analysis = analyze_bond_portfolio(sample_holdings())
    a = analysis.holdings.set_index("Bond").loc["Bond A"]
    b = analysis.holdings.set_index("Bond").loc["Bond B"]
    assert a["Clean Price"] == pytest.approx(956.2396803451)
    assert a["Current Yield"] == pytest.approx(0.0418305168)
    assert a["Macaulay Duration"] == pytest.approx(4.5695077325)
    assert a["Modified Duration"] == pytest.approx(4.4580563244)
    assert a["DV01"] == pytest.approx(0.4262970355)
    assert a["Convexity"] == pytest.approx(23.1944099076)
    assert b["Clean Price"] == pytest.approx(1038.0681303344)
    scenario, scenario_summary = portfolio_rate_scenario(analysis, 100)
    assert (scenario["Full Repricing Impact"] < 0).all()
    assert analysis.summary["Portfolio DV01"] == pytest.approx(
        analysis.holdings["DV01 Contribution"].sum()
    )
    assert scenario_summary["Contribution Total"] == pytest.approx(
        scenario_summary["Full Repricing Return"]
    )
