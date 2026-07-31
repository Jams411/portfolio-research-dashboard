"""Offline smoke tests for the Streamlit entrypoint."""

from streamlit.testing.v1 import AppTest


def test_app_renders_helpful_initial_state():
    app = AppTest.from_file("app.py").run(timeout=20)
    assert not app.exception
    assert app.title[0].value == "Portfolio Research Dashboard"
    assert any("No market data are downloaded" in item.value for item in app.info)


def test_app_rejects_multiple_benchmark_tickers_before_download():
    app = AppTest.from_file("app.py").run(timeout=20)
    benchmark = next(item for item in app.text_input if item.label == "Benchmark")
    benchmark.set_value("SPY, VTI")
    next(item for item in app.button if item.label == "Run analysis").click()
    app.run(timeout=20)
    assert not app.exception
    assert any("exactly one benchmark ticker" in item.value for item in app.error)
