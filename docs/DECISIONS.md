# Project decisions

Significant product, financial-methodology, architecture, and scope decisions are recorded here. Add new entries rather than rewriting prior decisions; mark superseded entries explicitly.

## D015 — Rename the product to PortfolioLens

- **Date:** 2026-08-01
- **Decision:** Rename the product from Portfolio Research Dashboard to PortfolioLens and use the subtitle “Multi-Asset Portfolio Analytics & Investment Research.”
- **Context:** The former name described the application accurately but was generic and did not provide a distinctive identity for demonstrations, deployment, or interview discussion.
- **Rationale:** PortfolioLens communicates a focused view into portfolio analysis, risk, benchmark comparison, allocation decisions, and investment research while remaining concise and memorable.
- **Alternatives considered:** Retain the descriptive former name or adopt a name implying institutional intelligence, forecasting, or advisory capabilities.
- **Consequences:** Application branding, report titles, documentation, repository identity, screenshots, and deployment presentation change. Product scope, architecture, financial calculations, methodology, and educational-use limitations do not change. The internal `portfolio_dashboard` Python package remains stable to avoid an unnecessary import migration.
- **Status:** Accepted.

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

## D013 — Maintain a living journal and architecture reference

- **Date:** 2026-07-31
- **Decision:** Record product-direction lessons in `PROJECT_JOURNAL.md`, keep current module and flow truth in `ARCHITECTURE.md`, and require coding agents to inspect the documentation system before major changes.
- **Context:** The initial governance files preserve milestones, decisions, planned scope, and user-facing changes but do not provide a complete maintenance reference or narrative engineering record.
- **Rationale:** Separating narrative evolution from current architecture reduces duplication and gives future maintainers both historical context and an accurate operating model.
- **Alternatives considered:** Expanding `PROJECT_HISTORY.md` into a long narrative, relying on source inspection alone, or keeping architecture knowledge in conversation history.
- **Consequences:** Product-direction changes may require a journal entry; module, dependency, startup, state, testing, or deployment changes require an architecture update.
- **Status:** Accepted.

## D014 — Invalidate results when analysis inputs change or a run fails

- **Date:** 2026-08-01
- **Decision:** Clear analysis outputs whenever an analysis-defining widget changes and before every submitted run; publish a new result only after the complete run succeeds.
- **Context:** A failed production run could leave metrics, charts, reports, and exports from a prior input set visible beneath the new error.
- **Rationale:** Displayed outputs must have one unambiguous relationship to the visible inputs. Hiding stale results is safer than presenting mismatched financial analysis.
- **Alternatives considered:** Preserve prior results with a stale-data banner or retain outputs only during execution failures.
- **Consequences:** Editing any analysis input hides the existing result until the user completes another successful run. Failed runs show an actionable error and empty-state guidance only.
- **Status:** Accepted.

## D015 — Separate arithmetic expected return from compound growth

- **Date:** 2026-08-01
- **Decision:** Use `252 × mean(daily return)` as the historical expected-return estimate for Sharpe, Sortino, and maximum-Sharpe optimization; retain CAGR exclusively as realized compound growth. Expose annualized sample variance and reusable `w′μ` and `w′Σw` calculations.
- **Context:** Performance Sharpe previously used CAGR while construction optimized arithmetic annualized excess return, so the same portfolio could be evaluated under two different Sharpe conventions.
- **Rationale:** The Portfolio Management course materials use average excess return for Sharpe and mean-variance construction. One shared formula makes the scorecard, strategy statistics, and optimizer auditable and internally consistent.
- **Alternatives considered:** Change optimization to use CAGR, display two different Sharpe ratios, or retain the mismatch with additional disclosure.
- **Consequences:** Historical Sharpe and Sortino values change. CAGR, total return, volatility, optimization constraints, and all non-return workflows remain intact. Arithmetic estimates remain historical and are not forecasts.
- **Status:** Accepted.

## D016 — Use one excess-return convention for single-index and CAPM metrics

- **Date:** 2026-08-01
- **Decision:** Regress daily portfolio excess returns on daily benchmark excess returns with an intercept, converting the annual risk-free input by simple division by 252. Annualize the fitted intercept arithmetically and derive CAPM required return, Jensen’s alpha, and Treynor from the same aligned sample.
- **Context:** PortfolioLens had covariance beta, tracking error, and information ratio but not the course-supported excess-return regression and CAPM performance-evaluation chain.
- **Rationale:** A shared sample and arithmetic convention makes fitted alpha reconcile exactly with Jensen’s alpha and makes every output traceable to the Phase 1 expected-return methodology.
- **Alternatives considered:** Regress raw returns, geometrically convert the risk-free rate, use an external regression package, or report CAPM metrics from an independently annualized sample.
- **Consequences:** Results are historical, benchmark-sensitive single-factor estimates. Residual standard error uses two fitted-parameter degrees of freedom; idiosyncratic variance uses sample variance so the displayed risk decomposition reconciles exactly.
- **Status:** Accepted.

## D017 — Keep the research layer deterministic and disclose the Health Score heuristic

- **Date:** 2026-08-01
- **Decision:** Build portfolio comparison, what-if analysis, research insights, and the Portfolio Health Score exclusively from tested PortfolioLens metrics. Publish every score component, weight, threshold, missing-metric treatment, insight value, and trigger rule.
- **Context:** Phase 3 changes PortfolioLens from a collection of analytical tabs into a research workflow, creating a risk that polished presentation could imply advice, prediction, or unsupported precision.
- **Rationale:** Traceability preserves interview and user explainability. A deterministic layer is reproducible, testable, deployment-safe, and consistent with the focused research product.
- **Alternatives considered:** LLM-written commentary, an opaque composite score, personalized recommendations, or a score presented without component coverage.
- **Consequences:** The score is explicitly an application-specific historical heuristic rather than a course formula or suitability measure. What-if scenarios remain long-only, explicit, and non-persistent; insights describe computed evidence and never prescribe trades.
- **Status:** Accepted.

## D018 — Limit frontier and CAL construction to long-only historical estimates

- **Date:** 2026-08-01
- **Decision:** Construct the efficient frontier with arithmetic sample means and annualized sample covariance, weights in `[0,1]`, weights summing to one, and exact feasible target-return constraints. Present the maximum-Sharpe solution as a constrained historical tangency estimate and stop the CAL at 100% risky allocation.
- **Context:** The course-supported Markowitz and capital-allocation workflow remained the principal approved construction gap.
- **Rationale:** This matches PortfolioLens’s established expected-return and Sharpe conventions while preserving the explicit no-shorting and no-leverage product boundary.
- **Alternatives considered:** Monte Carlo portfolio clouds, unconstrained analytical frontiers, borrowing beyond the tangency portfolio, and using CAGR as expected return.
- **Consequences:** Frontier positions can be unstable because historical means and covariances are estimates. Solver and feasibility failures are displayed, and no optimized allocation is described as a forecast or recommendation.
- **Status:** Accepted.

## D019 — Model rebalancing with holdings-level path accounting

- **Date:** 2026-08-01
- **Decision:** Simulate buy-and-hold, monthly, quarterly, annual, and threshold policies by drifting dollar holdings with observed asset returns and trading only at explicit triggers. Calculate one-way turnover as half gross traded notional and charge proportional costs on gross traded notional.
- **Context:** The main portfolio series assumes constant weights each day and cannot answer questions about natural weight drift, rebalancing frequency, or implementation cost.
- **Rationale:** Holdings-level accounting makes trade dates, before/after weights, turnover, costs, and value continuity auditable while preserving the existing analytical series for portfolio mathematics.
- **Alternatives considered:** Silently reinterpret the main series, rebalance daily, apply costs every period regardless of trades, or approximate drift from portfolio-level returns.
- **Consequences:** Simulation results differ from the main constant-weight scorecard by design. They assume fractional trading, close-of-period execution, and no taxes, cash flows, liquidity limits, or market impact.
- **Status:** Accepted.

## D020 — Require explicit classifications for constrained construction

- **Date:** 2026-08-01
- **Decision:** Support user-entered long-only asset bands, exclusions, target return, and group caps only when users explicitly supply group labels. Run a linear feasibility check before nonlinear optimization and publish a constraint-by-constraint validation table.
- **Context:** Course IPS materials support allocation limits, but market tickers do not provide a reliable universal sector or asset-class classification.
- **Rationale:** Explicit mappings prevent hidden assumptions and make every pass, failure, and breach auditable.
- **Alternatives considered:** Infer categories from tickers, silently relax infeasible limits, add unsupported maximum-volatility constraints, or allow shorting/leverage to restore feasibility.
- **Consequences:** Users do more setup for group caps, but results remain transparent. Infeasible combinations fail clearly and no constraint is relaxed automatically.
- **Status:** Accepted.

## D021 — Separate code verification from hosted deployment health

- **Date:** 2026-08-01
- **Decision:** Run deterministic application verification in GitHub Actions without sockets or live market data, and check the public Streamlit endpoint in a separate credential-free scheduled workflow that classifies redirects and network failures.
- **Context:** The managed Codex/Herdr environment can deny TCP socket binding or DNS access independently of application behavior. A local startup failure under that policy cannot establish that PortfolioLens is defective or that Streamlit Community Cloud is unhealthy.
- **Rationale:** GitHub-hosted runners provide an independent, reproducible environment. Separating CI from deployment health preserves clear attribution: formula and startup failures belong to code verification, while DNS, authentication, timeout, and server responses are operational evidence.
- **Alternatives considered:** Change Streamlit networking code to evade sandbox restrictions, require deployment credentials, treat every redirect as failure, or add a brittle Playwright dependency that cannot pass an authentication gate.
- **Consequences:** Pull requests and `main` pushes receive complete offline verification. The daily health workflow can prove direct HTTP success or Streamlit reachability, but an authentication redirect cannot prove signed-out UI rendering; that remains a documented manual check.
- **Status:** Accepted.

## D022 — Separate finite-scenario population risk from historical sample estimation

- **Date:** 2026-08-01
- **Decision:** Preserve Workbook 1's `VAR.P`, `STDEV.P`, and probability-weighted population formulas as the correct convention for its complete classroom scenario sets, while retaining sample variance/covariance (`ddof=1`) for PortfolioLens historical market estimates. Add explicit labels, HPR and geometric-mean helpers, coefficient of variation, and observed diversification reduction without duplicating population statistics in the live UI.
- **Context:** The workbook teaches both complete hypothetical outcome distributions and short historical exercises with population Excel functions. PortfolioLens observes a sample from an unknown market-return process.
- **Rationale:** Methodology should follow the statistical question, not copy an Excel function mechanically. Showing parallel population and sample market tables would add confusion without improving the research workflow.
- **Alternatives considered:** Replace PortfolioLens sample risk with population risk, display both conventions for all market series, or treat similarly named existing metrics as complete workbook coverage.
- **Consequences:** Exact workbook examples reconcile under their documented population convention; live historical estimates retain `n-1` denominators. Users receive explicit arithmetic/geometric and variance/covariance labels, while probability games and common-correlation limits remain educational-only.
- **Status:** Accepted.
