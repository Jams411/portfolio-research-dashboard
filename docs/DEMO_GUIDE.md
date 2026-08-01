# Demonstration guide

## Standard demo portfolio

Introduce the application as **PortfolioLens — Multi-Asset Portfolio Analytics & Investment Research**.

Use the same settings for screenshots and interviews so results remain easy to reproduce:

| Setting | Value |
|---|---|
| Tickers | `SPY, QQQ, TLT, GLD` |
| Weights | `35, 30, 20, 15` |
| Benchmark | `VTI` |
| Dates | `2020-01-01` to `2025-12-31` |
| Initial value | `$100,000` |
| Annual risk-free rate | `4.00%` |
| Transaction cost | `0.10%` per position change |
| Momentum windows | `50` and `200` trading days |

Results are historical and can change when yfinance revises adjusted data.

## Two-minute demo

1. **Inputs and Overview — 25 seconds.** Explain strict ticker/weight validation, separate benchmark download, common-date alignment, and the headline return/risk cards.
2. **Risk — 25 seconds.** Show VaR/CVaR, effective holdings, the correlation matrix, and Euler volatility contributions that reconcile to portfolio volatility.
3. **Benchmark & Attribution — 20 seconds.** Compare cumulative wealth, excess return, tracking error, information ratio, beta, and asset contributions.
4. **Research Workspace — 30 seconds.** Explain the disclosed Health Score components and coverage, compare allocation methods under one methodology, show an insight’s metric/rule evidence, and submit one hypothetical weight-and-shock scenario.
5. **Construction & Rebalancing — 20 seconds.** Compare current, equal, inverse-volatility, minimum-variance, and maximum-Sharpe weights; show the dollar buy/sell plan.
6. **Momentum and Stress — 20 seconds.** Point out the one-day signal lag, warm-up, transaction costs, direct per-asset shocks, and complete historical windows.
7. **Report — 10 seconds.** Show deterministic observations and the professional self-contained HTML/CSV exports.

Close with: “The design favors transparent financial conventions and deterministic tests over feature breadth or personalized recommendations.”

## Five-minute interview demo

1. **Product goal — 30 seconds.** PortfolioLens is a focused historical research workflow for portfolio analytics, risk, investment research, and systematic strategy analysis.
2. **Data boundary — 40 seconds.** Normalize tickers, validate long-only weights, download adjusted history separately for holdings and benchmark, reject missing assets, and inner-align without filling prices.
3. **Performance and risk — 60 seconds.** Explain daily simple returns, constant weights, CAGR, annualized volatility, downside metrics, beta, and Euler risk contribution.
4. **Benchmark and decisions — 50 seconds.** Explain tracking error/information ratio, contribution reconciliation, allocation methods, optimizer convergence checks, and the self-financing rebalance plan.
5. **Systematic research — 50 seconds.** Explain the first holding as the explicit strategy instrument, SMA crossover, one-day lag, warm-up, costs, and common comparison period.
6. **Stress and reporting — 35 seconds.** Explain editable shocks without silent classification, exact configured historical windows, deterministic narrative, and export formats.
7. **Architecture and validation — 45 seconds.** Show `app.py`, the pure-function package, the central pipeline, synthetic tests, cached data boundary, and deployment shape.
8. **Limitations — 30 seconds.** Historical estimates are not forecasts; yfinance can fail; constant weights imply daily rebalancing; taxes, liquidity, market impact, and live execution are excluded.

## Likely questions and concise answers

**Why simple rather than log returns?** Simple returns aggregate naturally into a weighted portfolio each day and compound into wealth; the convention is used consistently.

**How do risk contributions reconcile?** Euler decomposition uses `wᵢ(Σw)ᵢ / √(w′Σw)`. Summing the components returns annualized portfolio volatility within floating-point tolerance.

**How is look-ahead bias controlled?** The crossover signal is shifted one full trading day before returns are applied, and evaluation starts only after the long-window warm-up.

**Why run momentum on one asset?** Selecting the first requested holding is explicit and auditable. A synthetic weighted portfolio price would introduce an additional rebalancing assumption.

**Why not machine learning?** The current use case does not justify the extra leakage, tuning, point-in-time data, and explanation risks. One transparent strategy better serves this project’s goal.

**Can optimized weights be trusted?** They are historical sample-based comparisons, not forecasts. Long-only constraints and solver convergence are checked, and failures are shown instead of replaced.

**What would you improve next?** First align risk-adjusted-return conventions across scorecards and optimization, then add tested periodic-rebalancing analysis.

## Limitations to acknowledge

- yfinance data can be delayed, revised, incomplete, or temporarily unavailable.
- Complete-case alignment can shorten the sample.
- The analytics assume constant weights; realized buy-and-hold weights drift.
- Historical optimizers are estimation-sensitive and do not imply forecast certainty.
- Strategy results exclude taxes, liquidity, market impact, and slippage beyond the configured proportional cost.
- The application is educational research, not personalized financial advice.
