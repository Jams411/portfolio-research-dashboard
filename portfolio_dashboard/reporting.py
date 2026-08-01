"""Deterministic research narrative and deployment-safe HTML report."""
from datetime import datetime, timezone
from html import escape
import pandas as pd

from portfolio_dashboard.formatting import metric_value

def _pct(value: object) -> str:
    try:
        return f"{float(value):.2%}" if pd.notna(value) else "N/A"
    except (TypeError, ValueError):
        return "N/A"

def research_summary(performance: dict[str, float], benchmark: dict[str, float], weights: pd.Series,
                     return_contrib: pd.Series, risk_contrib: pd.Series,
                     strategy_metrics: dict[str, float], stress_summary: dict[str, object]) -> list[str]:
    """Create careful, rules-based observations without investment advice."""
    excess = benchmark.get("Excess Return", float("nan"))
    comparison = "could not be compared with" if pd.isna(excess) else "exceeded" if excess > 0 else "trailed" if excess < 0 else "matched"
    effective = 1 / float((weights ** 2).sum())
    concentration = "concentrated" if weights.max() >= 0.5 or effective < max(1.5, len(weights) / 2) else "moderately diversified"
    strat_excess = strategy_metrics.get("Total Return", float("nan")) - strategy_metrics.get("Buy & Hold Total Return", float("nan"))
    strat_text = "could not be compared with" if pd.isna(strat_excess) else "outpaced" if strat_excess > 0 else "lagged" if strat_excess < 0 else "matched"
    benchmark_amount = "an unavailable amount" if pd.isna(excess) else f"{abs(excess):.2%}"
    strategy_amount = "an unavailable amount" if pd.isna(strat_excess) else f"{abs(strat_excess):.2%}"
    return [f"The portfolio {comparison} the benchmark by {benchmark_amount} over the selected period.",
            f"Annualized volatility was {_pct(performance.get('Annualized Volatility'))}; maximum drawdown was {_pct(performance.get('Maximum Drawdown'))}.",
            f"{risk_contrib.idxmax()} was the largest volatility contributor and {return_contrib.idxmax()} was the largest total-return contributor.",
            f"The weight profile appears {concentration}; its effective number of holdings is {effective:.2f}.",
            f"The momentum strategy {strat_text} buy-and-hold by {strategy_amount}, after configured transaction costs.",
            f"The selected custom shock implies an estimated portfolio impact of {_pct(stress_summary.get('Estimated Portfolio Impact'))}."]

def _table(frame: pd.DataFrame) -> str:
    return frame.to_html(index=True, border=0, classes="data", na_rep="N/A", float_format=lambda x: f"{x:.4f}")


def _metric_table(frame: pd.DataFrame) -> str:
    """Render a one-column metric frame using semantically correct units."""
    formatted = frame.copy().astype(object)
    if "Value" in formatted.columns:
        formatted["Value"] = [metric_value(str(name), value) for name, value in frame["Value"].items()]
    return _table(formatted)


def _percentage_table(frame: pd.DataFrame) -> str:
    formatted = frame.copy().astype(object)
    for column in formatted.columns:
        formatted[column] = formatted[column].map(_pct)
    return _table(formatted)


def _financial_table(frame: pd.DataFrame) -> str:
    """Format mixed financial tables without changing their underlying exports."""
    formatted = frame.copy().astype(object)
    percent_columns = {"Weight", "Shock", "Portfolio Impact", "Current Weight", "Target Weight", "Weight Change"}
    money_columns = {"Dollar Impact", "Current Dollar Allocation", "Target Dollar Allocation", "Estimated Buy / Sell"}
    for column in formatted.columns:
        if column in percent_columns:
            formatted[column] = frame[column].map(_pct)
        elif column in money_columns:
            formatted[column] = frame[column].map(
                lambda value: f"${float(value):,.2f}" if pd.notna(value) else "N/A"
            )
    return _table(formatted)


def _comparison_table(frame: pd.DataFrame) -> str:
    formatted = frame.copy().astype(object)
    percent_columns = {
        "Arithmetic Return", "CAGR", "Annualized Volatility", "Maximum Drawdown",
        "Largest Weight", "Weight Distance from Current",
    }
    for column in formatted.columns:
        if column in percent_columns:
            formatted[column] = frame[column].map(_pct)
        else:
            formatted[column] = frame[column].map(
                lambda value: f"{float(value):.2f}" if pd.notna(value) else "N/A"
            )
    return _table(formatted)


def _health_table(frame: pd.DataFrame) -> str:
    formatted = frame.copy().astype(object)
    for column in ("Weight", "Normalized Result"):
        if column in formatted:
            formatted[column] = frame[column].map(_pct)
    if "Points" in formatted:
        formatted["Points"] = frame["Points"].map(
            lambda value: f"{float(value):.1f}" if pd.notna(value) else "N/A"
        )
    return _table(formatted)

def generate_html_report(*, title: str, tickers: list[str], weights: pd.Series, start: object, end: object,
                         summary: list[str], performance: pd.DataFrame, risk: pd.DataFrame,
                         benchmark: pd.DataFrame, attribution: pd.DataFrame, allocations: pd.DataFrame,
                         rebalancing: pd.DataFrame, rebalancing_method: str,
                         strategy: pd.DataFrame, stress: pd.DataFrame,
                         benchmark_ticker: str | None = None, risk_free_rate: float | None = None,
                         initial_value: float | None = None, health_score: float | None = None,
                         health_coverage: float | None = None, health_components: pd.DataFrame | None = None,
                         comparison: pd.DataFrame | None = None, insights: pd.DataFrame | None = None,
                         what_if: pd.DataFrame | None = None) -> bytes:
    """Generate a self-contained, deterministic investment research report."""
    assumptions = [
        "Daily simple returns and a 252-trading-day annualization convention.",
        "Constant long-only weights for historical portfolio analytics.",
        "Historical estimates are descriptive and are not forecasts or recommendations.",
    ]
    if benchmark_ticker:
        assumptions.append(f"Benchmark: {escape(benchmark_ticker)}.")
    if risk_free_rate is not None:
        assumptions.append(f"Annual risk-free assumption: {risk_free_rate:.2%}.")
    if initial_value is not None:
        assumptions.append(f"Illustrative initial portfolio value: ${initial_value:,.2f}.")
    health_content = "<p>Health diagnostic unavailable.</p>"
    if health_score is not None and pd.notna(health_score) and health_components is not None:
        coverage = "N/A" if health_coverage is None else f"{health_coverage:.0%}"
        health_content = (
            f"<div class='score'><strong>{health_score:.0f}/100</strong><span>Historical diagnostic · {coverage} metric coverage</span></div>"
            + _health_table(health_components)
            + "<p class='note'>This transparent heuristic summarizes selected historical diagnostics. It does not measure suitability, forecast returns, or prescribe an allocation.</p>"
        )
    sections = [("Executive summary", "<ul>" + "".join(f"<li>{escape(x)}</li>" for x in summary) + "</ul>"),
                ("Research assumptions", "<ul>" + "".join(f"<li>{item}</li>" for item in assumptions) + "</ul>"),
                ("Portfolio health diagnostic", health_content),
                ("Holdings and weights", _percentage_table(weights.rename("Weight").to_frame())),
                ("Performance metrics", _metric_table(performance)), ("Risk metrics", _metric_table(risk)),
                ("Benchmark comparison", _metric_table(benchmark)), ("Attribution", _percentage_table(attribution)),
                ("Portfolio comparison", _comparison_table(comparison) if comparison is not None else "<p>Comparison unavailable.</p>"),
                ("Deterministic research insights", _table(insights) if insights is not None else "<p>Insights unavailable.</p>"),
                ("What-if comparison", _comparison_table(what_if) if what_if is not None else "<p>No hypothetical scenario was included.</p>"),
                ("Allocation comparison", _percentage_table(allocations)),
                (f"Rebalancing plan — {rebalancing_method}", _financial_table(rebalancing)),
                ("Momentum-strategy results", _metric_table(strategy)), ("Stress-test results", _financial_table(stress)),
                ("Methodology", "<p>Simple daily returns; arithmetic annualized return for Sharpe, Sortino, CAPM evaluation, and optimization; CAGR for realized compound growth; annualized sample variance and volatility; 252-day annualization; constant weights; empirical 95% VaR/CVaR; excess-return single-index OLS with annualized alpha and residual volatility; CAPM required return, Jensen's alpha, and Treynor ratio; systematic/idiosyncratic variance decomposition; Euler volatility attribution; long-only constrained optimization; one-day-lagged dual-moving-average signal; proportional transaction costs. Regression and CAPM outputs are historical sample estimates, not forecasts or evidence of skill.</p>"),
                ("Limitations and disclaimer", "<p>Historical adjusted prices may contain provider errors and do not predict future results. Excludes taxes, liquidity constraints, market impact and slippage beyond configured cost. Optimization uses historical estimates. Research and educational use only; not personalized financial advice.</p>")]
    body = "".join(f"<section><h2>{escape(name)}</h2>{content}</section>" for name, content in sections)
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    html = f"""<!doctype html><html><head><meta charset='utf-8'><title>{escape(title)}</title><style>
    :root{{--ink:#172033;--navy:#102a43;--muted:#627d98;--line:#d9e2ec;--panel:#f5f8fb;--accent:#147d92}}
    *{{box-sizing:border-box}} body{{font:15px system-ui,-apple-system,sans-serif;max-width:1120px;margin:0 auto;padding:48px;color:var(--ink);line-height:1.55}}
    header{{border-bottom:3px solid var(--accent);padding-bottom:22px;margin-bottom:34px}} h1{{font-size:34px;margin:0;color:var(--navy)}}
    h2{{color:var(--navy);font-size:21px;margin-bottom:12px}} section{{margin:34px 0;break-inside:avoid}} table{{border-collapse:collapse;width:100%;font-size:12.5px}}
    th,td{{padding:8px;border-bottom:1px solid var(--line);text-align:right;vertical-align:top}} th{{background:var(--panel);color:var(--navy)}} th:first-child,td:first-child{{text-align:left}}
    .meta,.note{{color:var(--muted)}} .score{{display:flex;gap:18px;align-items:center;background:var(--panel);border-left:5px solid var(--accent);padding:18px;margin-bottom:16px}}
    .score strong{{font-size:30px;color:var(--navy)}} .score span{{color:var(--muted)}} footer{{margin-top:44px;border-top:1px solid var(--line);padding-top:16px;color:var(--muted);font-size:12px}}
    @media print{{body{{padding:20px}} section{{break-inside:auto}} a{{color:inherit;text-decoration:none}}}}
    </style></head><body><header><h1>{escape(title)}</h1><p class='meta'>PortfolioLens deterministic investment research</p><p class='meta'>Generated {generated} · Analysis period {escape(str(start))} to {escape(str(end))} · Holdings: {escape(', '.join(tickers))}</p></header>{body}<footer>PortfolioLens · Historical research and educational use only · Not personalized financial advice</footer></body></html>"""
    return html.encode("utf-8")
