# Changelog

User-facing and methodology changes are grouped by repository milestone. This project has no Git version tags yet, so commit-backed milestone names are used instead of invented version numbers.

## Unreleased

- Re-audited the efficient frontier independently against two-asset closed forms and a dense three-asset simplex search. The curve now guarantees the feasible upper branch from GMV, includes the tangency target, removes duplicate/dominated points, and skips failed solves instead of connecting them.
- Reconciled the Capital Allocation Line directly from the tangency return, volatility, and shared risk-free rate; added explicit endpoint, slope, complete-portfolio, condition-number, constraint-residual, and chart-data tests.
- Professionalized all public application and HTML-report terminology and added an automated public-string guard while retaining course provenance in internal evidence records.
- Added Workbook 3 quadratic-utility complete-portfolio selection with an explicit risk-aversion coefficient, the unconstrained classroom allocation, a visible lending-only product boundary, and deterministic reconciliation tests.
- Completed a six-worksheet Workbook 3 trace. The third-party risk questionnaire, generic policy-allocation features absent from the source, and an erroneous double-weighted complete-return cell are documented rather than reproduced.
- Added a deployment-facing package import contract covering every tracked `portfolio_dashboard` module, normalized internal report formatting to a relative import, and documented recovery when Streamlit Cloud is connected to an obsolete repository.
- Updated the canonical deployment URL and automated health check to `https://portfolio-lens.streamlit.app` after verifying the product-aligned Streamlit deployment.
- Rendered the complete top-level tab bar before analysis so **Portfolio Optimization** is discoverable on initial load, and added a runtime commit identifier for verifying the revision served by Streamlit Cloud.
- Promoted Workbook 2 analytics to a dedicated **Portfolio Optimization** application section, with explicit GMV/tangency labels, a consolidated optimized-weights table and export, and an honest risk-preference control that does not imply the workbook supplied a numerical utility model.

### Added

- Added Workbook 2 complete-portfolio analysis: a user-selected 0–100% allocation between the long-only tangency portfolio and risk-free asset, plotted on the CAL with reconciled expected return, volatility, weights, and direct CSV exports.
- Added deterministic Workbook 2 tests for CAL/complete-portfolio reconciliation, zero risky allocation, negative excess return, leverage rejection, singular covariance, and optimizer non-convergence.
- Added Workbook 1 foundations: explicit price-plus-income holding-period return, periodic arithmetic and geometric mean helpers, asset-level return/risk tables, coefficient of variation, and a covariance-based diversification-reduction summary with CSV export.
- Added deterministic Workbook 1 reconciliation tests for compounding, sample risk, correlation/covariance, two-asset and matrix portfolio variance, unit consistency, and invalid inputs.
- Added GitHub Actions CI for full pytest, compilation/import, Streamlit configuration, non-socket AppTest, dependency, Markdown-link, and repository-diff verification.
- Added a daily and manually dispatchable public-deployment health workflow with readable success, authentication-redirect, DNS, timeout, and server-error diagnostics.
- Expanded the offline initial-page smoke test to verify PortfolioLens branding, sidebar inputs, the no-download empty state, and absence of uncaught exceptions.
- Added a reproducible long-only efficient frontier, global minimum-variance portfolio, constrained tangency portfolio, feasible target-return construction, and non-leveraged Capital Allocation Line.
- Added holdings-level buy-and-hold, monthly, quarterly, annual, and threshold rebalancing simulations with drift, trade dates, one-way turnover, proportional costs, and exportable histories.
- Added explicit asset bands, exclusions, user-defined groups/caps, linear feasibility checks, and constraint-validation summaries.
- Added the self-contained Portfolio Management educational companion and expanded permanent course traceability.
- Added a professional investment research workspace and print-safe deterministic HTML report.
- Added like-for-like allocation comparison using the existing constant-weight return and performance methodology.
- Added a transparent Portfolio Health Score with disclosed component weights, thresholds, points, and missing-metric coverage.
- Added interactive long-only what-if weights and explicit asset shocks without mutating the analyzed portfolio.
- Added deterministic insights that display their computed metric, value, and trigger rule and contain no LLM-generated advice.
- Added excess-return single-index regression with alpha, beta, R², residual volatility, systematic/idiosyncratic variance and risk shares, and observation count.
- Added CAPM required return, Jensen’s alpha, and Treynor ratio to benchmark analysis and the deterministic research report.
- Added a Community Cloud deployment checklist, timed interview demo guide, final showcase review, and eight live-application screenshots.
- Added historical arithmetic annualized return and annualized sample variance to the performance scorecard and exports.
- Added reusable portfolio expected-return `w′μ` and variance `w′Σw` calculations with formula and reconciliation tests.

### Changed

- Distinguished cumulative excess return from annualized active return and reconciled the Information Ratio numerator.
- Expanded the professional research report with full inputs, frontier/optimized allocations, constraints, and rebalancing-policy analysis.
- Split benchmark output into cumulative relative performance, regression diagnostics, and CAPM performance evaluation with explicit historical-estimate limitations.
- Standardized displayed performance Sharpe, strategy Sharpe, Sortino, and maximum-Sharpe optimization on arithmetic annualized excess return; CAGR remains the separate realized compound-growth metric.
- Clarified arithmetic return, CAGR, performance Sharpe, and optimizer Sharpe in the dashboard and deterministic report.
- Renamed the product from Portfolio Research Dashboard to PortfolioLens, with the subtitle “Multi-Asset Portfolio Analytics & Investment Research”; product scope and financial methodology are unchanged.
- Renamed the GitHub repository in place to `Jams411/portfoliolens`; the deployment initially retained its legacy address until a product-aligned URL was verified.
- Collapsed secondary momentum controls, added a persistent research-only scope reminder, and established a native Streamlit showcase theme without changing analytics.
- Replaced the light showcase theme with a high-contrast native dark financial theme and made Streamlit theme inheritance explicit for Plotly charts.
- Expanded the README with a screenshot gallery, deployment status, architecture links, demonstration guidance, and the evidence-labeled project story.

### Fixed

- Equal-weight mode now ignores disabled manual weights and constructs `1/N` directly.
- Manual values such as `50,35,15` are converted once to decimal weights with accurate sum validation.
- Input changes and failed runs now remove prior metrics, charts, reports, and exports instead of displaying stale analysis.

### Documentation

- Added permanent project history, decision, roadmap, changelog, and documentation-governance records.
- Added a chronological engineering journal and living architecture reference with verified module contracts and system diagrams.
- Reinforced documentation rules for product-direction, architecture, methodology, course-derived work, and coding-agent changes.

## Dashboard hardening — 2026-07-31

Commits: `a080c52`, `33ed9f0`, `f74a683`

### Added

- Offline Streamlit entrypoint smoke tests.
- Strategy warm-up and common strategy/buy-and-hold evaluation period.
- Actual trading dates for historical stress windows.
- Semantic percentage, ratio, count, and currency formatting for reports.

### Changed

- Reports now use the active custom shocks, selected rebalancing method, and actual aligned analysis dates.
- Optional allocation failures now produce individual warnings instead of aborting all construction results.
- Historical stress uses the same constant-weight daily return model as the main analysis.
- Streamlit navigation uses state-aware lazy tab rendering and bounded market-data caching.

### Fixed

- Included initial wealth when calculating portfolio and relative drawdowns.
- Reported historical VaR and CVaR as nonnegative loss magnitudes.
- Corrected target downside-deviation handling in Sortino.
- Rejected insufficient momentum history instead of returning a silent all-cash result.
- Required one explicit finite shock for every holding.
- Prevented invalid or nonconverged optimizer output from being shown as valid.
- Corrected report and UI units for percentages and unitless ratios.

### Documentation

- Updated methodology for drawdown, tail risk, Sortino, optimization failure, strategy warm-up, stress assumptions, and report state.

## Initial application — 2026-07-31

Commit: `c3cd9c6`

### Added

- Streamlit controls, tabbed analysis workflow, charts, tables, and downloads.
- README with purpose, architecture, installation, testing, deployment, limitations, and interview explanation.
- Methodology and limitations guide.
- Repository ignore rules.

## Core analytics engine — 2026-07-31

Commit: `3b7ed4d`

### Added

- Validated adjusted-price loading and common-date alignment.
- Portfolio performance, risk, benchmark, attribution, construction, optimization, rebalancing, strategy, stress, reporting, and formatting modules.
- Deterministic synthetic unit and integration tests.
- Bounded Python dependencies and pytest configuration.
