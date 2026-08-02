# Project history

## 2026-08-02 — Deployment package and repository audit

- **What changed:** Audited all Python imports and legacy names, normalized the sole internal absolute import to package-relative form, added a regression test that imports every tracked `portfolio_dashboard` module, and documented the exact Streamlit Cloud repository/branch recovery procedure.
- **Root cause finding:** Current GitHub `main` contains `portfolio_dashboard/formatting.py`, and a fresh checkout passes the complete suite and AppTest. A build log naming an older repository therefore indicates stale Streamlit Cloud deployment configuration rather than a missing current-repository module.

## 2026-08-02 — Canonical Streamlit deployment URL

- **What changed:** Replaced current deployment references and the automated health-check target with `https://portfolio-lens.streamlit.app`.
- **Why:** The product-aligned Streamlit deployment URL is now verified and is the canonical public address.
- **Evidence:** README launch link, deployment runbook, demo guide, deployment-health workflow, CI, and the successful post-push deployment check.

## 2026-08-01 — Independent CI and deployment verification

- **What changed:** Added GitHub Actions CI for the complete offline suite and non-socket Streamlit startup, a scheduled credential-free deployment-health classifier, stronger initial-page AppTest assertions, and reusable Markdown-link validation.
- **Why it changed:** Managed Codex/Herdr execution can block socket binding or DNS independently of PortfolioLens correctness, so startup and public-endpoint evidence needed an external, reproducible runner.
- **Problem solved:** Every `main` push and pull request now receives deterministic application verification, while the hosted endpoint is checked independently and reports successful responses, authentication redirects, DNS failures, timeouts, and server errors without conflating them.
- **Tradeoffs:** Authentication redirects establish Streamlit reachability but not signed-out UI rendering. Playwright remains excluded until the endpoint can be tested anonymously without brittle credentials.
- **Evidence:** `.github/workflows/ci.yml`, `.github/workflows/deployment-health.yml`, `scripts/check_deployment.py`, `scripts/validate_markdown_links.py`, and the strengthened `tests/test_app.py` initial-state contract.

## 2026-08-01 — Approved Portfolio Management roadmap completion

- **What changed:** Completed long-only frontier/GMV/tangency/target-return/CAL construction, holdings-level periodic and threshold rebalancing with costs, standardized annualized active return, explicit allocation constraints with feasibility/compliance reporting, full report integration, educational companion material, UX hardening, and permanent traceability.
- **Why it changed:** These were the remaining course-supported and product-approved gaps after Phases 1, 2A, and 3.
- **Problem solved:** PortfolioLens now covers the approved portfolio construction, benchmark evaluation, implementation-policy, scenario, research, and educational workflows end to end without importing unsupported institutional features.
- **Career relevance:** Portfolio analytics, market risk, investment research, manager evaluation, portfolio construction, rebalancing/implementation analysis, and systematic-strategy interviews.
- **Tradeoffs:** Optimization remains sample-sensitive, long-only, and non-leveraged. Rebalancing assumes fractional close-of-period execution. Classifications are user-defined. Advanced factor, fixed-income, tax, and personalized-advice workflows remain educational, deferred, or excluded.
- **Evidence:** Synthetic optimization/rebalancing/constraint tests, offline Streamlit tab tests, report export tests, documentation validation, repository scans, and a deterministic four-ETF end-to-end sample workflow.

## 2026-08-01 — Phase 3 professional investment research application

- **What changed:** Added a dedicated investment research workspace, transparent Portfolio Health Score, like-for-like allocation comparison, interactive hypothetical weight/shock analysis, metric-and-rule-linked deterministic insights, and a print-safe professional HTML report.
- **Why it changed:** PortfolioLens already computed broad analytics but required users to assemble the research interpretation across separate tabs. Phase 3 creates a coherent evidence-first workflow without adding predictive or advisory claims.
- **Problem solved:** Users can now compare supported portfolios under one methodology, inspect every score point, test an explicit scenario, trace each observation to a computed metric, and export the same research structure.
- **Career relevance:** Portfolio analytics, investment research, manager/performance evaluation, risk communication, scenario analysis, and explainable financial software.
- **Tradeoffs:** The Health Score uses disclosed application thresholds that are necessarily judgmental. What-if results remain historical constant-weight estimates plus instantaneous shocks, not forecasts or implementation simulations. No LLM investment advice was added.
- **Evidence:** Synthetic unit tests cover score arithmetic and missing-metric coverage, portfolio comparison reconciliation, scenario validation/shock reconciliation, prohibited advice language, report sections, and offline Streamlit research-workspace rendering.

## 2026-08-01 — Phase 2A benchmark regression and CAPM evaluation

- **What changed:** Added an excess-return single-index OLS model with annualized alpha, beta, R², residual volatility, systematic/idiosyncratic variance and shares, observations, CAPM required return, Jensen’s alpha, and Treynor ratio. The dashboard and HTML report now explain and label the model separately from cumulative benchmark-relative results.
- **Why it changed:** The approved course-derived roadmap identified a gap between the existing covariance beta and the full benchmark regression/performance-evaluation workflow taught in the single-index and performance-evaluation materials.
- **Problem solved:** Benchmark analysis now connects fitted market exposure, explained and residual risk, and CAPM-based performance measures under one auditable excess-return convention.
- **Course or career connection:** `2026S_FIN5745 PM_Workbook 4. Securities Selection & Single Index Model _Q.xlsx`, `2026S_FIN5745 PM_Class Notes 4. Single Index Portfolio Model & Security Selection.pptx`, and `2026S_FIN5745 PM_Workbook 7. Evaluation of Portfolio Performance_Q.xlsx`; portfolio analytics, asset management, performance measurement, and quantitative research.
- **Tradeoffs:** Estimates remain benchmark- and sample-dependent. The model uses one benchmark factor, does not establish causality or skill, and does not add APT, multifactor, Treynor–Black, leverage, or short selling.
- **Evidence:** Deterministic synthetic tests recover known regression parameters, reconcile Jensen’s alpha to regression alpha, and reconcile systematic plus idiosyncratic variance to total excess-return variance.

## 2026-08-01 — Phase 1 portfolio-methodology alignment

- **What changed:** Added explicit historical arithmetic annualized return and annualized variance, exposed reusable portfolio expected-return and covariance-matrix variance formulas, and standardized performance, strategy, Sortino, and optimizer Sharpe on arithmetic annualized excess return.
- **Why it changed:** The course audit found that the scorecard used CAGR while maximum-Sharpe construction used arithmetic expected return. That mismatch made portfolio evaluation and optimization methodologically inconsistent.
- **Problem solved:** The same portfolio now has one auditable Sharpe formula across analytics and construction, while CAGR remains a distinct realized compound-growth measure.
- **Course or career connection:** FIN5745 risk-and-return, Markowitz, CML, and performance-evaluation workbooks; portfolio analytics, asset management, and interview explanation.
- **Tradeoffs:** Historical Sharpe and Sortino values change. Arithmetic expected return remains backward-looking and is explicitly not presented as a forecast. Frontier, regression, and rebalancing extensions remain Phase 2.
- **Evidence:** Synthetic formula, matrix reconciliation, scorecard-separation, and optimizer/display consistency tests added with this milestone.

## 2026-08-01 — PortfolioLens product rename

- **What changed:** Renamed the current product and exported report branding from Portfolio Research Dashboard to PortfolioLens, adopted the subtitle “Multi-Asset Portfolio Analytics & Investment Research,” and prepared the repository and deployment references for the new identity.
- **Why it changed:** The former name was accurate but generic; PortfolioLens is more distinctive while still describing portfolio analysis and investment-research work.
- **Problem solved:** Established one concise identity across the application, documentation, exports, GitHub repository, screenshots, and deployment.
- **Relevant course or career connection:** Portfolio analytics, risk communication, investment research, and interview-ready project presentation.
- **Important tradeoffs:** This is a branding-only change. The `portfolio_dashboard` import package, product scope, architecture, formulas, methodology, and tests remain intact.
- **Commit:** Rename commits created with this milestone; verify final hashes from Git history.

## 2026-08-01 — Native dark financial theme

- **What changed:** Replaced the light showcase palette with a native Streamlit dark theme covering application surfaces, sidebar, widgets, tables, semantic colors, and chart palettes. Plotly rendering now explicitly requests Streamlit theme inheritance.
- **Why it changed:** The production dashboard needed a consistent professional dark appearance with readable financial data and status messaging.
- **Problem solved:** Removed dependence on a light presentation while retaining supported Streamlit behavior and avoiding brittle CSS or JavaScript overrides.
- **Relevant course or career connection:** Financial-dashboard communication, investment-research presentation, and deployment-ready analytics.
- **Important tradeoffs:** The theme uses built-in sans-serif typography rather than a remotely loaded font, prioritizing reliable startup and deployment. The palette is conservative and accessibility-led rather than heavily branded.
- **Commit:** Theme commit created with this milestone; verify the final hash from Git history.

This file records major project milestones in chronological order. Git commits and repository files are the canonical evidence. Where a motivation is inferred from the current development session rather than recorded in Git, it is labeled accordingly.

## 2026-07-31 — Core analytics engine

- **What changed:** Added the modular `portfolio_dashboard` package, dependency configuration, pytest setup, synthetic tests, data validation, performance and risk analytics, portfolio construction, rebalancing, strategy, stress, reporting, formatting, and the reusable analytics pipeline.
- **Why it changed:** Established the financial calculation layer independently of the presentation layer.
- **Problem solved:** Replaced an empty project state with a testable, reusable portfolio-research engine.
- **Course or career connection:** Portfolio mathematics, benchmark evaluation, portfolio construction, systematic strategy research, and Python financial analysis.
- **Tradeoffs:** Used daily simple returns, constant weights, yfinance, and a small functional architecture instead of persistence, authentication, or institutional infrastructure.
- **Evidence:** Commit `3b7ed4d` (`build core portfolio analytics engine`).

## 2026-07-31 — Streamlit application and methodology

- **What changed:** Added the Streamlit entrypoint, user controls, analytics pages, charts, exports, README, methodology guide, deployment instructions, and ignore rules.
- **Why it changed:** Made the analytics engine usable, demonstrable, and deployable as a focused research application.
- **Problem solved:** Connected validated inputs and pure calculations to an interview-ready workflow.
- **Course or career connection:** Investment-research communication, portfolio analytics, market risk, rebalancing, and Streamlit deployment.
- **Tradeoffs:** Chose one application entrypoint and tabbed navigation; selected reliable HTML reporting instead of a fragile PDF stack.
- **Evidence:** Commit `c3cd9c6` (`add Streamlit research dashboard and documentation`).

## 2026-07-31 — Local tooling isolation

- **What changed:** Added local agent-tooling paths to `.gitignore`.
- **Why it changed:** Kept machine-specific development metadata out of version control.
- **Problem solved:** Prevented unrelated local tooling from contaminating the repository.
- **Course or career connection:** Reproducible software-development hygiene.
- **Tradeoffs:** Local tooling configuration is intentionally not shared through this project.
- **Evidence:** Commit `d07a5d9` (`ignore local agent tooling`).

## 2026-07-31 — Downside-risk corrections

- **What changed:** Corrected drawdown baselines, historical VaR/CVaR loss signs, relative drawdown, and Sortino downside-deviation handling; expanded tests and methodology documentation.
- **Why it changed:** Financial metrics needed consistent loss interpretation and initial-wealth treatment.
- **Problem solved:** Initial losses could be hidden by the drawdown series, and profitable lower tails could be displayed as negative losses.
- **Course or career connection:** Portfolio performance evaluation and market-risk measurement.
- **Tradeoffs:** VaR and CVaR remain historical one-day measures and cannot represent unseen tail events.
- **Evidence:** Commit `a080c52` (`fix downside risk calculations`).

## 2026-07-31 — Strategy, optimization, and stress hardening

- **What changed:** Added optimizer input/failure checks, isolated optional allocation failures, enforced strategy warm-up, aligned strategy and buy-and-hold evaluation periods, clarified strategy statistics, required complete shocks, and made historical stress use constant-weight daily returns and actual trading dates.
- **Why it changed:** Invalid estimates or insufficient history must not produce plausible-looking results.
- **Problem solved:** Prevented silent all-cash strategy output, incomplete shock assumptions, and misleading optimization results.
- **Course or career connection:** Look-ahead control, out-of-sample discipline, risk controls, portfolio construction, and stress testing.
- **Tradeoffs:** The strategy remains a single long/cash moving-average model; optimization remains historical and long-only.
- **Evidence:** Commit `33ed9f0` (`harden strategy allocation and stress analysis`).

## 2026-07-31 — Dashboard reporting and state hardening

- **What changed:** Corrected metric units, used active shocks and selected rebalancing targets in reports, used actual analysis dates, improved Streamlit state and lazy tab rendering, modernized width arguments, added application smoke tests, and raised the minimum Streamlit version.
- **Why it changed:** Displayed and exported results needed to match the active analysis state and financial units.
- **Problem solved:** Removed report/UI inconsistencies and added an offline check that the application entrypoint renders and validates inputs.
- **Course or career connection:** Investment-research communication, reporting controls, and deployment readiness.
- **Tradeoffs:** Streamlit 1.55 or newer is required; the UI remains in one entrypoint pending a future behavior-preserving split.
- **Evidence:** Commit `f74a683` (`harden dashboard reporting and state`).

## 2026-07-31 — Course-informed roadmap review

**Context from current development session — verify before treating as canonical.**

The current session reviewed local materials titled *Algorithmic Trading in Python*, *Machine Learning & AI*, and *Portfolio Management*. The review identified candidate future work around consistent risk-adjusted-return conventions, single-index regression, periodic rebalancing, and strategy subperiod analysis. It also concluded that machine learning, Treynor–Black, bond analytics, and personalized investment-policy features would currently add disproportionate data, methodology, or scope complexity. These are planning inputs, not implemented features or approved methodology changes.

## 2026-07-31 — Permanent documentation governance

- **What changed:** Added commit-backed project history, decisions, roadmap, and changelog records, followed by a living architecture reference and chronological engineering journal; linked the system from the README.
- **Why it changed:** Future maintainers and coding agents need current technical truth and recorded rationale before making material changes.
- **Problem solved:** Git history alone does not explain module contracts, product lessons, alternatives, consequences, or safe extension procedures.
- **Course or career connection:** Reproducibility, model-risk governance, technical communication, maintenance, and interview preparation.
- **Tradeoffs:** Kept the system in repository Markdown rather than introducing external project-management or architecture tooling.
- **Evidence:** Commit `2caedab` created the initial governance system. The journal and architecture additions are present in the repository after that commit.

## 2026-07-31 — Showcase interface and deployment preparation

- **What changed:** Performed a live nine-section review with a four-ETF sample; collapsed secondary strategy controls, added a persistent scope disclaimer, and added a native Streamlit theme. Added deployment, demo, and review documentation plus a real screenshot gallery.
- **Why it changed:** The final demonstration needed consistent rendering, concise controls, visible assumptions, reproducible assets, and an explicit Community Cloud verification path.
- **Problem solved:** Removed avoidable sidebar crowding and theme variability while preventing an unverified hosted URL from being presented as complete.
- **Course or career connection:** Investment-research communication, interview presentation, model-scope disclosure, and reproducible deployment practice.
- **Tradeoffs:** Retained the existing nine-tab navigation because responsive scrolling remained functional; did not add product features or alter financial methodology.
- **Evidence:** UI commit `2c55055`; documentation and screenshot commits follow this entry in Git history.

## 2026-08-01 — Production weight and stale-state correction

- **What changed:** Equal-weight mode now constructs `1/N` directly and ignores the disabled manual field; manual percentage parsing is centralized; analysis-defining input changes and failed runs clear prior outputs.
- **Why it changed:** Production exposed a mode-boundary error that interpreted three equal-weight placeholders as a 3% portfolio and left old results visible after failure.
- **Problem solved:** Three-asset equal weight now produces approximately 33.333% per asset, `50,35,15` converts once to `0.50,0.35,0.15`, and exports cannot remain attached to stale inputs.
- **Course or career connection:** Financial input correctness, state integrity, operational controls, and trustworthy investment-research presentation.
- **Tradeoffs:** Any input edit hides the prior result and requires a fresh successful run; this is intentionally stricter than retaining stale analysis with a warning.
- **Evidence:** Regression tests and the production-fix commit created with this milestone.

## 2026-08-01 — Workbook 1 risk-and-return trace and foundations

- **What changed:** Directly audited every nonempty worksheet in `2026S_FIN5745 PM_Workbook 1. Risk & Return of Portfolio Investments_Q.xlsx`; added HPR, periodic arithmetic/geometric return, coefficient-of-variation, asset foundation table, diversification-reduction calculations, UI explanations/export, deterministic tests, and permanent worksheet-level traceability.
- **Why it changed:** Similar metric names did not prove that PortfolioLens matched the workbook's formula, units, compounding, or population/sample assumptions.
- **Problem solved:** PortfolioLens now exposes the workbook-backed return/risk foundations while explicitly preserving sample statistics for historical estimation and population statistics for finite classroom scenarios.
- **Course or career connection:** Portfolio mathematics, financial-methodology governance, market-risk estimation, and interview explanation.
- **Tradeoffs:** Probability games and the identical-correlation limit remain educational-only; no generic scenario editor or duplicate population-risk dashboard was added.
- **Evidence:** Workbook 1 tests, `COURSE_TRACEABILITY.md`, Decision D022, and commits created for this milestone.

## 2026-08-01 — Workbook 2 construction and CML trace

- **What changed:** Directly audited all seven worksheets in `2026S_FIN5745 PM_Workbook 2. MW Efficient Frontier & Capital Market Line_A.xlsx`, recovered both material Solver configurations, reconciled the course models against PortfolioLens, and added non-leveraged complete-portfolio composition and exports.
- **Why it changed:** The prior course trace did not distinguish the workbook's long-only target-return frontier from its separate unconstrained short-selling tangency model.
- **Problem solved:** Users can now inspect any lending-only point between the risk-free asset and constrained tangency portfolio, while methodology labels prevent false equivalence with the workbook's unconstrained outputs.
- **Course or career connection:** Mean-variance construction, Solver translation, two-fund separation, CAL/CML interpretation, and model-risk governance.
- **Tradeoffs:** Borrowing, leverage, short sales, IPS authoring, and invented risk-aversion utility remain outside the production application.
- **Evidence:** Workbook 2 tests, permanent traceability, Decision D023, and commits created for this milestone.
## 2026-08-01 — Workbook 2 UI exposure correction

- **What changed:** Promoted the existing mean-variance backend from the combined Construction & Rebalancing tab to an explicitly named Portfolio Optimization section. Added direct GMV, tangency, target-return, complete-portfolio and optimized-weight labels/exports, while documenting why the direct risky-allocation control is not a risk-aversion coefficient.
- **Why:** Workbook 2 calculations were present and tested but were too difficult to discover in the application navigation.
- **Follow-up:** The tab bar originally rendered only after a successful analysis because the empty-state `st.stop()` preceded `st.tabs`. Navigation now renders on initial load, Portfolio Optimization has a dedicated pre-analysis empty state, and the running Git revision is visible in-app.

## 2026-08-02 — Workbook 3 capital-allocation and utility trace

- **What changed:** Audited all six nonempty worksheets in `2026S_FIN5745 PM_Workbook 3. Capital & Asset Classes Allocation_Q.xlsx`; recovered three Solver states and implemented the supported quadratic-utility complete-portfolio model with direct risk-aversion input, constraint disclosure and deterministic tests.
- **Why:** The workbook adds a numerical risk-aversion model that Workbook 2 did not contain, but does not substantiate a broad strategic/tactical asset-class policy workflow.
- **Boundary:** PortfolioLens uses historical long-only tangency estimates and `0≤y≤1`. It excludes the embedded third-party questionnaire, inferred asset classes, borrowing/leverage, and unsupported policy features. A source formula that double-weights complete-return components is documented and corrected rather than copied.
- **Evidence:** `construction.py`, the Portfolio Optimization UI, Workbook 3 tests, Decision D024 and the permanent course trace.

## 2026-08-02 — Independent frontier/CAL validation and public-language boundary

- **What changed:** Reconciled the optimizer against closed-form two-asset solutions and dense three-asset simplex searches; guaranteed an upper-branch frontier with tangency inclusion and failed-point filtering; rebuilt CAL slope from primitive inputs; added chart and diagnostic tests; removed development provenance from public application/report strings.
- **Why:** Passing unit tests did not by itself prove that the plotted curve, tangency marker and CAL were mutually consistent or professionally presented.
- **Assessment:** The previous frontier was mathematically sound in its core formulas and target range but partially complete as a plotted numerical product. It did not guarantee exact tangency-grid membership, and its CAL accepted a potentially stale Sharpe field.
- **Evidence:** Decision D025, expanded deterministic optimizer/AppTest coverage, Methodology reconciliation values and commits created for this milestone.

## 2026-08-02 — Transparent benchmark ticker aliases

- **What changed:** Added a centralized, case-insensitive benchmark alias allowlist; resolved provider symbols before download; retained friendly benchmark labels in charts/reports; added a visible mapping notice and more useful no-data guidance.
- **Why:** Common index notation such as `SPX` is natural to users but is not the Yahoo Finance symbol expected by yfinance.
- **Boundary:** Aliases apply only to the benchmark field. Portfolio holdings are never silently remapped, preserving the meaning of ambiguous equity symbols.
- **Evidence:** Alias unit tests, non-socket AppTest, Decision D026 and CI.
- **Follow-up:** `SPX` became the default benchmark label. Its expected `^GSPC` retrieval mapping is silent, while all alternate aliases continue to produce a notice; presentation and reports retain `SPX`.

## 2026-08-02 — Workbook 4 security-analysis trace

- **What changed:** Audited all six nonempty worksheets in the exact securities-selection workbook and added reusable per-security excess-return OLS, coefficient inference, systematic/idiosyncratic decomposition, characteristic-line and residual charts, comparison tables and CSV exports.
- **Why:** The application already had portfolio-level regression, but similarly named metrics did not cover the workbook's security-level fitted values, residuals, inference or cross-security comparison.
- **Boundary:** Historical alpha is labeled as a diagnostic, not a forecast or recommendation. The active/passive model is preserved as educational traceability because its supplied alpha forecasts and negative active weights conflict with the long-only product boundary.
- **Evidence:** Deterministic coefficient and variance-reconciliation tests, offline Streamlit AppTest, Decision D027, and the Workbook 4 section in course traceability.
- **UI correction:** The first implementation nested these outputs under Benchmark & Attribution despite describing them as publicly implemented. They are now promoted to an exact top-level `Security Analysis` tab with its own initial state and navigation assertion.
