"""Streamlit workspace for explicit fixed-income analytics."""
from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
import streamlit as st

from .bond_portfolio import (
    RANKING_FORMULAS,
    analyze_bond_portfolio,
    construct_bond_portfolio,
    filter_and_rank_bonds,
    portfolio_rate_scenario,
)
from .fixed_income import (
    BondTerms,
    bond_risk_metrics,
    cash_flow_schedule,
    yield_shock_analysis,
    yield_to_maturity,
)


RATE_SHOCKS = (-200, -100, -50, 0, 50, 100, 200)


def default_bond_holdings() -> pd.DataFrame:
    """Return deterministic explicit instruments for an editable starting point."""
    settlement = date(2026, 1, 1)
    return pd.DataFrame(
        [
            {
                "Bond": "Bond A", "Quantity": 10.0, "Face Value": 1000.0, "Coupon Rate (%)": 4.0,
                "Frequency": 2, "Settlement": settlement, "Maturity": date(2031, 1, 1),
                "Clean Price": np.nan, "YTM (%)": 5.0, "Day Count": "Actual/Actual",
                "Issuer": "Issuer A", "Sector": "Government", "Credit Quality": "AA",
                "Callable": "No", "Tax Status": "Taxable",
            },
            {
                "Bond": "Bond B", "Quantity": 5.0, "Face Value": 1000.0, "Coupon Rate (%)": 6.0,
                "Frequency": 2, "Settlement": settlement, "Maturity": date(2036, 1, 1),
                "Clean Price": np.nan, "YTM (%)": 5.5, "Day Count": "Actual/Actual",
                "Issuer": "Issuer B", "Sector": "Corporate", "Credit Quality": "A",
                "Callable": "No", "Tax Status": "Taxable",
            },
        ]
    )


def default_bond_universe() -> pd.DataFrame:
    base = default_bond_holdings()
    additional = pd.DataFrame(
        [
            {
                "Bond": "Bond C", "Quantity": 1.0, "Face Value": 1000.0, "Coupon Rate (%)": 3.25,
                "Frequency": 2, "Settlement": date(2026, 1, 1), "Maturity": date(2029, 1, 1),
                "Clean Price": np.nan, "YTM (%)": 4.7, "Day Count": "Actual/Actual",
                "Issuer": "Issuer C", "Sector": "Municipal", "Credit Quality": "AAA",
                "Callable": "No", "Tax Status": "Tax-exempt",
            },
            {
                "Bond": "Bond D", "Quantity": 1.0, "Face Value": 1000.0, "Coupon Rate (%)": 7.0,
                "Frequency": 4, "Settlement": date(2026, 1, 1), "Maturity": date(2041, 1, 1),
                "Clean Price": np.nan, "YTM (%)": 6.2, "Day Count": "Actual/Actual",
                "Issuer": "Issuer D", "Sector": "Corporate", "Credit Quality": "BBB",
                "Callable": "Yes", "Tax Status": "Taxable",
            },
        ]
    )
    return pd.concat([base, additional], ignore_index=True)


def _analytics_frame(editor: pd.DataFrame) -> pd.DataFrame:
    frame = editor.copy()
    frame["Coupon Rate"] = pd.to_numeric(frame.pop("Coupon Rate (%)"), errors="coerce") / 100
    frame["YTM"] = pd.to_numeric(frame.pop("YTM (%)"), errors="coerce") / 100
    return frame


def _editor(frame: pd.DataFrame, key: str) -> pd.DataFrame:
    return st.data_editor(
        frame,
        key=key,
        num_rows="dynamic",
        hide_index=True,
        width="stretch",
        column_config={
            "Bond": st.column_config.TextColumn(required=True, pinned=True),
            "Quantity": st.column_config.NumberColumn(min_value=0.000001, required=True, format="%.2f"),
            "Face Value": st.column_config.NumberColumn(min_value=0.01, required=True, format="$%.2f"),
            "Coupon Rate (%)": st.column_config.NumberColumn(min_value=0.0, required=True, format="%.3f%%"),
            "Frequency": st.column_config.SelectboxColumn(options=[1, 2, 4, 12], required=True),
            "Settlement": st.column_config.DateColumn(required=True),
            "Maturity": st.column_config.DateColumn(required=True),
            "Clean Price": st.column_config.NumberColumn(min_value=0.000001, format="$%.4f"),
            "YTM (%)": st.column_config.NumberColumn(format="%.4f%%"),
            "Day Count": st.column_config.SelectboxColumn(options=["Actual/Actual", "30/360"], required=True),
            "Callable": st.column_config.SelectboxColumn(options=["No", "Yes"], required=True),
            "Tax Status": st.column_config.SelectboxColumn(options=["Taxable", "Tax-exempt"], required=True),
        },
    )


def _metric_rows(items: list[tuple[str, str]]) -> None:
    with st.container(horizontal=True, gap="xsmall"):
        for label, value in items:
            st.metric(label, value, border=True, width=170)


def _render_calculator() -> None:
    st.markdown("### Bond calculator")
    st.caption(
        "Price a standard option-free fixed-rate or zero-coupon bond from explicit contractual cash flows. "
        "Yield is nominal annual YTM compounded at the selected coupon frequency."
    )
    input_mode = st.segmented_control(
        "Solve from", ["Yield to maturity", "Clean market price"], default="Yield to maturity",
        key="fi_calculator_mode", persist_state="session",
    )
    with st.form("fi_calculator_form", border=True):
        first, second, third = st.columns(3)
        with first:
            face = st.number_input("Face value", min_value=0.01, value=1000.0, step=100.0)
            coupon = st.number_input("Annual coupon rate (%)", min_value=0.0, value=4.0, step=0.25)
            frequency = st.selectbox("Coupon frequency", [1, 2, 4, 12], index=1)
        with second:
            settlement = st.date_input("Settlement date", date(2026, 1, 1))
            maturity = st.date_input("Maturity date", date(2031, 1, 1))
            day_count = st.selectbox("Day-count convention", ["Actual/Actual", "30/360"])
        with third:
            quoted_ytm = st.number_input("Yield to maturity (%)", value=5.0, step=0.10, disabled=input_mode != "Yield to maturity")
            quoted_price = st.number_input("Clean market price", min_value=0.01, value=956.24, step=1.0, disabled=input_mode != "Clean market price")
            shock_bps = st.selectbox("Yield shock (bps)", RATE_SHOCKS, index=5)
        submitted = st.form_submit_button("Calculate bond analytics", type="primary", icon=":material/calculate:")
    if submitted:
        try:
            terms = BondTerms(face, coupon / 100, frequency, settlement, maturity, day_count)
            ytm = quoted_ytm / 100 if input_mode == "Yield to maturity" else yield_to_maturity(terms, quoted_price)
            st.session_state["fi_calculator_result"] = {
                "terms": terms,
                "metrics": bond_risk_metrics(terms, ytm),
                "cash_flows": cash_flow_schedule(terms),
                "scenario": yield_shock_analysis(terms, ytm, shock_bps),
            }
        except ValueError as exc:
            st.session_state.pop("fi_calculator_result", None)
            st.error(f"Bond analytics could not run: {exc}")
    result = st.session_state.get("fi_calculator_result")
    if result is None:
        st.info("Enter explicit bond terms, then select **Calculate bond analytics**.")
        return
    metrics = result["metrics"]
    _metric_rows([
        ("Clean price", f"${metrics['Clean Price']:,.2f}"),
        ("Dirty price", f"${metrics['Dirty Price']:,.2f}"),
        ("Accrued interest", f"${metrics['Accrued Interest']:,.2f}"),
        ("Current yield", f"{metrics['Current Yield']:.2%}"),
        ("YTM", f"{metrics['Yield to Maturity']:.2%}"),
    ])
    _metric_rows([
        ("Macaulay duration", f"{metrics['Macaulay Duration']:.3f} years"),
        ("Modified duration", f"{metrics['Modified Duration']:.3f} years"),
        ("Dollar duration", f"${metrics['Dollar Duration']:,.2f}"),
        ("DV01 / PVBP", f"${metrics['DV01']:,.4f}"),
        ("Convexity", f"{metrics['Convexity']:.3f}"),
    ])
    scenario = result["scenario"]
    st.markdown("**Yield-shock comparison**")
    st.dataframe(
        pd.DataFrame({"Value": scenario}), width="stretch",
        column_config={"Value": st.column_config.NumberColumn(format="%.6f")},
    )
    st.markdown("**Cash-flow schedule**")
    st.dataframe(
        result["cash_flows"], hide_index=True, width="stretch",
        column_config={
            "Payment Date": st.column_config.DateColumn(format="MMM D, YYYY"),
            "Coupon": st.column_config.NumberColumn(format="$%.2f"),
            "Principal": st.column_config.NumberColumn(format="$%.2f"),
            "Total Cash Flow": st.column_config.NumberColumn(format="$%.2f"),
        },
    )
    st.download_button(
        "Download bond cash flows CSV", result["cash_flows"].to_csv(index=False),
        "bond_cash_flows.csv", "text/csv", icon=":material/download:",
    )
    with st.expander("Metric definitions and limitations", icon=":material/info:"):
        st.markdown(
            "Current yield is annual coupon divided by clean price; YTM is the single nominal discount rate that "
            "reconciles the clean price. Macaulay duration is a present-value-weighted time measure. Modified "
            "duration is Macaulay duration divided by the periodic yield factor. Dollar duration is modified "
            "duration times dirty price, and DV01 is dollar duration times 0.0001. Convexity is the standard "
            "second-order measure for option-free cash flows. Effective duration is not calculated or relabeled."
        )


def _render_portfolio() -> None:
    st.markdown("### Bond portfolio")
    st.caption(
        "Enter each instrument's contractual terms and either clean price or YTM. When both are present, clean "
        "price is authoritative and YTM is solved from that price. Portfolio market value includes accrued interest."
    )
    draft = st.session_state.get("fi_holdings_draft", default_bond_holdings())
    edited = _editor(draft, "fi_holdings_editor")
    st.session_state["fi_holdings_draft"] = edited.copy()
    if st.button("Analyze bond portfolio", type="primary", icon=":material/analytics:"):
        try:
            st.session_state["fi_portfolio_analysis"] = analyze_bond_portfolio(_analytics_frame(edited))
            st.session_state.pop("fi_portfolio_scenario", None)
        except ValueError as exc:
            st.session_state.pop("fi_portfolio_analysis", None)
            st.error(f"Bond portfolio analysis could not run: {exc}")
    analysis = st.session_state.get("fi_portfolio_analysis")
    if analysis is None:
        st.info("Review the editable holdings, then select **Analyze bond portfolio**.")
        return
    summary = analysis.summary
    _metric_rows([
        ("Market value", f"${summary['Total Market Value']:,.2f}"),
        ("Weighted YTM", f"{summary['Market-value-weighted YTM']:.2%}"),
        ("Modified duration", f"{summary['Portfolio Modified Duration']:.3f} years"),
        ("Portfolio DV01", f"${summary['Portfolio DV01']:,.2f}"),
        ("Portfolio convexity", f"{summary['Portfolio Convexity']:.3f}"),
    ])
    st.caption(
        "Weighted YTM is a market-value-weighted descriptive average, not a portfolio IRR. It does not represent "
        "the yield of a single aggregate cash-flow stream."
    )
    pricing = analysis.holdings[[
        "Bond", "Clean Price", "Market Value", "Portfolio Weight", "Current Yield", "Yield to Maturity",
    ]]
    st.markdown("**Pricing and yield**")
    st.dataframe(pricing, hide_index=True, width="stretch", column_config={
        "Clean Price": st.column_config.NumberColumn(format="dollar"),
        "Market Value": st.column_config.NumberColumn(format="dollar"),
        "Portfolio Weight": st.column_config.NumberColumn(format="percent"),
        "Current Yield": st.column_config.NumberColumn(format="percent"),
        "Yield to Maturity": st.column_config.NumberColumn(format="percent"),
    })
    rate_risk = analysis.holdings[[
        "Bond", "Macaulay Duration", "Modified Duration", "Dollar Duration", "DV01", "Convexity",
    ]]
    st.markdown("**Rate-risk measures**")
    st.dataframe(rate_risk, hide_index=True, width="stretch", column_config={
        "Dollar Duration": st.column_config.NumberColumn(format="$%.2f"),
        "DV01": st.column_config.NumberColumn(format="$%.4f"),
    })
    contribution = analysis.holdings[[
        "Bond", "Duration Contribution", "DV01 Contribution", "Convexity Contribution",
    ]]
    st.markdown("**Portfolio contributions**")
    st.dataframe(contribution, hide_index=True, width="stretch", column_config={
        "DV01 Contribution": st.column_config.NumberColumn(format="$%.4f"),
    })
    st.bar_chart(contribution.set_index("Bond"), height=400)
    st.download_button(
        "Download bond portfolio analytics CSV", analysis.holdings.to_csv(index=False),
        "bond_portfolio_analytics.csv", "text/csv", icon=":material/download:",
    )


def _render_scenarios() -> None:
    st.markdown("### Rate scenarios")
    st.caption(
        "Compare modified-duration, duration-plus-convexity, and full cash-flow repricing under one parallel "
        "yield shift. Parallel shifts do not capture curve-shape, spread, liquidity, optionality, or credit risk."
    )
    analysis = st.session_state.get("fi_portfolio_analysis")
    if analysis is None:
        st.info("Analyze explicit holdings in **Bond portfolio** before running a portfolio rate scenario.")
        return
    with st.form("fi_scenario_form", border=True):
        shock = st.selectbox("Parallel yield shock (bps)", RATE_SHOCKS, index=5)
        run = st.form_submit_button("Run rate scenario", type="primary", icon=":material/trending_up:")
    if run:
        try:
            st.session_state["fi_portfolio_scenario"] = portfolio_rate_scenario(analysis, shock)
        except ValueError as exc:
            st.session_state.pop("fi_portfolio_scenario", None)
            st.error(f"Rate scenario could not run: {exc}")
    result = st.session_state.get("fi_portfolio_scenario")
    if result is None:
        return
    detail, summary = result
    _metric_rows([
        ("Shock", f"{summary['Shock (bps)']:+.0f} bps"),
        ("Base value", f"${summary['Base Portfolio Value']:,.2f}"),
        ("Full repriced value", f"${summary['Full Repriced Portfolio Value']:,.2f}"),
        ("Full repricing impact", f"{summary['Full Repricing Return']:.2%}"),
        ("Convexity approximation error", f"${summary['Approximation Error']:,.2f}"),
    ])
    st.dataframe(detail, hide_index=True, width="stretch", column_config={
        column: st.column_config.NumberColumn(format="dollar")
        for column in [
            "Base Value", "Duration-only Value", "Duration + Convexity Value", "Full Repriced Value",
            "Duration-only Impact", "Duration + Convexity Impact", "Full Repricing Impact", "Approximation Error",
        ]
    } | {"Portfolio Impact Contribution": st.column_config.NumberColumn(format="percent")})
    comparison = pd.DataFrame(
        {
            "Method": ["Duration only", "Duration + convexity", "Full repricing"],
            "Portfolio Value": [
                summary["Duration-only Portfolio Value"], summary["Duration + Convexity Portfolio Value"],
                summary["Full Repriced Portfolio Value"],
            ],
        }
    )
    st.bar_chart(comparison, x="Method", y="Portfolio Value", height=400)
    st.download_button(
        "Download rate scenario CSV", detail.to_csv(index=False), "bond_rate_scenario.csv", "text/csv",
        icon=":material/download:",
    )


def _render_selection() -> None:
    st.markdown("### Bond selection")
    st.caption(
        "Screen and rank only the classifications and cash-flow terms supplied below. The selected criterion is "
        "the complete ranking rule; no hidden composite score is used."
    )
    draft = st.session_state.get("fi_universe_draft", default_bond_universe())
    edited = _editor(draft, "fi_universe_editor")
    st.session_state["fi_universe_draft"] = edited.copy()
    with st.expander("Filters and ranking", expanded=True, icon=":material/filter_alt:"):
        one, two, three = st.columns(3)
        with one:
            min_maturity = st.number_input("Minimum maturity (years)", min_value=0.0, value=0.0)
            max_maturity = st.number_input("Maximum maturity (years)", min_value=0.0, value=50.0)
            min_ytm = st.number_input("Minimum YTM (%)", value=-10.0)
            max_ytm = st.number_input("Maximum YTM (%)", value=100.0)
        with two:
            min_duration = st.number_input("Minimum modified duration", min_value=0.0, value=0.0)
            max_duration = st.number_input("Maximum modified duration", min_value=0.0, value=50.0)
            min_coupon = st.number_input("Minimum coupon (%)", min_value=0.0, value=0.0)
            min_price = st.number_input("Minimum clean price", min_value=0.01, value=0.01)
            max_price = st.number_input("Maximum clean price", min_value=0.01, value=100000.0)
        with three:
            issuer = st.multiselect("Issuer", sorted(edited["Issuer"].dropna().astype(str).unique()))
            sector = st.multiselect("Sector", sorted(edited["Sector"].dropna().astype(str).unique()))
            quality = st.multiselect("Credit quality", sorted(edited["Credit Quality"].dropna().astype(str).unique()))
            callable_status = st.multiselect("Callable status", ["No", "Yes"])
            tax_status = st.multiselect("Tax status", ["Taxable", "Tax-exempt"])
        criterion = st.selectbox("Ranking criterion", list(RANKING_FORMULAS))
        target_maturity = st.number_input("Target maturity (years)", min_value=0.0, value=7.0, disabled=criterion != "Maturity fit")
        target_duration = st.number_input("Target duration (years)", min_value=0.0, value=5.0, disabled=criterion != "Duration-target fit")
        rank = st.button("Apply filters and rank", type="primary", icon=":material/format_list_numbered:")
    if rank:
        try:
            filters = {
                "min_maturity": min_maturity, "max_maturity": max_maturity,
                "min_ytm": min_ytm / 100, "max_ytm": max_ytm / 100,
                "min_duration": min_duration, "max_duration": max_duration,
                "min_coupon": min_coupon / 100, "min_price": min_price, "max_price": max_price,
                "issuer": issuer, "sector": sector, "credit_quality": quality,
                "callable_status": callable_status, "tax_status": tax_status,
            }
            st.session_state["fi_selection_result"] = filter_and_rank_bonds(
                _analytics_frame(edited), filters=filters, criterion=criterion,
                target_maturity=target_maturity, target_duration=target_duration,
            )
        except ValueError as exc:
            st.session_state.pop("fi_selection_result", None)
            st.error(f"Bond selection could not run: {exc}")
    selection = st.session_state.get("fi_selection_result")
    if selection is None:
        st.info("Set explicit filters and one ranking criterion, then apply the screen.")
        return
    ranked, formula = selection
    st.info(f"Ranking formula: {formula}")
    st.dataframe(ranked, hide_index=True, width="stretch", column_config={
        "Yield to Maturity": st.column_config.NumberColumn(format="percent"),
        "Current Yield": st.column_config.NumberColumn(format="percent"),
        "Coupon Rate": st.column_config.NumberColumn(format="percent"),
        "Clean Price": st.column_config.NumberColumn(format="dollar"),
    })
    st.download_button(
        "Download selected bonds CSV", ranked.to_csv(index=False), "selected_bonds.csv", "text/csv",
        icon=":material/download:",
    )
    with st.expander("Construct a constrained bond portfolio", icon=":material/account_balance:"):
        st.caption("The linear model maximizes the displayed market-value-weighted YTM subject to the selected constraints.")
        target_enabled = st.checkbox("Use target duration")
        construction_target = st.number_input("Portfolio target duration", min_value=0.0, value=5.0, disabled=not target_enabled)
        band_enabled = st.checkbox("Use duration band")
        band = st.slider("Duration band", 0.0, 30.0, (3.0, 8.0), disabled=not band_enabled)
        min_position = st.number_input("Minimum position (%)", min_value=0.0, max_value=100.0, value=0.0)
        max_position = st.number_input("Maximum position (%)", min_value=0.01, max_value=100.0, value=100.0)
        issuer_cap = st.number_input("Issuer cap (%)", min_value=0.01, max_value=100.0, value=100.0)
        quality_cap = st.number_input("Credit-quality cap (%)", min_value=0.01, max_value=100.0, value=100.0)
        sector_cap = st.number_input("Sector cap (%)", min_value=0.01, max_value=100.0, value=100.0)
        yield_floor = st.number_input("Portfolio yield floor (%)", value=-10.0)
        duration_ceiling = st.number_input("Portfolio duration ceiling", min_value=0.0, value=30.0)
        buckets_enabled = st.checkbox("Use maturity-bucket allocation")
        bucket_one, bucket_two, bucket_three = st.columns(3)
        with bucket_one:
            short_bucket = st.number_input("Under 5 years (%)", 0.0, 100.0, 25.0, disabled=not buckets_enabled)
        with bucket_two:
            intermediate_bucket = st.number_input("5–10 years (%)", 0.0, 100.0, 25.0, disabled=not buckets_enabled)
        with bucket_three:
            long_bucket = st.number_input("10+ years (%)", 0.0, 100.0, 50.0, disabled=not buckets_enabled)
        construct = st.button("Construct bond portfolio", icon=":material/build:")
        if construct:
            try:
                maturity_buckets = None
                if buckets_enabled:
                    if not np.isclose(short_bucket + intermediate_bucket + long_bucket, 100.0):
                        raise ValueError("Maturity-bucket target weights must sum to 100%.")
                    maturity_buckets = {
                        "Under 5 years": (0.0, 5.0, short_bucket / 100),
                        "5–10 years": (5.0, 10.0, intermediate_bucket / 100),
                        "10+ years": (10.0, 1000.0, long_bucket / 100),
                    }
                st.session_state["fi_construction_result"] = construct_bond_portfolio(
                    ranked,
                    target_duration=construction_target if target_enabled else None,
                    duration_band=band if band_enabled else None,
                    min_position=min_position / 100,
                    max_position=max_position / 100,
                    issuer_cap=issuer_cap / 100,
                    credit_quality_cap=quality_cap / 100,
                    sector_cap=sector_cap / 100,
                    yield_floor=yield_floor / 100,
                    duration_ceiling=duration_ceiling,
                    maturity_buckets=maturity_buckets,
                )
            except ValueError as exc:
                st.session_state.pop("fi_construction_result", None)
                st.error(f"Bond portfolio construction could not run: {exc}")
        construction = st.session_state.get("fi_construction_result")
        if construction is not None:
            weights, summary, validation = construction
            st.dataframe(
                weights.to_frame(), width="stretch",
                column_config={"Portfolio Weight": st.column_config.NumberColumn(format="percent")},
            )
            st.dataframe(
                summary.to_frame(), width="stretch",
                column_config={"Value": st.column_config.NumberColumn(format="%.6f")},
            )
            st.dataframe(validation, hide_index=True, width="stretch")
    with st.expander("Methodology and limitations", icon=":material/info:"):
        st.write(
            "Filters are inclusive and rankings use exactly one displayed formula. Issuer, sector, credit quality, "
            "callable status, and tax status are never inferred. Portfolio construction is a long-only linear "
            "allocation using explicit classifications. It does not model default, recovery, liquidity, embedded "
            "options, taxes, transaction costs, liabilities, or nonparallel yield-curve movements."
        )


def render_fixed_income_workspace() -> None:
    """Render the fixed-income secondary workspace and preserve completed outputs in session state."""
    st.subheader("Fixed Income")
    st.caption(
        "Explicit cash-flow analytics for option-free bonds, separate from adjusted-price market-history analysis. "
        "Outputs are research diagnostics, not personalized investment advice."
    )
    view = st.segmented_control(
        "Fixed-income view",
        ["Bond calculator", "Bond portfolio", "Rate scenarios", "Bond selection"],
        default="Bond calculator",
        key="fi_view",
        width="stretch",
        persist_state="session",
    )
    if view == "Bond portfolio":
        _render_portfolio()
    elif view == "Rate scenarios":
        _render_scenarios()
    elif view == "Bond selection":
        _render_selection()
    else:
        _render_calculator()
