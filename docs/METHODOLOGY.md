# Methodology and limitations

## Data and returns

The data source is yfinance adjusted close, falling back to its close field only when adjusted close is absent from the response. The portfolio and benchmark are fetched separately. Each requested holding must be available; analysis never silently drops a symbol. Holding prices are inner-aligned on complete common trading dates, and no prices are filled or invented. Benchmark comparisons use a further inner alignment.

Daily return is the simple return `r_t = P_t / P_(t-1) - 1`. Portfolio return assumes constant target weights: `r_p,t = Σ w_i r_i,t`. This describes a daily rebalanced analytical portfolio and does not claim to reproduce an un-rebalanced brokerage account.

## Performance

- Total return: `Π(1+r_t)-1`
- CAGR: `(Π(1+r_t))^(252/n)-1`
- Annualized volatility: sample standard deviation of daily returns times `sqrt(252)`
- Sharpe: `(CAGR - annual risk-free rate) / annualized volatility`
- Sortino: `(CAGR - annual risk-free rate) / annualized target downside deviation`; the annual risk-free rate is converted to an equivalent daily minimum acceptable return, and every observation contributes either its squared shortfall or zero
- Drawdown: wealth divided by its running peak minus one, with the initial portfolio value included as the first peak
- Calmar: CAGR divided by the absolute maximum drawdown

The risk-free input is annual and is not converted into a daily cash return. It is used in annualized ratios only. A 252-trading-day convention is used throughout.

## Risk and benchmark comparison

Historical 95% VaR is reported as a nonnegative loss magnitude at the empirical fifth percentile. Historical 95% CVaR is the nonnegative magnitude of mean returns at or below that percentile. If the observed lower tail contains gains rather than losses, the reported loss measure is zero. These are backward-looking one-day statistics and can understate unseen tail events.

Beta is sample covariance of portfolio and benchmark daily returns divided by benchmark daily variance. Tracking error is the annualized sample standard deviation of active daily returns. Information ratio is annualized mean active return divided by tracking error. Relative drawdown is computed from portfolio wealth divided by benchmark wealth.

## Attribution and concentration

Return contribution allocates each day's weighted asset return through the prior day's portfolio wealth. Summing all assets and dates therefore reconciles exactly to portfolio total return under the constant-weight return model.

For annualized covariance matrix `Σ`, weights `w`, and portfolio volatility `σ_p = sqrt(w′Σw)`, asset `i` volatility contribution is `w_i(Σw)_i / σ_p`. Euler homogeneity makes contributions sum to `σ_p`, including negative contributions where covariance makes an asset a hedge.

Weight concentration is shown directly and through effective number of holdings `1 / Σw_i²`.

## Construction and rebalancing

Equal weights allocate `1/N`. Inverse-volatility weights are proportional to `1/σ_i`. Minimum variance minimizes `w′Σw`; maximum Sharpe maximizes historical arithmetic annualized excess return divided by portfolio volatility. Both optimized methods constrain every weight to `[0,1]` and the sum to one. A failed solver result is never displayed as valid. Historical inputs are estimates, not forecasts, and “maximum Sharpe” names the mathematical objective rather than a recommendation.

Rebalancing assumes the stated portfolio value, no cash flow, fractional trading, and no taxes. Estimated trade is target dollars minus current dollars. Buys and sells reconcile before costs and rounding. By default, only an exactly unchanged weight is labeled Hold; callers may opt into a display threshold, which changes the action label but not the disclosed target-allocation gap.

## Momentum strategy

The strategy operates on the first requested holding so the traded instrument is explicit. It is long when the short simple moving average is above the long simple moving average and otherwise in cash. A signal observed at close on day `t` becomes the position for day `t+1`; the signal is shifted one full period to avoid look-ahead bias. Before both averages exist, the strategy remains in cash. Performance comparison begins only after the long-window warm-up, so strategy and buy-and-hold use the same evaluation period. Proportional transaction cost is deducted on each absolute position change. The MVP does not search or optimize parameters.

Positive active-day rate is the fraction of in-market daily returns above zero. Daily-return profit factor is the sum of positive in-market daily returns divided by the absolute sum of negative in-market daily returns. Turnover is the sum of absolute position changes, and position changes count entries and exits separately. These definitions are intentionally simple and are not trade-level round-trip analytics.

## Stress tests

Custom shocks are explicit per-asset instantaneous percentage shocks; the application does not infer asset classes or silently replace a missing shock with zero. Portfolio impact is `Σw_i s_i`. Historical windows and exact configured dates live in `portfolio_dashboard/config.py`. A window is shown only when the selected common history covers both endpoints, and the displayed result includes the actual first and last trading dates used. Historical portfolio returns use the same daily constant-weight method as the main analysis.

The downloadable report uses the actual common-price analysis dates, the currently edited custom shocks, and the rebalancing method currently selected in the application. Percentage, currency, count, and unitless ratio fields are formatted according to their metric definitions.

## General limitations and disclaimer

Historical data may contain provider errors and do not predict future performance. The system excludes taxes, liquidity and position-size limits, financing, corporate-action edge cases, market impact, and slippage beyond the configured proportional cost. It has no live execution, authentication, persistence, or intraday data. For research and educational use only; not personalized financial advice.
