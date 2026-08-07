"""Pure fixed-income pricing and interest-rate-risk analytics.

All calculations use explicit contractual cash flows. Prices are amounts per
instrument face value, yields and coupon rates are annual decimals, and yield
shocks are annual decimal changes.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Literal

import numpy as np
import pandas as pd
from scipy.optimize import brentq


SUPPORTED_FREQUENCIES = (1, 2, 4, 12)
SUPPORTED_DAY_COUNTS = ("Actual/Actual", "30/360")


@dataclass(frozen=True)
class BondTerms:
    """Explicit contractual terms for a standard option-free fixed-rate bond."""

    face_value: float
    coupon_rate: float
    frequency: int
    settlement: date | pd.Timestamp
    maturity: date | pd.Timestamp
    day_count: Literal["Actual/Actual", "30/360"] = "Actual/Actual"


def _timestamp(value: date | pd.Timestamp, name: str) -> pd.Timestamp:
    try:
        result = pd.Timestamp(value).normalize()
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a valid date.") from exc
    if pd.isna(result):
        raise ValueError(f"{name} must be a valid date.")
    return result


def _validate_terms(terms: BondTerms) -> tuple[pd.Timestamp, pd.Timestamp]:
    if not np.isfinite(terms.face_value) or terms.face_value <= 0:
        raise ValueError("Face value must be positive.")
    if not np.isfinite(terms.coupon_rate) or terms.coupon_rate < 0:
        raise ValueError("Coupon rate must be non-negative.")
    if terms.frequency not in SUPPORTED_FREQUENCIES:
        raise ValueError("Coupon frequency must be annual, semiannual, quarterly, or monthly.")
    if terms.day_count not in SUPPORTED_DAY_COUNTS:
        raise ValueError(f"Day-count convention must be one of {SUPPORTED_DAY_COUNTS}.")
    settlement = _timestamp(terms.settlement, "Settlement")
    maturity = _timestamp(terms.maturity, "Maturity")
    if maturity <= settlement:
        raise ValueError("Maturity must be after settlement.")
    return settlement, maturity


def _coupon_dates(terms: BondTerms) -> tuple[pd.Timestamp, list[pd.Timestamp]]:
    settlement, maturity = _validate_terms(terms)
    months = 12 // terms.frequency
    dates = [maturity]
    cursor = maturity
    while True:
        previous = cursor - pd.DateOffset(months=months)
        if previous <= settlement:
            return previous, sorted(dates)
        dates.append(previous)
        cursor = previous


def _days_30_360(start: pd.Timestamp, end: pd.Timestamp) -> int:
    d1 = min(start.day, 30)
    d2 = min(end.day, 30) if d1 == 30 else end.day
    return 360 * (end.year - start.year) + 30 * (end.month - start.month) + d2 - d1


def accrual_fraction(terms: BondTerms) -> float:
    """Return the elapsed fraction of the current coupon period at settlement."""
    previous, dates = _coupon_dates(terms)
    settlement, _ = _validate_terms(terms)
    next_coupon = dates[0]
    if settlement == previous:
        return 0.0
    if terms.day_count == "30/360":
        elapsed = _days_30_360(previous, settlement)
        period = _days_30_360(previous, next_coupon)
    else:
        elapsed = (settlement - previous).days
        period = (next_coupon - previous).days
    if period <= 0:
        raise ValueError("Coupon period must contain at least one day.")
    return float(elapsed / period)


def accrued_interest(terms: BondTerms) -> float:
    """Return accrued coupon interest per instrument at settlement."""
    coupon = terms.face_value * terms.coupon_rate / terms.frequency
    return float(coupon * accrual_fraction(terms))


def cash_flow_schedule(terms: BondTerms) -> pd.DataFrame:
    """Create the contractual future cash-flow schedule after settlement."""
    _, dates = _coupon_dates(terms)
    accrued_period = accrual_fraction(terms)
    coupon = terms.face_value * terms.coupon_rate / terms.frequency
    periods = np.arange(1, len(dates) + 1, dtype=float) - accrued_period
    principal = np.zeros(len(dates), dtype=float)
    principal[-1] = terms.face_value
    frame = pd.DataFrame(
        {
            "Payment Date": dates,
            "Periods from Settlement": periods,
            "Years from Settlement": periods / terms.frequency,
            "Coupon": coupon,
            "Principal": principal,
        }
    )
    frame["Total Cash Flow"] = frame["Coupon"] + frame["Principal"]
    return frame.loc[frame["Total Cash Flow"].ne(0)].reset_index(drop=True)


def _validate_yield(yield_to_maturity: float, frequency: int) -> float:
    if not np.isfinite(yield_to_maturity):
        raise ValueError("Yield to maturity must be finite.")
    if 1 + yield_to_maturity / frequency <= 0:
        raise ValueError("Yield produces a non-positive periodic discount factor.")
    return float(yield_to_maturity)


def dirty_price(terms: BondTerms, yield_to_maturity: float) -> float:
    """Price all future cash flows at a nominal annual YTM compounded by frequency."""
    ytm = _validate_yield(yield_to_maturity, terms.frequency)
    schedule = cash_flow_schedule(terms)
    base = 1 + ytm / terms.frequency
    pv = schedule["Total Cash Flow"].to_numpy(dtype=float) / np.power(
        base, schedule["Periods from Settlement"].to_numpy(dtype=float)
    )
    return float(pv.sum())


def clean_price(terms: BondTerms, yield_to_maturity: float) -> float:
    """Return quoted clean price, excluding accrued coupon interest."""
    return dirty_price(terms, yield_to_maturity) - accrued_interest(terms)


def current_yield(terms: BondTerms, market_clean_price: float) -> float:
    """Return annual coupon cash flow divided by clean market price."""
    if not np.isfinite(market_clean_price) or market_clean_price <= 0:
        raise ValueError("Market clean price must be positive.")
    return float(terms.face_value * terms.coupon_rate / market_clean_price)


def yield_to_maturity(
    terms: BondTerms,
    market_clean_price: float,
    *,
    lower: float | None = None,
    upper: float = 10.0,
    max_iterations: int = 200,
) -> float:
    """Recover nominal annual YTM from a clean price using a bracketed root solver."""
    if not np.isfinite(market_clean_price) or market_clean_price <= 0:
        raise ValueError("Market clean price must be positive.")
    if max_iterations < 1:
        raise ValueError("Maximum iterations must be positive.")
    floor = -0.95 * terms.frequency if lower is None else float(lower)
    if floor >= upper or 1 + floor / terms.frequency <= 0:
        raise ValueError("YTM solver bounds are invalid.")

    def objective(value: float) -> float:
        return clean_price(terms, value) - market_clean_price

    try:
        low_value, high_value = objective(floor), objective(upper)
        if not np.isfinite(low_value) or not np.isfinite(high_value) or low_value * high_value > 0:
            raise ValueError("YTM could not be bracketed for the supplied price.")
        return float(brentq(objective, floor, upper, maxiter=max_iterations, xtol=1e-12, rtol=1e-12))
    except RuntimeError as exc:
        raise ValueError("YTM solver did not converge.") from exc


def bond_risk_metrics(terms: BondTerms, yield_to_maturity_value: float) -> dict[str, float]:
    """Return price, yield, duration, dollar-duration, DV01, and convexity measures."""
    ytm = _validate_yield(yield_to_maturity_value, terms.frequency)
    schedule = cash_flow_schedule(terms)
    periods = schedule["Periods from Settlement"].to_numpy(dtype=float)
    cash_flows = schedule["Total Cash Flow"].to_numpy(dtype=float)
    base = 1 + ytm / terms.frequency
    pv = cash_flows / np.power(base, periods)
    dirty = float(pv.sum())
    if dirty <= 0:
        raise ValueError("Dirty price must be positive.")
    macaulay = float(np.sum((periods / terms.frequency) * pv) / dirty)
    modified = float(macaulay / base)
    dollar = float(modified * dirty)
    convexity = float(
        np.sum(pv * periods * (periods + 1) / (terms.frequency**2 * base**2)) / dirty
    )
    clean = dirty - accrued_interest(terms)
    return {
        "Clean Price": clean,
        "Dirty Price": dirty,
        "Accrued Interest": accrued_interest(terms),
        "Current Yield": current_yield(terms, clean),
        "Yield to Maturity": ytm,
        "Macaulay Duration": macaulay,
        "Modified Duration": modified,
        "Dollar Duration": dollar,
        "DV01": dollar * 0.0001,
        "Convexity": convexity,
    }


def duration_price_change(modified_duration: float, yield_shock: float) -> float:
    """Estimate proportional price change from modified duration alone."""
    return float(-modified_duration * yield_shock)


def duration_convexity_price_change(
    modified_duration: float, convexity: float, yield_shock: float
) -> float:
    """Estimate proportional price change from modified duration and convexity."""
    return float(-modified_duration * yield_shock + 0.5 * convexity * yield_shock**2)


def price_approximation_error(approximated_price: float, fully_repriced_price: float) -> float:
    """Return approximation minus full-repricing price in currency units."""
    if not np.isfinite(approximated_price) or not np.isfinite(fully_repriced_price):
        raise ValueError("Approximate and fully repriced values must be finite.")
    return float(approximated_price - fully_repriced_price)


def yield_shock_analysis(
    terms: BondTerms, yield_to_maturity_value: float, shock_bps: float
) -> dict[str, float]:
    """Compare duration approximations with full repricing for a parallel yield shock."""
    if not np.isfinite(shock_bps):
        raise ValueError("Yield shock must be finite basis points.")
    metrics = bond_risk_metrics(terms, yield_to_maturity_value)
    shock = float(shock_bps) / 10_000
    shocked_yield = yield_to_maturity_value + shock
    _validate_yield(shocked_yield, terms.frequency)
    base_price = metrics["Dirty Price"]
    duration_change = duration_price_change(metrics["Modified Duration"], shock)
    combined_change = duration_convexity_price_change(
        metrics["Modified Duration"], metrics["Convexity"], shock
    )
    full_price = dirty_price(terms, shocked_yield)
    full_change = full_price / base_price - 1
    duration_price = base_price * (1 + duration_change)
    combined_price = base_price * (1 + combined_change)
    return {
        "Shock (bps)": float(shock_bps),
        "Shocked YTM": shocked_yield,
        "Base Dirty Price": base_price,
        "Duration-only Change": duration_change,
        "Duration-only Price": duration_price,
        "Duration + Convexity Change": combined_change,
        "Duration + Convexity Price": combined_price,
        "Full Repricing Change": full_change,
        "Full Repriced Price": full_price,
        "Duration-only Error": price_approximation_error(duration_price, full_price),
        "Duration + Convexity Error": price_approximation_error(combined_price, full_price),
        "Approximation Error": combined_change - full_change,
    }
