# Project decisions

Significant product, financial-methodology, architecture, and scope decisions are recorded here. Add new entries rather than rewriting prior decisions; mark superseded entries explicitly.

## D001 — Keep the product focused and educational

- **Date:** 2026-07-31
- **Decision:** Build a focused portfolio-research dashboard without authentication, a database, paid APIs, live execution, or generative-AI dependencies.
- **Context:** The project is intended to be internship-ready, explainable, testable, and deployable on Streamlit Community Cloud.
- **Rationale:** A narrow product provides a clearer demonstration of financial analysis and Python engineering than an institutional-platform simulation.
- **Alternatives considered:** Authentication, persistence, paid market data, live brokerage integration, and AI-generated research.
- **Consequences:** Results are session-based, historical, educational, and not suitable for trade execution or personalized advice.
- **Status:** Accepted.

## D002 — Separate financial logic from Streamlit

- **Date:** 2026-07-31
- **Decision:** Keep financial calculations in small modules and pure functions where practical; use `app.py` for orchestration and presentation.
- **Context:** Financial methods require deterministic offline testing and reuse outside Streamlit.
- **Rationale:** Separation reduces hidden state and makes formulas easier to test and explain.
- **Alternatives considered:** A single Streamlit script or a class-heavy service architecture.
- **Consequences:** The package has clear calculation boundaries, while `app.py` remains comparatively large and may later need a behavior-preserving view split.
- **Status:** Accepted.

## D003 — Use strict adjusted-price market-data handling

- **Date:** 2026-07-31
- **Decision:** Use yfinance adjusted history where available, reject unavailable requested holdings, align holdings on complete common dates, never invent prices, and download the benchmark separately.
- **Context:** Silent ticker removal or price filling would change the portfolio being analyzed.
- **Rationale:** Explicit failure is more defensible than presenting incomplete results as the requested portfolio.
- **Alternatives considered:** Outer joins, forward filling, silently dropping assets, and mixing the benchmark with holdings.
- **Consequences:** Common-date alignment can shorten history, and a single unavailable holding stops the analysis.
- **Status:** Accepted.

## D004 — Use daily simple returns and a constant-weight analytical portfolio

- **Date:** 2026-07-31
- **Decision:** Calculate simple daily returns and portfolio returns as the daily weighted sum using constant target weights.
- **Context:** The dashboard needs one consistent model across performance, attribution, risk, and historical stress.
- **Rationale:** The model is transparent and supports exact return-contribution reconciliation.
- **Alternatives considered:** Buy-and-hold drift, periodic rebalancing, log returns, and transaction-level accounting.
- **Consequences:** The result represents a daily rebalanced analytical portfolio, not an unmanaged brokerage account. Periodic rebalancing remains a planned candidate.
- **Status:** Accepted.

## D005 — Report historical tail risk as nonnegative loss magnitudes

- **Date:** 2026-07-31
- **Decision:** Define historical 95% VaR and CVaR as nonnegative magnitudes from the empirical lower tail.
- **Context:** Risk displays should not show a negative “loss” when the observed lower tail contains gains.
- **Rationale:** Positive loss magnitudes are intuitive and consistent with the dashboard’s labels.
- **Alternatives considered:** Signed return quantiles and parametric normal VaR.
- **Consequences:** The measures remain backward-looking and may be zero in an all-positive sample.
- **Status:** Accepted.

## D006 — Use Euler volatility contribution

- **Date:** 2026-07-31
- **Decision:** Calculate component volatility contribution as `w_i(Σw)_i / sqrt(w′Σw)` using the annualized sample covariance matrix.
- **Context:** Asset-level risk contribution must reconcile to total portfolio volatility.
- **Rationale:** Euler decomposition is mathematically additive for a homogeneous volatility measure.
- **Alternatives considered:** Weight-times-standalone-volatility and non-additive percentage heuristics.
- **Consequences:** Contributions can be negative when an asset acts as a covariance hedge.
- **Status:** Accepted.

## D007 — Keep allocation methods explainable and long-only

- **Date:** 2026-07-31
- **Decision:** Support current, equal, inverse-volatility, minimum-variance, and maximum-Sharpe weights; constrain optimization to `[0, 1]` weights summing to one and reject failed solver results.
- **Context:** The application needs practical allocation comparisons without implying forecast certainty.
- **Rationale:** These methods are recognizable, testable, and explainable in interviews.
- **Alternatives considered:** Shorting, leverage, Monte Carlo optimization, efficient-frontier display, and opaque allocation models.
- **Consequences:** Historical sample estimates can be unstable; optimized methods are comparisons, not recommendations.
- **Status:** Accepted.

## D008 — Use one explicit, lagged momentum strategy

- **Date:** 2026-07-31
- **Decision:** Run a dual-moving-average long/cash strategy on the first requested holding, lag signals by one full trading period, enforce warm-up, and charge proportional costs on position changes.
- **Context:** The strategy must be simple enough to audit and demonstrate without look-ahead bias.
- **Rationale:** An explicit instrument is clearer than constructing a synthetic tradable portfolio series, and one strategy keeps the product focused.
- **Alternatives considered:** Multiple indicator strategies, automatic parameter search, machine learning, and portfolio-level synthetic execution.
- **Consequences:** Results depend on ticker order and chosen windows; statistics are historical and not evidence of future profitability.
- **Status:** Accepted.

## D009 — Require explicit stress assumptions

- **Date:** 2026-07-31
- **Decision:** Require one custom shock per holding and show historical scenarios only when the selected history fully covers configured dates.
- **Context:** Ticker-to-asset-class inference can be unreliable, and incomplete windows should not be labeled complete.
- **Rationale:** User-provided assumptions and fixed configuration are auditable.
- **Alternatives considered:** Automatic asset classification, silent zero shocks, and partial-period scenario labels.
- **Consequences:** Custom shocks require more user input, and some selected date ranges show no historical scenarios.
- **Status:** Accepted.

## D010 — Use deterministic HTML reporting

- **Date:** 2026-07-31
- **Decision:** Generate a rules-based, self-contained HTML report and CSV exports without an LLM or PDF dependency.
- **Context:** Reporting must work reliably on Streamlit Community Cloud.
- **Rationale:** HTML is lightweight, inspectable, and deployment-safe.
- **Alternatives considered:** Generative-AI summaries and PDF libraries with native or rendering dependencies.
- **Consequences:** Narrative variety is limited by design; PDF is not supplied.
- **Status:** Accepted.

## D011 — Treat course-derived ideas as evidence, not code sources

- **Date:** 2026-07-31
- **Decision:** Course materials may motivate features or formulas, but implementations must be independently designed, documented, and tested.
- **Context:** Local notebooks, workbooks, assignments, and formulas were treated as unverified during the current development session.
- **Rationale:** Blind copying would import unknown assumptions and weaken provenance and maintainability.
- **Alternatives considered:** Reusing course code directly or adding machine learning because a course covered it.
- **Consequences:** Course-derived additions must name the relevant course source and pass the same engineering and financial review as other changes.
- **Status:** Accepted. **Context from current development session — verify before treating as canonical.**

## D012 — Maintain history, decisions, roadmap, and changelog together

- **Date:** 2026-07-31
- **Decision:** Material features and methodology changes must update the relevant permanent project records.
- **Context:** Git history records code changes but not always rationale, alternatives, or consequences.
- **Rationale:** Lightweight documentation preserves institutional memory without introducing a separate project-management system.
- **Alternatives considered:** Git messages alone, external issue trackers, and full formal ADR directories.
- **Consequences:** Documentation review is part of the definition of done for material changes.
- **Status:** Accepted.
