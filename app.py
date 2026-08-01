"""Streamlit entrypoint for PortfolioLens."""
from __future__ import annotations

from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st

from portfolio_dashboard.config import PRESETS, TRADING_DAYS
from portfolio_dashboard.data import MarketDataError, download_prices, parse_tickers, parse_weight_input, validate_dates
from portfolio_dashboard.formatting import metric_value, money, pct, ratio
from portfolio_dashboard.performance import drawdown_series, monthly_returns
from portfolio_dashboard.pipeline import run_analysis
from portfolio_dashboard.rebalancing import rebalancing_plan
from portfolio_dashboard.reporting import generate_html_report, research_summary
from portfolio_dashboard.risk import historical_cvar, historical_var
from portfolio_dashboard.strategy import momentum_backtest
from portfolio_dashboard.stress import custom_shock, historical_stress

st.set_page_config(page_title="PortfolioLens", page_icon="📊", layout="wide")

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


ANALYSIS_STATE_KEYS = (
    "result", "current_shocks", "selected_target_method", "normalized", "analysis_tab", "shock_editor"
)


def clear_analysis_state() -> None:
    """Remove outputs whose inputs no longer match the current widget values."""
    for key in ANALYSIS_STATE_KEYS:
        st.session_state.pop(key, None)


st.title("PortfolioLens")
st.caption("Multi-Asset Portfolio Analytics & Investment Research")

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
        "Transaction cost per position change (%)", min_value=0.0, max_value=10.0, value=0.10, step=0.05,
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
        st.session_state["result"] = {
            "tickers": tickers, "benchmark_ticker": benchmark, "weights": weights,
            "requested_start": start, "requested_end": end, "initial_value": initial_value,
            "risk_free": risk_free, "transaction_cost": transaction_cost, "analysis": analysis,
            "strategy_asset": strategy_asset, "strategy_data": strategy_data,
            "strategy_stats": strategy_stats, "historical": historical, "plans": plans,
        }
        st.session_state["current_shocks"] = default_shocks
        st.session_state["selected_target_method"] = "Equal Weight" if "Equal Weight" in plans else next(iter(plans))
        st.session_state["normalized"] = normalized
        st.session_state["analysis_tab"] = "Overview"
    except (ValueError, MarketDataError) as exc:
        st.error(f"Analysis could not run: {exc}")

if "result" not in st.session_state:
    st.info("Choose a preset or enter portfolio inputs in the sidebar, then select **Run analysis**. No market data are downloaded until then.")
    st.markdown("### What this application answers")
    st.write("How has the portfolio performed? What risks and assets drive results? How does it compare with a benchmark? What allocation trades, momentum behavior, and stress losses merit attention?")
    st.stop()

r = st.session_state["result"]
a = r["analysis"]
if st.session_state.get("normalized"):
    st.warning("Weights were within the allowed 0.1% tolerance and were normalized to exactly 100%.")
for warning in a.allocation_warnings:
    st.warning(warning)
st.caption(
    f"Common adjusted-price history: {a.prices.index.min().date()} to {a.prices.index.max().date()} · "
    f"{len(a.prices):,} observations · benchmark: {r['benchmark_ticker']}"
)
st.caption("Historical research only · constant portfolio weights · not personalized financial advice")

tab_names = [
    "Overview", "Performance", "Risk", "Benchmark & Attribution", "Construction & Rebalancing",
    "Momentum Strategy", "Stress Testing", "Research Report", "Methodology & Limitations",
]
tabs = st.tabs(tab_names, key="analysis_tab", on_change="rerun")

if tabs[0].open:
    with tabs[0]:
        st.subheader("Portfolio at a glance")
        cols = st.columns(6)
        cards = [
            ("Total return", pct(a.performance["Total Return"])),
            ("Arithmetic return", pct(a.performance["Historical Arithmetic Annualized Return"])),
            ("CAGR", pct(a.performance["CAGR"])),
            ("Volatility", pct(a.performance["Annualized Volatility"])),
            ("Performance Sharpe", ratio(a.performance["Sharpe Ratio"])),
            ("Max drawdown", pct(a.performance["Maximum Drawdown"])),
        ]
        for col, (label, value) in zip(cols, cards):
            col.metric(label, value)
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
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Historical VaR (95%)", pct(var95)); c2.metric("Historical CVaR (95%)", pct(cvar95))
        c3.metric("Effective holdings", f"{effective:.2f}"); c4.metric("Largest risk contributor", a.volatility_contributions.idxmax())
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
        st.dataframe(display_metric_frame(a.benchmark), width="stretch")
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
        st.subheader("Allocation comparison and rebalancing")
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

if tabs[5].open:
    with tabs[5]:
        st.subheader(f"Dual-moving-average momentum · {r['strategy_asset']}")
        first_evaluation = r["strategy_data"]["Strategy Growth"].first_valid_index()
        st.caption(
            f"The first portfolio ticker is the explicit strategy instrument. Signals lag one trading day. "
            f"The shared strategy/buy-and-hold evaluation begins {first_evaluation.date()}."
        )
        stats = r["strategy_stats"]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Strategy return", pct(stats["Total Return"])); c2.metric("Buy & hold", pct(stats["Buy & Hold Total Return"]))
        c3.metric("Position changes", str(stats["Position Changes"])); c4.metric("Time in market", pct(stats["Time in Market"]))
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
        c1, c2, c3 = st.columns(3)
        c1.metric("Estimated impact", pct(shock_summary["Estimated Portfolio Impact"])); c2.metric("After-shock value", money(shock_summary["After Value"]))
        c3.metric("Largest loss contributor", shock_summary["Largest Loss Contributor"])
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
        report = generate_html_report(
            title="PortfolioLens Investment Research Report", tickers=r["tickers"], weights=r["weights"],
            start=a.prices.index.min().date(), end=a.prices.index.max().date(), summary=summary,
            performance=metric_frame(a.performance), risk=metric_frame(risk_values),
            benchmark=metric_frame(a.benchmark), attribution=attribution, allocations=a.allocations,
            rebalancing=r["plans"][selected_target], rebalancing_method=selected_target,
            strategy=metric_frame(r["strategy_stats"]), stress=shock_table,
        )
        downloads = {
            "Performance metrics": metric_frame(a.performance).to_csv(),
            "Asset metrics": attribution.to_csv(),
            "Daily returns": a.asset_returns.assign(Portfolio=a.portfolio_returns).to_csv(),
        }
        with st.container(horizontal=True):
            st.download_button("Download HTML report", report, "portfoliolens_research_report.html", "text/html")
            for label, payload in downloads.items():
                st.download_button(label + " CSV", payload, label.lower().replace(" ", "_") + ".csv", "text/csv")

if tabs[8].open:
    with tabs[8]:
        st.subheader("Methodology and limitations")
        st.markdown("""
**Returns and annualization.** Adjusted prices are converted to simple daily returns. Historical arithmetic annualized return is the daily sample mean × 252 and is the expected-return estimate used by Sharpe, Sortino, and maximum-Sharpe optimization. CAGR separately measures realized compound growth. Annualized variance is the daily sample variance × 252; volatility is its square root. Performance Sharpe and optimizer Sharpe both equal arithmetic annualized excess return divided by annualized volatility. Sortino uses the same arithmetic excess-return numerator and target downside deviation after converting the annual risk-free rate to an equivalent daily minimum acceptable return.

**Data and missing values.** yfinance is the sole data source. Holdings are aligned to complete common trading dates; prices are never filled or invented. Any unavailable requested ticker stops the analysis. The benchmark is downloaded separately and then inner-aligned for comparison.

**Risk.** Historical 95% VaR and CVaR are nonnegative loss measures based on the empirical lower tail. Beta is covariance with the benchmark divided by benchmark variance. Euler volatility contributions use the annualized sample covariance matrix and sum to portfolio volatility. Drawdowns include the initial portfolio value as the first peak.

**Portfolio assumptions.** Analytics and historical stress periods use constant long-only weights. Equal weight and inverse volatility are deterministic. Minimum variance and maximum Sharpe use SLSQP with weights in [0,1] summing to one; failure is shown rather than replaced. Historical estimates are not forecasts.

**Strategy.** The first requested holding is the explicit strategy instrument. It is long when its short moving average exceeds its long moving average, otherwise cash. Positions lag signals by one full day. Strategy and buy-and-hold statistics use the same post-warm-up period. Proportional transaction costs apply to every position change; no automatic parameter search is performed.

**Limitations.** yfinance can be delayed, revised, incomplete, or unavailable. Results exclude taxes, liquidity constraints, market impact, and slippage beyond the configured cost. Historical stress results appear only when full configured windows are covered. This application is for research and educational use only and is not personalized financial advice.
""")
