# Methodology and limitations

## Data and returns

The data source is yfinance adjusted close, falling back to its close field only when adjusted close is absent from the response. The portfolio and benchmark are fetched separately. Each requested holding must be available; analysis never silently drops a symbol. Holding prices are inner-aligned on complete common trading dates, and no prices are filled or invented. Benchmark comparisons use a further inner alignment.

Daily return is the simple return `r_t = P_t / P_(t-1) - 1`. Portfolio return assumes constant target weights: `r_p,t = Σ w_i r_i,t`. This describes a daily rebalanced analytical portfolio and does not claim to reproduce an un-rebalanced brokerage account.

## Performance

- Total return: `Π(1+r_t)-1`
- Historical arithmetic annualized return: `252 × mean(r_t)`; this is the historical expected-return estimate used by Sharpe, Sortino, and maximum-Sharpe optimization
- CAGR: `(Π(1+r_t))^(252/n)-1`
- Annualized variance: sample variance of daily returns times `252`
- Annualized volatility: sample standard deviation of daily returns times `sqrt(252)`

### Portfolio Management Workbook 1 — Risk & Return of Portfolio Investments

The explicit holding-period-return helper follows the workbook relationship
`HPR = (ending value - beginning value + cash income) / beginning value`. The
live market pipeline uses simple adjusted-price returns, `P_t/P_(t-1)-1`;
because adjusted prices embed distributions, separately adding those same
distributions would double count income. Log returns are not used.

Periodic arithmetic mean is `sum(r_t)/n`. Periodic geometric mean is
`[product(1+r_t)]^(1/n)-1`; CAGR is the same compound path annualized as
`[product(1+r_t)]^(252/n)-1`. The app labels arithmetic annualized return as a
historical expected-return estimate and CAGR as realized compound growth.

Workbook probability tables and short finite exercises use population
variance, `sum[p_s(r_s-E[r])^2]`, or Excel `VAR.P`/`STDEV.P`. PortfolioLens does
not silently carry that classroom convention into observed market estimation:
historical asset variance, covariance, and correlation use sample estimators
(`ddof=1`) because the observations estimate an unknown return distribution.
Annualized covariance is daily sample covariance times 252; annualized
portfolio variance is `w'Σw` and volatility is its square root. This convention
is explicitly labeled in the UI and exports.

Coefficient of variation is the unitless relationship `CV=σ/E[r]`, computed
with annualized volatility and annualized arithmetic expected return so its
numerator and denominator share a horizon. It is undefined at zero expected
return; negative expected returns produce mathematically valid negative values
whose rankings require care.

The displayed diversification reduction is
`sum(w_i σ_i) - sqrt(w'Σw)` for long-only weights. The percentage divides that
gap by weighted standalone volatility. It describes the effect of observed
cross-asset covariance; it is neither a forecast nor a systematic-risk measure.
Return and Euler volatility contributions remain separate reconciled analyses.
- Performance Sharpe: `(historical arithmetic annualized return - annual risk-free rate) / annualized volatility`
- Optimizer Sharpe: the same arithmetic annualized excess-return formula evaluated for candidate weights; it is mathematically identical to performance Sharpe for the same return series and weights
- Sortino: `(historical arithmetic annualized return - annual risk-free rate) / annualized target downside deviation`; the annual risk-free rate is converted to an equivalent daily minimum acceptable return, and every observation contributes either its squared shortfall or zero
- Drawdown: wealth divided by its running peak minus one, with the initial portfolio value included as the first peak
- Calmar: CAGR divided by the absolute maximum drawdown

Arithmetic return and CAGR answer different questions. Arithmetic annualized return is a historical mean estimate suitable for one-period mean-variance comparisons; CAGR is the realized compound growth rate over the selected path. Neither is presented as a forecast. The annual risk-free input is subtracted from annualized ratio numerators. For Sortino's downside target only, it is converted to an equivalent daily rate. A 252-trading-day convention is used throughout.

## Risk and benchmark comparison

Historical 95% VaR is reported as a nonnegative loss magnitude at the empirical fifth percentile. Historical 95% CVaR is the nonnegative magnitude of mean returns at or below that percentile. If the observed lower tail contains gains rather than losses, the reported loss measure is zero. These are backward-looking one-day statistics and can understate unseen tail events.

Active daily return is `r_p,t-r_m,t`. Annualized Active Return is `252 × mean(r_p,t-r_m,t)` and Tracking Error is `std(r_p,t-r_m,t, ddof=1) × sqrt(252)`. Information Ratio is Annualized Active Return divided by Tracking Error. The separately labeled cumulative Excess Return is portfolio total return minus benchmark total return over the selected path; it is not the Information Ratio numerator. Relative drawdown is computed from portfolio wealth divided by benchmark wealth.

The single-index model uses the same aligned daily observations and regresses portfolio excess return on benchmark excess return:

`r_p,t - r_f,t = α_t + β(r_m,t - r_f,t) + ε_t`

The annual risk-free input is divided by `252` for this arithmetic daily model. OLS beta is `Cov(r_p-r_f, r_m-r_f) / Var(r_m-r_f)`, daily intercept is the mean portfolio excess return minus beta times mean benchmark excess return, and regression alpha is `252 × α_t`. R² is `1-SSE/SST`. Residual volatility is the residual standard error `std(ε, ddof=2) × sqrt(252)` because an intercept and slope are estimated.

Systematic variance is `β² Var(r_m-r_f) × 252`; idiosyncratic variance is `Var(ε, ddof=1) × 252`. Their displayed risk shares divide each component by their sum and therefore reconcile to 100%. Residual volatility and idiosyncratic variance intentionally use different degrees of freedom: the former estimates regression error volatility, while the latter is the sample variance component needed for exact historical variance decomposition.

CAPM required return is `r_f + β(E[r_m]-r_f)`, using arithmetic annualized benchmark return. Jensen's alpha is `E[r_p] - CAPM required return`; under these shared arithmetic conventions it reconciles to annualized regression alpha. Treynor ratio is `(E[r_p]-r_f)/β` and is unavailable when beta is effectively zero. These historical estimates are highly sample- and benchmark-dependent; alpha is not a forecast or proof of manager skill, R² is not a measure of performance quality, and low idiosyncratic risk is not inherently preferable.

## Attribution and concentration

Return contribution allocates each day's weighted asset return through the prior day's portfolio wealth. Summing all assets and dates therefore reconciles exactly to portfolio total return under the constant-weight return model.

For annualized covariance matrix `Σ`, weights `w`, and portfolio volatility `σ_p = sqrt(w′Σw)`, asset `i` volatility contribution is `w_i(Σw)_i / σ_p`. Euler homogeneity makes contributions sum to `σ_p`, including negative contributions where covariance makes an asset a hedge.

Weight concentration is shown directly and through effective number of holdings `1 / Σw_i²`.

## Construction and rebalancing

Manual UI weights may be entered as percentage points (for example `50,35,15`) or decimal weights (`0.50,0.35,0.15`) and are converted to decimal weights exactly once. Equal-weight mode ignores the disabled manual field and constructs `1/N` directly from the validated ticker count.

Equal weights allocate `1/N`. Inverse-volatility weights are proportional to `1/σ_i`. For arithmetic annualized asset-return vector `μ`, annualized sample covariance matrix `Σ`, and weights `w`, portfolio expected return is `w′μ` and portfolio variance is `w′Σw`; volatility is `sqrt(w′Σw)`. Minimum variance minimizes `w′Σw`. Maximum Sharpe maximizes `(w′μ-r_f)/sqrt(w′Σw)`, using the same Sharpe formula as the displayed scorecard. Both optimized methods constrain every weight to `[0,1]` and the sum to one. A failed solver result is never displayed as valid. Historical inputs are estimates, not forecasts, and “maximum Sharpe” names the mathematical objective rather than a recommendation.

The long-only efficient frontier is the upper mean-variance branch from the global minimum-variance portfolio to the highest-return individual asset in the sample. For evenly spaced arithmetic target returns on that branch, PortfolioLens minimizes `w′Σw` subject to `w′μ = μ_target`, `Σw_i = 1`, and `0 ≤ w_i ≤ 1`. Targets outside the minimum-to-maximum individual-asset return range are rejected as infeasible. The displayed constrained tangency portfolio is the long-only maximum-Sharpe solution. The Capital Allocation Line is `E[r_c] = r_f + y(E[r_T]-r_f)` and `σ_c = yσ_T` for risky allocation `0 ≤ y ≤ 1`; it stops at the tangency portfolio and therefore assumes lending but no borrowing or leverage.

### Portfolio Management Workbook 2 — Mean-Variance Efficient Frontier & Capital Market Line

Workbook 2 separates two optimization conventions. Its global-frontier worksheet minimizes portfolio standard deviation for a specified target mean using weights bounded from 0 to 1, weights summing to one, and an exact target-return equality. Its optimal-risky-portfolio worksheet instead maximizes an excess-return Sharpe ratio with only a sum-to-one constraint; saved negative weights confirm that this classroom tangency model permits short sales. PortfolioLens intentionally uses the first worksheet's long-only convention for GMV, target-return, frontier, and maximum-Sharpe construction. Therefore its tangency estimate will not reproduce the workbook's unconstrained country-index weights.

The workbook expresses its CML in excess-return space as `risk premium = σ_c × Sharpe_T`, with the risk-free intercept implicit. PortfolioLens displays the equivalent total-return CAL, `E[r_c]=r_f+y(E[r_T]-r_f)`, and `σ_c=yσ_T`. A complete portfolio allocates `y` to the long-only tangency portfolio and `1-y` to the risk-free asset. The UI restricts `0≤y≤1`: lending is supported, but the workbook's illustrated borrowing region (`y>1`) remains educational-only because PortfolioLens does not enable leverage.

Workbook expected returns, standard deviations, correlations, covariances, and excess returns are entered assumptions with no recoverable source period or annualization process. PortfolioLens instead estimates arithmetic annual returns and annualized sample covariance from aligned daily adjusted-price returns. Realized CAGR remains separate. The risk-free input is annual and is subtracted from arithmetic expected return for Sharpe; optimized results are historical estimates, not forecasts or recommendations.

The workbook mentions expected utility, diminishing marginal utility, and risk aversion but provides no risk-aversion coefficient, quadratic utility formula, indifference-curve calculation, or Solver model for optimal complete-portfolio selection. PortfolioLens therefore does not manufacture a utility optimizer from this source.

Custom constrained construction retains `Σw_i=1` and long-only weights while allowing explicit user-entered asset minimums and maximums, exclusions represented by a zero maximum, and group caps `Σ(i in group)w_i ≤ cap_group`. Group membership is never inferred: users must enter labels and matching caps. A linear feasibility program first verifies the complete constraint set; only a feasible point is passed to the nonlinear minimum-variance, maximum-Sharpe, or target-return optimizer. The validation table reports every minimum, maximum, group cap, sum result, pass/fail outcome, breach magnitude, and affected asset. Maximum-volatility constraints are not implemented because approved course traceability does not establish them as a required stable feature.

Optimizer expected return is the arithmetic historical estimate `w′μ`, optimizer volatility is `sqrt(w′Σw)`, and optimizer Sharpe is `(w′μ-r_f)/sqrt(w′Σw)`. Realized CAGR remains the compound growth of the observed return path and is not used as an optimizer input. Frontier points and optimized weights are shown with restrained display precision, and all solver failures or infeasible targets are surfaced rather than silently replaced.

Rebalancing assumes the stated portfolio value, no cash flow, fractional trading, and no taxes. Estimated trade is target dollars minus current dollars. Buys and sells reconcile before costs and rounding. By default, only an exactly unchanged weight is labeled Hold; callers may opt into a display threshold, which changes the action label but not the disclosed target-allocation gap.

The rebalancing simulator is path-dependent and distinct from the main constant-weight analytical portfolio. It initializes dollar holdings at target weights, applies each asset’s daily return to its own holding, calculates pre-trade drift, and trades only when the selected policy triggers. Monthly, quarterly, and annual policies trade after the last available trading observation of a completed calendar period; the final sample date is not treated as a scheduled rebalance because no subsequent holding period remains. Threshold policy trades when any absolute asset-weight drift reaches the user’s band. Buy and hold never trades.

At a trigger, pre-cost trade for asset `i` is `target weight_i × gross portfolio value - holding_i`. These trades sum to zero before costs. Gross traded notional is `Σ|trade_i|`; displayed one-way turnover is `0.5 × gross traded notional / pre-trade portfolio value`; estimated cost is `cost rate × gross traded notional`. Cost is deducted once, only on a triggered trade, and remaining value is allocated to target weights. Daily net return links prior post-trade value to current post-trade value, so the compounded return path reconciles to portfolio value. The simulator assumes fractional trading and excludes taxes, bid/ask spreads beyond the configured proportional rate, liquidity limits, cash flows, and market impact.

## Research workspace and Portfolio Health Score

Portfolio comparison evaluates every available allocation method on the same aligned asset-return history, annual risk-free rate, constant-weight portfolio-return model, and performance formulas. The displayed weight distance from current is `0.5 × Σ|w_scenario,i - w_current,i|`. It describes allocation difference only; it is not realized turnover, a trade-cost estimate, or a rebalance simulation.

The Portfolio Health Score is an application-specific historical diagnostic, not a formula copied from the Portfolio Management course. It is a bounded weighted average of five disclosed components:

| Component | Weight | Normalized rule |
|---|---:|---|
| Diversification | 25% | `effective holdings / number of holdings` |
| Risk-adjusted return | 25% | Sharpe linearly mapped from `-1 → 0%` to `2 → 100%` |
| Drawdown resilience | 20% | `1 - abs(maximum drawdown) / 50%` |
| Tail resilience | 15% | `1 - daily historical 95% CVaR / 10%` |
| Benchmark efficiency | 15% | information ratio linearly mapped from `-1 → 0%` to `1 → 100%` |

Every normalized result is clipped to `[0,1]`. If a metric is unavailable, its component is excluded and the remaining weighted points are rescaled to 100; metric coverage is always displayed. Formally, `score = Σ(weight_i × normalized_i) / Σ(available weight_i)`. The thresholds are transparent presentation choices, not universal investment standards. The score does not measure suitability, forecast return, diversification across unobserved risk factors, or portfolio optimality.

What-if analysis accepts hypothetical nonnegative weights that must sum to 100% and one explicit finite shock per holding. Historical comparison uses the same constant-weight formulas as the main analysis. Instantaneous shock impact is `Σw_i s_i`, and the scenario does not overwrite the analyzed portfolio, simulate a rebalance path, or include taxes, market impact, and trading costs.

Deterministic insights are selected by fixed rules using computed Sharpe, cumulative excess return, maximum drawdown, largest weight, effective holdings, beta, idiosyncratic risk share, Euler volatility contribution, and CVaR. The interface displays the supporting metric, value, and rule beside every observation. No LLM or generative model creates, ranks, or rewrites insights, and the statements do not instruct users to buy, sell, or change an allocation.

## Momentum strategy

The strategy operates on the first requested holding so the traded instrument is explicit. It is long when the short simple moving average is above the long simple moving average and otherwise in cash. A signal observed at close on day `t` becomes the position for day `t+1`; the signal is shifted one full period to avoid look-ahead bias. Before both averages exist, the strategy remains in cash. Performance comparison begins only after the long-window warm-up, so strategy and buy-and-hold use the same evaluation period. Proportional transaction cost is deducted on each absolute position change. The MVP does not search or optimize parameters.

Positive active-day rate is the fraction of in-market daily returns above zero. Daily-return profit factor is the sum of positive in-market daily returns divided by the absolute sum of negative in-market daily returns. Turnover is the sum of absolute position changes, and position changes count entries and exits separately. These definitions are intentionally simple and are not trade-level round-trip analytics.

## Stress tests

Custom shocks are explicit per-asset instantaneous percentage shocks; the application does not infer asset classes or silently replace a missing shock with zero. Portfolio impact is `Σw_i s_i`. Historical windows and exact configured dates live in `portfolio_dashboard/config.py`. A window is shown only when the selected common history covers both endpoints, and the displayed result includes the actual first and last trading dates used. Historical portfolio returns use the same daily constant-weight method as the main analysis.

The downloadable report uses the actual common-price analysis dates, the currently edited custom shocks, and the rebalancing method currently selected in the application. Percentage, currency, count, and unitless ratio fields are formatted according to their metric definitions.

## General limitations and disclaimer

Historical data may contain provider errors and do not predict future performance. The system excludes taxes, liquidity and position-size limits, financing, corporate-action edge cases, market impact, and slippage beyond the configured proportional cost. It has no live execution, authentication, persistence, or intraday data. For research and educational use only; not personalized financial advice.
