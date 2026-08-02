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
- Phase 1 Portfolio Management methodology alignment: arithmetic annualized return, annualized variance, `w′μ`, `w′Σw`, and one shared arithmetic Sharpe convention across performance and optimization
- Phase 2A benchmark research: excess-return single-index OLS, alpha, beta, R², residual volatility, systematic/idiosyncratic variance, CAPM required return, Jensen’s alpha, and Treynor ratio
- Phase 3 professional investment research: structured HTML report, like-for-like portfolio comparison, transparent Portfolio Health Score, interactive long-only what-if scenarios, and deterministic metric-traceable insights
- Phase 2B construction: long-only efficient frontier, global minimum variance, constrained historical tangency, feasible target-return portfolios, and a non-leveraged CAL
- Phase 2C rebalancing realism: buy-and-hold drift, monthly/quarterly/annual and threshold policies, one-way turnover, proportional transaction costs, rebalance dates, before/after weights, and exportable histories
- Phase 2D benchmark evaluation completion: standardized cumulative excess versus annualized active return labels; tracking error, information ratio, CAPM, Jensen, Treynor, regression, and risk decomposition verified without duplication
- Phase 2E constrained construction: explicit asset bands, exclusions, user-defined groups/caps, target-return integration, linear feasibility checks, and constraint validation summaries
- Phase 4 educational companion: two-asset variance derivation, frontier/CAL intuition, CAPM/single-index interpretation, and educational-only Treynor–Black/APT/multifactor boundaries
- Workbook 1 deep trace: HPR, periodic arithmetic/geometric means, asset sample variance/volatility, coefficient of variation, covariance/correlation matrices, portfolio moments, and observed diversification reduction

## Deferred — separately approved future work only

The approved Portfolio Management implementation roadmap is complete. These items are not current commitments and require separate approval.

### Strategy robustness

- Add calendar-year or fixed-subperiod strategy comparisons.
- Optionally allow a fixed validation split without parameter optimization.
- Preserve one-period lag, common evaluation periods, and transaction costs.

Why: subperiod evidence is more informative than a single full-period result and supports discussion of regime dependence and overfitting.

### Engineering hardening

- Add lightweight Ruff configuration and financial invariant tests.
- Split Streamlit views into modules without behavior changes if the entrypoint continues to grow.
- Refine domain-specific error types.
- Add an optional validated local CSV input for outage-resistant demonstrations.

## Deferred

- **Equal-risk-contribution optimization:** More complete than inverse volatility, but adds nonlinear optimization and edge cases. Defer until existing construction conventions are fully aligned.
- **Volatility targeting and regime rotation:** Course-relevant but would add another portfolio/strategy layer before the single momentum model has subperiod diagnostics.
- **Brinson allocation/selection attribution:** Requires trustworthy benchmark constituent weights and classifications; current holdings contribution should not be mislabeled as Brinson attribution.
- **Bond duration and convexity:** Requires explicit coupon, maturity, yield, frequency, and instrument assumptions that yfinance price history does not reliably provide.
- **Fundamental clustering:** A defensible machine-learning research idea only with reproducible, point-in-time fundamental data. It should begin outside the core dashboard if revisited.
- **Multifactor or Treynor–Black live models:** Educational companion only unless reliable factor data and a separately approved estimation design become available.
- **Preferred Streamlit subdomain:** The verified deployment remains `portfolio-research-dashboard.streamlit.app`; `portfoliolens.streamlit.app` belongs to another deployment and requires manual platform availability before reconsideration.

## Educational-only

- Two-asset return/variance derivation and diversification intuition
- Efficient-frontier, constrained tangency, and CAL intuition
- CAPM and single-index interpretation
- Treynor–Black, APT, and multifactor conceptual overview

## Intentionally excluded

- **Generative-AI research dependency:** Reduces determinism and adds cost and deployment dependencies without improving core financial calculations.
- **Machine-learning price-direction prediction:** Adds leakage, label, tuning, and stability risks disproportionate to this focused project.
- **Automatic strategy parameter optimization:** Encourages overfitting and weakens the MVP’s explainability.
- **Monte Carlo optimization for visual effect:** Does not improve decision quality over the tested deterministic methods.
- **Risk parity as a course-derived feature:** The completed Portfolio Management audit did not substantively support it; inverse volatility remains an application-specific heuristic, not course-derived risk parity.
- **Rolling alpha and beta:** Not required by approved course traceability.
- **Maximum-volatility construction constraint:** Not established as a required stable feature by approved traceability.
- **Short selling, leverage, and borrowing:** Conflict with the approved long-only, non-leveraged product boundary.
- **Silent asset-class inference:** Ticker classification is unreliable and can create hidden stress assumptions.
- **Personalized recommendations, risk scoring, or investment-policy generation:** Outside the educational research scope and risks implying individualized advice.
- **Live trading and brokerage integration:** Introduces execution, security, compliance, and operational responsibilities beyond the product goal.
- **Fragile PDF tooling:** HTML provides a more reliable deployment-safe report.
