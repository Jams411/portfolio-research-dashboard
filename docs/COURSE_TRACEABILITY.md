# Portfolio Management course traceability

This document maps implemented PortfolioLens methods to the course evidence that supported the approved roadmap. It does not imply that course files were copied or that similarly named outputs are methodologically equivalent. Course files remain unmodified.

| Course material | Worksheet or section | Concept | PortfolioLens feature | Status | Related code | Tests | Methodology |
|---|---|---|---|---|---|---|---|
| `2026S_FIN5745 PM_Workbook 1. Risk & Return of Portfolio Investments_Q.xlsx` | Risk/return portfolio exercises | Arithmetic expected return, variance, covariance, portfolio return and variance | Historical arithmetic annualized return, annualized variance, `w′μ`, `w′Σw` | Implemented — Phase 1 | `portfolio_dashboard/performance.py` | `tests/test_analytics.py` performance and matrix-formula tests | `docs/METHODOLOGY.md` Performance |
| `2026S_FIN5745 PM_Workbook 2. MW Efficient Frontier & Capital Market Line_Q.xlsx` and `_A.xlsx` | Sharpe and mean-variance construction sections | Excess-return Sharpe and maximum-Sharpe construction | Shared performance/optimizer arithmetic Sharpe | Implemented — Phase 1; frontier/CAL deferred to Phase 2B | `portfolio_dashboard/performance.py`, `portfolio_dashboard/construction.py` | optimizer/display Sharpe reconciliation | `docs/METHODOLOGY.md` Performance and Construction |
| `2026S_FIN5745 PM_Workbook 4. Securities Selection & Single Index Model _Q.xlsx` | Single-index regression model | Excess-return alpha, beta, R², residual/systematic/idiosyncratic risk | Excess-return OLS and variance decomposition | Implemented — Phase 2A | `portfolio_dashboard/risk.py`, `portfolio_dashboard/pipeline.py`, `app.py` | synthetic known-regression and validation tests | `docs/METHODOLOGY.md` Risk and benchmark comparison |
| `2026S_FIN5745 PM_Class Notes 4. Single Index Portfolio Model & Security Selection.pptx` | Single-index model and security selection | Interpretation of market and residual risk | Regression explanations and historical-estimate limitations | Implemented — Phase 2A | `app.py`, `portfolio_dashboard/reporting.py` | Streamlit smoke test and report tests | `docs/METHODOLOGY.md` Risk and benchmark comparison |
| `2026S_FIN5745 PM_Workbook 5-1. CAPM, APT & Multifactor Models_Q.xlsx` | CAPM section only | CAPM required return and Jensen-style abnormal return | CAPM required return and Jensen’s alpha from the single-index beta | Implemented — Phase 2A; APT and multifactor models excluded | `portfolio_dashboard/risk.py` | synthetic CAPM/Jensen reconciliation tests | `docs/METHODOLOGY.md` Risk and benchmark comparison |
| `2026S_FIN5745 PM_Workbook 7. Evaluation of Portfolio Performance_Q.xlsx` | Performance evaluation | Jensen’s alpha and Treynor ratio | Jensen’s alpha and Treynor ratio using arithmetic annualized returns | Implemented — Phase 2A | `portfolio_dashboard/risk.py`, `app.py`, `portfolio_dashboard/reporting.py` | synthetic formula tests | `docs/METHODOLOGY.md` Risk and benchmark comparison |

## Approved boundaries

- Phase 2B retains the efficient frontier, feasible target-return portfolios, and carefully framed historical tangency/CAL work.
- Rebalancing simulation, turnover, and additional constraints remain later roadmap work.
- Monte Carlo and risk parity are not course-derived roadmap features because the completed audit did not substantively support them.
- Treynor–Black, APT, multifactor models, fixed-income workflows, IPS authoring, tax-lot optimization, leverage, and short selling remain outside the approved PortfolioLens scope.
