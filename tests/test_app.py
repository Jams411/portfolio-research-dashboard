"""Offline smoke tests for the Streamlit entrypoint."""

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


def test_app_renders_helpful_initial_state():
    app = AppTest.from_file("app.py").run(timeout=20)
    assert not app.exception
    assert app.title[0].value == "PortfolioLens"
    assert any("Multi-Asset Portfolio Analytics & Investment Research" in item.value for item in app.caption)
    assert any("No market data are downloaded" in item.value for item in app.info)


def test_app_rejects_multiple_benchmark_tickers_before_download():
    app = AppTest.from_file("app.py").run(timeout=20)
    benchmark = next(item for item in app.text_input if item.label == "Benchmark")
    benchmark.set_value("SPY, VTI")
    next(item for item in app.button if item.label == "Run analysis").click()
    app.run(timeout=20)
    assert not app.exception
    assert any("exactly one benchmark ticker" in item.value for item in app.error)


def test_equal_weight_mode_ignores_invalid_manual_weights(offline_app):
    widget(offline_app.text_input, "Portfolio tickers").set_value("SPY, AGG, GLD")
    widget(offline_app.text_input, "Weights (%)").set_value("invalid, stale, weights")
    widget(offline_app.checkbox, "Use equal weights").set_value(True)
    run_analysis(offline_app)
    assert not offline_app.exception and not offline_app.error
    weights = offline_app.session_state["result"]["weights"]
    assert weights.tolist() == pytest.approx([1 / 3, 1 / 3, 1 / 3])
    assert widget(offline_app.text_input, "Weights (%)").disabled


def test_failed_run_clears_prior_results_and_successful_rerun_recovers(offline_app):
    widget(offline_app.text_input, "Portfolio tickers").set_value("SPY, AGG, GLD")
    widget(offline_app.text_input, "Weights (%)").set_value("50,35,15")
    run_analysis(offline_app)
    assert "result" in offline_app.session_state
    assert offline_app.tabs

    widget(offline_app.text_input, "Benchmark").set_value("SPY, VTI")
    offline_app.run(timeout=20)
    assert "result" not in offline_app.session_state
    assert not offline_app.tabs
    run_analysis(offline_app)
    assert any("exactly one benchmark ticker" in item.value for item in offline_app.error)
    assert "result" not in offline_app.session_state
    assert not offline_app.tabs
    assert not offline_app.metric

    widget(offline_app.text_input, "Benchmark").set_value("SPY")
    run_analysis(offline_app)
    assert not offline_app.error
    assert "result" in offline_app.session_state
    assert offline_app.tabs
    assert offline_app.session_state["result"]["weights"].tolist() == pytest.approx([.50, .35, .15])
