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

def generate_html_report(*, title: str, tickers: list[str], weights: pd.Series, start: object, end: object,
                         summary: list[str], performance: pd.DataFrame, risk: pd.DataFrame,
                         benchmark: pd.DataFrame, attribution: pd.DataFrame, allocations: pd.DataFrame,
                         rebalancing: pd.DataFrame, rebalancing_method: str,
                         strategy: pd.DataFrame, stress: pd.DataFrame) -> bytes:
    """Generate a self-contained concise HTML research report."""
    sections = [("Executive summary", "<ul>" + "".join(f"<li>{escape(x)}</li>" for x in summary) + "</ul>"),
                ("Holdings and weights", _percentage_table(weights.rename("Weight").to_frame())),
                ("Performance metrics", _metric_table(performance)), ("Risk metrics", _metric_table(risk)),
                ("Benchmark comparison", _metric_table(benchmark)), ("Attribution", _percentage_table(attribution)),
                ("Allocation comparison", _percentage_table(allocations)),
                (f"Rebalancing plan — {rebalancing_method}", _financial_table(rebalancing)),
                ("Momentum-strategy results", _metric_table(strategy)), ("Stress-test results", _financial_table(stress)),
                ("Methodology", "<p>Simple daily returns; arithmetic annualized return for Sharpe, Sortino, CAPM evaluation, and optimization; CAGR for realized compound growth; annualized sample variance and volatility; 252-day annualization; constant weights; empirical 95% VaR/CVaR; excess-return single-index OLS with annualized alpha and residual volatility; CAPM required return, Jensen's alpha, and Treynor ratio; systematic/idiosyncratic variance decomposition; Euler volatility attribution; long-only constrained optimization; one-day-lagged dual-moving-average signal; proportional transaction costs. Regression and CAPM outputs are historical sample estimates, not forecasts or evidence of skill.</p>"),
                ("Limitations and disclaimer", "<p>Historical adjusted prices may contain provider errors and do not predict future results. Excludes taxes, liquidity constraints, market impact and slippage beyond configured cost. Optimization uses historical estimates. Research and educational use only; not personalized financial advice.</p>")]
    body = "".join(f"<section><h2>{escape(name)}</h2>{content}</section>" for name, content in sections)
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    html = f"""<!doctype html><html><head><meta charset='utf-8'><title>{escape(title)}</title><style>body{{font:15px system-ui;max-width:1050px;margin:40px auto;color:#172033;line-height:1.5}}h1,h2{{color:#102a43}}section{{margin:28px 0}}table{{border-collapse:collapse;width:100%;font-size:13px}}th,td{{padding:7px;border-bottom:1px solid #d9e2ec;text-align:right}}th:first-child,td:first-child{{text-align:left}}.meta{{color:#627d98}}</style></head><body><h1>{escape(title)}</h1><p class='meta'>Generated {generated} · Analysis period {escape(str(start))} to {escape(str(end))} · Holdings: {escape(', '.join(tickers))}</p>{body}</body></html>"""
    return html.encode("utf-8")
