"""Bond portfolio aggregation, parallel-rate scenarios, selection, and construction."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

import numpy as np
import pandas as pd
from scipy.optimize import linprog

from .fixed_income import BondTerms, bond_risk_metrics, yield_shock_analysis, yield_to_maturity


REQUIRED_HOLDING_COLUMNS = {
    "Bond", "Quantity", "Face Value", "Coupon Rate", "Frequency", "Settlement", "Maturity",
}


@dataclass(frozen=True)
class BondPortfolioAnalysis:
    holdings: pd.DataFrame
    summary: pd.Series


def _number(value: Any, name: str, *, positive: bool = False, nonnegative: bool = False) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be numeric.") from exc
    if not np.isfinite(result):
        raise ValueError(f"{name} must be finite.")
    if positive and result <= 0:
        raise ValueError(f"{name} must be positive.")
    if nonnegative and result < 0:
        raise ValueError(f"{name} must be non-negative.")
    return result


def _validate_ids(frame: pd.DataFrame) -> None:
    if "Bond" not in frame:
        raise ValueError("Bond identifier column is required.")
    ids = frame["Bond"].astype("string").str.strip()
    if ids.isna().any() or (ids == "").any():
        raise ValueError("Every bond requires a non-empty identifier.")
    duplicates = ids[ids.duplicated()].unique().tolist()
    if duplicates:
        raise ValueError(f"Duplicate bond identifiers are not allowed: {', '.join(duplicates)}.")


def _terms(row: pd.Series) -> BondTerms:
    return BondTerms(
        face_value=_number(row["Face Value"], "Face value", positive=True),
        coupon_rate=_number(row["Coupon Rate"], "Coupon rate", nonnegative=True),
        frequency=int(_number(row["Frequency"], "Frequency", positive=True)),
        settlement=row["Settlement"],
        maturity=row["Maturity"],
        day_count=str(row.get("Day Count", "Actual/Actual")),
    )


def _holding_metrics(row: pd.Series) -> dict[str, Any]:
    terms = _terms(row)
    has_price = pd.notna(row.get("Clean Price"))
    has_yield = pd.notna(row.get("YTM"))
    if not has_price and not has_yield:
        raise ValueError(f"{row['Bond']} requires either Clean Price or YTM.")
    if has_price:
        clean = _number(row["Clean Price"], "Clean price", positive=True)
        ytm = yield_to_maturity(terms, clean)
    else:
        ytm = _number(row["YTM"], "YTM")
    metrics = bond_risk_metrics(terms, ytm)
    quantity = _number(row["Quantity"], "Quantity", positive=True)
    return {
        **row.to_dict(),
        **metrics,
        "Quantity": quantity,
        "Market Value": quantity * metrics["Dirty Price"],
        "Maturity (Years)": float(
            (pd.Timestamp(terms.maturity) - pd.Timestamp(terms.settlement)).days / 365.25
        ),
    }


def analyze_bond_portfolio(holdings: pd.DataFrame) -> BondPortfolioAnalysis:
    """Analyze explicit holdings and reconcile market-value-weighted risk contributions."""
    missing = REQUIRED_HOLDING_COLUMNS - set(holdings.columns)
    if missing:
        raise ValueError(f"Missing holding columns: {', '.join(sorted(missing))}.")
    if holdings.empty:
        raise ValueError("At least one bond holding is required.")
    _validate_ids(holdings)
    analyzed = pd.DataFrame([_holding_metrics(row) for _, row in holdings.iterrows()])
    total_value = float(analyzed["Market Value"].sum())
    if total_value <= 0:
        raise ValueError("Portfolio market value must be positive.")
    analyzed["Portfolio Weight"] = analyzed["Market Value"] / total_value
    analyzed["Duration Contribution"] = analyzed["Portfolio Weight"] * analyzed["Modified Duration"]
    analyzed["DV01 Contribution"] = analyzed["Quantity"] * analyzed["DV01"]
    analyzed["Convexity Contribution"] = analyzed["Portfolio Weight"] * analyzed["Convexity"]
    summary = pd.Series(
        {
            "Total Market Value": total_value,
            "Market-value-weighted YTM": float(
                (analyzed["Portfolio Weight"] * analyzed["Yield to Maturity"]).sum()
            ),
            "Portfolio Macaulay Duration": float(
                (analyzed["Portfolio Weight"] * analyzed["Macaulay Duration"]).sum()
            ),
            "Portfolio Modified Duration": float(analyzed["Duration Contribution"].sum()),
            "Portfolio Dollar Duration": float(
                (analyzed["Quantity"] * analyzed["Dollar Duration"]).sum()
            ),
            "Portfolio DV01": float(analyzed["DV01 Contribution"].sum()),
            "Portfolio Convexity": float(analyzed["Convexity Contribution"].sum()),
            "Duration Contribution Total": float(analyzed["Duration Contribution"].sum()),
            "DV01 Contribution Total": float(analyzed["DV01 Contribution"].sum()),
            "Convexity Contribution Total": float(analyzed["Convexity Contribution"].sum()),
        },
        name="Value",
    )
    return BondPortfolioAnalysis(analyzed, summary)


def portfolio_rate_scenario(
    analysis: BondPortfolioAnalysis, shock_bps: float
) -> tuple[pd.DataFrame, pd.Series]:
    """Run a common parallel yield shock and reconcile holding-level value impacts."""
    rows: list[dict[str, Any]] = []
    for _, row in analysis.holdings.iterrows():
        terms = _terms(row)
        result = yield_shock_analysis(terms, float(row["Yield to Maturity"]), shock_bps)
        quantity = float(row["Quantity"])
        base_value = float(row["Market Value"])
        full_value = quantity * result["Full Repriced Price"]
        rows.append(
            {
                "Bond": row["Bond"],
                "Shock (bps)": float(shock_bps),
                "Base Value": base_value,
                "Duration-only Value": quantity * result["Duration-only Price"],
                "Duration + Convexity Value": quantity * result["Duration + Convexity Price"],
                "Full Repriced Value": full_value,
                "Duration-only Impact": quantity * result["Duration-only Price"] - base_value,
                "Duration + Convexity Impact": quantity * result["Duration + Convexity Price"] - base_value,
                "Full Repricing Impact": full_value - base_value,
                "Approximation Error": quantity * result["Duration + Convexity Error"],
                "Portfolio Impact Contribution": (full_value - base_value) / analysis.summary["Total Market Value"],
            }
        )
    detail = pd.DataFrame(rows)
    base = float(detail["Base Value"].sum())
    summary = pd.Series(
        {
            "Shock (bps)": float(shock_bps),
            "Base Portfolio Value": base,
            "Duration-only Portfolio Value": float(detail["Duration-only Value"].sum()),
            "Duration + Convexity Portfolio Value": float(detail["Duration + Convexity Value"].sum()),
            "Full Repriced Portfolio Value": float(detail["Full Repriced Value"].sum()),
            "Duration-only Impact": float(detail["Duration-only Impact"].sum()),
            "Duration + Convexity Impact": float(detail["Duration + Convexity Impact"].sum()),
            "Full Repricing Impact": float(detail["Full Repricing Impact"].sum()),
            "Full Repricing Return": float(detail["Full Repricing Impact"].sum() / base),
            "Approximation Error": float(detail["Approximation Error"].sum()),
            "Contribution Total": float(detail["Portfolio Impact Contribution"].sum()),
        },
        name="Value",
    )
    return detail, summary


RANKING_FORMULAS = {
    "Highest YTM": ("Yield to Maturity", False, "Rank descending by nominal annual YTM."),
    "Lowest duration": ("Modified Duration", True, "Rank ascending by modified duration in years."),
    "Highest yield per unit of duration": (
        "Yield per Duration", False, "Yield to Maturity / Modified Duration; rank descending."
    ),
    "Lowest DV01": ("DV01", True, "Rank ascending by DV01 per entered instrument face value."),
    "Highest convexity": ("Convexity", False, "Rank descending by standard discrete convexity."),
    "Maturity fit": ("Maturity Gap", True, "Absolute maturity-years gap from the selected target; rank ascending."),
    "Duration-target fit": (
        "Duration Gap", True, "Absolute modified-duration gap from the selected target; rank ascending."
    ),
}


def filter_and_rank_bonds(
    universe: pd.DataFrame,
    *,
    filters: Mapping[str, Any] | None = None,
    criterion: str = "Highest YTM",
    target_maturity: float | None = None,
    target_duration: float | None = None,
) -> tuple[pd.DataFrame, str]:
    """Apply explicit filters and one transparent ranking rule to a bond universe."""
    _validate_ids(universe)
    if criterion not in RANKING_FORMULAS:
        raise ValueError(f"Unsupported ranking criterion: {criterion}.")
    analysis = analyze_bond_portfolio(universe.assign(Quantity=1.0)).holdings.copy()
    criteria = dict(filters or {})
    ranges = {
        "min_maturity": ("Maturity (Years)", "ge"), "max_maturity": ("Maturity (Years)", "le"),
        "min_ytm": ("Yield to Maturity", "ge"), "max_ytm": ("Yield to Maturity", "le"),
        "min_duration": ("Modified Duration", "ge"), "max_duration": ("Modified Duration", "le"),
        "min_coupon": ("Coupon Rate", "ge"), "min_price": ("Clean Price", "ge"),
        "max_price": ("Clean Price", "le"),
    }
    mask = pd.Series(True, index=analysis.index)
    for key, (column, operator) in ranges.items():
        if criteria.get(key) is not None:
            value = _number(criteria[key], key)
            mask &= analysis[column].ge(value) if operator == "ge" else analysis[column].le(value)
    for key, column in {
        "issuer": "Issuer", "sector": "Sector", "credit_quality": "Credit Quality",
        "callable_status": "Callable", "tax_status": "Tax Status",
    }.items():
        selected = criteria.get(key)
        if selected not in (None, "", [], ()):
            if (
                column not in analysis
                or analysis[column].isna().any()
                or analysis[column].astype(str).str.strip().eq("").any()
            ):
                raise ValueError(f"{column} must be explicitly supplied for this filter.")
            values = {str(value) for value in (selected if isinstance(selected, (list, tuple, set)) else [selected])}
            mask &= analysis[column].astype(str).isin(values)
    result = analysis.loc[mask].copy()
    result["Yield per Duration"] = result["Yield to Maturity"] / result["Modified Duration"].replace(0, np.nan)
    if criterion == "Maturity fit":
        if target_maturity is None:
            raise ValueError("Maturity-fit ranking requires a target maturity.")
        result["Maturity Gap"] = (result["Maturity (Years)"] - float(target_maturity)).abs()
    if criterion == "Duration-target fit":
        if target_duration is None:
            raise ValueError("Duration-target ranking requires a target duration.")
        result["Duration Gap"] = (result["Modified Duration"] - float(target_duration)).abs()
    column, ascending, formula = RANKING_FORMULAS[criterion]
    result = result.sort_values([column, "Bond"], ascending=[ascending, True]).reset_index(drop=True)
    result.insert(0, "Rank", np.arange(1, len(result) + 1))
    return result, formula


def construct_bond_portfolio(
    candidates: pd.DataFrame,
    *,
    target_duration: float | None = None,
    duration_band: tuple[float, float] | None = None,
    min_position: float = 0.0,
    max_position: float = 1.0,
    issuer_cap: float | None = None,
    credit_quality_cap: float | None = None,
    sector_cap: float | None = None,
    yield_floor: float | None = None,
    duration_ceiling: float | None = None,
    maturity_buckets: Mapping[str, tuple[float, float, float]] | None = None,
) -> tuple[pd.Series, pd.Series, pd.DataFrame]:
    """Maximize weighted YTM subject to transparent linear portfolio constraints.

    Maturity bucket values are ``(minimum years, maximum years, target weight)``.
    Position bounds apply to every included candidate; no hidden security score is used.
    """
    if candidates.empty:
        raise ValueError("At least one candidate bond is required.")
    if "Yield to Maturity" not in candidates or "Modified Duration" not in candidates:
        candidates = analyze_bond_portfolio(candidates.assign(Quantity=1.0)).holdings
    _validate_ids(candidates)
    n = len(candidates)
    lower = _number(min_position, "Minimum position", nonnegative=True)
    upper = _number(max_position, "Maximum position", positive=True)
    if lower > upper or lower * n > 1 + 1e-10 or upper * n < 1 - 1e-10:
        raise ValueError("Position limits cannot support weights summing to one.")
    ytm = candidates["Yield to Maturity"].to_numpy(dtype=float)
    duration = candidates["Modified Duration"].to_numpy(dtype=float)
    a_eq = [np.ones(n)]
    b_eq = [1.0]
    labels = ["Weights sum to one"]
    if target_duration is not None:
        a_eq.append(duration)
        b_eq.append(float(target_duration))
        labels.append("Target duration")
    a_ub: list[np.ndarray] = []
    b_ub: list[float] = []
    if duration_band is not None:
        low, high = map(float, duration_band)
        if low > high:
            raise ValueError("Duration-band minimum cannot exceed maximum.")
        a_ub.extend([duration, -duration]); b_ub.extend([high, -low])
    if duration_ceiling is not None:
        a_ub.append(duration); b_ub.append(float(duration_ceiling))
    if yield_floor is not None:
        a_ub.append(-ytm); b_ub.append(-float(yield_floor))
    for column, cap, label in (
        ("Issuer", issuer_cap, "Issuer cap"),
        ("Credit Quality", credit_quality_cap, "Credit-quality cap"),
        ("Sector", sector_cap, "Sector cap"),
    ):
        if cap is None:
            continue
        if (
            column not in candidates
            or candidates[column].isna().any()
            or candidates[column].astype(str).str.strip().eq("").any()
        ):
            raise ValueError(f"{column} must be explicitly supplied to apply its cap.")
        cap_value = _number(cap, label, nonnegative=True)
        for value in candidates[column].astype(str).unique():
            a_ub.append((candidates[column].astype(str) == value).to_numpy(dtype=float))
            b_ub.append(cap_value)
    if maturity_buckets:
        maturity = candidates["Maturity (Years)"].to_numpy(dtype=float)
        for name, (minimum, maximum, target) in maturity_buckets.items():
            bucket = ((maturity >= minimum) & (maturity < maximum)).astype(float)
            if not bucket.any() and target > 0:
                raise ValueError(f"Maturity bucket {name} has no eligible bonds.")
            a_eq.append(bucket); b_eq.append(float(target)); labels.append(f"Maturity bucket: {name}")
    result = linprog(
        -ytm,
        A_ub=np.asarray(a_ub) if a_ub else None,
        b_ub=np.asarray(b_ub) if b_ub else None,
        A_eq=np.asarray(a_eq),
        b_eq=np.asarray(b_eq),
        bounds=[(lower, upper)] * n,
        method="highs",
    )
    if not result.success:
        raise ValueError(f"Bond portfolio constraints are infeasible: {result.message}")
    weights = pd.Series(result.x, index=candidates["Bond"].astype(str), name="Portfolio Weight")
    summary = pd.Series(
        {
            "Weighted YTM": float(result.x @ ytm),
            "Modified Duration": float(result.x @ duration),
            "Convexity": float(result.x @ candidates["Convexity"].to_numpy(dtype=float)),
            "Maximum Position": float(result.x.max()),
        },
        name="Value",
    )
    validation = pd.DataFrame(
        {
            "Constraint": labels,
            "Result": [float(np.asarray(row) @ result.x) for row in a_eq],
            "Target": b_eq,
        }
    )
    return weights, summary, validation
