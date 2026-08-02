"""Offline smoke tests for the Streamlit entrypoint."""

import base64
import json
import numpy as np
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest


def fake_download_prices(tickers, start, end):
    """Return deterministic adjusted-price-like history without network access."""
    index = pd.bdate_range("2020-01-01", periods=320)
    x = np.arange(len(index))
    return pd.DataFrame(
        {
            ticker: 100 * np.cumprod(1 + 0.0003 + 0.002 * np.sin(x / (11 + offset)))
            for offset, ticker in enumerate(tickers)
        },
        index=index,
    )


@pytest.fixture
def offline_app(monkeypatch):
    monkeypatch.setattr("portfolio_dashboard.data.download_prices", fake_download_prices)
    return AppTest.from_file("app.py").run(timeout=20)


def widget(items, label):
    return next(item for item in items if item.label == label)


def run_analysis(app):
    widget(app.button, "Run analysis").click()
    return app.run(timeout=20)


def plotly_values(value):
    """Decode Plotly's compact numeric-array representation used by AppTest."""
    if isinstance(value, dict) and "bdata" in value:
        return np.frombuffer(base64.b64decode(value["bdata"]), dtype=np.dtype(value["dtype"]))
    return np.asarray(value)


def test_app_renders_helpful_initial_state():
    app = AppTest.from_file("app.py").run(timeout=20)
    assert not app.exception
    assert app.title[0].value == "PortfolioLens"
    assert any("Multi-Asset Portfolio Analytics & Investment Research" in item.value for item in app.caption)
    assert any(item.value == "Analysis inputs" for item in app.header)
    expected_controls = {
        "Portfolio tickers", "Weights (%)", "Benchmark", "Initial portfolio value",
        "Annual risk-free rate (%)", "Transaction cost rate (%)",
        "Rebalancing drift threshold (%)",
    }
    assert expected_controls <= {
        item.label for collection in (app.text_input, app.number_input) for item in collection
    }
    assert any(item.label == "Example portfolio" for item in app.selectbox)
    assert any(item.label == "Use equal weights" for item in app.checkbox)
    assert any(item.label == "Run analysis" for item in app.button)
    assert widget(app.text_input, "Benchmark").value == "SPX"
    assert any("No market data are downloaded" in item.value for item in app.info)
    assert [tab.label for tab in app.tabs] == [
        "Overview", "Performance", "Risk", "Benchmark & Attribution", "Portfolio Optimization",
        "Momentum Strategy", "Stress Testing", "Research Workspace", "Research Report", "Methodology & Limitations",
    ]
    assert any("Application build:" in item.value for item in app.caption)
    assert not app.metric


def test_portfolio_optimization_is_visible_before_analysis():
    app = AppTest.from_file("app.py").run(timeout=20)
    app.session_state["analysis_tab"] = "Portfolio Optimization"
    app.run(timeout=20)
    assert not app.exception
    assert any(tab.label == "Portfolio Optimization" for tab in app.tabs)
    assert any(item.value == "Portfolio Optimization" for item in app.subheader)
    assert any("efficient frontier" in item.value.lower() for item in app.info)
    assert any("Global Minimum Variance" in item.value for item in app.markdown)


def test_app_rejects_multiple_benchmark_tickers_before_download():
    app = AppTest.from_file("app.py").run(timeout=20)
    benchmark = next(item for item in app.text_input if item.label == "Benchmark")
    benchmark.set_value("SPY, VTI")
    next(item for item in app.button if item.label == "Run analysis").click()
    app.run(timeout=20)
    assert not app.exception
    assert any("exactly one benchmark ticker" in item.value for item in app.error)


def test_default_spx_uses_provider_symbol_without_mapping_banner(offline_app):
    run_analysis(offline_app)
    assert not offline_app.exception and not offline_app.error
    result = offline_app.session_state["result"]
    assert result["benchmark_ticker"] == "SPX"
    assert result["benchmark_provider_ticker"] == "^GSPC"
    assert result["analysis"].benchmark_prices.name == "Benchmark"
    assert result["benchmark_alias_notice"] is None
    assert not any("mapped to Yahoo Finance symbol" in item.value for item in offline_app.info)
    assert any("benchmark: SPX" in item.value for item in offline_app.caption)
    offline_app.session_state["analysis_tab"] = "Benchmark & Attribution"
    offline_app.run(timeout=30)
    chart_payload = " ".join(item.proto.spec for item in offline_app.get("plotly_chart"))
    assert "SPX" in chart_payload
    assert "^GSPC" not in chart_payload


def test_nondefault_benchmark_alias_shows_mapping_banner(offline_app):
    widget(offline_app.text_input, "Benchmark").set_value("sp500")
    run_analysis(offline_app)
    result = offline_app.session_state["result"]
    assert result["benchmark_ticker"] == "SP500"
    assert result["benchmark_provider_ticker"] == "^GSPC"
    assert any(
        "SP500 was mapped to Yahoo Finance symbol ^GSPC." in item.value
        for item in offline_app.info
    )


def test_equal_weight_mode_ignores_invalid_manual_weights(offline_app):
    widget(offline_app.text_input, "Portfolio tickers").set_value("SPY, AGG, GLD")
    widget(offline_app.text_input, "Weights (%)").set_value("invalid, stale, weights")
    widget(offline_app.checkbox, "Use equal weights").set_value(True)
    run_analysis(offline_app)
    assert not offline_app.exception and not offline_app.error
    weights = offline_app.session_state["result"]["weights"]
    assert weights.tolist() == pytest.approx([1 / 3, 1 / 3, 1 / 3])
    assert widget(offline_app.text_input, "Weights (%)").disabled


def test_research_workspace_is_initialized_from_computed_analysis(offline_app):
    widget(offline_app.text_input, "Portfolio tickers").set_value("SPY, AGG, GLD")
    widget(offline_app.text_input, "Weights (%)").set_value("50,35,15")
    run_analysis(offline_app)
    assert not offline_app.exception
    assert "what_if_weights" in offline_app.session_state
    assert "what_if_shocks" in offline_app.session_state
    assert any(tab.label == "Research Workspace" for tab in offline_app.tabs)
    assert any(metric.label == "Health score" for metric in offline_app.metric)
    offline_app.session_state["analysis_tab"] = "Research Workspace"
    offline_app.run(timeout=20)
    assert not offline_app.exception
    assert any(item.value == "Investment research workspace" for item in offline_app.subheader)
    assert any(button.label == "Run what-if analysis" for button in offline_app.button)


def test_portfolio_optimization_view_exposes_workbook_two_tools_offline(offline_app):
    widget(offline_app.text_input, "Portfolio tickers").set_value("SPY, QQQ, TLT, GLD")
    widget(offline_app.text_input, "Weights (%)").set_value("40,30,20,10")
    run_analysis(offline_app)
    offline_app.session_state["analysis_tab"] = "Portfolio Optimization"
    offline_app.run(timeout=30)
    assert not offline_app.exception
    assert any(item.value == "Portfolio Optimization" for item in offline_app.subheader)
    assert any(item.label == "Policy detail" for item in offline_app.selectbox)
    assert any(item.label == "Construct target-return portfolio" for item in offline_app.button)
    assert any(
        item.label == "Risk preference — allocation to the tangency portfolio (%)"
        for item in offline_app.slider
    )
    assert any(item.label == "Risk aversion coefficient (A)" for item in offline_app.number_input)
    assert any(item.label == "Complete portfolio selection method" for item in offline_app.get("button_group"))
    assert any("Modern portfolio construction tools" in item.value for item in offline_app.caption)
    assert any("Current and optimized portfolio statistics" in item.value for item in offline_app.markdown)
    assert any("Optimized weights" in item.value for item in offline_app.markdown)
    assert any(item.label == "Download complete-portfolio weights" for item in offline_app.get("download_button"))
    assert any(item.label == "Download optimized weights" for item in offline_app.get("download_button"))


def test_frontier_chart_reconciles_professional_traces_offline(offline_app):
    widget(offline_app.text_input, "Portfolio tickers").set_value("SPY, AGG, GLD")
    widget(offline_app.text_input, "Weights (%)").set_value("50,35,15")
    widget(offline_app.number_input, "Annual risk-free rate (%)").set_value(4.0)
    run_analysis(offline_app)
    offline_app.session_state["analysis_tab"] = "Portfolio Optimization"
    offline_app.run(timeout=30)
    assert not offline_app.exception
    specification = json.loads(offline_app.get("plotly_chart")[0].proto.spec)
    assert specification["layout"]["title"]["text"] == "Efficient Frontier and Capital Allocation Line"
    names = {trace.get("name") for trace in specification["data"]}
    assert {
        "Efficient Frontier", "Capital Allocation Line", "Current Portfolio",
        "Global Minimum Variance", "Tangency Portfolio", "Complete Portfolio",
    } <= names
    line = next(trace for trace in specification["data"] if trace.get("name") == "Capital Allocation Line")
    line_x, line_y = plotly_values(line["x"]), plotly_values(line["y"])
    assert line_x[0] == pytest.approx(0.0)
    assert line_y[0] == pytest.approx(.04)
    tangency = next(trace for trace in specification["data"] if trace.get("name") == "Tangency Portfolio")
    tangency_x, tangency_y = plotly_values(tangency["x"]), plotly_values(tangency["y"])
    assert line_x[-1] == pytest.approx(tangency_x[0])
    assert line_y[-1] == pytest.approx(tangency_y[0])
    assert any(item.label == "Optimization Diagnostics" for item in offline_app.expander)


def test_workbook_one_risk_foundations_render_and_export_offline(offline_app):
    widget(offline_app.text_input, "Portfolio tickers").set_value("SPY, QQQ, TLT, GLD")
    widget(offline_app.text_input, "Weights (%)").set_value("40,30,20,10")
    run_analysis(offline_app)
    offline_app.session_state["analysis_tab"] = "Risk"
    offline_app.run(timeout=30)
    assert not offline_app.exception
    assert any(item.value == "Risk and diversification" for item in offline_app.subheader)
    labels = {item.label for item in offline_app.metric}
    assert {
        "Weighted standalone volatility", "Portfolio volatility",
        "Diversification reduction", "Reduction vs. standalone",
    } <= labels
    assert any("Asset-level return and risk foundations" in item.value for item in offline_app.markdown)
    assert any(
        button.label == "Download asset risk-and-return table"
        for button in offline_app.get("download_button")
    )


def test_failed_run_clears_prior_results_and_successful_rerun_recovers(offline_app):
    widget(offline_app.text_input, "Portfolio tickers").set_value("SPY, AGG, GLD")
    widget(offline_app.text_input, "Weights (%)").set_value("50,35,15")
    run_analysis(offline_app)
    assert "result" in offline_app.session_state
    assert offline_app.tabs

    widget(offline_app.text_input, "Benchmark").set_value("SPY, VTI")
    offline_app.run(timeout=20)
    assert "result" not in offline_app.session_state
    assert any(tab.label == "Portfolio Optimization" for tab in offline_app.tabs)
    run_analysis(offline_app)
    assert any("exactly one benchmark ticker" in item.value for item in offline_app.error)
    assert "result" not in offline_app.session_state
    assert any(tab.label == "Portfolio Optimization" for tab in offline_app.tabs)
    assert not offline_app.metric

    widget(offline_app.text_input, "Benchmark").set_value("SPY")
    run_analysis(offline_app)
    assert not offline_app.error
    assert "result" in offline_app.session_state
    assert offline_app.tabs
    assert offline_app.session_state["result"]["weights"].tolist() == pytest.approx([.50, .35, .15])
