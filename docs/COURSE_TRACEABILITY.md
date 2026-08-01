# Portfolio Management course traceability

This is the permanent mapping from audited course evidence to PortfolioLens. Course files were not modified or copied. A matching name is never treated as methodological equivalence without formula, assumption, code, and test evidence.

| Exact course source and section | Concept and PortfolioLens status | Formula or rule | Assumptions | Code and tests | Limitations and documentation |
|---|---|---|---|---|---|
| `2026S_FIN5745 PM_Workbook 1. Risk & Return of Portfolio Investments_Q.xlsx`; risk/return exercises | Arithmetic expected return, variance, covariance, portfolio moments — **Completed, Phase 1** | `E[r_p]=w′μ`; `Var(r_p)=w′Σw`; annualization `252×mean`, `252×sample variance` | Daily simple returns; constant weights; complete aligned observations | `performance.py`; formula, matrix, label, and reconciliation tests in `test_analytics.py` | Historical estimates are not forecasts; see `METHODOLOGY.md` Performance |
| `2026S_FIN5745 PM_Workbook 2. MW Efficient Frontier & Capital Market Line_Q.xlsx` and `_A.xlsx`; Sharpe/Markowitz/CML sections | Shared Sharpe, GMV, long-only frontier, target-return portfolios, constrained tangency, non-leveraged CAL — **Completed, Phases 1/2B** | minimize `w′Σw`; target `w′μ=μ*`; maximize `(w′μ-r_f)/sqrt(w′Σw)`; CAL `r_f+y(E[r_T]-r_f)`, `yσ_T` | `0≤w≤1`; sum one; `0≤y≤1`; arithmetic sample means/covariance; no borrowing | `construction.py`, `performance.py`, `app.py`; bounds, sum, feasibility, GMV, Sharpe, monotonicity, reproducibility, CAL, and failure tests | Sample-sensitive; no shorting/leverage or recommendation claim; see Construction methodology |
| `2026S_FIN5745 PM_Workbook 4. Securities Selection & Single Index Model _Q.xlsx`; single-index model | Excess-return OLS, alpha, beta, R², residual/systematic/idiosyncratic risk — **Completed, Phase 2A** | `r_p-r_f=α+β(r_m-r_f)+ε`; `β=Cov/Var`; `R²=1-SSE/SST`; systematic variance `β²Var(m)` | Aligned daily excess returns; annual risk-free divided by 252; one benchmark factor | `risk.py`, `pipeline.py`; known-coefficient, risk-decomposition, validation, and integration tests | Benchmark/sample dependent; not causality or skill evidence; see Risk and benchmark methodology |
| `2026S_FIN5745 PM_Workbook 5-1. CAPM, APT & Multifactor Models_Q.xlsx`; CAPM section | CAPM required return and Jensen’s alpha — **Completed, Phase 2A** | `r_f+β(E[r_m]-r_f)`; Jensen `E[r_p]-required return` | Arithmetic annualized returns; same aligned sample and beta | `risk.py`; CAPM/Jensen/regression-alpha reconciliation tests | Expected market return is historical sample estimate; APT/multifactor live features excluded |
| `2026S_FIN5745 PM_Workbook 7. Evaluation of Portfolio Performance_Q.xlsx`; performance evaluation | Jensen, Treynor, active return, tracking error, information ratio — **Completed, Phases 2A/2D** | Treynor `(E[r_p]-r_f)/β`; active `252×mean(r_p-r_b)`; TE `std(r_p-r_b)√252`; IR `active/TE` | Daily aligned portfolio/benchmark returns; beta must be nonzero for Treynor | `risk.py`, `formatting.py`, `app.py`; synthetic formula and active-return/IR tests | Cumulative excess return is separately labeled; rolling alpha/beta not audit-approved |
| `2026S_FIN5745 PM_Workbook 6. Portfolio Management Strategies_Q.xlsx`; strategy/rebalancing sections | Buy-and-hold, monthly/quarterly/annual/threshold rebalancing, drift, turnover, costs — **Completed, Phase 2C** | drift from holdings; one-way turnover `0.5Σ|trade|/V`; cost `rate×Σ|trade|` | Returns occur before close-of-period trade; fractional holdings; no cash flows/taxes/market impact | `rebalancing.py`, `app.py`, `reporting.py`; no-trade, schedules, triggers, turnover, cost, continuity, drift, reconciliation tests | Simulation differs intentionally from daily constant-weight analytics; see Rebalancing methodology |
| `PF_IPS_CFA_Final.docx`, `investment policy statement_individual investors_CFA-1.pdf`, `investment policy statement_institutional investors_CFA-1.pdf`; constraints/monitoring | Asset bands, exclusions, explicit category caps — **Completed, Phase 2E** | `min_i≤w_i≤max_i`; exclusions `max_i=0`; group `Σw_i≤cap`; sum one | User supplies every group label and cap; long-only; no silent relaxation | `construction.py`, `app.py`, `reporting.py`; band, exclusion, group, feasibility, parser, and breach-summary tests | No inferred classifications; maximum-volatility constraint not approved; see Construction methodology |
| Workbook 2 mean-variance comparison sections | Like-for-like supported portfolio comparison — **Completed, Phase 3** | Existing performance formulas applied to each weight vector; distance `0.5Σ|w_s-w_c|` | Same return sample, risk-free rate, and constant-weight model | `research.py`, `app.py`, `reporting.py`; comparison reconciliation tests | Weight distance is not realized turnover |
| Course-supported sensitivity concepts; PortfolioLens synthesis | Explicit long-only weights and holding shocks — **Completed, Phase 3** | scenario performance via existing formulas; instantaneous impact `Σw_is_i` | Nonnegative weights sum one; one finite explicit shock per holding | `research.py`, `stress.py`, `app.py`; validation and shock reconciliation tests | Not a forecast, rebalance simulation, or implicit asset-class scenario |
| Application-specific synthesis; not a course formula | Transparent Portfolio Health Score — **Completed, Phase 3; not course-derived** | disclosed weighted/clipped components and available-weight rescaling | Historical Sharpe, drawdown, CVaR, diversification, IR; coverage shown | `research.py`; arithmetic, bounds, and missing-coverage tests | Heuristic only; not suitability, optimality, or advice; see Research workspace methodology |
| Workbook 1/2/4/5-1 concepts | Two-asset, frontier/CAL, CAPM and single-index intuition — **Educational-only, Phase 4** | Worked formulas in companion | Deterministic examples; no external data | `docs/education/PORTFOLIO_MANAGEMENT_COMPANION.md` | Explanatory material, not separate production models |
| Workbook 5-1 and `Assignment/treynor_black_portfolio_model.py`; advanced-model sections | Treynor–Black, APT, multifactor overview — **Educational-only, Phase 4** | Conceptual factor/active-model forms only | No approved factor data or alpha-forecast process | Educational companion; no runtime implementation | Intentionally excluded from live app due data/estimation scope |

## Final classification

### Completed

- Foundational portfolio moments and consistent Sharpe methodology
- Excess-return regression, CAPM, Jensen, Treynor, active return, tracking error, and information ratio
- Long-only frontier, GMV, constrained tangency, target-return construction, and non-leveraged CAL
- Holdings-level buy-and-hold, periodic and threshold rebalancing with turnover/costs
- Explicit asset bands, exclusions, user-defined group caps, feasibility and compliance validation
- Research comparison, what-if analysis, deterministic insights, Health Score, and professional report

### Deferred

- Strategy subperiod/validation-split diagnostics and engineering refactors are useful but are not remaining approved Portfolio Management requirements.
- Equal-risk-contribution, volatility targeting, Brinson attribution, and fixed-income analytics require additional methodology or data design.

### Educational-only

- Two-asset derivation, frontier/CAL intuition, CAPM interpretation, and Treynor–Black/APT/multifactor overview.

### Intentionally excluded

- Monte Carlo portfolio clouds and course-derived “risk parity,” which the audit did not substantively support.
- Rolling alpha/beta and maximum-volatility constraints, which approved traceability does not require.
- Short selling, leverage/borrowing, inferred classifications, Treynor–Black/APT/multifactor live models, fixed-income instrument workflows, IPS authoring, tax-lot optimization, personalized advice, and LLM-generated investment commentary.
