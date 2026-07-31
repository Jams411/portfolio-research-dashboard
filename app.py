"""Streamlit entrypoint for the Portfolio Research Dashboard."""
from __future__ import annotations

from datetime import date
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from portfolio_dashboard.config import PRESETS, TRADING_DAYS
from portfolio_dashboard.data import InputError, MarketDataError, download_prices, parse_tickers, validate_dates, validate_weights
from portfolio_dashboard.formatting import money, pct, ratio
from portfolio_dashboard.performance import drawdown_series, monthly_returns, performance_metrics
from portfolio_dashboard.pipeline import run_analysis
from portfolio_dashboard.rebalancing import rebalancing_plan
from portfolio_dashboard.reporting import generate_html_report, research_summary
from portfolio_dashboard.risk import historical_cvar, historical_var
from portfolio_dashboard.strategy import momentum_backtest
from portfolio_dashboard.stress import custom_shock, historical_stress

st.set_page_config(page_title="Portfolio Research Dashboard", page_icon="📊", layout="wide")
st.markdown("""<style>.block-container{max-width:1350px;padding-top:1.5rem}.stMetric{background:#f7f9fc;border:1px solid #e6ebf2;padding:12px;border-radius:8px}h1,h2,h3{color:#172b4d}</style>""", unsafe_allow_html=True)

@st.cache_data(ttl=3600, show_spinner=False)
def cached_prices(tickers: tuple[str, ...], start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    return download_prices(tickers, start, end)

def metric_frame(values: dict[str, float]) -> pd.DataFrame:
    return pd.DataFrame({"Metric": list(values), "Value": list(values.values())}).set_index("Metric")

def percent_table(frame: pd.DataFrame) -> pd.io.formats.style.Styler:
    return frame.style.format("{:.2%}", na_rep="—")

def line_chart(frame: pd.DataFrame, title: str, y_title: str) -> None:
    fig = px.line(frame, title=title, labels={"value": y_title, "index": "Date", "variable": "Series"})
    fig.update_layout(legend_title_text="", hovermode="x unified", margin=dict(l=10, r=10, t=50, b=10))
    st.plotly_chart(fig, use_container_width=True)

st.title("Portfolio Research Dashboard")
st.caption("Historical portfolio analytics, benchmark-relative research, allocation decisions, momentum testing and stress analysis.")

with st.sidebar:
    st.header("Analysis inputs")
    preset = st.selectbox("Example portfolio", ["Custom"] + list(PRESETS))
    default_tickers, default_weights = PRESETS.get(preset, ("SPY, AGG, GLD", "50, 35, 15"))
    ticker_text = st.text_input("Portfolio tickers", value=default_tickers, help="Comma-separated; duplicates are removed.")
    equal = st.checkbox("Use equal weights", value=False)
    weight_text = st.text_input("Weights (%)", value=default_weights, disabled=equal,
                                help="Same order as tickers. Approximate totals within 0.1% are normalized with notice.")
    start_input = st.date_input("Start date", date(2018, 1, 1))
    end_input = st.date_input("End date", date.today())
    benchmark_ticker = st.text_input("Benchmark", "SPY")
    initial_value = st.number_input("Initial portfolio value", min_value=1.0, value=100000.0, step=5000.0)
    risk_free = st.number_input("Annual risk-free rate (%)", value=4.0, step=0.1) / 100
    transaction_cost = st.number_input("Transaction cost per trade (%)", min_value=0.0, max_value=10.0, value=0.10, step=0.05) / 100
    st.subheader("Momentum parameters")
    short_window = st.number_input("Short moving average", 2, 500, 50)
    long_window = st.number_input("Long moving average", 3, 1000, 200)
    run = st.button("Run analysis", type="primary", use_container_width=True)
    if st.button("Reset", use_container_width=True):
        st.session_state.clear()
        st.rerun()

if run:
    try:
        tickers = parse_tickers(ticker_text)
        benchmark = parse_tickers(benchmark_ticker)[0]
        start, end = validate_dates(start_input, end_input)
        raw_weights = [1.0] * len(tickers) if equal else [float(x.strip()) for x in weight_text.split(",") if x.strip()]
        weights, normalized = validate_weights(tickers, raw_weights)
        if short_window >= long_window:
            raise InputError("Short moving-average window must be below the long window.")
        with st.spinner("Downloading adjusted market history and running analytics…"):
            # Portfolio and benchmark are requested separately by design.
            prices = cached_prices(tuple(tickers), start, end)
            benchmark_prices = cached_prices((benchmark,), start, end)[benchmark]
            analysis = run_analysis(prices, benchmark_prices, weights, risk_free)
            strategy_asset = tickers[0]
            strategy_data, strategy_stats = momentum_backtest(
                analysis.prices[strategy_asset], int(short_window), int(long_window), transaction_cost, risk_free
            )
            strategy_stats["Buy & Hold Total Return"] = float(strategy_data["Buy & Hold Growth"].iloc[-1] - 1)
            shocks = pd.Series(-0.10, index=tickers)
            shock_table, shock_summary = custom_shock(weights, shocks, initial_value)
            historical = historical_stress(analysis.prices, weights, analysis.benchmark_prices)
            plans = {name: rebalancing_plan(weights, analysis.allocations[name], initial_value)
                     for name in analysis.allocations.columns}
        st.session_state["result"] = dict(tickers=tickers, benchmark_ticker=benchmark, weights=weights,
            start=start, end=end, initial_value=initial_value, risk_free=risk_free, transaction_cost=transaction_cost,
            analysis=analysis, strategy_asset=strategy_asset, strategy_data=strategy_data, strategy_stats=strategy_stats,
            shocks=shocks, shock_table=shock_table, shock_summary=shock_summary, historical=historical, plans=plans)
        st.session_state["normalized"] = normalized
    except ValueError as exc:
        st.error(f"Input error: {exc}")
    except (InputError, MarketDataError) as exc:
        st.error(str(exc))

if "result" not in st.session_state:
    st.info("Choose a preset or enter portfolio inputs in the sidebar, then select **Run analysis**. No market data are downloaded until then.")
    st.markdown("### What this application answers")
    st.write("How has the portfolio performed? What risks and assets drive results? How does it compare with a benchmark? What allocation trades, momentum behavior, and stress losses merit attention?")
    st.stop()

r = st.session_state.result
a = r["analysis"]
if st.session_state.get("normalized"):
    st.warning("Weights were within the allowed 0.1% tolerance and were normalized to exactly 100%.")
for warning in a.allocation_warnings:
    st.warning(warning)
st.caption(f"Common adjusted-price history: {a.prices.index.min().date()} to {a.prices.index.max().date()} · {len(a.prices):,} observations · benchmark: {r['benchmark_ticker']}")

tabs = st.tabs(["Overview", "Performance", "Risk", "Benchmark & Attribution", "Construction & Rebalancing",
                "Momentum Strategy", "Stress Testing", "Research Report", "Methodology & Limitations"])

with tabs[0]:
    st.subheader("Portfolio at a glance")
    cols = st.columns(5)
    cards = [("Total return", pct(a.performance["Total Return"])), ("CAGR", pct(a.performance["CAGR"])),
             ("Volatility", pct(a.performance["Annualized Volatility"])), ("Sharpe", ratio(a.performance["Sharpe Ratio"])),
             ("Max drawdown", pct(a.performance["Maximum Drawdown"]))]
    for col, (label, value) in zip(cols, cards): col.metric(label, value)
    growth = pd.concat([(1 + a.portfolio_returns).cumprod().rename("Portfolio"),
                        (1 + a.benchmark_returns).cumprod().rename(r["benchmark_ticker"])], axis=1)
    line_chart(growth * r["initial_value"], "Growth of the initial portfolio value", "Value ($)")
    st.dataframe(percent_table(r["weights"].rename("Weight").to_frame()), use_container_width=True)

with tabs[1]:
    st.subheader("Performance")
    st.dataframe(metric_frame(a.performance).style.format({"Value": lambda x: pct(x) if abs(x) <= 1 else ratio(x)}), use_container_width=True)
    line_chart((1 + a.portfolio_returns).cumprod().to_frame("Portfolio"), "Cumulative portfolio growth", "Growth of $1")
    line_chart(drawdown_series(a.portfolio_returns).to_frame("Drawdown"), "Portfolio drawdown", "Drawdown")
    rolling_vol = a.portfolio_returns.rolling(63).std() * TRADING_DAYS ** 0.5
    line_chart(rolling_vol.to_frame("63-day volatility"), "Rolling annualized volatility", "Volatility")
    st.markdown("#### Monthly returns")
    st.dataframe(percent_table(monthly_returns(a.portfolio_returns)), use_container_width=True)

with tabs[2]:
    st.subheader("Risk and diversification")
    var95, cvar95 = historical_var(a.portfolio_returns), historical_cvar(a.portfolio_returns)
    effective = 1 / float((r["weights"] ** 2).sum())
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Historical VaR (95%)", pct(var95)); c2.metric("Historical CVaR (95%)", pct(cvar95))
    c3.metric("Effective holdings", f"{effective:.2f}"); c4.metric("Largest risk contributor", a.volatility_contributions.idxmax())
    corr = a.asset_returns.corr(); cov = a.asset_returns.cov() * TRADING_DAYS
    fig = px.imshow(corr, text_auto=".2f", zmin=-1, zmax=1, color_continuous_scale="RdBu_r", title="Daily return correlations")
    st.plotly_chart(fig, use_container_width=True)
    with st.expander("Annualized covariance matrix"):
        st.dataframe(cov.style.format("{:.4f}"), use_container_width=True)
    concentration = pd.DataFrame({"Weight": r["weights"], "Weight Squared": r["weights"] ** 2,
                                  "Volatility Contribution": a.volatility_contributions})
    st.dataframe(percent_table(concentration), use_container_width=True)
    st.caption("Volatility contribution uses Euler decomposition: wᵢ(Σw)ᵢ / √(w′Σw); contributions reconcile to annualized portfolio volatility.")

with tabs[3]:
    st.subheader("Benchmark-relative results and attribution")
    st.dataframe(metric_frame(a.benchmark).style.format({"Value": lambda x: pct(x) if abs(x) <= 1 else ratio(x)}), use_container_width=True)
    comparison = pd.concat([(1 + a.portfolio_returns).cumprod().rename("Portfolio"),
                            (1 + a.benchmark_returns).cumprod().rename(r["benchmark_ticker"])], axis=1)
    line_chart(comparison, "Portfolio versus benchmark", "Growth of $1")
    relative = (comparison["Portfolio"] / comparison[r["benchmark_ticker"]]).rename("Relative wealth")
    line_chart(relative.to_frame(), "Rolling relative performance", "Portfolio / benchmark")
    attribution = pd.concat([a.return_contributions, a.volatility_contributions], axis=1)
    st.dataframe(percent_table(attribution), use_container_width=True)
    st.caption(f"Return contributions sum to {a.return_contributions.sum():.2%}; portfolio total return is {a.performance['Total Return']:.2%}.")

with tabs[4]:
    st.subheader("Allocation comparison and rebalancing")
    st.dataframe(percent_table(a.allocations), use_container_width=True)
    target_method = st.selectbox("Rebalance target", list(a.allocations.columns), index=min(1, len(a.allocations.columns)-1))
    plan = r["plans"][target_method]
    display_plan = plan.style.format({"Current Weight": "{:.2%}", "Target Weight": "{:.2%}", "Weight Change": "{:+.2%}",
                                      "Current Dollar Allocation": "${:,.2f}", "Target Dollar Allocation": "${:,.2f}", "Estimated Buy / Sell": "${:+,.2f}"})
    st.dataframe(display_plan, use_container_width=True)
    st.caption("Positive estimated amounts are buys; negative amounts are sells. Totals reconcile before transaction costs and rounding.")
    st.download_button("Download rebalancing CSV", plan.to_csv(index=False), "rebalancing_plan.csv", "text/csv")

with tabs[5]:
    st.subheader(f"Dual-moving-average momentum · {r['strategy_asset']}")
    st.caption("The first portfolio ticker is used to keep the strategy instrument explicit. The signal is shifted one full trading day; warm-up stays in cash.")
    stats = r["strategy_stats"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Strategy return", pct(stats["Total Return"])); c2.metric("Buy & hold", pct(stats["Buy & Hold Total Return"]))
    c3.metric("Trades", str(stats["Number of Trades"])); c4.metric("Time in market", pct(stats["Time in Market"]))
    prices_plot = r["strategy_data"][["Price", "Short MA", "Long MA"]]
    line_chart(prices_plot, "Price and moving averages", "Price")
    line_chart(r["strategy_data"][["Strategy Growth", "Buy & Hold Growth"]], "Strategy versus buy-and-hold", "Growth of $1")
    dd_compare = pd.concat([drawdown_series(r["strategy_data"]["Strategy Return"]).rename("Strategy"),
                            drawdown_series(r["strategy_data"]["Buy & Hold Return"]).rename("Buy & hold")], axis=1)
    line_chart(dd_compare, "Drawdown comparison", "Drawdown")
    st.dataframe(metric_frame(stats), use_container_width=True)
    st.download_button("Download strategy results CSV", r["strategy_data"].to_csv(), "strategy_results.csv", "text/csv")

with tabs[6]:
    st.subheader("Custom shock test")
    st.caption("No asset classes are inferred. Enter a direct shock for each holding.")
    edited = st.data_editor(pd.DataFrame({"Ticker": r["tickers"], "Shock (%)": [r["shocks"][x] * 100 for x in r["tickers"]]}),
                            disabled=["Ticker"], hide_index=True, use_container_width=True)
    shock_values = pd.Series(edited["Shock (%)"].to_numpy() / 100, index=edited["Ticker"])
    shock_table, shock_summary = custom_shock(r["weights"], shock_values, r["initial_value"])
    c1, c2, c3 = st.columns(3)
    c1.metric("Estimated impact", pct(shock_summary["Estimated Portfolio Impact"])); c2.metric("After-shock value", money(shock_summary["After Value"]))
    c3.metric("Largest loss contributor", shock_summary["Largest Loss Contributor"])
    st.dataframe(shock_table.style.format({"Weight": "{:.2%}", "Shock": "{:.2%}", "Portfolio Impact": "{:.2%}", "Dollar Impact": "${:,.2f}"}), use_container_width=True)
    st.download_button("Download stress-test CSV", shock_table.to_csv(), "stress_test.csv", "text/csv")
    st.markdown("#### Historical windows")
    if r["historical"].empty: st.info("The selected common history does not fully cover a configured historical stress window.")
    else: st.dataframe(r["historical"].style.format({"Portfolio Return": "{:.2%}", "Benchmark Return": "{:.2%}"}), use_container_width=True)

with tabs[7]:
    st.subheader("Deterministic investment-research report")
    shock_table, shock_summary = custom_shock(r["weights"], r["shocks"], r["initial_value"])
    summary = research_summary(a.performance, a.benchmark, r["weights"], a.return_contributions,
                               a.volatility_contributions, r["strategy_stats"], shock_summary)
    for item in summary: st.write("• " + item)
    attribution = pd.concat([a.return_contributions, a.volatility_contributions], axis=1)
    risk_values = {"Historical VaR (95%)": historical_var(a.portfolio_returns), "Historical CVaR (95%)": historical_cvar(a.portfolio_returns),
                   "Effective Number of Holdings": 1 / float((r["weights"] ** 2).sum())}
    report = generate_html_report(title="Portfolio Research Report", tickers=r["tickers"], weights=r["weights"], start=r["start"].date(), end=r["end"].date(),
        summary=summary, performance=metric_frame(a.performance), risk=metric_frame(risk_values), benchmark=metric_frame(a.benchmark),
        attribution=attribution, allocations=a.allocations, rebalancing=r["plans"]["Equal Weight"],
        strategy=metric_frame(r["strategy_stats"]), stress=shock_table)
    downloads = {"Performance metrics": metric_frame(a.performance).to_csv(), "Asset metrics": attribution.to_csv(),
                 "Daily returns": a.asset_returns.assign(Portfolio=a.portfolio_returns).to_csv()}
    cols = st.columns(4)
    cols[0].download_button("Download HTML report", report, "portfolio_research_report.html", "text/html")
    for col, (label, payload) in zip(cols[1:], downloads.items()):
        col.download_button(label + " CSV", payload, label.lower().replace(" ", "_") + ".csv", "text/csv")

with tabs[8]:
    st.subheader("Methodology and limitations")
    st.markdown("""
**Returns and annualization.** Adjusted prices are converted to simple daily returns. CAGR compounds realized daily returns; volatility uses sample standard deviation × √252. The annual risk-free rate is subtracted from CAGR in Sharpe and Sortino ratios.

**Data and missing values.** yfinance is the sole data source. Holdings are aligned to complete common trading dates; prices are never filled or invented. Any unavailable requested ticker stops the analysis. The benchmark is downloaded separately and then inner-aligned for comparison.

**Risk.** Historical 95% VaR is the positive loss at the empirical fifth percentile; CVaR is the average loss at or below it. Beta is covariance with the benchmark divided by benchmark variance. Euler volatility contributions use the annualized sample covariance matrix and sum to portfolio volatility.

**Portfolio assumptions.** Analytics use constant long-only weights. Equal weight and inverse volatility are deterministic. Minimum variance and maximum Sharpe use SLSQP with weights in [0,1] summing to one; failure is shown rather than replaced. Historical estimates are not forecasts.

**Strategy.** The first requested holding is the explicit strategy instrument. It is long when its short moving average exceeds its long moving average, otherwise cash. Positions lag signals by one full day. Proportional transaction costs apply to every position change; no automatic parameter search is performed.

**Limitations.** yfinance can be delayed, revised, incomplete, or unavailable. Results exclude taxes, liquidity constraints, market impact, and slippage beyond the configured cost. Historical stress results appear only when full configured windows are covered. This application is for research and educational use only and is not personalized financial advice.
""")
