# Project decisions

Significant product, financial-methodology, architecture, and scope decisions are recorded here. Add new entries rather than rewriting prior decisions; mark superseded entries explicitly.

## D032 — Replace the crowded tab rail with six professional workspaces

- **Date:** 2026-08-06
- **Status:** Accepted; supersedes the navigation portion of D031.
- **Decision:** Group all existing feature sections under Dashboard, Analytics, Research, Portfolio Construction, Strategies, and Reports. Use native Streamlit selection controls, preserve the legacy section state key for compatibility, keep global inputs in a grouped sidebar, and place build metadata in About and Methodology rather than the main header.
- **Context:** The 15 top-level tabs overflowed at 1366×768, required a hidden scroll action to discover later sections, and made related analysis feel like separate modules. The initial page also spent prime vertical space on metadata and explanatory copy.
- **Rationale:** Six stable workspaces match professional research tasks, fit a laptop canvas, and preserve feature reachability without duplicating calculations or introducing custom navigation code.
- **Consequences:** Dashboard becomes the executive entry point; secondary selectors expose every former section; global analysis state survives navigation; advanced sidebar inputs are collapsed; documentation and AppTest treat the mapping registry as authoritative. Rendering remains in the single entrypoint, which is a known maintainability limitation but avoids a risky financial-methodology refactor.

## D029 — Consolidate performance evaluation without changing established metric conventions

- **Date:** 2026-08-02
- **Status:** Accepted
- **Decision:** Add a top-level Performance Evaluation workspace and the source-supported Fama selectivity chain. Preserve the existing annual arithmetic Sharpe/Treynor/Jensen conventions and target-downside Sortino convention. Keep the source's category attribution, Modified Dietz and time-weighted formulas as tested primitives until explicit category or external-cash-flow inputs exist.
- **Context:** The direct seven-worksheet audit showed that the source supports Sharpe, Treynor, Jensen, Fama selectivity, a combined selection-plus-interaction convention, fee-horizon exercises, time/dollar-weighted returns and a mean-semideviation Sortino example. It does not contain tracking error, Information Ratio, M², Calmar, drawdown or rolling metrics, despite an older summary trace row attributing some of those features to it.
- **Rationale:** Consolidation improves professional usability, while precise provenance prevents similarly named measures from being treated as methodological equivalents. Price data cannot safely supply manager cash flows or benchmark category weights.
- **Consequences:** Fama metrics are visible and exportable. Rolling metrics are explicitly labeled professional enhancements. The source attribution term is named “Selection Effect Including Interaction.” Fund-fee and money-weighted workflows remain educational/deferred rather than being fabricated from adjusted prices.

## D024 — Adopt the verified product-aligned Streamlit URL

- **Date:** 2026-08-02
- **Status:** Accepted
- **Decision:** Use `https://portfolio-lens.streamlit.app` as the canonical PortfolioLens deployment URL in current documentation, demos, badges or links, and automated health checks.
- **Context:** The product-aligned address is now the verified Streamlit deployment. Earlier slug-availability concerns are historical and no longer govern current links.
- **Consequences:** Public references and operational checks resolve to one URL; future URL changes require the same repository-wide validation and governance update.

## D015 — Rename the product to PortfolioLens

- **Date:** 2026-08-01
- **Decision:** Rename the product from Portfolio Research Dashboard to PortfolioLens and use the subtitle “Multi-Asset Portfolio Analytics & Investment Research.”
- **Context:** The former name described the application accurately but was generic and did not provide a distinctive identity for demonstrations, deployment, or interview discussion.
- **Rationale:** PortfolioLens communicates a focused view into portfolio analysis, risk, benchmark comparison, allocation decisions, and investment research while remaining concise and memorable.
- **Alternatives considered:** Retain the descriptive former name or adopt a name implying institutional intelligence, forecasting, or advisory capabilities.
- **Consequences:** Application branding, report titles, documentation, repository identity, screenshots, and deployment presentation change. Product scope, architecture, financial calculations, methodology, and educational-use limitations do not change. The internal `portfolio_dashboard` Python package remains stable to avoid an unnecessary import migration.
- **Status:** Accepted.

## D030 — Refactor the research chain; do not reproduce its manual automation gaps

- **Decision:** Implement transparent historical screening, weighted holdings look-through and regression candidate ranking as pure PortfolioLens functions. Keep incomplete Treynor–Black active/passive mixing and ungoverned live fundamentals out of the public construction workflow.
- **Context:** The five-source package is connected by manual copy/paste and code edits; its notebook and final spreadsheet use different universes and benchmarks, and several formulas/labels are inconsistent.
- **Rationale:** The selected functions are testable, explainable and useful. Automatic recommendations, hard-coded analyst targets and undated holdings would create false precision and data-governance risk.
- **Consequences:** The ETF Research tab requires explicit holdings disclosures and states coverage limitations. Existing Security Analysis and Portfolio Optimization remain the authoritative regression and construction workspaces.
- **Status:** Accepted.

## D031 — Complete product stitching without expanding methodology

- **Decision:** Add a dedicated Asset Allocation workspace and include all major public analytics in the deterministic report/export package. Retain the existing pure-function formula owners and defer a full multipage navigation migration.
- **Context:** Allocation results were scattered, and reports omitted security, CAPM, evaluation and ETF tables. Fifteen tabs are crowded, but restructuring the entire stateful app during a methodology audit carries disproportionate regression risk.
- **Rationale:** Discoverability and report completeness are High-priority integration requirements; no new investment model is needed.
- **Consequences:** Public allocation and report coverage are complete. Navigation architecture remains a documented Medium UX debt.
- **Status:** Accepted.

## D028 — Separate CAPM/SML production analysis from assumption-based multifactor pricing

- **Date:** 2026-08-02
- **Decision:** Add a professional Asset Pricing workspace for CAPM required return, realized-minus-required Jensen's alpha and the Security Market Line. Keep APT and four-factor arithmetic as a reusable supplied-assumption framework, without live factor exposure estimation.
- **Context:** Workbook 5-1 contains directly recoverable CAPM/SML formulas, an APT two-factor example, and market/SMB/HML/momentum contribution tables. It does not contain a recoverable factor-data pipeline, factor regressions, standard errors, or production classifications.
- **Rationale:** CAPM uses existing governed benchmark data and tested regression beta. A live multifactor model would require trustworthy aligned factor returns and new estimation governance that the source does not establish.
- **Consequences:** Users receive a transparent historical CAPM comparison. Multifactor data and exposure estimation remain deferred; historical position above the SML is never labeled a buy signal or persistent mispricing.
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

## D023 — Implement lending-only complete portfolios while preserving long-only construction

- **Date:** 2026-08-01
- **Decision:** Add a user-selected complete portfolio with 0–100% in PortfolioLens's long-only tangency portfolio and the remainder in the risk-free asset. Keep short selling and borrowing/leverage educational-only even though Workbook 2's unconstrained tangency Solver and CML illustration support them.
- **Context:** Workbook 2 contains a recoverable long-only target-return Solver, a separate unconstrained maximum-Sharpe Solver with negative weights, and a CML diagram extending through lending and borrowing. It mentions utility but provides no coefficient or computational selection rule.
- **Rationale:** The lending segment is financially correct, testable, explainable, and consistent with the existing non-leveraged CAL. Enabling the workbook's unconstrained or borrowing cases would conflict with PortfolioLens's focused product boundary and materially increase user and model risk.
- **Alternatives considered:** Reproduce the unconstrained tangency weights, enable `y>1` behind a checkbox, or infer a quadratic utility function and risk-aversion coefficient.
- **Consequences:** Complete-portfolio points reconcile exactly with the displayed CAL. They are historical scenarios rather than recommendations. Workbook tangency outputs are documented as methodologically different, and no claim of exact reproduction is made.
- **Status:** Accepted.

## D024 — Use Workbook 3 quadratic utility without turning PortfolioLens into a suitability tool

- **Date:** 2026-08-02
- **Decision:** Let users enter a positive risk-aversion coefficient `A`, calculate the workbook's unconstrained `y*=(E[r_T]−r_f)/(Aσ_T²)`, and report the lending-only allocation after applying `0≤y≤1`. Retain direct allocation as an alternative. Do not reproduce the embedded third-party questionnaire or its score-to-`A` rule.
- **Context:** Workbook 3 provides a recoverable quadratic utility model and Solver-constrained complete-portfolio allocation. It also embeds an Advisor Group questionnaire, while another worksheet contains a double-weighted complete-return formula and conflicting short-sale labels/Solver bounds.
- **Rationale:** Direct `A` preserves the supported financial model while avoiding an unvalidated personal-risk assessment. Showing both unconstrained and applied allocations makes PortfolioLens's product constraint explicit. Correct CAL arithmetic is more defensible than copying a demonstrably inconsistent cell.
- **Alternatives considered:** Recreate the questionnaire, silently cap `y`, enable borrowing/leverage, reproduce the erroneous cell, or infer a full strategic asset-allocation workflow from the workbook title.
- **Consequences:** The output is a historical mean-variance sensitivity, not advice. Users see when the lending-only boundary binds. Asset classes are not inferred from tickers, and unsupported policy, tactical, liability, and lifecycle features are not attributed to Workbook 3.
- **Status:** Accepted.

## D025 — Treat the plotted frontier and CAL as reconciled numerical products

- **Date:** 2026-08-02
- **Decision:** Plot only the feasible long-only efficient upper branch from GMV to maximum return; explicitly include the tangency target; exclude duplicate, dominated and failed points; and construct the CAL directly from the shared tangency return, volatility and risk-free rate. Publish optional numerical diagnostics. Keep academic-development terminology out of public UI/report strings while retaining source provenance in internal records.
- **Context:** The prior core formulas were correct, but a fixed target grid did not guarantee an exact tangency point and the CAL function accepted a stored Sharpe field that could theoretically disagree with its other inputs.
- **Rationale:** A financial chart is part of the analytical output, not decoration. Curve membership, ordering, endpoints and line reconciliation require the same controls as optimizer tables. Public product language and internal evidence serve different audiences and should be governed separately.
- **Alternatives considered:** Smooth/interpolate the curve, plot the full minimum-variance boundary, regularize covariance silently, trust cached Sharpe, or remove course provenance from all documentation.
- **Consequences:** The curve may have fewer points when a solve fails, rather than drawing through invalid data. Singular matrices are not silently altered. Diagnostics disclose residuals, condition number and stabilization policy. Internal traceability remains intact.
- **Status:** Accepted.

## D026 — Resolve only explicit benchmark aliases

- **Date:** 2026-08-02
- **Decision:** Default the benchmark display label to `SPX`, resolve it to `^GSPC` only for Yahoo Finance retrieval, suppress the redundant default notice, disclose other alias mappings, and retain normalized user labels in presentation. Do not apply aliases to portfolio holdings.
- **Context:** Users commonly enter `SPX`, while Yahoo Finance requires `^GSPC`. Some requested aliases, particularly `DOW`, can also be valid equity symbols outside benchmark context.
- **Rationale:** Field-scoped resolution improves usability without silently changing an investment holding. A centralized allowlist is auditable and avoids fuzzy symbol guessing.
- **Consequences:** Unknown and provider-native symbols pass through unchanged. Portfolio holdings still require their exact Yahoo Finance symbols. Financial calculations are unaffected.
- **Status:** Accepted.

## D027 — Expose security-level single-index diagnostics without automating active bets

- **Date:** 2026-08-02
- **Decision:** Generalize excess-return OLS to each selected security and expose characteristic lines, residuals, coefficient inference, risk decomposition, comparison tables and exports. Do not implement the workbook's active/passive portfolio construction.
- **Context:** Workbook 4 contains two detailed security regressions and an index-portfolio model whose active weights depend on supplied alpha forecasts divided by residual variance. Saved active weights include negative positions.
- **Rationale:** Security diagnostics are supported, testable and relevant to research and market-risk roles. Converting historical alpha into unconstrained positions would violate the long-only boundary and imply persistence without forecast governance.
- **Consequences:** Historical alpha screens carry non-forecast warnings and no Buy/Sell labels. Treynor–Black-style allocation stays educational-only; rolling stability and outlier diagnostics remain possible enhancements.
- **Status:** Accepted.

## D029 — Surface strategy comparison without attributing unsupported rules to Workbook 6

- **Date:** 2026-08-02
- **Decision:** Promote the existing rebalancing and momentum outputs into a top-level Portfolio Strategies workspace and add workbook-supported benchmark-difference diagnostics. Do not claim that the source teaches the existing rebalancing schedules or momentum rule.
- **Context:** Workbook 6 directly supports passive tracking, active-manager comparison, turnover distinctions and fixed-income strategy examples, but contains no CPPI, momentum, periodic-rebalancing, threshold-rebalancing, transaction-cost, or trade-timing model.
- **Rationale:** A consolidated strategy comparison is professionally useful, while provenance must distinguish source-derived metrics from existing product methodology. Specialized tax and bond workflows require data that adjusted-price history does not provide.
- **Consequences:** Policy histories gain aligned active return, absolute periodic difference, tracking error and information ratio. Fixed-income, tax, index-construction and valuation exercises remain internally traced and educational-only.
- **Status:** Accepted.
