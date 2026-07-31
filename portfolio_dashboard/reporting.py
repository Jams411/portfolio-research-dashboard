"""Deterministic research narrative and deployment-safe HTML report."""
from datetime import datetime, timezone
from html import escape
import pandas as pd

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
    comparison = "exceeded" if excess > 0 else "trailed" if excess < 0 else "matched"
    effective = 1 / float((weights ** 2).sum())
    concentration = "concentrated" if weights.max() >= 0.5 or effective < max(1.5, len(weights) / 2) else "moderately diversified"
    strat_excess = strategy_metrics.get("Total Return", float("nan")) - strategy_metrics.get("Buy & Hold Total Return", float("nan"))
    strat_text = "outpaced" if strat_excess > 0 else "lagged" if strat_excess < 0 else "matched"
    return [f"The portfolio {comparison} the benchmark by {abs(excess):.2%} over the selected period.",
            f"Annualized volatility was {_pct(performance.get('Annualized Volatility'))}; maximum drawdown was {_pct(performance.get('Maximum Drawdown'))}.",
            f"{risk_contrib.idxmax()} was the largest volatility contributor and {return_contrib.idxmax()} was the largest total-return contributor.",
            f"The weight profile appears {concentration}; its effective number of holdings is {effective:.2f}.",
            f"The momentum strategy {strat_text} buy-and-hold by {abs(strat_excess):.2%}, after configured transaction costs.",
            f"The selected custom shock implies an estimated portfolio impact of {_pct(stress_summary.get('Estimated Portfolio Impact'))}."]

def _table(frame: pd.DataFrame) -> str:
    return frame.to_html(index=True, border=0, classes="data", na_rep="N/A", float_format=lambda x: f"{x:.4f}")

def generate_html_report(*, title: str, tickers: list[str], weights: pd.Series, start: object, end: object,
                         summary: list[str], performance: pd.DataFrame, risk: pd.DataFrame,
                         benchmark: pd.DataFrame, attribution: pd.DataFrame, allocations: pd.DataFrame,
                         rebalancing: pd.DataFrame, strategy: pd.DataFrame, stress: pd.DataFrame) -> bytes:
    """Generate a self-contained concise HTML research report."""
    sections = [("Executive summary", "<ul>" + "".join(f"<li>{escape(x)}</li>" for x in summary) + "</ul>"),
                ("Holdings and weights", _table(weights.rename("Weight").to_frame())),
                ("Performance metrics", _table(performance)), ("Risk metrics", _table(risk)),
                ("Benchmark comparison", _table(benchmark)), ("Attribution", _table(attribution)),
                ("Allocation comparison", _table(allocations)), ("Rebalancing plan", _table(rebalancing)),
                ("Momentum-strategy results", _table(strategy)), ("Stress-test results", _table(stress)),
                ("Methodology", "<p>Simple daily returns; 252-day annualization; constant weights; empirical 95% VaR/CVaR; covariance beta; Euler volatility attribution; long-only constrained optimization; one-day-lagged dual-moving-average signal; proportional transaction costs.</p>"),
                ("Limitations and disclaimer", "<p>Historical adjusted prices may contain provider errors and do not predict future results. Excludes taxes, liquidity constraints, market impact and slippage beyond configured cost. Optimization uses historical estimates. Research and educational use only; not personalized financial advice.</p>")]
    body = "".join(f"<section><h2>{escape(name)}</h2>{content}</section>" for name, content in sections)
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    html = f"""<!doctype html><html><head><meta charset='utf-8'><title>{escape(title)}</title><style>body{{font:15px system-ui;max-width:1050px;margin:40px auto;color:#172033;line-height:1.5}}h1,h2{{color:#102a43}}section{{margin:28px 0}}table{{border-collapse:collapse;width:100%;font-size:13px}}th,td{{padding:7px;border-bottom:1px solid #d9e2ec;text-align:right}}th:first-child,td:first-child{{text-align:left}}.meta{{color:#627d98}}</style></head><body><h1>{escape(title)}</h1><p class='meta'>Generated {generated} · Analysis period {escape(str(start))} to {escape(str(end))} · Holdings: {escape(', '.join(tickers))}</p>{body}</body></html>"""
    return html.encode("utf-8")
