# PortfolioLens

**Multi-asset portfolio analytics and investment research**

[![CI](https://github.com/Jams411/portfoliolens/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Jams411/portfoliolens/actions/workflows/ci.yml)

PortfolioLens is a focused, internship-ready Streamlit application for historical portfolio research. It turns a ticker-and-weight input into a reproducible investment-research workflow spanning performance, market risk, benchmark-relative results, attribution, allocation alternatives, a transparent Portfolio Health Score, interactive what-if analysis, deterministic insights, rebalancing trades, a lagged momentum backtest, stress tests, and a professional downloadable HTML report.

[Launch PortfolioLens](https://portfolio-lens.streamlit.app/) · [View the GitHub repository](https://github.com/Jams411/portfoliolens)

The project is intentionally small enough to explain in an interview: market data enter through one validated boundary, financial calculations are pure functions, the UI only orchestrates those functions, and core formulas and reconciliation rules are covered by deterministic local tests.

## Product navigation

PortfolioLens uses six primary workspaces that fit on a common laptop without a horizontally scrolling tab rail: **Dashboard**, **Analytics**, **Research**, **Portfolio Construction**, **Strategies**, and **Reports**. Each workspace has one compact secondary view selector. The sidebar keeps portfolio, period, and benchmark assumptions visible; implementation and strategy settings are collapsed until needed.

The Dashboard is the executive starting point. It combines portfolio value, return, CAGR, arithmetic return, volatility, Sharpe ratio, drawdown, beta, tracking error, information ratio, allocation, risk contribution, benchmark-relative performance, an efficient-frontier preview, and deterministic insights. Detailed methodology and exports remain available in their authoritative workspaces rather than being repeated across the app.

> **Deployment status:** PortfolioLens retains the current Streamlit URL above. The scheduled [deployment-health workflow](https://github.com/Jams411/portfoliolens/actions/workflows/deployment-health.yml) records whether the endpoint returns successfully, redirects to Streamlit authentication, or fails at DNS, timeout, or server level. A redirect alone does not prove that the signed-out application UI rendered.

## Why this project matters

This application demonstrates:

- portfolio analytics
- market-risk measurement
- benchmark-relative evaluation
- portfolio construction
- rebalancing decisions
- systematic strategy research
- financial-data engineering
- investment-research communication

## Features

- Comma-separated ticker validation, equal/custom weights, presets, date range, benchmark, capital, risk-free rate and transaction-cost controls
- Adjusted yfinance history with caching, safe single/MultiIndex handling, strict failed-ticker reporting and complete-common-date alignment
- Transparent benchmark aliases for common index names such as SPX, DJIA, NASDAQ, VIX and RUT, with provider-symbol disclosure and friendly report labels
- Explicit holding-period-return logic; asset-level periodic arithmetic/geometric returns, annualized arithmetic return/CAGR, sample variance/volatility, coefficient of variation, and downloadable foundation tables
- Total return, consistently defined Sharpe, Sortino, drawdown, Calmar, tail risk, monthly returns and wealth charts
- A dedicated **Performance Evaluation** workspace consolidating return/risk, Sharpe, Sortino, Treynor, Jensen alpha, active risk, Information Ratio, Fama selectivity, rolling stability diagnostics, and CSV exports
- Portfolio- and security-level excess-return single-index analysis with alpha/beta/R², coefficient inference, characteristic lines, residual plots, systematic/idiosyncratic risk, CAPM required return, Jensen’s alpha, Treynor and downloadable comparison diagnostics
- A dedicated Asset Pricing workspace with a Security Market Line, realized-versus-required return comparison, Jensen’s alpha, and a clearly bounded assumption-based factor-pricing framework
- A dedicated **Security Analysis** view with a holding selector, benchmark context, comparison table, fitted characteristic line, residual diagnostics, methodology warnings, and CSV exports
- Benchmark excess return, tracking error, information ratio, relative drawdown and relative wealth
- Current, equal-weight, inverse-volatility, minimum-variance and maximum-Sharpe long-only allocations
- Audited long-only efficient upper frontier, GMV, constrained tangency, target-return portfolios, a reconciled non-leveraged Capital Allocation Line, and direct or quadratic-utility complete portfolios
- A dedicated **Portfolio Optimization** view with current/optimized statistics, direct or utility-based allocation, numerical diagnostics, consolidated optimized weights, and CSV exports
- Explicit asset bands, exclusions, user-defined groups/caps, feasibility checks, and compliance summaries
- Buy-and-hold, monthly, quarterly, annual, and threshold rebalancing simulations with drift, turnover, costs, dates, and trade-history exports
- A dedicated **Portfolio Strategies** workspace comparing rebalancing policies with SPX using active return, tracking error, information ratio, drawdown, turnover, costs, and downloadable histories
- Like-for-like portfolio comparison, a fully disclosed historical Health Score, validated hypothetical weights/shocks, and metric-traceable deterministic insights
- Dollar rebalancing plan with intuitive buy/sell signs and CSV export
- Dual-moving-average long/cash strategy on the first requested holding, with one-day signal lag and transaction costs
- Editable per-asset custom shocks and complete historical stress windows
- Rules-based summary, six CSV exports and a self-contained HTML research report

## Architecture

```text
app.py                              Streamlit controls, navigation and charts
portfolio_dashboard/
  config.py                         conventions, presets, historical windows
  data.py                           inputs, yfinance parsing, missing-data policy
  performance.py                    returns and performance metrics
  evaluation.py                     manager evaluation, attribution and cash-flow return primitives
  risk.py                           benchmark metrics and attribution
  research.py                       research comparison, score, scenarios and deterministic insights
  construction.py                   allocation methods and SLSQP optimizers
  rebalancing.py                    target trade plan
  strategy.py                       lagged momentum backtest
  stress.py                         custom and historical stress tests
  reporting.py                      deterministic narrative and HTML export
  pipeline.py                       reusable end-to-end analytics pipeline
  formatting.py                     shared UI and report number formats
tests/test_analytics.py             synthetic financial unit and integration tests
tests/test_app.py                   offline Streamlit entrypoint smoke tests
docs/METHODOLOGY.md                 formulas, assumptions and limitations
docs/ARCHITECTURE.md                living system and module reference
docs/PROJECT_HISTORY.md             evidence-backed project milestones
docs/PROJECT_JOURNAL.md             chronological engineering narrative
docs/DECISIONS.md                   product and methodology decisions
docs/ROADMAP.md                     completed, planned, deferred and avoided work
docs/DEPLOYMENT.md                  Community Cloud setup and verification checklist
docs/DEMO_GUIDE.md                  two- and five-minute interview demonstrations
docs/SHOWCASE_REVIEW.md             final visual and functional review record
docs/images/                        reproducible application screenshot gallery
CHANGELOG.md                        user-facing milestone changes
```

For module ownership, dependencies, state, and end-to-end diagrams, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). Foundational derivations and advanced-model boundaries are in the [Portfolio Management companion](docs/education/PORTFOLIO_MANAGEMENT_COMPANION.md).

## Screenshot gallery

All captures use the documented four-ETF sample portfolio. Displayed market results are historical examples, not expected returns.

| Landing and workflow | Performance |
|---|---|
| ![Application landing page](docs/images/01-application-overview.jpg) | ![Performance dashboard](docs/images/02-performance-dashboard.jpg) |
| Risk and correlation | Benchmark and attribution |
| ![Risk and correlation analysis](docs/images/03-risk-correlation.jpg) | ![Benchmark and attribution analysis](docs/images/04-benchmark-attribution.jpg) |
| Construction and rebalancing | Momentum strategy |
| ![Portfolio construction and rebalancing](docs/images/05-construction-rebalancing.jpg) | ![Momentum strategy](docs/images/06-momentum-strategy.jpg) |
| Stress testing | Research report |
| ![Stress testing](docs/images/07-stress-testing.jpg) | ![Research report and downloads](docs/images/08-research-report.jpg) |

## Installation and local execution

Python 3.11 or 3.12 is recommended.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

Open the local URL Streamlit prints. Select a preset, adjust inputs if desired, and click **Run analysis**. Internet access is needed only when the app downloads market history; tests are offline.

## Testing

```bash
.venv/bin/pytest -q
.venv/bin/python -m compileall app.py portfolio_dashboard tests
.venv/bin/python scripts/validate_markdown_links.py
```

Tests cover validation, data layout/missingness, arithmetic return, CAGR, annualized variance/volatility, portfolio `w′μ` and `w′Σw`, displayed/optimizer Sharpe reconciliation, Sortino, portfolio aggregation, drawdown, VaR/CVaR, excess-return regression and CAPM reconciliation, tracking error, information ratio, risk-contribution reconciliation, allocation comparison, Health Score arithmetic and coverage, what-if validation and reconciliation, deterministic insight traceability, allocation failure handling, rebalancing, signal lag, costs, stress tests, professional report units/sections, the integrated analytics pipeline, and the offline Streamlit research workspace.

GitHub Actions runs the complete offline suite on every push to `main`, every pull request targeting `main`, and manual dispatch. CI also compiles and imports the application, validates Streamlit configuration, runs the non-socket AppTest smoke suite, checks repository-local Markdown links, checks dependency integrity, and rejects whitespace errors. It requires no secrets and does not contact Yahoo Finance.

The Codex/Herdr sandbox can prohibit local TCP socket binding even when the application imports and executes correctly. That operating-system restriction cannot be repaired in PortfolioLens code. Non-socket AppTest covers application startup in CI, while the separate deployment-health workflow checks the hosted URL from an independent GitHub runner.

## Streamlit Community Cloud deployment

1. Push this repository to GitHub.
2. In Streamlit Community Cloud, create an app from the repository.
3. Set the entrypoint to `app.py` and choose Python 3.11 if the runtime selector is available.
4. Deploy. No secrets, database, paid API, system packages, or local paths are required.

The app downloads data only after the user clicks **Run analysis**. `requirements.txt` uses bounded versions compatible with Community Cloud; Streamlit 1.55 or newer is required for the native navigation and state behavior used by the app.

Follow the complete [deployment and post-deployment checklist](docs/DEPLOYMENT.md). Do not describe the app as deployed until its public URL passes that signed-out verification.

## Methodology and assumptions

Daily simple returns and 252 trading days are used consistently. Arithmetic annualized return is the historical expected-return estimate used by Sharpe, Sortino, CAPM evaluation, and optimization; CAGR remains realized compound growth. The main analytical portfolio uses constant weights, while the separate holdings-level simulator models natural drift and explicit rebalancing trades. The benchmark is separately downloaded and aligned. The single-index model uses excess returns. Historical VaR/CVaR use the empirical lower tail. Optimization is long-only, sample-based, feasibility-checked, and never presented as a forecast. The momentum signal is lagged one period and pays configured proportional costs on position changes. See [docs/METHODOLOGY.md](docs/METHODOLOGY.md).

## Limitations and disclaimer

yfinance data can be delayed, revised, incomplete, or temporarily unavailable. Common-date alignment can shorten history. Historical estimates and optimized weights are not forecasts. Results exclude taxes, liquidity constraints, market impact, and slippage beyond the configured cost, and do not model live execution. Historical stress windows are shown only when fully covered.

For research and educational use only. This application does not provide personalized financial advice.

## Project Story

PortfolioLens was created to demonstrate an end-to-end portfolio-research workflow that is easy to use, test, deploy, and explain in an internship interview. It connects portfolio analytics, market-risk measurement, benchmark-relative investment research, allocation and rebalancing decisions, and one transparent systematic strategy without becoming a collection of unrelated institutional features.

Clarity and financial correctness were prioritized over breadth. That choice led to explicit missing-data handling, reconciled contribution formulas, long-only optimization checks, one-period strategy lag, deterministic reporting, and synthetic offline tests. Advanced machine learning, automatic strategy tuning, live execution, personalized advice, and fragile report tooling were deferred or avoided because their data and model risks would weaken this project’s central story.

External methodology sources informed the roadmap around performance measurement, single-index benchmark research, rebalancing, transaction costs, warm-up periods, and overfitting controls. Source formulas were independently implemented and validated rather than copied or treated as verified production evidence.

The project is separate from the frozen Portfolio Intelligence Platform. That platform was not inspected or modified during this showcase phase, and no claim is made here about its internal architecture. This repository intentionally remains the smaller, focused, interview-ready application.

### Benchmark symbols

The benchmark defaults to the professional display label `SPX`, which resolves internally to Yahoo Finance symbol `^GSPC` for retrieval only. The default mapping does not produce a redundant notice; charts, tables, reports and exports continue to display `SPX`. Other explicit aliases remain disclosed: `S&P500` and `SP500` resolve to `^GSPC`; `DJIA` and `DOW` to `^DJI`; `NASDAQ` to `^IXIC`; `VIX` to `^VIX`; and `RUT` to `^RUT`. Aliases apply only to the benchmark field so ordinary portfolio equity tickers are never silently rewritten.

## Interview-ready explanation

“I built a modular Streamlit research dashboard that validates and aligns adjusted market data, computes portfolio and benchmark-relative analytics, decomposes risk using Euler contributions, compares explainable long-only allocations, produces a self-financing rebalance plan, and backtests a one-day-lagged momentum rule with costs. I separated calculations from presentation and tested the main pipeline entirely with synthetic data, so the financial logic is reproducible without network access.”

Use [docs/DEMO_GUIDE.md](docs/DEMO_GUIDE.md) for a timed walkthrough and interview questions.

## Suggested next improvement

Add an optional user-uploaded local price CSV path using the same validation boundary. That would improve reproducibility and demos during yfinance outages without adding a database or changing the analytical model.

## Development and documentation rules

- Every material feature or methodology change must update the relevant [project history](docs/PROJECT_HISTORY.md), [decision log](docs/DECISIONS.md), [roadmap](docs/ROADMAP.md), [changelog](CHANGELOG.md), or [methodology guide](docs/METHODOLOGY.md).
- Material feature changes must update the [project journal](docs/PROJECT_JOURNAL.md) when they affect product direction, important tradeoffs, or engineering lessons.
- Architectural changes must update the living [architecture reference](docs/ARCHITECTURE.md).
- Commit messages should explain the intent of a change, not merely list changed files.
- Every financial-formula change must include deterministic tests and a methodology update.
- Externally sourced financial methods must identify their provenance and be independently implemented and verified; source formulas are not assumed correct.
- Decisions must not be reconstructed from memory when repository evidence is unavailable. Label development-session context explicitly until it is independently confirmed.
- Codex or any coding agent must inspect the documentation system and current code before making a major change.

### ETF research workflow

The top-level **ETF Research** workspace adds transparent historical universe filters, security-level alpha screening, optional user-supplied holdings look-through, consolidated underlying exposure, pairwise ETF overlap, and downloadable research tables. PortfolioLens does not scrape holdings or infer missing classifications; disclosures and weights remain explicit user inputs.

### Integrated research coverage

PortfolioLens connects return/risk analytics, benchmark and security diagnostics, CAPM, long-only construction, asset-allocation comparison, rebalancing, strategies, evaluation, ETF research and deterministic reporting through one aligned-return pipeline. The **Asset Allocation** workspace makes model weights, contribution profiles and implementation trades discoverable. The HTML report and CSV package include the major public analytics while preserving explicit limitations.
