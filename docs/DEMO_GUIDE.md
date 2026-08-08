# Demonstration guide

Verified demo URL: [portfolio-lens.streamlit.app](https://portfolio-lens.streamlit.app/)

## Visual preflight

1. Use browser zoom at 100%. The primary demo remains best at 1,100 pixels or wider, but the app is also verified at 390×844 and 430×932.
2. Confirm **Run analysis** and **Reset** are visible immediately below the compact allocation status, before the analysis-period and benchmark controls, without scrolling the sidebar.
3. Confirm **Portfolio allocation (%)** explains that one percentage is required per ticker, the live total is shown, and the allocation preview includes a Total row.
4. Enter a non-100% positive allocation and confirm **Normalize to 100%** appears; click it and verify the adjusted values are shown before analysis.
5. Keep Advanced assumptions, Implementation, and Strategy settings collapsed until their values need explanation.
6. At 1366×768, confirm all six workspaces remain on one line and the Dashboard cards show complete values.
7. Treat horizontal movement inside a wide dataframe as intentional table scrolling; the page itself should not scroll horizontally.
8. At 1,920 pixels, confirm both metric groups and the growth chart share the same full-width content edges with no empty metric column.
9. At approximately 1,100 pixels, confirm the six primary metrics wrap 4+2 and the five benchmark/risk metrics wrap 3+2; every wrapped row should fill its available width.
10. At a narrow width, collapse the sidebar and confirm the cards use two columns, then one below 420 pixels. The page itself must not scroll horizontally.
11. Confirm Plotly legends sit below each chart, the toolbar shows only download, zoom, reset, and fullscreen, and titles remain clear of those controls.
12. On Performance, Asset Pricing, and Reports, confirm wide tables scroll inside their own surface without widening the page; downloadable exports retain the full columns.
13. On Analytics → Performance, confirm **Normalized performance by holding** begins every selected line at 1.00, displays the optional benchmark with a dashed neutral line, and offers the normalized CSV download.
14. On Portfolio Optimization, confirm GMV, Tangency, Current, and Complete use marker-only display with complete names available on hover.

The 700-pixel mobile breakpoint reduces content padding to 10–12 pixels. Streamlit does not expose viewport width to server-side chart code, so the robust shared contract also keeps legends below charts on desktop. Simple charts use a 360-pixel height; correlation, CAPM, regression, and efficient-frontier views use 440 pixels.

Fresh responsive-review evidence: [390px dashboard charts](images/mobile-review/dashboard-charts-390.jpg), [430px dashboard cards](images/mobile-review/dashboard-cards-430.jpg), [768px dashboard](images/mobile-review/dashboard-768.jpg), [390px efficient frontier](images/mobile-review/efficient-frontier-390.jpg), [390px Asset Pricing](images/mobile-review/asset-pricing-390.jpg), [390px Fixed Income](images/mobile-review/fixed-income-390.jpg), [390px Reports](images/mobile-review/reports-390.jpg), and [1366px dashboard](images/mobile-review/dashboard-1366.jpg).

Dashboard color semantics are intentionally restrained: blue marks the primary portfolio value and active controls; green/red identify directionally meaningful results; gray identifies neutral risk information; amber remains reserved for warnings. Labels, signs, and context text carry the same meaning when color is unavailable.

## Normalized holding-performance walkthrough

1. Run an analysis with at least two holdings and the default SPX benchmark.
2. Open **Analytics → Performance** and review the portfolio-versus-benchmark growth chart first.
3. In **Normalized performance by holding**, leave all holdings selected. Confirm every line starts at 1.00 on the common first date.
4. Enable the optional benchmark toggle to compare the benchmark on the same normalized scale, then switch between Linear and Log presentation.
5. Hover a line to show the date, holding, Growth of $1, and cumulative change. Download `portfoliolens_normalized_holding_performance.csv` and confirm its first row contains 1.00 for every included series.

The normalized chart uses adjusted prices and is not a weighted portfolio-return calculation. Distributions are reflected according to the data provider’s adjusted-price series; provider revisions and incomplete histories can change the displayed path.

## Fixed-income walkthrough (three minutes)

1. Open **Research → Fixed Income** before running market-history analysis. Bond terms are explicit and independent of equity/ETF tickers.
2. In **Bond calculator**, use face 1,000; coupon 4%; semiannual frequency; settlement 2026-01-01; maturity 2031-01-01; YTM 5%; Actual/Actual; and +100 bps. Show clean/dirty price, current yield, Macaulay/modified duration, dollar duration, DV01, convexity, cash flows, and the three repricing methods.
3. In **Bond portfolio**, retain Bond A and Bond B defaults and select **Analyze bond portfolio**. Explain that dirty value drives weights and each contribution family reconciles.
4. In **Rate scenarios**, run +100 bps. Compare duration-only, duration-plus-convexity and full repricing, then show holding impact contributions.
5. In **Bond selection**, apply one ranking rule and show its displayed formula. Issuer, sector, credit quality, callable and tax fields are explicit editable inputs.
6. Optionally construct a long-only portfolio with duration, position, classification, yield, and maturity-bucket constraints. The objective is displayed weighted YTM, not a hidden score.
7. After running the standard market-history portfolio, open **Reports → Research Report**. Fixed-income sections appear only when bond analysis exists, alongside bond CSV exports.

Bond A deterministic checkpoints are approximately: clean price `$956.24`, current yield `4.18%`, Macaulay duration `4.570 years`, modified duration `4.458 years`, DV01 `$0.4263` per entered instrument, and convexity `23.194`. Outputs are research diagnostics, not personalized investment advice.

## Standard demo portfolio

Introduce the application as **PortfolioLens — Multi-Asset Portfolio Analytics & Investment Research**.

Use the same settings for screenshots and interviews so results remain easy to reproduce:

| Setting | Value |
|---|---|
| Tickers | `SPY, QQQ, TLT, GLD` |
| Weights | `40, 25, 20, 15` |
| Benchmark | `SPX` |
| Dates | `2020-01-01` to `2025-12-31` |
| Initial value | `$100,000` |
| Annual risk-free rate | `4.00%` |
| Transaction cost | `0.10%` proportional rate |
| Rebalancing threshold | `5.00%` absolute weight drift |
| Momentum windows | `50` and `200` trading days |

Results are historical and can change when yfinance revises adjusted data.

## Two-minute demo

1. **Dashboard — 25 seconds.** Run the four-ETF portfolio and show value, total return, CAGR, volatility, Sharpe, drawdown, beta, tracking error, information ratio, largest risk contributor, benchmark-relative result, growth, and allocation. Arithmetic return remains available in Analytics → Performance.
2. **Analytics → Risk — 20 seconds.** Show VaR/CVaR, effective holdings, correlation, and Euler volatility contributions that reconcile to portfolio volatility.
3. **Analytics → Benchmark & Attribution — 15 seconds.** Compare cumulative wealth, active return, tracking error, information ratio, beta, and contributions.
4. **Research → Security Analysis — 20 seconds.** Use the obvious security selector, then show alpha/beta, risk decomposition, characteristic line, and residuals.
5. **Portfolio Construction → Portfolio Optimization & Rebalancing — 25 seconds.** Show the frontier, GMV/tangency/CAL, optimized weights, constraints, target trades, and policy diagnostics.
6. **Strategies → Portfolio Strategies & Momentum — 15 seconds.** Point out policy comparison, the one-day momentum signal lag, shared evaluation period, turnover, costs, and drawdown.
7. **Analytics → Stress Testing — 10 seconds.** Show direct holding shocks and historical windows.
8. **Reports → Research Report — 10 seconds.** Show deterministic observations and the self-contained HTML/CSV exports.

The six primary workspaces should all be visible at once on a 1366-pixel-wide display. If the sidebar is collapsed for a chart-focused presentation, reopen it before discussing assumptions so the audience can see the portfolio, date range, benchmark, and risk-free rate.

Close with: “The design favors transparent financial conventions and deterministic tests over feature breadth or personalized recommendations.”

## Five-minute interview demo

1. **Product goal — 30 seconds.** PortfolioLens is a focused historical research workflow for portfolio analytics, risk, investment research, and systematic strategy analysis.
2. **Data boundary — 40 seconds.** Normalize tickers, validate long-only weights, download adjusted history separately for holdings and benchmark, reject missing assets, and inner-align without filling prices.
3. **Performance and risk — 60 seconds.** Explain daily simple returns, constant weights, CAGR, annualized volatility, downside metrics, beta, and Euler risk contribution.
4. **Benchmark and decisions — 50 seconds.** Explain active return/tracking error/information ratio, frontier/target construction, explicit constraint validation, and holdings-level rebalancing policies.
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

**What would you improve next?** The approved Portfolio Management roadmap is complete. Further work would be engineering hardening or separately approved strategy robustness, not additional feature breadth.

## Limitations to acknowledge

- yfinance data can be delayed, revised, incomplete, or temporarily unavailable.
- Complete-case alignment can shorten the sample.
- The main analytics assume constant weights; the separate holdings-level simulator explicitly models buy-and-hold drift and scheduled or threshold rebalancing.
- Historical optimizers are estimation-sensitive and do not imply forecast certainty.
- Strategy results exclude taxes, liquidity, market impact, and slippage beyond the configured proportional cost.
- The application is educational research, not personalized financial advice.
# Integrated workflow checkpoint

For the standard SPY/QQQ/TLT/GLD demonstration, visit **Asset Allocation** after **Portfolio Optimization** to compare current/model weights, contribution profiles and implementation trades. Then open **Research Report** and confirm the HTML/CSV package includes performance evaluation, security analysis, CAPM and ETF research in addition to construction, rebalancing, strategies and stress testing.
