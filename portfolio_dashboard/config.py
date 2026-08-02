"""Shared financial conventions and scenario configuration."""

TRADING_DAYS = 252
WEIGHT_TOLERANCE = 0.001
MIN_OBSERVATIONS = 30

# Explicit benchmark aliases accepted by the public UI. This deliberately small
# list avoids guessing at ordinary equity symbols; provider-native Yahoo Finance
# symbols and unknown inputs pass through unchanged.
BENCHMARK_TICKER_ALIASES = {
    "SPX": "^GSPC",
    "S&P500": "^GSPC",
    "SP500": "^GSPC",
    "DJIA": "^DJI",
    "DOW": "^DJI",
    "NASDAQ": "^IXIC",
    "VIX": "^VIX",
    "RUT": "^RUT",
}

HISTORICAL_STRESS_PERIODS = {
    "COVID-19 market decline": ("2020-02-19", "2020-03-23"),
    "2022 equity and rate shock": ("2022-01-03", "2022-10-12"),
}

PRESETS = {
    "Balanced ETF Portfolio": ("SPY, AGG, GLD", "50, 35, 15"),
    "Equity Growth Portfolio": ("VTI, QQQ, VXUS", "45, 35, 20"),
    "Multi-Asset Portfolio": ("VTI, VXUS, AGG, GLD", "40, 20, 25, 15"),
}
