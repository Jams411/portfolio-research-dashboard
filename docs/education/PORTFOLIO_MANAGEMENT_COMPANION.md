# Portfolio Management educational companion

This companion explains course-supported concepts that help interpret PortfolioLens or are better kept outside the production interface. All examples are deterministic and self-contained. Nothing here is personalized investment advice, a forecast, or a production implementation of an advanced classroom model.

## Source map

| Topic | Course source | PortfolioLens disposition |
|---|---|---|
| Two-asset return, variance, covariance, and diversification | `2026S_FIN5745 PM_Workbook 1. Risk & Return of Portfolio Investments_Q.xlsx`; `2026S_FIN5745 PM_Class Notes 1. Risk & Return of Portfolio Investments.pptx` | Core formulas implemented; derivation retained here |
| Efficient frontier, GMV, tangency, and CAL/CML intuition | `2026S_FIN5745 PM_Workbook 2. MW Efficient Frontier & Capital Market Line_Q.xlsx` and `_A.xlsx`; `2026S_FIN5745 PM_Class Notes 2. MW Efficient Frontier & Captial Market Line.pptx` | Long-only implementation in the app; intuition retained here |
| CAPM and single-index interpretation | `2026S_FIN5745 PM_Workbook 4. Securities Selection & Single Index Model _Q.xlsx`; `2026S_FIN5745 PM_Workbook 5-1. CAPM, APT & Multifactor Models_Q.xlsx`; corresponding Class Notes 4 | Single-index/CAPM metrics implemented; interpretation retained here |
| Treynor–Black, APT, and multifactor overview | `2026S_FIN5745 PM_Workbook 5-1. CAPM, APT & Multifactor Models_Q.xlsx`; `Assignment/treynor_black_portfolio_model.py` | Educational-only; intentionally excluded from the app |

## Two-asset portfolio mathematics

For weights `w_A` and `w_B=1-w_A`, arithmetic expected returns `μ_A, μ_B`, volatilities `σ_A, σ_B`, and correlation `ρ_AB`:

`E[r_p] = w_A μ_A + w_B μ_B`

`Var(r_p) = w_A²σ_A² + w_B²σ_B² + 2w_Aw_Bρ_ABσ_Aσ_B`

The covariance term explains why portfolio volatility is generally not the weighted average of asset volatilities. Correlation below one can reduce portfolio variance; negative correlation can reduce it further. Diversification changes risk, not the arithmetic weighted-return identity.

Deterministic example:

- `w_A=60%`, `w_B=40%`
- `μ_A=8%`, `μ_B=4%`
- `σ_A=15%`, `σ_B=7%`, `ρ_AB=0.20`
- Expected return: `0.60×8% + 0.40×4% = 6.40%`
- Variance: `0.60²×0.15² + 0.40²×0.07² + 2×0.60×0.40×0.20×0.15×0.07 = 0.009892`
- Volatility: `sqrt(0.009892) ≈ 9.95%`

PortfolioLens generalizes this to many assets with `E[r_p]=w′μ` and `Var(r_p)=w′Σw`.

## Efficient-frontier intuition

For a target arithmetic return, a frontier portfolio minimizes `w′Σw` while satisfying the target and budget constraints. The global minimum-variance portfolio is the feasible portfolio with the lowest variance regardless of return. Only the upper branch from GMV toward higher expected return is efficient: below-GMV portfolios can have the same or greater risk with lower expected return.

PortfolioLens adds long-only bounds `0≤w_i≤1`. Therefore its numerical frontier is a constrained historical frontier, not the unconstrained closed-form curve sometimes derived in class. Historical means and covariances are estimates, so the frontier can move substantially when the sample changes.

## Tangency portfolio and Capital Allocation Line

With risk-free rate `r_f`, a risky portfolio has Sharpe ratio `(E[r_p]-r_f)/σ_p`. The tangency portfolio maximizes that slope. PortfolioLens’s “Maximum Sharpe” is the constrained historical tangency estimate because short selling is prohibited.

For fraction `y` in the tangency portfolio and `1-y` in the risk-free asset:

- `E[r_c] = r_f + y(E[r_T]-r_f)`
- `σ_c = yσ_T`

If `r_f=3%`, `E[r_T]=9%`, `σ_T=12%`, and `y=50%`, then expected return is `6%` and volatility is `6%`. PortfolioLens restricts `0≤y≤1`; it does not draw the borrowing/leverage extension beyond the tangency portfolio.

## CAPM and single-index interpretation

CAPM required return is `r_f + β(E[r_m]-r_f)`. For `r_f=3%`, `β=1.2`, and market expected return `9%`, required return is `10.2%`. Jensen’s alpha compares portfolio arithmetic return with that required return.

The excess-return single-index regression is `r_p-r_f = α + β(r_m-r_f) + ε`.

- Beta is fitted benchmark sensitivity, not a complete description of risk.
- R² is the fraction of sample variation explained by the benchmark factor, not performance quality.
- Residual/idiosyncratic variation is the portion left by this one-factor model.
- Alpha is sample- and benchmark-dependent; it is not proof of manager skill or a forecast.

## Treynor–Black overview — educational only

Treynor–Black combines an indexed passive portfolio with an actively selected portfolio based on estimated alphas and residual risk. Its outputs are highly sensitive to alpha forecasts, residual-variance estimates, security selection, and implementation constraints. The course materials support understanding the framework, but PortfolioLens does not have a defensible alpha-forecasting process or the data controls needed to present it as a production allocation. It therefore remains educational-only.

## APT and multifactor overview — educational only

APT and multifactor models explain returns using more than one systematic factor. A general form is `r_i = α_i + β_i1F_1 + … + β_ikF_k + ε_i`. A production feature would require approved factor definitions, trustworthy aligned factor data, frequency conventions, exposure interpretation, and stability diagnostics. Those inputs are outside the focused PortfolioLens data boundary, so the app retains its transparent single-index model.

## Intentionally excluded live workflows

- Short selling, leverage, and risk-free borrowing
- Treynor–Black allocation
- APT and multifactor regression
- Bond immunization, swaps, and other fixed-income instrument workflows
- Tax-lot optimization
- Monte Carlo portfolio clouds
- Risk parity described as course-derived functionality

These exclusions prevent incomplete classroom templates or unsupported data assumptions from appearing as production research features.
