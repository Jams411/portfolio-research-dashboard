# Project journal

This journal explains the project’s evolution in plain language. It complements, rather than replaces, the evidence-focused [project history](PROJECT_HISTORY.md), formal [decision log](DECISIONS.md), user-facing [changelog](../CHANGELOG.md), and forward-looking [roadmap](ROADMAP.md).

## 2026-08-02 — Verified PortfolioLens deployment address

- **Goal:** Align every current public-deployment reference with the verified product URL.
- **What changed:** Updated documentation, governance records, and the credential-free deployment-health workflow to `https://portfolio-lens.streamlit.app`.
- **Why it changed:** The prior address was no longer the verified canonical deployment.
- **Tradeoffs:** Historical deployment decisions remain understandable through the journal, while operational links now have one source of truth.
- **Verification:** Repository-wide URL search, full offline tests, documentation validation, CI, and deployment-health workflow.

## Product origin and boundaries

**Context from current development session — verify before treating as canonical.**

The project was created under the former working name `portfolio-research-dashboard` as a focused, internship-ready application that can be demonstrated, tested, deployed, and explained without institutional-platform complexity. It was renamed PortfolioLens on 2026-08-01 without changing that purpose. The current session states that it is separate from a frozen Portfolio Intelligence Platform and must not import from, depend on, simplify, or modify that platform. The frozen platform was not inspected to prepare this journal, so no technical comparison is claimed here.

Interview explainability and financial correctness were prioritized over feature count. That principle explains the use of small financial functions, one explicit strategy, deterministic reporting, strict data validation, and synthetic tests. Advanced features were deferred when they required unreliable classifications, new data sources, opaque models, personalized advice, or disproportionate methodology and deployment complexity.

## 2026-08-01 — End-to-end approved roadmap completion

- **Goal:** Finish every remaining approved Portfolio Management capability while preserving the focused PortfolioLens product boundary.
- **Delivered:** Long-only frontier/GMV/tangency/target-return/CAL construction; buy-and-hold and periodic/threshold rebalancing with drift, turnover and costs; active-return labeling; explicit allocation constraints and compliance validation; report/UX completion; and an educational companion.
- **Methodology controls:** Arithmetic optimizer inputs remain distinct from CAGR; CAL is non-leveraged; holdings-level simulation is distinct from daily constant-weight analytics; classifications are user-entered; constraint feasibility is checked before optimization.
- **Verification:** Deterministic unit and integration tests cover formulas, bounds, solver failure, schedules, triggers, costs, continuity, constraints, reports, and Streamlit views. Repository-wide checks and a four-ETF sample workflow close the milestone.
- **Boundary result:** Monte Carlo, course-derived risk parity, rolling regression, maximum-volatility constraints, shorting, leverage, advanced live factor models, fixed-income workflows, tax lots, IPS authoring, and LLM advice remain excluded, deferred, or educational-only.
- **Next step:** No approved Portfolio Management roadmap implementation remains. Future changes require a new scoped decision.

## 2026-08-01 — Phase 3 research workflow

- **Date:** 2026-08-01
- **Goal:** Turn the existing analytical dashboard into a professional research application without introducing opaque narrative generation or investment advice.
- **What changed:** Added a reusable research module, professional HTML report, Health Score and component audit table, allocation comparison, submitted what-if workflow, and deterministic insights with explicit evidence and rules.
- **Methodology choice:** All historical portfolio comparisons reuse the established constant-weight and arithmetic-return conventions. The Health Score is openly labeled an application heuristic, and unavailable component weights are rescaled with visible coverage.
- **Engineering choice:** Business logic remains independent of Streamlit and is tested synthetically. Streamlit owns form state and presentation only; scenario inputs never mutate the saved analysis.
- **Risks managed:** No LLM dependency, predictive language, personalized recommendations, silent score imputation, implicit asset classification, or scenario-weight normalization was introduced.
- **Next step:** Phase 2B construction work remains the tested long-only frontier, feasible target-return portfolios, and carefully framed tangency/CAL presentation. Rebalancing simulation and turnover remain separate later work.

## 2026-08-01 — Phase 2A benchmark research

- **Date:** 2026-08-01
- **Goal:** Extend benchmark analysis from a standalone covariance beta to the course-supported excess-return single-index and CAPM evaluation workflow.
- **What changed:** Added OLS alpha/beta/R², residual volatility, systematic and idiosyncratic variance shares, CAPM required return, Jensen’s alpha, and Treynor ratio, with distinct UI sections and non-predictive explanations.
- **Why it changed:** The single-index and performance-evaluation workbooks connect market exposure, residual risk, and risk-adjusted evaluation; implementing only a similarly named beta did not satisfy that methodology.
- **Tests and evidence:** A constructed return series with known slope, intercept, and orthogonal residual recovers its parameters and risk decomposition. Edge tests cover inadequate observations and constant benchmark returns.
- **Tradeoffs:** Arithmetic risk-free conversion was selected so annualized regression alpha exactly reconciles with Jensen’s alpha. Results depend on the selected benchmark and history and are not evidence of manager skill.
- **Next step:** Phase 2B remains the long-only efficient frontier, feasible target-return portfolios, and careful historical tangency/CAL presentation; no such construction behavior changed in Phase 2A.

## 2026-08-01 — Phase 1 course-roadmap implementation

- **Date:** 2026-08-01
- **Goal:** Resolve the foundational return and Sharpe inconsistency identified by the complete Portfolio Management course audit.
- **Context:** PortfolioLens displayed CAGR-based Sharpe while its maximum-Sharpe optimizer used arithmetic annualized expected return. The course risk/return, Markowitz, CML, and performance-evaluation materials consistently supported arithmetic average excess return for this purpose.
- **What changed:** Added explicit arithmetic annualized return, annualized sample variance, portfolio `w′μ` and `w′Σw` helpers, and one shared Sharpe formula used by performance, strategy, Sortino, and optimization. CAGR remains a separate realized compound-growth metric.
- **Why it changed:** Portfolio evaluation and construction must use the same financial convention if users are expected to compare the displayed scorecard with optimized allocations.
- **Relevant career or course connection:** FIN5745 portfolio theory and performance measurement; asset-management, portfolio-analytics, and quantitative-research interviews.
- **Tradeoffs:** Historical Sharpe and Sortino outputs change. The arithmetic estimate is backward-looking and is not a forecast. No frontier, regression, rebalancing simulation, shorting, leverage, or advanced course model was added.
- **Lessons learned:** A familiar metric name is insufficient evidence of methodological equivalence; numerator, annualization, risk-free treatment, and optimizer objective must reconcile explicitly.
- **Next step:** Phase 2 begins with benchmark excess-return regression and CAPM performance metrics, followed by frontier/target-return construction and rebalancing realism.

## 2026-08-01 — PortfolioLens identity

- **Date:** 2026-08-01
- **Goal:** Give the application a concise, distinctive name without changing what it does.
- **Context:** Portfolio Research Dashboard was descriptive but generic. The implementation had reached a stable public-deployment stage and needed consistent product, repository, export, and demo branding.
- **What changed:** Renamed the product to PortfolioLens, added the subtitle “Multi-Asset Portfolio Analytics & Investment Research,” updated current-product documentation and report branding, and retained the stable internal Python package name.
- **Why it changed:** PortfolioLens better communicates a focused analytical view across portfolio risk, benchmark comparison, construction, rebalancing, strategy research, and reporting.
- **Relevant career or course connection:** Investment-research communication, portfolio analytics, and interview presentation.
- **Tradeoffs:** Kept `portfolio_dashboard` as the internal namespace to avoid a cosmetic import migration. The name does not imply prediction, advice, or institutional-platform scope.
- **Lessons learned:** Product identity can improve presentation without requiring product expansion; branding and methodology should remain separate decisions.
- **Open questions:** Whether Streamlit Community Cloud permits the public app slug to be renamed in place without recreation.
- **Next step:** Rename GitHub in place, verify redirects and synchronization, then complete the Streamlit URL transition if supported.
- **Related commit hashes:** Rename commits created with this milestone; verify final hashes from Git history.

## 2026-08-01 — Production dark-theme standardization

- **Date:** 2026-08-01
- **Goal:** Give the deployed dashboard a consistent professional dark appearance without unsupported styling.
- **Context:** The showcase milestone introduced a fixed native light theme; the production presentation was subsequently directed toward a finance-appropriate dark default.
- **What changed:** Configured native Streamlit colors for backgrounds, text, controls, borders, semantic states, dataframes, the sidebar, and charts; made Plotly's Streamlit theme inheritance explicit.
- **Why it changed:** Financial tables and charts need predictable contrast across local and Community Cloud environments.
- **Relevant career or course connection:** Investment-research communication and production dashboard delivery.
- **Tradeoffs:** Used the built-in sans-serif font to avoid an external font request, and avoided CSS and JavaScript entirely. A dark default is consistent but does not offer a user-selectable light variant.
- **Lessons learned:** Native design tokens can cover the full dashboard surface while remaining safer across Streamlit upgrades than DOM-targeted styling.
- **Open questions:** Revisit the palette only if future accessibility testing identifies a specific contrast or color-vision issue.
- **Next step:** Verify every analysis section and the public deployment using the same sample workflow.
- **Related commit hashes:** Theme commit created with this milestone; verify the final hash from Git history.

## 2026-07-31 — Core analytics foundation

- **Date:** 2026-07-31
- **Goal:** Establish a complete, reusable financial-analysis engine before building the interface.
- **Context:** The repository needed a defensible calculation boundary for data, performance, risk, construction, strategy, stress, and reporting.
- **What changed:** Added the `portfolio_dashboard` package, configuration, dependencies, pytest setup, synthetic tests, and the reusable `run_analysis` pipeline.
- **Why it changed:** Financial logic needed to be testable without Streamlit or internet access.
- **Relevant career or course connection:** Python financial analysis, portfolio analytics, market risk, benchmark evaluation, portfolio construction, and systematic strategy research.
- **Tradeoffs:** Chose functional modules and a small immutable analysis result instead of a database, service layer, or object-heavy domain model. Used yfinance and daily adjusted history rather than paid or intraday data.
- **Lessons learned:** A stable calculation boundary makes the UI simpler and gives interviews a clear architecture story: validate once, compute in pure functions, then present results.
- **Open questions:** How should return and risk-free-rate conventions be standardized across scorecards and optimization? Should the constant-weight model eventually be compared with periodic rebalancing?
- **Next step:** Build the Streamlit workflow and document the methodology.
- **Related commit hashes:** `3b7ed4d`.

## 2026-07-31 — Streamlit workflow and research communication

- **Date:** 2026-07-31
- **Goal:** Turn the calculation engine into a professional end-to-end research application.
- **Context:** A portfolio project must be usable by someone who does not know the package internals.
- **What changed:** Added sidebar inputs, tabbed analytics, charts, allocation and rebalancing views, strategy and stress pages, exports, README, methodology documentation, and deployment instructions.
- **Why it changed:** The project needed a coherent demonstration path from user inputs to an investment-research report.
- **Relevant career or course connection:** Investment-research communication, market-risk reporting, portfolio decisions, trade operations, and Streamlit deployment.
- **Tradeoffs:** Used one Streamlit entrypoint and tabs for a compact experience. Selected deterministic HTML instead of PDF and avoided authentication, persistence, and live trading.
- **Lessons learned:** A focused interface benefits from short explanations and explicit assumptions more than from additional charts.
- **Open questions:** At what point should page rendering move out of `app.py`? How should live-data outages be handled in demonstrations?
- **Next step:** Audit financial edge cases and state/report consistency.
- **Related commit hashes:** `c3cd9c6`, `d07a5d9`.

## 2026-07-31 — Downside-risk methodology corrections

- **Date:** 2026-07-31
- **Goal:** Correct financially misleading downside-risk edge cases.
- **Context:** A code review found that initial losses could be hidden from drawdown and that signed lower-tail returns could be presented as negative losses.
- **What changed:** Included initial wealth in portfolio and relative drawdown peaks, reported VaR/CVaR as nonnegative loss magnitudes, corrected Sortino downside-deviation handling, and added deterministic tests and methodology updates.
- **Why it changed:** Risk metrics must have stable signs, baselines, and denominators if users are expected to compare portfolios.
- **Relevant career or course connection:** Portfolio performance evaluation, downside-risk measurement, and market-risk control.
- **Tradeoffs:** Historical VaR/CVaR remain backward-looking one-day empirical measures; the correction does not make them predictive.
- **Lessons learned:** Small baseline and sign choices can materially change the interpretation of otherwise familiar metrics. Formula fixes require tests and documentation together.
- **Open questions:** The roadmap still calls for reviewing the numerator and risk-free-rate convention used by Sharpe and Sortino.
- **Next step:** Harden optimizer, strategy, and stress failure paths.
- **Related commit hashes:** `a080c52`.

## 2026-07-31 — Optimizer, strategy, and stress hardening

- **Date:** 2026-07-31
- **Goal:** Prevent incomplete data or invalid estimates from producing plausible-looking analysis.
- **Context:** Optional optimizers, moving-average warm-up, custom shocks, and historical scenarios have distinct failure conditions.
- **What changed:** Isolated allocation failures, validated optimizer inputs and convergence, rejected insufficient strategy history, aligned strategy and buy-and-hold evaluation periods, clarified statistics, required complete custom shocks, and aligned historical stress with the constant-weight return model.
- **Why it changed:** Silent fallback can be more dangerous than an actionable error in financial software.
- **Relevant career or course connection:** Long-only optimization, look-ahead avoidance, transaction costs, stress testing, and systematic-research discipline.
- **Tradeoffs:** The application may omit an unavailable optimized method rather than replace it. The strategy remains one explainable long/cash rule and does not tune parameters automatically.
- **Lessons learned:** Optional analysis should fail locally; one failed optimizer should not erase valid deterministic allocations. Strategy comparison must begin after the same warm-up date.
- **Open questions:** Would calendar-year or fixed validation-period strategy diagnostics provide enough value without creating an optimization workflow?
- **Next step:** Make presentation state and exported reports match the active analysis exactly.
- **Related commit hashes:** `33ed9f0`.

## 2026-07-31 — Reporting, units, and Streamlit state

- **Date:** 2026-07-31
- **Goal:** Ensure that UI tables and downloaded research reports reflect the same state and financial units.
- **Context:** Ratios and percentages require different formatting, and editable shocks or target allocations can change after the initial run.
- **What changed:** Centralized semantic formatting, used current shocks and selected rebalancing methods in reports, used actual aligned dates, bounded cached downloads, lazily rendered open tabs, modernized Streamlit calls, and added entrypoint smoke tests.
- **Why it changed:** A correct calculation is not enough if the presentation changes its meaning or exports stale choices.
- **Relevant career or course connection:** Investment-report controls, financial communication, and deployment-quality analytics.
- **Tradeoffs:** State-aware tabs require Streamlit 1.55 or newer. The entrypoint remains large to preserve a simple deployment shape.
- **Lessons learned:** Presentation formatting is part of financial correctness. Report generation should consume the current state, not defaults captured earlier.
- **Open questions:** Should report tables eventually carry explicit machine-readable units in exported CSV metadata?
- **Next step:** Preserve the rationale behind these changes in permanent governance documents.
- **Related commit hashes:** `f74a683`.

## 2026-07-31 — Permanent decision and change tracking

- **Date:** 2026-07-31
- **Goal:** Preserve project intent, methodology decisions, milestones, and scope boundaries for future maintainers and coding agents.
- **Context:** Git explains file changes but does not consistently preserve rationale, alternatives, consequences, or deferred scope.
- **What changed:** Added the project history, decision log, roadmap, changelog, and README governance rules.
- **Why it changed:** Future work should begin from recorded evidence instead of reconstructing history from memory.
- **Relevant career or course connection:** Engineering governance, model-risk documentation, reproducibility, and professional project communication.
- **Tradeoffs:** The system is intentionally lightweight Markdown rather than an external tracker or a directory of formal ADR files.
- **Lessons learned:** History, decisions, roadmap, methodology, and changelog serve different audiences and should link to one another rather than duplicate every detail.
- **Open questions:** Which roadmap items will be approved, and when should milestone names become formal version tags?
- **Next step:** Add a living architecture reference and this engineering journal.
- **Related commit hashes:** `2caedab`.

## 2026-07-31 — University-course review and roadmap refinement

**Context from current development session — verify before treating as canonical.**

- **Date:** 2026-07-31
- **Goal:** Use relevant coursework as evidence for a focused extension roadmap without copying unverified implementations.
- **Context:** The session reviewed local folders titled *Algorithmic Trading in Python*, *Machine Learning & AI*, and *Portfolio Management*.
- **What changed:** No application behavior changed. Planning emphasized financial-convention consistency, single-index benchmark research, periodic rebalancing, and strategy subperiod analysis.
- **Why it changed:** These topics offer stronger career relevance and interview value than adding unrelated advanced features.
- **Relevant career or course connection:** Portfolio Management supported performance ratios, CAPM/single-index methods, and rebalancing; Algorithmic Trading supported lagging, costs, warm-up, subperiod testing, and overfitting controls; Machine Learning & AI supported cautious validation but did not justify an ML dependency for the dashboard.
- **Tradeoffs:** Efficient frontier, equal-risk contribution, volatility targeting, Brinson attribution, bond duration/convexity, multifactor models, Treynor–Black, and fundamental clustering were deferred. Price-direction ML, automatic tuning, personalized advice, and live execution were avoided.
- **Lessons learned:** Coursework can motivate questions and validation standards, but it is not proof that a specific notebook formula or implementation belongs in production code.
- **Open questions:** Which candidate milestone should be approved first, and what source details should be recorded if a course-derived feature proceeds?
- **Next step:** Review and approve a small roadmap unit before changing methodology or behavior.
- **Related commit hashes:** No implementation commit; planning context was recorded in `2caedab`.

## 2026-07-31 — Final showcase and deployment readiness

- **Date:** 2026-07-31
- **Goal:** Prepare the tested application for a consistent interview demonstration and Community Cloud deployment without expanding product scope.
- **Context:** A live browser review used SPY, QQQ, TLT, and GLD with non-equal weights and VTI as the benchmark across all nine sections.
- **What changed:** Secondary momentum controls moved into a native expander; a visible research-only disclaimer and native light theme were added; deployment, demo, and review runbooks plus eight live screenshots were created.
- **Why it changed:** A final showcase needs predictable rendering, concise controls, visible scope assumptions, repeatable demo settings, and deployment claims grounded in a public URL check.
- **Relevant career or course connection:** Investment-research communication, portfolio-risk presentation, interview readiness, and reproducible Python deployment.
- **Tradeoffs:** The tab row remains dense on narrow screens, but Streamlit’s responsive tab scrolling worked. A navigation rewrite was not justified. No financial calculation or product feature changed.
- **Lessons learned:** Deployment readiness and deployment completion are separate states. Screenshots and a hosted URL should be generated from the verified application rather than placeholders or assumptions.
- **Open questions:** The candidate hosted URL still requires Streamlit account authorization/public-access verification.
- **Next step:** Push the prepared repository, authorize or create the Community Cloud app, and execute the signed-out post-deployment checklist.
- **Related commit hashes:** `2c55055`; documentation and screenshot commits follow this entry in Git history.

## 2026-08-01 — Workbook 1 methodology reconciliation

- **Date:** 2026-08-01
- **Goal:** Trace one risk-and-return workbook completely and close only the practical, supported PortfolioLens gaps.
- **Context:** The workbook mixes complete probability universes, short historical exercises, drawing-based instructor logic, a student photo, and stale Excel add-in residue.
- **What changed:** Added explicit HPR, arithmetic/geometric, asset risk, CV, and diversification functions and UI; recorded all nine sheets and their status.
- **Why it changed:** A deep source audit showed the key missing value was terminology and convention transparency, not another advanced model.
- **Relevant career or course connection:** Risk/return calculation, covariance reasoning, statistical-estimator choice, and model documentation.
- **Tradeoffs:** Retained sample statistics for observed markets instead of mechanically copying `VAR.P`; excluded probability games/common-correlation limits from the main UI.
- **Lessons learned:** Workbook formatting and named ranges are not methodology. Formula provenance, units, denominator choice, and the difference between finite scenarios and estimated distributions must be evaluated together.
- **Open questions:** None requiring a product decision; the unrecoverable historical Solver bounds are documented rather than inferred.
- **Next step:** Run full repository and deployment verification and preserve commit/CI evidence.
- **Related commit hashes:** Commits created with this milestone; verify final hashes from Git history.

## 2026-08-01 — Workbook 2 Solver and complete-portfolio reconciliation

- **Date:** 2026-08-01
- **Goal:** Determine exactly which frontier, tangency, and CML conventions survive in Workbook 2 and implement only the focused product gap.
- **Context:** The workbook contains two materially different Solver designs plus screenshots, drawings, fixed output matrices, course exhibits, and extensive stale add-in names.
- **What changed:** Recovered objective cells, changing cells, constraint relations and methods; added a lending-only complete portfolio and UI/export reconciliation with the CAL.
- **Why it changed:** “Tangency portfolio” was not enough to establish equivalence: the workbook tangency solution permits negative weights, while PortfolioLens deliberately does not.
- **Relevant career or course connection:** Optimization audit, constraint interpretation, model translation, investment-research communication, and testing of numerical invariants.
- **Tradeoffs:** Borrowing and shorting remain educational-only. Expected-return and covariance assumption sensitivity is proposed rather than added automatically.
- **Lessons learned:** Solver metadata, screenshots, saved negative weights, and chart coordinates must be reviewed together; any one source alone can conceal the actual constraint set.
- **Open questions:** None requiring a methodology decision. The source period for the workbook's assumed moments is not identified and is documented as unknown.
- **Next step:** Complete repository verification, CI, deployment health, and synchronization evidence.
- **Related commit hashes:** Commits created with this milestone; verify final hashes from Git history.

## 2026-08-02 — Workbook 3 evidence boundary and utility implementation

- **Date:** 2026-08-02
- **Goal:** Trace the exact capital-and-asset-classes workbook and implement every focused, recoverable gap without inventing policy-allocation functionality.
- **Context:** Six visible worksheets combine formulas, Solver metadata, classroom charts, handwritten work, third-party questionnaire images and extensive stale add-in names.
- **What changed:** Added quadratic utility and optimal complete-portfolio allocation using direct `A`; exposed it alongside direct risky allocation; documented worksheet formulas, three recoverable Solver states, assumptions and conflicts.
- **Why it changed:** Workbook 3 supplies `U` and `y*`, closing the risk-aversion gap left by Workbook 2. Its title alone does not support strategic/tactical weights, policy bands, liabilities, glide paths or inferred asset classifications.
- **Relevant career or course connection:** Capital allocation, risk preference, Solver/model audit, covariance-driven diversification and model-risk communication.
- **Tradeoffs:** The classroom unconstrained result is shown, but the applied result remains lending-only. The suitability questionnaire is not reproduced, and a double-weighted workbook return formula is corrected using the CAL identity.
- **Lessons learned:** Workbook labels, saved Solver constraints and formulas can conflict. Exact reproduction claims require agreement among all three; otherwise the discrepancy belongs in traceability.
- **Open questions:** The period underlying assumed returns/volatilities and the intended short-sale setting in `Optimal Complete Pf` cannot be recovered safely.
- **Next step:** Complete repository validation, push both logical commits, and verify CI/deployment evidence.
- **Related commit hashes:** `e67ea01` and the documentation commit created for this milestone.
