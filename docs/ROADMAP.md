# Project roadmap

This roadmap is intentionally conservative. Items move to **Completed** only when implementation, tests, documentation, and relevant verification are present in the repository.

## Completed

- Modular analytics package and reusable pipeline
- Strict ticker, date, weight, and market-data validation
- Daily simple-return and constant-weight portfolio analytics
- Performance, drawdown, historical VaR/CVaR, beta, tracking error, and information ratio
- Correlation, covariance, concentration, return contribution, and Euler volatility contribution
- Current, equal, inverse-volatility, minimum-variance, and maximum-Sharpe allocation comparisons
- Practical target-weight rebalancing plan and CSV export
- Lagged dual-moving-average long/cash strategy with warm-up and transaction costs
- Explicit per-asset custom shocks and complete historical stress windows
- Deterministic research summary, CSV exports, and HTML report
- Streamlit application smoke tests and synthetic analytics integration tests
- README, methodology, deployment instructions, project history, project journal, architecture reference, decision log, roadmap, and changelog
- Live visual/functional review, Community Cloud checklist, demo guide, and eight-screen showcase gallery
- PortfolioLens product branding and repository identity, without scope or methodology changes

## In progress

- Public Streamlit Community Cloud deployment and signed-out URL verification. Repository preparation is complete; account authorization remains external to the codebase.

## Planned

**Context from current development session — verify before treating as canonical.**

These are prioritized candidates from the code audit and course-material review, not yet approved methodology changes.

### Milestone 1 — Financial convention consistency

- Standardize the Sharpe numerator and periodic risk-free-rate treatment across performance and optimization.
- Review Sortino’s numerator against the same convention while retaining target downside deviation.
- Centralize annual-to-periodic rate conversion.
- Add synthetic formula tests and update methodology before changing displayed results.

Why: the current scorecard uses CAGR in Sharpe and Sortino while maximum-Sharpe construction uses arithmetic expected return. The Portfolio Management materials reviewed in the current session use average excess return for Sharpe.

### Milestone 2 — Benchmark research

- Add a tested excess-return single-index regression.
- Report historical alpha, beta, R², residual volatility, and observations.
- Consider Treynor ratio and Jensen’s alpha with precise definitions.
- Integrate results into the report with non-predictive language.

Why: these extend existing benchmark analytics with high career and interview value while remaining explainable.

### Milestone 3 — Rebalancing realism

- Add buy-and-hold weight drift and monthly, quarterly, and annual rebalance simulations.
- Track turnover, costs, and portfolio value.
- Compare these models with the existing daily constant-weight analytical portfolio.

Why: rebalancing frequency materially affects realized weights, costs, and results, and makes the current daily-rebalancing assumption easier to explain.

### Milestone 4 — Strategy robustness

- Add calendar-year or fixed-subperiod strategy comparisons.
- Optionally allow a fixed validation split without parameter optimization.
- Preserve one-period lag, common evaluation periods, and transaction costs.

Why: subperiod evidence is more informative than a single full-period result and supports discussion of regime dependence and overfitting.

### Milestone 5 — Engineering hardening

- Add lightweight Ruff configuration and financial invariant tests.
- Split Streamlit views into modules without behavior changes if the entrypoint continues to grow.
- Refine domain-specific error types.
- Add an optional validated local CSV input for outage-resistant demonstrations.

## Deferred

- **Efficient frontier:** Relevant to mean–variance theory, but requires a stable target-return optimizer, feasibility tests, and careful uncertainty language. Current allocation comparisons deliver most of the interview value with less complexity.
- **Equal-risk-contribution optimization:** More complete than inverse volatility, but adds nonlinear optimization and edge cases. Defer until existing construction conventions are fully aligned.
- **Volatility targeting and regime rotation:** Course-relevant but would add another portfolio/strategy layer before the single momentum model has subperiod diagnostics.
- **Brinson allocation/selection attribution:** Requires trustworthy benchmark constituent weights and classifications; current holdings contribution should not be mislabeled as Brinson attribution.
- **Bond duration and convexity:** Requires explicit coupon, maturity, yield, frequency, and instrument assumptions that yfinance price history does not reliably provide.
- **Fundamental clustering:** A defensible machine-learning research idea only with reproducible, point-in-time fundamental data. It should begin outside the core dashboard if revisited.
- **Multifactor or Treynor–Black models:** Strong academic value but substantially expand data, estimation, and explanation requirements.

## Avoided

- **Generative-AI research dependency:** Reduces determinism and adds cost and deployment dependencies without improving core financial calculations.
- **Machine-learning price-direction prediction:** Adds leakage, label, tuning, and stability risks disproportionate to this focused project.
- **Automatic strategy parameter optimization:** Encourages overfitting and weakens the MVP’s explainability.
- **Monte Carlo optimization for visual effect:** Does not improve decision quality over the tested deterministic methods.
- **Silent asset-class inference:** Ticker classification is unreliable and can create hidden stress assumptions.
- **Personalized recommendations, risk scoring, or investment-policy generation:** Outside the educational research scope and risks implying individualized advice.
- **Live trading and brokerage integration:** Introduces execution, security, compliance, and operational responsibilities beyond the product goal.
- **Fragile PDF tooling:** HTML provides a more reliable deployment-safe report.
