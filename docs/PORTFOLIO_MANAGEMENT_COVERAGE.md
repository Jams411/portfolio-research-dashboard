# Portfolio Management Coverage

This internal audit reconciles the external Portfolio Management source archive with PortfolioLens as of 2026-08-02. Source files were inspected read-only. “Implemented” below means the concept is mapped to code, deterministic tests, public UI where appropriate, methodology documentation, and report/export coverage; it does not mean a literal spreadsheet reproduction. Absolute workstation paths are intentionally not retained in tracked documentation.

## What PortfolioLens covers

- Daily simple-return foundations: holding-period, arithmetic, geometric and compound returns; sample variance, covariance, correlation and volatility; portfolio return/variance; diversification; return and Euler volatility contribution; downside risk and coefficient of variation.
- Benchmark-relative performance: active return, sample tracking error, Information Ratio, excess-return regression, alpha, beta, R², residual risk, CAPM required return, Jensen’s alpha and Treynor ratio.
- Long-only historical portfolio construction: equal weight, inverse volatility, global minimum variance, maximum Sharpe/tangency, target return, efficient upper frontier, non-leveraged CAL, complete portfolio, explicit utility input, asset bands and user-defined group caps.
- Allocation and implementation: current/model allocation comparison, contribution profile, implementation trades, periodic and threshold rebalancing, drift, turnover and proportional transaction costs.
- Strategy and evaluation: buy-and-hold, monthly/quarterly/annual/threshold policies, one-day-lagged momentum, drawdown, Sharpe, Sortino, Treynor, Jensen, Information Ratio, Fama selectivity and rolling diagnostics.
- Research workflow: security characteristic line, regression diagnostics, CAPM/SML, ETF return-risk filters, holdings normalization, look-through exposure, overlap, candidate screen, stress tests, deterministic insights and professional HTML/CSV exports.

## What PortfolioLens intentionally does not cover

- Personalized risk profiling, investment-policy authoring, suitability conclusions or target allocations presented as advice.
- Short selling, borrowing, leverage, options, tax-lot optimization, brokerage execution or live trade recommendations.
- Production Treynor–Black, APT or multifactor estimation without governed factor data; the public factor section documents the framework and unavailable inputs.
- Key-rate duration, yield-curve construction, credit/default/recovery modeling, embedded-option valuation, immunization, swaps, or liability workflows. Standard option-free bond analytics now use separate explicit instrument inputs; adjusted ETF prices remain outside that workflow.
- Automatic ticker-to-sector/asset-class inference, undated holdings scraping, analyst-target signals, CPPI, Brinson/style attribution without classifications, and Monte Carlo/risk parity not substantively supported by the audited sources.

## Complete source inventory

The exact path for each root-level item is the folder above plus the shown filename. Items prefixed `Assignment/` use that subfolder. “Evidence” states whether implementation, tests, UI and report/export coverage exist. Detailed formula/worksheet mappings for Workbooks 1–7 are in [COURSE_TRACEABILITY.md](COURSE_TRACEABILITY.md); the final-project chain is in [FINAL_ASSIGNMENT_AUDIT.md](FINAL_ASSIGNMENT_AUDIT.md).

| Source | Type | Purpose and substantive topics | Inspection and product classification | Evidence |
|---|---|---|---|---|
| `2026S_FIN5745 PM_Workbook 1. Risk & Return of Portfolio Investments_Q.xlsx` | XLSX | Probability, return/risk, covariance, correlation, diversification | Previously deep-reviewed; **Fully implemented and verified** except classroom-only probability illustrations | `performance.py`, Risk/Performance UI, report, `test_analytics.py`, traceability |
| `2026S_FIN5745 PM_Workbook 2. MW Efficient Frontier & Capital Market Line_A.xlsx` | XLSX | Two/three-asset math, GMV, frontier, tangency, CAL, IPS example | Previously deep-reviewed; construction **Fully implemented and verified**; IPS **Educational companion only** | `construction.py`, Portfolio Optimization, report/CSV, optimizer tests |
| `2026S_FIN5745 PM_Workbook 2. MW Efficient Frontier & Capital Market Line_Q.xlsx` | XLSX | Question/template version of the same model | Every nonempty sheet inventoried; **Documentation only** because answer workbook is the authoritative numerical reference | Coverage inventory; no duplicate feature |
| `2026S_FIN5745 PM_Workbook 3. Capital & Asset Classes Allocation_Q.xlsx` | XLSX | Capital allocation, two-asset allocation, complete portfolio, utility, minimum variance | Previously deep-reviewed; formulas **Implemented differently with justification** using historical estimates and explicit long-only inputs | Portfolio Optimization + new Asset Allocation UI, report/export, tests |
| `2026S_FIN5745 PM_Workbook 4. Securities Selection & Single Index Model _Q.xlsx` | XLSX | Security regressions, index model, alpha/residual-risk screen, active portfolio | Regression **Fully implemented and verified**; incomplete/short-enabled active mix **Educational companion only** | `risk.py`, Security Analysis, report/CSV, regression tests |
| `2026S_FIN5745 PM_Workbook 5-1. CAPM, APT & Multifactor Models_Q.xlsx` | XLSX | CAPM, SML, index/CAPM comparison, APT and multifactor examples | CAPM **Fully implemented and verified**; APT/multifactor numerical framework **Documentation only / Deferred** pending factor data | `asset_pricing.py`, Asset Pricing, report/CSV, CAPM tests |
| `2026S_FIN5745 PM_Workbook 5-2. Draft Pf Model for Final Project_Jameel_Shaikh.xlsx` | XLSX | Draft capital/asset/security allocation and embedded data | All five nonempty sheets inventoried; **Documentation only** as an intermediate duplicate superseded by final model | This inventory and final-project audit |
| `2026S_FIN5745 PM_Workbook 6. Portfolio Management Strategies_Q.xlsx` | XLSX | Index construction/tracking, active funds, taxes, equity/bond strategies, duration, immunization, swap | Previously deep-reviewed; benchmark policy comparison **Implemented differently**; option-free pricing/duration/convexity/portfolio sensitivity now **Implemented differently with explicit inputs**; tax, immunization and swap remain educational-only | `strategy.py`, `fixed_income.py`, `bond_portfolio.py`, Fixed Income, report/exports, tests |
| `2026S_FIN5745 PM_Workbook 7. Evaluation of Portfolio Performance_Q.xlsx` | XLSX | Sharpe/Treynor/Jensen, selection/allocation, Fama, fees, weighted returns, Sortino | Previously deep-reviewed; supported measures **Fully implemented and verified**; cash-flow/fee account models **Deferred** | `evaluation.py`, Performance Evaluation, report/CSV, tests |
| `Basic Investment Pf Model_Tech & SPY_Forecasting adjusted_Example-2.xlsx` | XLSX | Five-sheet example capital/asset/security model | Every sheet inventoried; **Educational companion only**, materially duplicated by final model | Internal inventory only |
| `Portfolio Management.xlsx` | XLSX | Two small formula sheets (32 formulas total) | Every nonempty sheet inventoried; **Source could not be interpreted safely** because labels/provenance are insufficient for a unique model mapping | No implementation |
| `Assignment/Portfolio_Management_Final_Assignment_Jameel_Shaikh.xlsx` | XLSX | Seven-sheet final capital/asset/security/TB/evidence model | Deep-reviewed; **Partially implemented / Implemented differently with justification** | Final audit, ETF Research, Security Analysis, Optimization, tests and exports |
| `Assignment/stock_data.xlsx` | XLSX | 60-period wide history, fundamentals and 12 security sheets | Every sheet inspected; **Documentation only** static dataset with no reproducible as-of provenance | Final audit; fixed CI fixtures are synthetic instead |
| `Assignment/etf_scanner.py` | Python | Monthly Yahoo return/risk ETF scanner and hard-coded bond composite | Deep-reviewed; return-risk logic **Implemented differently**; live import-time scanner/bond constants excluded | `etf_research.py`, ETF Research, tests/export |
| `Assignment/etf_holdings.py` | Python | Manual paste catalog of 28 ETF constituent lists | Deep-reviewed; source is not an extractor. Weighted look-through is a **Professional enhancement** requiring user disclosure | ETF Research holdings upload, tests/export |
| `Assignment/alpha_screen_short.py` | Python | Monthly excess-return alpha and mutable fundamental/analyst screen | Deep-reviewed; regression **Implemented differently with justification**; analyst-target gate excluded | `risk.py`, `etf_research.py`, Security/ETF UI, tests/report |
| `Assignment/stock_weights_optimizer.ipynb` | IPYNB | Unexecuted single-index/Treynor–Black-style weights and charts | All 13 cells inspected; **Educational companion only** due incomplete active/passive mix and inconsistent CAPM-alpha branch | Final audit; code cells compile; no copied model |
| `Assignment/portfolio_optimizer.py` | Python | Long-only price-download optimizer with synthetic fallback | Imports/functions inspected; **Implemented differently with justification** through deterministic construction module; synthetic fallback is not used in production | Existing optimizer tests/UI/report |
| `Assignment/full_market_alpha_screen.py` | Python | Statsmodels-based live ETF/security screen | Imports/functions inspected; **Deferred** broad-universe live workflow because universe/as-of data are not governed | Existing exact local screen only |
| `Assignment/treynor_black_portfolio_model.py` | Python | Large live alpha, bond and portfolio model | Imports/functions inspected; **Educational companion only / Intentionally excluded** from production | Treynor–Black scope decision and traceability |
| `Assignment/download_stock_data.py` | Python | Live Yahoo stock workbook generator with absolute Downloads path | Inspected; **Intentionally excluded** as brittle data-acquisition utility | `data.py` owns market retrieval |
| `Assignment/download_bond_data.py` | Python | Live Yahoo bond workbook generator with absolute Downloads path | Inspected; **Intentionally excluded** as brittle data-acquisition utility | Fixed Income uses no live bond-data inference |
| `Assignment/portfolio_weights.png` | PNG | Saved notebook chart | Inspected as output evidence; **Documentation only** | No model logic |
| `2026S_FIN5745 PM_Class Notes 1. Risk & Return of Portfolio Investments.pptx` | PPTX | 30-slide foundations lecture | Slide text/structure inspected; **Documentation only**, corroborates Workbook 1 | Workbook 1 mappings/tests |
| `2026S_FIN5745 PM_Class Notes 2. MW Efficient Frontier & Captial Market Line.pptx` | PPTX | 36-slide Markowitz/CML lecture | Inspected; **Documentation only**, corroborates Workbook 2 | Workbook 2 mappings/tests |
| `2026S_FIN5745 PM_Class Notes 3. Capital & Asset Classes Allocation.pptx` | PPTX | 37-slide capital/asset allocation and indifference curves | Inspected; **Documentation only**, corroborates Workbook 3 | Workbook 3 mappings/tests |
| `2026S_FIN5745 PM_Class Notes 4. Single Index Portfolio Model & Security Selection.pptx` | PPTX | 15-slide single-index/security-selection lecture | Inspected; **Documentation only**, corroborates Workbook 4 | Workbook 4 mappings/tests |
| `An Introduction to Portfolio Management_Ch06-1.pptx` | PPTX | Portfolio-management overview | Slide text inspected; **Educational companion only** | No distinct production gap |
| `Asset Allocation and Security Decision_Ch02-1.pptx` | PPTX | Asset/security allocation decisions | Slide text inspected; **Educational companion only** | No distinct production gap |
| `The Investment Settings_Ch01-1.pptx` | PPTX | Expected return, variance and SML settings | 53-slide text inspected; **Educational companion only** | Foundation/CAPM mappings |
| `Bodie_Investments_12e_PPT_CH06_Accessible-1.pptx` | PPTX | Capital allocation, utility and risk aversion | 41-slide text inspected; **Educational companion only** | Complete-portfolio methodology |
| `Bodie_Investments_12e_PPT_CH07_Accessible-1.pptx` | PPTX | Efficient diversification | 49-slide text inspected; **Educational companion only** | Diversification/optimization methodology |
| `Bodie_Investments_12e_PPT_CH08_Accessible-1.pptx` | PPTX | Index models and risk-premium estimation | 31-slide text inspected; **Educational companion only** | Single-index methodology |
| `2026S_FIN5745 PFM_Risk Aversion (Tolerance) Measure.pdf` | PDF | Blank weighted client risk questionnaire | Text inspected; **Intentionally excluded** personalized profiling | Explicit user-entered `A` only |
| `2026S_FIN5745 PFM_Risk Aversion (Tolerance) Measure JAM.pdf` | PDF | Completed risk questionnaire | Text inspected; **Intentionally excluded** personal/suitability data | No public exposure |
| `Assignment/2026S_FIN5745 PFM_Risk Aversion (Tolerance) Measure JAM.pdf` | PDF | Duplicate completed questionnaire | Text inspected; **Documentation only / duplicate** | No public exposure |
| `investment policy statement_individual investors_CFA-1.pdf` | PDF | Individual IPS guidance | Text inspected; **Educational companion only** | IPS authoring excluded |
| `investment policy statement_institutional investors_CFA-1.pdf` | PDF | Institutional IPS guidance | Text inspected; **Educational companion only** | IPS authoring excluded |
| `Investment-Policy-Statement_Simple Sample Versioin-1.pdf` | PDF | Sample individual IPS | Text inspected; **Educational companion only** | IPS authoring excluded |
| `IPS-70-Equity_30-Fixed_Wealth Management LLC-1.pdf` | PDF | Example 70/30 IPS | Text inspected; **Educational companion only** | No target recommendation |
| `InvestmentPolicy_POOLED ENDOWMENT FUNDS MARQUETTE UNIVERSITY -1.pdf` | PDF | Endowment objectives, liquidity and policy allocation | Text inspected; **Educational companion only** | Institutional/liability workflow excluded |
| `investment-policy-statement_Morgan Stanely-1.pdf` | PDF | Retirement-plan IPS template | Text inspected; **Educational companion only** | Fiduciary/plan workflow excluded |
| `investment_policy_statement_Raymond James-1.pdf` | PDF | Advisory IPS template | Text inspected; **Educational companion only** | IPS authoring excluded |
| `PF_IPS_CFA_Final.docx` | DOCX | Completed individual IPS document | Document XML/text inspected; **Documentation only**, contains personal policy material | No public exposure |
| `IMG_0102.HEIC` | HEIC | Photograph/supporting evidence | **Source could not be interpreted safely** as a financial model; no machine-readable methodology | None |
| `IMG_0131.HEIC` | HEIC | Photograph/supporting evidence | **Source could not be interpreted safely** | None |
| `IMG_0218.HEIC` | HEIC | Photograph/supporting evidence | **Source could not be interpreted safely** | None |
| `IMG_0248.HEIC` | HEIC | Photograph/supporting evidence | **Source could not be interpreted safely** | None |
| `IMG_0262.HEIC` | HEIC | Photograph/supporting evidence | **Source could not be interpreted safely** | None |

## Workbook worksheet completeness

The read-only scan found 12 XLSX files and no nonempty hidden worksheets. It inspected every nonempty sheet, formula count, chart count, table count, hidden row/column flags, defined names, external-link package parts and VBA presence. Workbooks 1–7 and the final model are traced worksheet-by-worksheet in `COURSE_TRACEABILITY.md` and `FINAL_ASSIGNMENT_AUDIT.md`. Additional sheets were:

- Workbook 2 question version: `Pf Concepts (H)`, `two Assets Pf with W`, `MW Efficient Global Pf`, `MW Optimal Pf & CML`, `three Assets Pf with W`, `EX. IPS`, `Pf Models`.
- Draft model: `Capital Allocation`, `Asset Classes Allocation`, `Security Allocation`, `Data. Securities`, `Data. Bond Duration & Convexity`.
- Basic example: the same five functional sheets.
- `stock_data.xlsx`: `All Historical (Wide)`, `Fundamentals`, and twelve security sheets (`MSFT`, `NEE`, `CRM`, `WM`, `V`, `AAPL`, `GOOGL`, `ADBE`, `LLY`, `UNH`, `NVDA`, `AVGO`).
- `Portfolio Management.xlsx`: `Sheet1`, `Sheet2`; labels were insufficient for safe unique concept attribution.

No VBA was found. Several instructional workbooks contain thousands of template defined names and 2–8 external-link parts; these are treated as template residue unless a live formula area uses them. Solver objectives and constraints are reported only where saved names made them recoverable.

## Master concept coverage matrix

| Concept family | Canonical formula/rule | Module | Public UI | Report/export | Deterministic tests | Status and limitations |
|---|---|---|---|---|---|---|
| Return/risk foundations | Simple returns; arithmetic `mean×252`; CAGR; sample `var×252`; covariance/correlation | `performance.py` | Performance, Risk | Performance/risk/asset CSV | `test_analytics.py` | **Fully implemented and verified** |
| Portfolio moments/contributions | `w'μ`, `w'Σw`; exact return contribution; Euler volatility contribution | `performance.py`, `risk.py` | Risk, Asset Allocation | Attribution and allocation exports | formula/reconciliation tests | **Fully implemented and verified** |
| Downside risk | Target downside deviation, Sortino, drawdown, empirical VaR/CVaR | `performance.py`, `risk.py` | Performance, Risk, Performance Evaluation | HTML/CSV | edge-case tests | **Fully implemented and verified** |
| Mean-variance construction | Long-only GMV, tangency, target return, efficient upper branch | `construction.py` | Portfolio Optimization | Frontier/weights/report | closed-form, brute-force and failure tests | **Fully implemented and verified** |
| CAL/complete portfolio | `rf + Sharpe_t σc`; `y=(E[rt]-rf)/(Aσt²)`, clipped 0–1 | `construction.py` | Portfolio Optimization | Report/weights | CAL/utility tests | **Implemented differently with justification**: no borrowing/leverage |
| Allocation comparison | Current/model weights, risk/return, contributions and implementation trades | shared analytics/rebalancing | Asset Allocation | HTML plus three CSV exports | AppTest/integration | **Fully implemented and verified** after this audit; no inferred asset classes |
| Explicit constraints | `Σw=1`, bounds, exclusions, target and user-defined group caps | `construction.py` | Portfolio Optimization | validation/report/CSV | feasibility/residual tests | **Fully implemented and verified** |
| Rebalancing | Buy-and-hold; calendar/threshold trades; one-way turnover; costs on trade dates | `rebalancing.py` | Portfolio Strategies | report/history/trades | schedule/cost/drift tests | **Implemented differently with justification**; not silently daily |
| Single-index model | Excess-return OLS, alpha/beta/R², residual/systematic decomposition | `risk.py` | Security Analysis | HTML and CSV | synthetic recovery/edge tests | **Fully implemented and verified** |
| CAPM/SML | `rf+β(E[Rm]-rf)`; realized minus required return | `asset_pricing.py` | Asset Pricing | HTML and CSV | zero/negative/high beta tests | **Fully implemented and verified** |
| APT/multifactor | Linear factor expected-return framework | `asset_pricing.py` | Asset Pricing framework expander | Methodology only | factor arithmetic tests | **Documentation only / Deferred**: no governed factor series |
| Strategy comparison | Lagged momentum plus rebalancing-policy paths and benchmark-relative measures | `strategy.py`, `rebalancing.py` | Portfolio Strategies | HTML/history/trades | lag/cost/active-risk tests | **Implemented differently with justification** |
| Performance evaluation | Sharpe, Sortino, Treynor, Jensen, Information Ratio, Fama selectivity, rolling metrics | `performance.py`, `risk.py`, `evaluation.py` | Performance Evaluation | HTML and CSV | formula/rolling tests | **Fully implemented and verified**; M²/Calmar unsupported by source and excluded |
| ETF research pipeline | Return-risk screen → disclosed holdings → overlap/exposure → regression screen → existing optimizer | `etf_research.py`, `risk.py`, `construction.py` | ETF Research + Portfolio Optimization | HTML and CSV | fixed end-to-end test | **Partially implemented** as connected research stages; no live holdings/universe service |
| Option-free bond analytics | Explicit cash flows; `PV`; YTM root; clean/dirty/accrual; Macaulay/modified/dollar duration; DV01; convexity; full repricing | `fixed_income.py` | Research → Fixed Income → Bond calculator | Conditional HTML and CSV | `test_fixed_income.py` pricing/risk cases | **Fully implemented and verified** for supported periodic fixed-rate and zero-coupon instruments |
| Bond portfolio and parallel-rate risk | Dirty-market-value weights; weighted duration/convexity; additive dollar duration/DV01; full repricing contributions | `bond_portfolio.py` | Bond portfolio; Rate scenarios | Conditional HTML and CSV | portfolio/scenario reconciliation | **Fully implemented and verified** for explicit holdings; no curve/spread/credit model |
| Bond selection and construction | Inclusive explicit filters; one displayed ranking formula; long-only linear constraints | `bond_portfolio.py` | Bond selection | Conditional HTML and CSV | filter/rank/constraint tests | **Implemented differently with justification**; no hard-coded score or inferred classifications |
| Professional report | Deterministic consolidation of all available analytics | `reporting.py` | Research Report | HTML + CSV package | report-content/integration tests | **Fully implemented and verified** after this audit |

## Canonical formula registry

The pure-function source of truth remains the domain module named above; this registry prevents UI/report reimplementation.

| Measure | Convention |
|---|---|
| Returns | Adjusted-price simple returns, never logarithmic |
| Arithmetic return | Periodic sample mean × `TRADING_DAYS=252` |
| Geometric/CAGR | Compound observed simple returns; CAGR is not an optimizer input |
| Variance/covariance | Sample (`ddof=1`) daily estimate × 252 |
| Volatility | Square root of annualized variance; annualized once |
| Sharpe | `(arithmetic annual return−annual rf)/annual volatility` |
| Sortino | Arithmetic excess-return numerator over annualized target downside deviation |
| Beta/regression alpha | Aligned daily excess-return OLS; beta slope, intercept ×252 |
| Residual volatility | Regression residual sample standard deviation × `sqrt(252)` |
| CAPM/Jensen/Treynor | Same annual arithmetic return, benchmark premium and risk-free rate |
| Tracking error/Information Ratio | Sample SD of aligned active daily returns × `sqrt(252)`; arithmetic active return / TE |
| Portfolio moments | `w'μ`, `w'Σw`; labeled weights must reconcile |
| Contributions | Exact compounded return attribution; Euler volatility contribution sums to portfolio volatility |
| VaR/CVaR | Nonnegative empirical 95% loss measures |
| Turnover/cost | One-way turnover = half gross trade / pre-trade value; gross traded notional × cost rate |
| Drift | Actual pre-trade weight minus explicit target weight |
| Bond price/yield | Explicit periodic cash flows; dirty PV at nominal annual YTM compounded by frequency; clean = dirty − accrued; bracketed clean-price YTM root |
| Bond rate risk | Macaulay/modified/dollar duration; DV01 = dollar duration × 0.0001; standard discrete convexity; full repricing at shocked YTM |
| Bond portfolio | Dirty-market-value weights; weighted duration/convexity; additive dollar duration/DV01; weighted YTM labeled descriptive, not portfolio IRR |

## Product-stitching findings

- **Fixed:** added a discoverable Asset Allocation workspace rather than leaving allocation comparison scattered across Risk, Optimization and rebalancing.
- **Fixed:** the HTML report now includes performance evaluation, security regression, CAPM/asset pricing, ETF universe research and security-screen tables; matching CSV exports are available.
- **Preserved:** one analytics pipeline creates aligned simple returns; UI/report code consumes domain outputs rather than recalculating formulas.
- **Preserved:** SPX remains the display benchmark while `^GSPC` is retrieval-only; unknown equity tickers are not silently mapped.
- **Fixed:** fifteen peer tabs were regrouped into six laptop-width primary workspaces. Fixed Income is a Research secondary view and does not add another primary item.
- **No formula conflict found:** performance and optimizer Sharpe share the arithmetic convention; CAGR stays separate; covariance, risk-free rate and annualization are not independently recomputed in the new surfaces.

## Unresolved ambiguities

- Five HEIC photographs contain no safely machine-readable financial model and require manual visual interpretation if they are intended as substantive evidence.
- `Portfolio Management.xlsx` lacks sufficient labels/provenance for unique mapping.
- Template external links and thousands of defined names do not establish active methodology by themselves.
- Saved Solver names do not prove the exact sequence of historical Solver runs or manual overrides.
- Static holdings/fundamental data lack authoritative as-of/source metadata; live production ingestion remains deferred.
- IPS and risk-questionnaire materials support professional governance concepts but do not authorize personalized policy generation in PortfolioLens.

## Evidence-based assessment

PortfolioLens remains **substantially covered**, not fully covered. Standard option-free fixed-income pricing, portfolio rate risk, selection and constrained construction are now covered with explicit inputs. Full coverage is still not claimed because immunization/liability matching, key-rate duration, curve construction, credit/default/recovery, embedded options, tax and swap workflows remain unsupported; some source artifacts are educational-only or ambiguous, and five photographs plus one weakly labeled workbook cannot be interpreted safely.
