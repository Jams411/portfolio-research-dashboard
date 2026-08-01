# Project history

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
