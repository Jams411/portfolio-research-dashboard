"""Streamlit entrypoint for PortfolioLens."""
from __future__ import annotations

from datetime import date
import os
from pathlib import Path
import subprocess

import pandas as pd
import plotly.express as px
import streamlit as st

from portfolio_dashboard.config import PRESETS, TRADING_DAYS
from portfolio_dashboard.construction import (
    capital_allocation_line, constrained_portfolio_weights, constraint_validation_summary,
    complete_portfolio_statistics, complete_portfolio_weights, efficient_frontier,
    optimizer_statistics, parse_group_caps, target_return_weights,
)
from portfolio_dashboard.data import MarketDataError, download_prices, parse_tickers, parse_weight_input, validate_dates
from portfolio_dashboard.formatting import metric_value, money, pct, ratio
from portfolio_dashboard.performance import (
    asset_risk_return_table, diversification_effect, drawdown_series, monthly_returns,
)
from portfolio_dashboard.pipeline import run_analysis
from portfolio_dashboard.rebalancing import compare_rebalancing_policies, rebalancing_plan
from portfolio_dashboard.reporting import generate_html_report, research_summary
from portfolio_dashboard.research import (
    deterministic_insights, portfolio_comparison, portfolio_health_score, what_if_analysis,
)
from portfolio_dashboard.risk import historical_cvar, historical_var
from portfolio_dashboard.strategy import momentum_backtest
from portfolio_dashboard.stress import custom_shock, historical_stress

st.set_page_config(page_title="PortfolioLens", page_icon=":material/analytics:", layout="wide")

@st.cache_data(ttl=3600, max_entries=32, show_spinner=False)
def cached_prices(tickers: tuple[str, ...], start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    return download_prices(tickers, start, end)


def metric_frame(values: dict[str, float]) -> pd.DataFrame:
    """Return a numeric metric table suitable for export and reporting."""
    return pd.DataFrame({"Metric": list(values), "Value": list(values.values())}).set_index("Metric")


def display_metric_frame(values: dict[str, float]) -> pd.DataFrame:
    """Return a metric table with units selected by metric identity."""
    formatted = [metric_value(name, value) for name, value in values.items()]
    return pd.DataFrame({"Metric": list(values), "Value": formatted}).set_index("Metric")


def percent_table(frame: pd.DataFrame) -> pd.io.formats.style.Styler:
    return frame.style.format("{:.2%}", na_rep="—")


def line_chart(frame: pd.DataFrame, title: str, y_title: str) -> None:
    fig = px.line(frame, title=title, labels={"value": y_title, "index": "Date", "variable": "Series"})
    fig.update_layout(legend_title_text="", hovermode="x unified", margin=dict(l=10, r=10, t=50, b=10))
    st.plotly_chart(fig, width="stretch", theme="streamlit")


@st.cache_data(show_spinner=False)
def build_identifier() -> str:
    """Return the deployed source revision without requiring a build-time secret."""
    for variable in ("STREAMLIT_GIT_COMMIT", "COMMIT_SHA", "GITHUB_SHA"):
        value = os.environ.get(variable, "").strip()
        if value:
            return value[:12]
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short=12", "HEAD"],
            cwd=Path(__file__).resolve().parent,
            check=True,
            capture_output=True,
            text=True,
            timeout=2,
        )
        return result.stdout.strip() or "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


ANALYSIS_STATE_KEYS = (
    "result", "current_shocks", "selected_target_method", "normalized", "analysis_tab", "shock_editor",
    "what_if_weights", "what_if_shocks", "what_if_result", "what_if_weight_editor", "what_if_shock_editor",
    "target_return_result",
    "selected_rebalancing_policy",
    "constrained_result", "constraint_editor",
)


def clear_analysis_state() -> None:
    """Remove outputs whose inputs no longer match the current widget values."""
    for key in ANALYSIS_STATE_KEYS:
        st.session_state.pop(key, None)


st.title("PortfolioLens")
st.caption("Multi-Asset Portfolio Analytics & Investment Research")
st.caption(f"Application build: `{build_identifier()}`")

with st.sidebar:
    st.header("Analysis inputs")
    preset = st.selectbox("Example portfolio", ["Custom"] + list(PRESETS), on_change=clear_analysis_state)
    default_tickers, default_weights = PRESETS.get(preset, ("SPY, AGG, GLD", "50, 35, 15"))
    ticker_text = st.text_input(
        "Portfolio tickers", value=default_tickers, help="Comma-separated; duplicates are removed.",
        on_change=clear_analysis_state,
    )
    equal = st.checkbox("Use equal weights", value=False, on_change=clear_analysis_state)
    weight_text = st.text_input(
        "Weights (%)", value=default_weights, disabled=equal,
        help="Same order as tickers. Approximate totals within 0.1% are normalized with notice.",
        on_change=clear_analysis_state,
    )
    start_input = st.date_input("Start date", date(2018, 1, 1), on_change=clear_analysis_state)
    end_input = st.date_input("End date", date.today(), on_change=clear_analysis_state)
    benchmark_ticker = st.text_input(
        "Benchmark", "SPY", help="Enter exactly one benchmark ticker.", on_change=clear_analysis_state
    )
    initial_value = st.number_input(
        "Initial portfolio value", min_value=1.0, value=100000.0, step=5000.0,
        on_change=clear_analysis_state,
    )
    risk_free = st.number_input(
        "Annual risk-free rate (%)", min_value=-99.0, max_value=100.0, value=4.0, step=0.1,
        on_change=clear_analysis_state,
    ) / 100
    transaction_cost = st.number_input(
        "Transaction cost rate (%)", min_value=0.0, max_value=10.0, value=0.10, step=0.05,
        help="Applied proportionally to strategy position changes and rebalancing gross trade notional.",
        on_change=clear_analysis_state,
    ) / 100
    rebalancing_threshold = st.number_input(
        "Rebalancing drift threshold (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.5,
        help="Threshold policy trades when any holding's absolute weight drift reaches this level.",
        on_change=clear_analysis_state,
    ) / 100
    with st.expander("Momentum parameters"):
        short_window = st.number_input("Short moving average", 2, 500, 50, on_change=clear_analysis_state)
        long_window = st.number_input("Long moving average", 3, 1000, 200, on_change=clear_analysis_state)
    run = st.button("Run analysis", type="primary", width="stretch")
    if st.button("Reset", width="stretch"):
        st.session_state.clear()
        st.rerun()

if run:
    clear_analysis_state()
    try:
        tickers = parse_tickers(ticker_text)
        benchmark_candidates = parse_tickers(benchmark_ticker)
        if len(benchmark_candidates) != 1:
            raise ValueError("Enter exactly one benchmark ticker.")
        benchmark = benchmark_candidates[0]
        start, end = validate_dates(start_input, end_input)
        weights, normalized = parse_weight_input(tickers, weight_text, equal_weight=equal)
        if short_window >= long_window:
            raise ValueError("Short moving-average window must be below the long window.")
        with st.spinner("Downloading adjusted market history and running analytics…"):
            prices = cached_prices(tuple(tickers), start, end)
            benchmark_prices = cached_prices((benchmark,), start, end)[benchmark]
            analysis = run_analysis(prices, benchmark_prices, weights, risk_free)
            strategy_asset = tickers[0]
            strategy_data, strategy_stats = momentum_backtest(
                analysis.prices[strategy_asset], int(short_window), int(long_window), transaction_cost, risk_free
            )
            default_shocks = pd.Series(-0.10, index=tickers, dtype=float)
            historical = historical_stress(analysis.prices, weights, analysis.benchmark_prices)
            plans = {
                name: rebalancing_plan(weights, analysis.allocations[name], initial_value)
                for name in analysis.allocations.columns
            }
            policy_summary, policy_histories, policy_trades = compare_rebalancing_policies(
                analysis.asset_returns, weights, initial_value, transaction_cost,
                rebalancing_threshold, risk_free,
            )
            try:
                frontier, frontier_weights = efficient_frontier(analysis.asset_returns, risk_free, points=25)
                construction_stats = pd.DataFrame({
                    name: optimizer_statistics(analysis.asset_returns, analysis.allocations[name], risk_free)
                    for name in analysis.allocations.columns
                }).T
                tangency_stats = construction_stats.loc["Maximum Sharpe"].to_dict()
                cal = capital_allocation_line(tangency_stats, risk_free)
                construction_error = None
            except (ValueError, RuntimeError) as exc:
                frontier, frontier_weights, construction_stats, cal = (
                    pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
                )
                construction_error = str(exc)
        st.session_state["result"] = {
            "tickers": tickers, "benchmark_ticker": benchmark, "weights": weights,
            "requested_start": start, "requested_end": end, "initial_value": initial_value,
            "risk_free": risk_free, "transaction_cost": transaction_cost, "analysis": analysis,
            "strategy_asset": strategy_asset, "strategy_data": strategy_data,
            "strategy_stats": strategy_stats, "historical": historical, "plans": plans,
            "short_window": int(short_window), "long_window": int(long_window),
            "frontier": frontier, "frontier_weights": frontier_weights,
            "construction_stats": construction_stats, "cal": cal,
            "construction_error": construction_error,
            "rebalancing_threshold": rebalancing_threshold,
            "policy_summary": policy_summary, "policy_histories": policy_histories,
            "policy_trades": policy_trades,
        }
        st.session_state["current_shocks"] = default_shocks
        st.session_state["what_if_weights"] = weights.copy()
        st.session_state["what_if_shocks"] = default_shocks.copy()
        st.session_state["selected_target_method"] = "Equal Weight" if "Equal Weight" in plans else next(iter(plans))
        st.session_state["normalized"] = normalized
        st.session_state["analysis_tab"] = "Overview"
    except (ValueError, MarketDataError) as exc:
        st.error(f"Analysis could not run: {exc}")

tab_names = [
    "Overview", "Performance", "Risk", "Benchmark & Attribution", "Portfolio Optimization",
    "Momentum Strategy", "Stress Testing", "Research Workspace", "Research Report", "Methodology & Limitations",
]
tabs = st.tabs(tab_names, key="analysis_tab", on_change="rerun")

if "result" not in st.session_state:
    open_tab = next((index for index, tab in enumerate(tabs) if tab.open), 0)
    with tabs[open_tab]:
        if open_tab == 4:
            st.subheader("Portfolio Optimization")
            st.info("Run an analysis from the sidebar to calculate the efficient frontier and optimized portfolios.")
            st.markdown("""
**This top-level workspace displays:**

- Efficient Frontier and current portfolio point
- Global Minimum Variance and Maximum Sharpe / Tangency portfolios
- Target Return portfolio construction
- Non-leveraged Capital Allocation Line
- Complete portfolio risk preference
- Expected return, volatility, Sharpe ratio, and optimized weights
- Methodology, limitations, and downloadable results
""")
            st.caption(
                "Historical arithmetic returns and sample covariance are estimation inputs, not forecasts. "
                "Long-only weights sum to 100%; short selling and leverage are disabled. Workbook 2 does not "
                "supply a numerical risk-aversion utility function, so risk preference is selected directly."
            )
        elif open_tab == 9:
            st.subheader("Methodology and limitations")
            st.write(f"Application build: `{build_identifier()}`")
            st.info("Run an analysis to view the complete methodology alongside calculated results.")
        else:
            st.info("Choose a preset or enter portfolio inputs in the sidebar, then select **Run analysis**. No market data are downloaded until then.")
            if open_tab == 0:
                st.markdown("### What this application answers")
                st.write("How has the portfolio performed? What drives risk? How does it compare with a benchmark? Which historical long-only portfolios satisfy explicit constraints? How do rebalancing policies, implementation costs, strategy behavior, and stress losses differ?")
    st.stop()

r = st.session_state["result"]
a = r["analysis"]
cvar95 = historical_cvar(a.portfolio_returns)
allocation_comparison = portfolio_comparison(a.asset_returns, a.allocations, r["weights"], r["risk_free"])
health_score, health_coverage, health_components = portfolio_health_score(
    a.performance, a.benchmark, r["weights"], cvar95,
)
insights = deterministic_insights(
    a.performance, a.benchmark, r["weights"], a.volatility_contributions, cvar95,
)
if st.session_state.get("normalized"):
    st.warning("Weights were within the allowed 0.1% tolerance and were normalized to exactly 100%.")
for warning in a.allocation_warnings:
    st.warning(warning)
st.caption(
    f"Common adjusted-price history: {a.prices.index.min().date()} to {a.prices.index.max().date()} · "
    f"{len(a.prices):,} observations · benchmark: {r['benchmark_ticker']}"
)
st.caption("Historical research only · constant portfolio weights · not personalized financial advice")

if tabs[0].open:
    with tabs[0]:
        st.subheader("Portfolio at a glance")
        cards = [
            ("Health score", f"{health_score:.0f}/100"),
            ("Total return", pct(a.performance["Total Return"])),
            ("Arithmetic return", pct(a.performance["Historical Arithmetic Annualized Return"])),
            ("CAGR", pct(a.performance["CAGR"])),
            ("Volatility", pct(a.performance["Annualized Volatility"])),
            ("Performance Sharpe", ratio(a.performance["Sharpe Ratio"])),
            ("Max drawdown", pct(a.performance["Maximum Drawdown"])),
        ]
        with st.container(horizontal=True):
            for label, value in cards:
                st.metric(label, value, border=True)
        st.caption(f"Health Score is a transparent historical diagnostic with {health_coverage:.0%} metric coverage, not an investment recommendation.")
        growth = pd.concat([
            (1 + a.portfolio_returns).cumprod().rename("Portfolio"),
            (1 + a.benchmark_returns).cumprod().rename(r["benchmark_ticker"]),
        ], axis=1)
        line_chart(growth * r["initial_value"], "Growth of the initial portfolio value", "Value ($)")
        st.dataframe(r["weights"].rename("Weight").to_frame(), width="stretch", column_config={
            "Weight": st.column_config.NumberColumn(format="percent")
        })

if tabs[1].open:
    with tabs[1]:
        st.subheader("Performance")
        st.caption(
            "Arithmetic return is the historical expected-return estimate used by Sharpe and optimization. "
            "CAGR is realized compound growth. Performance Sharpe and optimizer Sharpe use the same arithmetic convention."
        )
        st.dataframe(display_metric_frame(a.performance), width="stretch")
        line_chart((1 + a.portfolio_returns).cumprod().to_frame("Portfolio"), "Cumulative portfolio growth", "Growth of $1")
        line_chart(drawdown_series(a.portfolio_returns).to_frame("Drawdown"), "Portfolio drawdown", "Drawdown")
        rolling_vol = a.portfolio_returns.rolling(63).std() * TRADING_DAYS ** 0.5
        line_chart(rolling_vol.to_frame("63-day volatility"), "Rolling annualized volatility", "Volatility")
        st.markdown("#### Monthly returns")
        st.dataframe(monthly_returns(a.portfolio_returns), width="stretch", column_config={
            month: st.column_config.NumberColumn(format="percent") for month in monthly_returns(a.portfolio_returns).columns
        })

if tabs[2].open:
    with tabs[2]:
        st.subheader("Risk and diversification")
        var95, cvar95 = historical_var(a.portfolio_returns), historical_cvar(a.portfolio_returns)
        effective = 1 / float((r["weights"] ** 2).sum())
        diversification = diversification_effect(a.asset_returns, r["weights"])
        with st.container(horizontal=True):
            st.metric("Historical VaR (95%)", pct(var95), border=True)
            st.metric("Historical CVaR (95%)", pct(cvar95), border=True)
            st.metric("Effective holdings", f"{effective:.2f}", border=True)
            st.metric("Largest risk contributor", a.volatility_contributions.idxmax(), border=True)
        with st.container(horizontal=True):
            st.metric("Weighted standalone volatility", pct(diversification["Weighted Standalone Volatility"]), border=True)
            st.metric("Portfolio volatility", pct(diversification["Portfolio Volatility"]), border=True)
            st.metric("Diversification reduction", pct(diversification["Diversification Reduction"]), border=True)
            st.metric("Reduction vs. standalone", pct(diversification["Diversification Reduction Percentage"]), border=True)
        st.caption(
            "Diversification reduction compares portfolio volatility with the weighted average of standalone asset volatilities. "
            "It reflects observed covariance and is descriptive, not a forecast or a systematic-risk estimate."
        )
        st.markdown("**Asset-level return and risk foundations**")
        asset_foundations = asset_risk_return_table(a.asset_returns)
        st.dataframe(asset_foundations, width="stretch", column_config={
            "Periodic Arithmetic Mean": st.column_config.NumberColumn(format="percent"),
            "Periodic Geometric Mean": st.column_config.NumberColumn(format="percent"),
            "Historical Arithmetic Annualized Return": st.column_config.NumberColumn(format="percent"),
            "CAGR": st.column_config.NumberColumn(format="percent"),
            "Annualized Sample Variance": st.column_config.NumberColumn(format="%.4f"),
            "Annualized Sample Volatility": st.column_config.NumberColumn(format="percent"),
            "Coefficient of Variation": st.column_config.NumberColumn(format="%.2f"),
        })
        st.download_button(
            "Download asset risk-and-return table",
            asset_foundations.to_csv().encode("utf-8"),
            "portfoliolens_asset_risk_return.csv",
            "text/csv",
        )
        st.caption(
            "Returns are simple adjusted-price returns. Arithmetic mean is the historical expected-return estimate; "
            "geometric mean is periodic compound growth; CAGR annualizes compound growth. Historical variance and covariance use sample estimates (n−1)."
        )
        corr = a.asset_returns.corr(); cov = a.asset_returns.cov() * TRADING_DAYS
        fig = px.imshow(corr, text_auto=".2f", zmin=-1, zmax=1, color_continuous_scale="RdBu_r", title="Daily return correlations")
        st.plotly_chart(fig, width="stretch", theme="streamlit")
        covariance = st.expander("Annualized covariance matrix", on_change="rerun")
        if covariance.open:
            with covariance:
                st.dataframe(cov, width="stretch", column_config={
                    column: st.column_config.NumberColumn(format="%.4f") for column in cov.columns
                })
        concentration = pd.DataFrame({
            "Weight": r["weights"], "Weight Squared": r["weights"] ** 2,
            "Volatility Contribution": a.volatility_contributions,
        })
        st.dataframe(concentration, width="stretch", column_config={
            column: st.column_config.NumberColumn(format="percent") for column in concentration.columns
        })
        st.caption("Volatility contribution uses Euler decomposition: wᵢ(Σw)ᵢ / √(w′Σw); contributions reconcile to annualized portfolio volatility.")

if tabs[3].open:
    with tabs[3]:
        st.subheader("Benchmark-relative results and attribution")
        relative_names = [
            "Portfolio Return", "Benchmark Return", "Excess Return", "Tracking Error",
            "Annualized Active Return", "Information Ratio", "Correlation", "Relative Drawdown",
        ]
        regression_names = [
            "Regression Alpha", "Beta", "R-Squared", "Residual Volatility",
            "Systematic Variance", "Idiosyncratic Variance", "Systematic Risk Share",
            "Idiosyncratic Risk Share", "Regression Observations",
        ]
        capm_names = ["CAPM Required Return", "Jensen's Alpha", "Treynor Ratio"]
        st.markdown("**Benchmark-relative performance**")
        st.dataframe(display_metric_frame({name: a.benchmark[name] for name in relative_names}), width="stretch")
        st.caption(
            "Excess Return is the difference between cumulative portfolio and benchmark returns over the selected path. "
            "Annualized Active Return is 252 times mean daily portfolio-minus-benchmark return and is the Information Ratio numerator."
        )
        st.markdown("**Excess-return single-index regression**")
        st.dataframe(display_metric_frame({name: a.benchmark[name] for name in regression_names}), width="stretch")
        st.caption(
            "Regression uses aligned daily excess returns: portfolio excess return = alpha + beta × benchmark excess return + residual. "
            "Risk shares decompose annualized excess-return variance; residual volatility uses the regression residual standard error."
        )
        st.markdown("**CAPM performance evaluation**")
        st.dataframe(display_metric_frame({name: a.benchmark[name] for name in capm_names}), width="stretch")
        st.caption(
            "CAPM required return is the risk-free rate plus beta times the benchmark risk premium. "
            "Jensen’s alpha is realized arithmetic return minus that required return; Treynor is excess return per unit of beta."
        )
        comparison = pd.concat([
            (1 + a.portfolio_returns).cumprod().rename("Portfolio"),
            (1 + a.benchmark_returns).cumprod().rename(r["benchmark_ticker"]),
        ], axis=1)
        line_chart(comparison, "Portfolio versus benchmark", "Growth of $1")
        relative = (comparison["Portfolio"] / comparison[r["benchmark_ticker"]]).rename("Relative wealth")
        line_chart(relative.to_frame(), "Rolling relative performance", "Portfolio / benchmark")
        attribution = pd.concat([a.return_contributions, a.volatility_contributions], axis=1)
        st.dataframe(attribution, width="stretch", column_config={
            column: st.column_config.NumberColumn(format="percent") for column in attribution.columns
        })
        st.caption(f"Return contributions sum to {a.return_contributions.sum():.2%}; portfolio total return is {a.performance['Total Return']:.2%}.")

if tabs[4].open:
    with tabs[4]:
        st.subheader("Portfolio Optimization")
        st.caption(
            "Workbook 2 tools: long-only efficient frontier, global minimum-variance portfolio, "
            "constrained tangency portfolio, target-return portfolio, non-leveraged Capital Allocation Line, "
            "complete portfolio, and exportable optimized weights."
        )
        if r["construction_error"]:
            st.warning(f"Efficient frontier unavailable: {r['construction_error']}")
        else:
            st.markdown("**Historical mean-variance construction**")
            st.caption(
                "Optimizer expected return is the annualized arithmetic sample mean; optimizer volatility uses the annualized sample covariance matrix. "
                "These differ from realized CAGR and are historical estimates, not forecasts or recommendations."
            )
            tangency_stats = r["construction_stats"].loc["Maximum Sharpe"].to_dict()
            risky_allocation = st.slider(
                "Risk preference — allocation to the tangency portfolio (%)", 0, 100, 100, 5,
                help=(
                    "The remainder is held in the risk-free asset. This directly selects the complete portfolio; it is not a "
                    "risk-aversion coefficient. Workbook 2 supplies no numerical utility function from which to derive one. "
                    "PortfolioLens models lending from 0% to 100% risky allocation; borrowing and leverage are not enabled."
                ),
            ) / 100
            complete_stats = complete_portfolio_statistics(tangency_stats, r["risk_free"], risky_allocation)
            complete_weights = complete_portfolio_weights(
                a.allocations["Maximum Sharpe"], risky_allocation,
            )
            comparison_stats = r["construction_stats"].copy()
            comparison_stats.loc["Complete Portfolio"] = {
                key: complete_stats[key] for key in comparison_stats.columns
            }
            if "target_return_result" in st.session_state:
                _, saved_target_stats = st.session_state["target_return_result"]
                comparison_stats.loc["Target Return"] = saved_target_stats
            comparison_stats = comparison_stats.rename(index={
                "Minimum Variance": "Global Minimum Variance",
                "Maximum Sharpe": "Tangency (Maximum Sharpe)",
            })
            st.markdown("**Current and optimized portfolio statistics**")
            st.dataframe(comparison_stats, width="stretch", column_config={
                "Optimizer Expected Return": st.column_config.NumberColumn(format="percent"),
                "Optimizer Volatility": st.column_config.NumberColumn(format="percent"),
                "Optimizer Sharpe": st.column_config.NumberColumn(format="%.2f"),
            })
            frontier_chart = px.line(
                r["frontier"].reset_index(), x="Optimizer Volatility", y="Optimizer Expected Return",
                title="Long-only efficient frontier and non-leveraged capital allocation line",
                labels={"Optimizer Volatility": "Annualized volatility", "Optimizer Expected Return": "Arithmetic expected return"},
            )
            frontier_chart.add_scatter(
                x=r["cal"]["Volatility"], y=r["cal"]["Expected Return"], mode="lines",
                name="Capital allocation line (0–100% risky portfolio)",
            )
            for name in ["Current", "Minimum Variance", "Maximum Sharpe"]:
                if name in r["construction_stats"].index:
                    point = r["construction_stats"].loc[name]
                    frontier_chart.add_scatter(
                        x=[point["Optimizer Volatility"]], y=[point["Optimizer Expected Return"]],
                        mode="markers+text", text=[name], textposition="top center", name=name,
                    )
            frontier_chart.add_scatter(
                x=[complete_stats["Optimizer Volatility"]], y=[complete_stats["Optimizer Expected Return"]],
                mode="markers+text", text=["Complete"], textposition="bottom center", name="Complete Portfolio",
            )
            if "target_return_result" in st.session_state:
                _, saved_target_stats = st.session_state["target_return_result"]
                frontier_chart.add_scatter(
                    x=[saved_target_stats["Optimizer Volatility"]],
                    y=[saved_target_stats["Optimizer Expected Return"]],
                    mode="markers+text", text=["Target"], textposition="top center", name="Target Return",
                )
            frontier_chart.update_layout(hovermode="closest", legend_title_text="", margin=dict(l=10, r=10, t=50, b=10))
            st.plotly_chart(frontier_chart, width="stretch", theme="streamlit")
            st.caption(
                "The frontier begins at the global minimum-variance portfolio. The constrained tangency estimate is the long-only maximum-Sharpe portfolio. "
                "The CAL stops at 100% risky allocation: borrowing, leverage, and short selling are not modeled."
            )
            st.markdown("**Complete portfolio: risk-free asset plus tangency portfolio**")
            with st.container(horizontal=True):
                st.metric("Risky allocation", pct(complete_stats["Risky Portfolio Weight"]), border=True)
                st.metric("Risk-free allocation", pct(complete_stats["Risk-Free Asset Weight"]), border=True)
                st.metric("Expected return", pct(complete_stats["Optimizer Expected Return"]), border=True)
                st.metric("Volatility", pct(complete_stats["Optimizer Volatility"]), border=True)
            st.dataframe(complete_weights.to_frame(), width="stretch", column_config={
                "Complete Portfolio Weight": st.column_config.NumberColumn(format="percent")
            })
            st.caption(
                "This is a point on the non-leveraged CAL, not a recommendation. With zero risky allocation, expected return equals the entered risk-free rate and volatility is zero."
            )
            risk_aversion = st.expander("Risk aversion and utility: Workbook 2 boundary")
            if risk_aversion.open:
                with risk_aversion:
                    st.write(
                        "Workbook 2 discusses risk aversion, diminishing marginal utility, and complete portfolios, "
                        "but it does not provide a risk-aversion coefficient, quadratic utility equation, indifference-curve "
                        "calculation, or Solver rule for choosing an optimal complete portfolio. PortfolioLens therefore exposes "
                        "the complete-portfolio allocation directly above and does not label it as a numerical risk-aversion model."
                    )
            with st.container(horizontal=True):
                st.download_button(
                    "Download complete-portfolio weights", complete_weights.to_csv(),
                    "complete_portfolio_weights.csv", "text/csv",
                )
                st.download_button(
                    "Download efficient-frontier data", r["frontier"].to_csv(),
                    "efficient_frontier.csv", "text/csv",
                )
                st.download_button(
                    "Download frontier weights", r["frontier_weights"].to_csv(),
                    "frontier_weights.csv", "text/csv",
                )
            expected_assets = a.asset_returns.mean() * TRADING_DAYS
            with st.form("target_return_form", border=True):
                target_percent = st.number_input(
                    "Target arithmetic annual return (%)",
                    min_value=float(expected_assets.min() * 100),
                    max_value=float(expected_assets.max() * 100),
                    value=float(r["construction_stats"].loc["Current", "Optimizer Expected Return"] * 100),
                    step=0.25,
                )
                target_submit = st.form_submit_button("Construct target-return portfolio", icon=":material/target:")
            if target_submit:
                try:
                    target_weights = target_return_weights(a.asset_returns, target_percent / 100)
                    target_stats = optimizer_statistics(a.asset_returns, target_weights, r["risk_free"])
                    st.session_state["target_return_result"] = (target_weights, target_stats)
                except (ValueError, RuntimeError) as exc:
                    st.error(f"Target-return portfolio unavailable: {exc}")
            if "target_return_result" in st.session_state:
                target_weights, target_stats = st.session_state["target_return_result"]
                with st.container(horizontal=True):
                    st.metric("Target expected return", pct(target_stats["Optimizer Expected Return"]), border=True)
                    st.metric("Optimizer volatility", pct(target_stats["Optimizer Volatility"]), border=True)
                    st.metric("Optimizer Sharpe", ratio(target_stats["Optimizer Sharpe"]), border=True)
                st.dataframe(target_weights.rename("Target Weight").to_frame(), width="stretch", column_config={
                    "Target Weight": st.column_config.NumberColumn(format="percent")
                })
            constraints = st.expander("Custom construction constraints", icon=":material/rule:", on_change="rerun")
            if constraints.open:
                with constraints:
                    st.caption(
                        "Define every classification explicitly. PortfolioLens does not infer sectors or asset classes. "
                        "Excluding an asset sets its maximum weight to zero."
                    )
                    with st.form("constraint_form"):
                        objective = st.selectbox(
                            "Objective", ["Minimum Variance", "Maximum Sharpe", "Target Return"],
                        )
                        constraint_editor = st.data_editor(
                            pd.DataFrame({
                                "Ticker": r["tickers"], "Included": True,
                                "Minimum Weight (%)": 0.0, "Maximum Weight (%)": 100.0,
                                "User-defined Group": "",
                            }),
                            disabled=["Ticker"], hide_index=True, width="stretch", key="constraint_editor",
                            column_config={
                                "Included": st.column_config.CheckboxColumn(required=True),
                                "Minimum Weight (%)": st.column_config.NumberColumn(min_value=0.0, max_value=100.0, format="%.2f%%", required=True),
                                "Maximum Weight (%)": st.column_config.NumberColumn(min_value=0.0, max_value=100.0, format="%.2f%%", required=True),
                                "User-defined Group": st.column_config.TextColumn(help="Optional explicit group label, such as Growth."),
                            },
                        )
                        group_cap_text = st.text_input(
                            "Group caps (%)", placeholder="Growth:60, Defensive:50",
                            help="Optional comma-separated Group:percent pairs matching the editable group labels.",
                        )
                        constrained_target = st.number_input(
                            "Target arithmetic annual return (%)",
                            min_value=float(expected_assets.min() * 100),
                            max_value=float(expected_assets.max() * 100),
                            value=float(r["construction_stats"].loc["Current", "Optimizer Expected Return"] * 100),
                            step=0.25, help="Used only when the selected objective is Target Return.",
                        )
                        constraint_submit = st.form_submit_button(
                            "Run constrained optimization", type="primary", icon=":material/calculate:",
                        )
                    if constraint_submit:
                        try:
                            tickers_index = pd.Index(constraint_editor["Ticker"])
                            included = pd.Series(constraint_editor["Included"].to_numpy(dtype=bool), index=tickers_index)
                            minimums = pd.Series(
                                constraint_editor["Minimum Weight (%)"].to_numpy(dtype=float) / 100,
                                index=tickers_index,
                            )
                            maximums = pd.Series(
                                constraint_editor["Maximum Weight (%)"].to_numpy(dtype=float) / 100,
                                index=tickers_index,
                            )
                            minimums.loc[~included] = 0.0
                            maximums.loc[~included] = 0.0
                            groups = pd.Series(
                                constraint_editor["User-defined Group"].fillna("").astype(str).str.strip().to_numpy(),
                                index=tickers_index,
                            )
                            group_caps = parse_group_caps(group_cap_text)
                            constrained_weights = constrained_portfolio_weights(
                                a.asset_returns, objective, r["risk_free"],
                                constrained_target / 100 if objective == "Target Return" else None,
                                minimums, maximums, groups, group_caps,
                            )
                            constrained_stats = optimizer_statistics(
                                a.asset_returns, constrained_weights, r["risk_free"],
                            )
                            validation = constraint_validation_summary(
                                constrained_weights, minimums, maximums, groups, group_caps,
                            )
                            st.session_state["constrained_result"] = (
                                constrained_weights, constrained_stats, validation,
                            )
                        except (ValueError, RuntimeError) as exc:
                            st.error(f"Constrained optimization unavailable: {exc}")
                    if "constrained_result" in st.session_state:
                        constrained_weights, constrained_stats, validation = st.session_state["constrained_result"]
                        with st.container(horizontal=True):
                            st.metric("Expected return", pct(constrained_stats["Optimizer Expected Return"]), border=True)
                            st.metric("Volatility", pct(constrained_stats["Optimizer Volatility"]), border=True)
                            st.metric("Sharpe", ratio(constrained_stats["Optimizer Sharpe"]), border=True)
                        st.dataframe(constrained_weights.rename("Constrained Weight").to_frame(), width="stretch", column_config={
                            "Constrained Weight": st.column_config.NumberColumn(format="percent")
                        })
                        st.dataframe(validation, width="stretch", hide_index=True, column_config={
                            "Result": st.column_config.NumberColumn(format="percent"),
                            "Limit": st.column_config.NumberColumn(format="percent"),
                            "Pass": st.column_config.CheckboxColumn(),
                            "Breach": st.column_config.NumberColumn(format="percent"),
                        })
            optimized_weights = pd.DataFrame({
                "Current Portfolio": r["weights"],
                "Global Minimum Variance": a.allocations["Minimum Variance"],
                "Tangency (Maximum Sharpe)": a.allocations["Maximum Sharpe"],
            })
            if "target_return_result" in st.session_state:
                target_weights, _ = st.session_state["target_return_result"]
                optimized_weights["Target Return"] = target_weights
            optimized_weights = optimized_weights.reindex(complete_weights.index)
            optimized_weights["Complete Portfolio"] = complete_weights
            st.markdown("**Optimized weights**")
            st.dataframe(optimized_weights, width="stretch", column_config={
                column: st.column_config.NumberColumn(format="percent")
                for column in optimized_weights.columns
            })
            st.download_button(
                "Download optimized weights", optimized_weights.to_csv(),
                "portfolio_optimization_weights.csv", "text/csv",
            )
            st.caption(
                "All risky portfolios are long-only and fully invested. The complete portfolio adds the risk-free asset; "
                "historical arithmetic estimates are inputs, not forecasts or recommendations."
            )
        st.divider()
        st.markdown("### Rebalancing decision support")
        st.markdown("**Allocation weights and target trade plan**")
        st.dataframe(a.allocations, width="stretch", column_config={
            column: st.column_config.NumberColumn(format="percent") for column in a.allocations.columns
        })
        available = list(a.allocations.columns)
        if st.session_state.get("selected_target_method") not in available:
            st.session_state["selected_target_method"] = "Equal Weight" if "Equal Weight" in available else available[0]
        target_method = st.selectbox("Rebalance target", available, key="selected_target_method")
        plan = r["plans"][target_method]
        st.dataframe(plan, width="stretch", hide_index=True, column_config={
            "Current Weight": st.column_config.NumberColumn(format="percent"),
            "Target Weight": st.column_config.NumberColumn(format="percent"),
            "Weight Change": st.column_config.NumberColumn(format="percent"),
            "Current Dollar Allocation": st.column_config.NumberColumn(format="dollar"),
            "Target Dollar Allocation": st.column_config.NumberColumn(format="dollar"),
            "Estimated Buy / Sell": st.column_config.NumberColumn(format="dollar"),
        })
        st.caption("Positive estimated amounts are buys; negative amounts are sells. Totals reconcile before transaction costs and rounding.")
        st.download_button("Download rebalancing CSV", plan.to_csv(index=False), "rebalancing_plan.csv", "text/csv")
        st.markdown("**Rebalancing policy simulation**")
        st.caption(
            "Unlike the constant-weight analytical portfolio, these holdings drift with asset returns. Monthly, quarterly, and annual policies trade at completed period ends; "
            f"the threshold policy trades at {r['rebalancing_threshold']:.2%} maximum absolute drift. Costs apply only when trades occur."
        )
        st.dataframe(r["policy_summary"], width="stretch", column_config={
            column: st.column_config.NumberColumn(format="percent")
            for column in ["Total Return", "CAGR", "Annualized Volatility", "Maximum Drawdown", "Total Turnover", "Ending Maximum Drift"]
        } | {
            "Sharpe Ratio": st.column_config.NumberColumn(format="%.2f"),
            "Transaction Costs": st.column_config.NumberColumn(format="dollar"),
            "Rebalancing Dates": st.column_config.NumberColumn(format="%d"),
        })
        policies = list(r["policy_summary"].index)
        if st.session_state.get("selected_rebalancing_policy") not in policies:
            st.session_state["selected_rebalancing_policy"] = "Quarterly"
        selected_policy = st.selectbox(
            "Policy detail", policies, key="selected_rebalancing_policy",
            help="Select a policy to inspect value, drift, rebalance dates, and trades.",
        )
        policy_history = r["policy_histories"][selected_policy]
        line_chart(policy_history[["Portfolio Value"]], f"{selected_policy} portfolio value", "Value ($)")
        line_chart(policy_history[["Maximum Drift"]], f"{selected_policy} maximum drift", "Absolute weight drift")
        rebalance_dates = policy_history.loc[policy_history["Rebalanced"], ["Portfolio Value", "Turnover", "Transaction Costs"]]
        if rebalance_dates.empty:
            st.info("This policy produced no rebalancing dates in the selected history.")
        else:
            st.dataframe(rebalance_dates, width="stretch", column_config={
                "Portfolio Value": st.column_config.NumberColumn(format="dollar"),
                "Turnover": st.column_config.NumberColumn(format="percent"),
                "Transaction Costs": st.column_config.NumberColumn(format="dollar"),
            })
        selected_trades = r["policy_trades"][selected_policy]
        if selected_trades.empty:
            st.info("No trades were generated for this policy and sample.")
        else:
            st.dataframe(selected_trades, width="stretch", hide_index=True, column_config={
                "Date": st.column_config.DateColumn(format="MMM DD, YYYY"),
                "Before Weight": st.column_config.NumberColumn(format="percent"),
                "Target Weight": st.column_config.NumberColumn(format="percent"),
                "After Weight": st.column_config.NumberColumn(format="percent"),
                "Trade Before Cost": st.column_config.NumberColumn(format="dollar"),
                "Estimated Transaction Cost": st.column_config.NumberColumn(format="dollar"),
                "Drift Before Trade": st.column_config.NumberColumn(format="percent"),
            })
        with st.container(horizontal=True):
            st.download_button(
                "Download policy history", policy_history.to_csv(),
                f"{selected_policy.lower().replace(' ', '_')}_history.csv", "text/csv",
            )
            st.download_button(
                "Download trade history", selected_trades.to_csv(index=False),
                f"{selected_policy.lower().replace(' ', '_')}_trades.csv", "text/csv",
            )

if tabs[5].open:
    with tabs[5]:
        st.subheader(f"Dual-moving-average momentum · {r['strategy_asset']}")
        first_evaluation = r["strategy_data"]["Strategy Growth"].first_valid_index()
        st.caption(
            f"The first portfolio ticker is the explicit strategy instrument. Signals lag one trading day. "
            f"The shared strategy/buy-and-hold evaluation begins {first_evaluation.date()}."
        )
        stats = r["strategy_stats"]
        with st.container(horizontal=True):
            st.metric("Strategy return", pct(stats["Total Return"]), border=True)
            st.metric("Buy & hold", pct(stats["Buy & Hold Total Return"]), border=True)
            st.metric("Position changes", str(stats["Position Changes"]), border=True)
            st.metric("Time in market", pct(stats["Time in Market"]), border=True)
        line_chart(r["strategy_data"][["Price", "Short MA", "Long MA"]], "Price and moving averages", "Price")
        line_chart(r["strategy_data"][["Strategy Growth", "Buy & Hold Growth"]], "Strategy versus buy-and-hold", "Growth of $1")
        dd_compare = pd.concat([
            drawdown_series(r["strategy_data"].loc[first_evaluation:, "Strategy Return"]).rename("Strategy"),
            drawdown_series(r["strategy_data"].loc[first_evaluation:, "Buy & Hold Return"]).rename("Buy & hold"),
        ], axis=1)
        line_chart(dd_compare, "Drawdown comparison", "Drawdown")
        st.dataframe(display_metric_frame(stats), width="stretch")
        st.download_button("Download strategy results CSV", r["strategy_data"].to_csv(), "strategy_results.csv", "text/csv")

if tabs[6].open:
    with tabs[6]:
        st.subheader("Custom shock test")
        st.caption("No asset classes are inferred. Enter a direct shock for every holding.")
        shock_seed = st.session_state["current_shocks"]
        edited = st.data_editor(
            pd.DataFrame({"Ticker": r["tickers"], "Shock (%)": [shock_seed[x] * 100 for x in r["tickers"]]}),
            disabled=["Ticker"], hide_index=True, width="stretch", key="shock_editor",
            column_config={"Shock (%)": st.column_config.NumberColumn(format="%.2f%%", required=True)},
        )
        shock_values = pd.Series(edited["Shock (%)"].to_numpy(dtype=float) / 100, index=edited["Ticker"])
        st.session_state["current_shocks"] = shock_values
        shock_table, shock_summary = custom_shock(r["weights"], shock_values, r["initial_value"])
        with st.container(horizontal=True):
            st.metric("Estimated impact", pct(shock_summary["Estimated Portfolio Impact"]), border=True)
            st.metric("After-shock value", money(shock_summary["After Value"]), border=True)
            st.metric("Largest loss contributor", shock_summary["Largest Loss Contributor"], border=True)
        st.dataframe(shock_table, width="stretch", column_config={
            "Weight": st.column_config.NumberColumn(format="percent"),
            "Shock": st.column_config.NumberColumn(format="percent"),
            "Portfolio Impact": st.column_config.NumberColumn(format="percent"),
            "Dollar Impact": st.column_config.NumberColumn(format="dollar"),
        })
        st.download_button("Download stress-test CSV", shock_table.to_csv(), "stress_test.csv", "text/csv")
        st.markdown("#### Historical windows")
        if r["historical"].empty:
            st.info("The selected common history does not fully cover a configured historical stress window.")
        else:
            st.dataframe(r["historical"], width="stretch", hide_index=True, column_config={
                "Portfolio Return": st.column_config.NumberColumn(format="percent"),
                "Benchmark Return": st.column_config.NumberColumn(format="percent"),
            })

if tabs[7].open:
    with tabs[7]:
        st.subheader("Investment research workspace")
        with st.container(horizontal=True):
            st.metric("Portfolio Health Score", f"{health_score:.0f}/100", border=True)
            st.metric("Metric coverage", pct(health_coverage), border=True)
            st.metric("Compared portfolios", str(len(allocation_comparison)), border=True)
            st.metric("Traceable insights", str(len(insights)), border=True)
        st.caption(
            "The score is a bounded historical diagnostic. Every component, threshold, and point is disclosed below; "
            "it does not measure investor suitability or forecast performance."
        )
        st.markdown("**Health Score components**")
        st.dataframe(
            health_components, width="stretch",
            column_config={
                "Weight": st.column_config.NumberColumn(format="percent"),
                "Metric Value": st.column_config.NumberColumn(format="%.4f"),
                "Normalized Result": st.column_config.ProgressColumn(min_value=0, max_value=1, format="percent"),
                "Points": st.column_config.NumberColumn(format="%.1f"),
            },
        )
        st.markdown("**Portfolio comparison**")
        st.dataframe(
            allocation_comparison, width="stretch",
            column_config={
                column: st.column_config.NumberColumn(format="percent")
                for column in ["Arithmetic Return", "CAGR", "Annualized Volatility", "Maximum Drawdown", "Largest Weight", "Weight Distance from Current"]
            },
        )
        st.caption("Each portfolio uses the same asset history, constant-weight return model, arithmetic Sharpe convention, and risk-free assumption. Weight distance is one-half the absolute allocation difference from current weights; it is not simulated turnover.")
        st.markdown("**Deterministic investment insights**")
        st.dataframe(insights, width="stretch", hide_index=True, column_config={
            "Value": st.column_config.NumberColumn(format="%.4f"),
        })
        st.caption("Observations are selected by the displayed rules using computed metrics only. They are not generated by an LLM and do not recommend trades.")

        st.markdown("**Interactive what-if analysis**")
        st.caption("Set hypothetical long-only weights and explicit instantaneous shocks. Submit to compare the scenario with the current constant-weight portfolio.")
        with st.form("what_if_form"):
            weight_editor = st.data_editor(
                pd.DataFrame({
                    "Ticker": r["tickers"],
                    "Weight (%)": [st.session_state["what_if_weights"][ticker] * 100 for ticker in r["tickers"]],
                }),
                disabled=["Ticker"], hide_index=True, width="stretch", key="what_if_weight_editor",
                column_config={"Weight (%)": st.column_config.NumberColumn(min_value=0.0, max_value=100.0, format="%.2f%%", required=True)},
            )
            shock_editor = st.data_editor(
                pd.DataFrame({
                    "Ticker": r["tickers"],
                    "Shock (%)": [st.session_state["what_if_shocks"][ticker] * 100 for ticker in r["tickers"]],
                }),
                disabled=["Ticker"], hide_index=True, width="stretch", key="what_if_shock_editor",
                column_config={"Shock (%)": st.column_config.NumberColumn(format="%.2f%%", required=True)},
            )
            submit_what_if = st.form_submit_button("Run what-if analysis", type="primary", icon=":material/science:")
        if submit_what_if:
            try:
                scenario_weights = pd.Series(
                    weight_editor["Weight (%)"].to_numpy(dtype=float) / 100,
                    index=weight_editor["Ticker"], dtype=float,
                )
                scenario_shocks = pd.Series(
                    shock_editor["Shock (%)"].to_numpy(dtype=float) / 100,
                    index=shock_editor["Ticker"], dtype=float,
                )
                scenario_result = what_if_analysis(
                    a.asset_returns, r["weights"], scenario_weights, scenario_shocks,
                    r["initial_value"], r["risk_free"],
                )
                st.session_state["what_if_weights"] = scenario_weights
                st.session_state["what_if_shocks"] = scenario_shocks
                st.session_state["what_if_result"] = scenario_result
            except ValueError as exc:
                st.error(f"What-if analysis could not run: {exc}")
        if "what_if_result" in st.session_state:
            scenario_comparison, scenario_shock_table, scenario_summary = st.session_state["what_if_result"]
            with st.container(horizontal=True):
                st.metric("Scenario shock impact", pct(scenario_summary["Estimated Portfolio Impact"]), border=True)
                st.metric("After-shock value", money(scenario_summary["After Value"]), border=True)
                st.metric("Largest loss contributor", str(scenario_summary["Largest Loss Contributor"]), border=True)
            st.dataframe(scenario_comparison, width="stretch", column_config={
                column: st.column_config.NumberColumn(format="percent")
                for column in ["Arithmetic Return", "CAGR", "Annualized Volatility", "Maximum Drawdown", "Largest Weight", "Weight Distance from Current"]
            })
            st.dataframe(scenario_shock_table, width="stretch", column_config={
                "Weight": st.column_config.NumberColumn(format="percent"),
                "Shock": st.column_config.NumberColumn(format="percent"),
                "Portfolio Impact": st.column_config.NumberColumn(format="percent"),
                "Dollar Impact": st.column_config.NumberColumn(format="dollar"),
            })

if tabs[8].open:
    with tabs[8]:
        st.subheader("Deterministic investment-research report")
        current_shocks = st.session_state["current_shocks"]
        shock_table, shock_summary = custom_shock(r["weights"], current_shocks, r["initial_value"])
        summary = research_summary(
            a.performance, a.benchmark, r["weights"], a.return_contributions,
            a.volatility_contributions, r["strategy_stats"], shock_summary,
        )
        for item in summary:
            st.write("• " + item)
        attribution = pd.concat([a.return_contributions, a.volatility_contributions], axis=1)
        risk_values = {
            "Historical VaR (95%)": historical_var(a.portfolio_returns),
            "Historical CVaR (95%)": historical_cvar(a.portfolio_returns),
            "Effective Number of Holdings": 1 / float((r["weights"] ** 2).sum()),
        }
        selected_target = st.session_state.get("selected_target_method", "Equal Weight")
        if selected_target not in r["plans"]:
            selected_target = next(iter(r["plans"]))
        report_policy = st.session_state.get("selected_rebalancing_policy", "Quarterly")
        if report_policy not in r["policy_histories"]:
            report_policy = "Quarterly"
        constrained_report = st.session_state.get("constrained_result")
        report = generate_html_report(
            title="PortfolioLens Investment Research Report", tickers=r["tickers"], weights=r["weights"],
            start=a.prices.index.min().date(), end=a.prices.index.max().date(), summary=summary,
            performance=metric_frame(a.performance), risk=metric_frame(risk_values),
            benchmark=metric_frame(a.benchmark), attribution=attribution, allocations=a.allocations,
            rebalancing=r["plans"][selected_target], rebalancing_method=selected_target,
            strategy=metric_frame(r["strategy_stats"]), stress=shock_table,
            benchmark_ticker=r["benchmark_ticker"], risk_free_rate=r["risk_free"],
            initial_value=r["initial_value"], health_score=health_score,
            health_coverage=health_coverage, health_components=health_components,
            comparison=allocation_comparison, insights=insights,
            what_if=st.session_state.get("what_if_result", (None, None, None))[0],
            efficient_frontier=r["frontier"] if not r["frontier"].empty else None,
            optimized_allocations=r["frontier_weights"] if not r["frontier_weights"].empty else None,
            rebalancing_policies=r["policy_summary"],
            rebalancing_history=r["policy_histories"][report_policy],
            constrained_allocation=(
                constrained_report[0].rename("Constrained Weight").to_frame()
                if constrained_report is not None else None
            ),
            constraint_validation=constrained_report[2] if constrained_report is not None else None,
            transaction_cost_rate=r["transaction_cost"],
            rebalancing_threshold=r["rebalancing_threshold"],
            selected_rebalancing_policy=report_policy,
            strategy_short_window=r["short_window"], strategy_long_window=r["long_window"],
        )
        downloads = {
            "Performance metrics": metric_frame(a.performance).to_csv(),
            "Asset metrics": attribution.to_csv(),
            "Daily returns": a.asset_returns.assign(Portfolio=a.portfolio_returns).to_csv(),
            "Portfolio comparison": allocation_comparison.to_csv(),
            "Efficient frontier": r["frontier"].to_csv(),
            "Frontier weights": r["frontier_weights"].to_csv(),
            "Rebalancing policies": r["policy_summary"].to_csv(),
            "Deterministic insights": insights.to_csv(index=False),
        }
        with st.container(horizontal=True):
            st.download_button("Download HTML report", report, "portfoliolens_research_report.html", "text/html")
            for label, payload in downloads.items():
                st.download_button(label + " CSV", payload, label.lower().replace(" ", "_") + ".csv", "text/csv")

if tabs[9].open:
    with tabs[9]:
        st.subheader("Methodology and limitations")
        st.caption(f"Application build: `{build_identifier()}`")
        st.markdown("""
**Returns and annualization.** Adjusted prices are converted to simple daily returns. Historical arithmetic annualized return is the daily sample mean × 252 and is the expected-return estimate used by Sharpe, Sortino, and maximum-Sharpe optimization. CAGR separately measures realized compound growth. Annualized variance is the daily sample variance × 252; volatility is its square root. Performance Sharpe and optimizer Sharpe both equal arithmetic annualized excess return divided by annualized volatility. Sortino uses the same arithmetic excess-return numerator and target downside deviation after converting the annual risk-free rate to an equivalent daily minimum acceptable return.

**Data and missing values.** yfinance is the sole data source. Holdings are aligned to complete common trading dates; prices are never filled or invented. Any unavailable requested ticker stops the analysis. The benchmark is downloaded separately and then inner-aligned for comparison.

**Risk and benchmark regression.** Historical 95% VaR and CVaR are nonnegative loss measures based on the empirical lower tail. The single-index model regresses aligned daily portfolio excess returns on benchmark excess returns. Its intercept and residual volatility are annualized; beta is the fitted slope; R² is the explained share of variation. Systematic and idiosyncratic variance are shown separately. CAPM required return, Jensen’s alpha, and Treynor use the same arithmetic return and annual risk-free assumptions. These are historical sample estimates, not forecasts or evidence of manager skill. Euler volatility contributions use the annualized sample covariance matrix and sum to portfolio volatility. Drawdowns include the initial portfolio value as the first peak.

**Portfolio construction.** Baseline analytics and historical stress periods use constant long-only weights. Equal weight and inverse volatility are deterministic comparison allocations; inverse volatility is not described as risk parity. The efficient frontier, global minimum-variance, maximum-Sharpe, and target-return portfolios use historical arithmetic annualized returns and the annualized sample covariance matrix. SLSQP portfolios have weights in [0,1] summing to one, with no leverage or short selling; custom asset bands, exclusions, and explicit user-defined group caps receive a separate feasibility check. The Capital Allocation Line is analytical and nonleveraged. A complete portfolio combines 0–100% in the long-only tangency portfolio with the remainder in the risk-free asset; borrowing and leverage are not modeled. Optimization failure is shown rather than replaced, and optimized portfolios are neither forecasts nor recommendations.

**Rebalancing simulation.** Rebalancing is a separate holdings-level simulation, not part of the constant-weight baseline. Buy-and-hold, monthly, quarterly, annual, and threshold policies allow weights to drift between trade dates. One-way turnover is half the gross traded value divided by pre-trade portfolio value; proportional transaction costs apply only when trades occur. Trade history records rebalancing dates and before/after allocations.

**Research diagnostics.** Portfolio comparison applies the same return history and methodology to each allocation. The Health Score is an explicitly weighted heuristic built from diversification, Sharpe, maximum drawdown, daily CVaR, and information ratio; unavailable components are excluded and metric coverage is disclosed. What-if analysis uses hypothetical long-only weights and explicit shocks without changing the saved portfolio. Deterministic insights are fixed rules tied to displayed metrics and contain no LLM-generated content or investment recommendations.

**Strategy.** The first requested holding is the explicit strategy instrument. It is long when its short moving average exceeds its long moving average, otherwise cash. Positions lag signals by one full day. Strategy and buy-and-hold statistics use the same post-warm-up period. Proportional transaction costs apply to every position change; no automatic parameter search is performed.

**Limitations.** yfinance can be delayed, revised, incomplete, or unavailable. Results exclude taxes, liquidity constraints, market impact, and slippage beyond the configured cost. Historical stress results appear only when full configured windows are covered. This application is for research and educational use only and is not personalized financial advice.
""")
