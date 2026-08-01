# Changelog

User-facing and methodology changes are grouped by repository milestone. This project has no Git version tags yet, so commit-backed milestone names are used instead of invented version numbers.

## Unreleased

### Added

- Added a Community Cloud deployment checklist, timed interview demo guide, final showcase review, and eight live-application screenshots.

### Changed

- Renamed the product from Portfolio Research Dashboard to PortfolioLens, with the subtitle “Multi-Asset Portfolio Analytics & Investment Research”; product scope and financial methodology are unchanged.
- Collapsed secondary momentum controls, added a persistent research-only scope reminder, and established a native Streamlit showcase theme without changing analytics.
- Replaced the light showcase theme with a high-contrast native dark financial theme and made Streamlit theme inheritance explicit for Plotly charts.
- Expanded the README with a screenshot gallery, deployment status, architecture links, demonstration guidance, and the evidence-labeled project story.

### Fixed

- Equal-weight mode now ignores disabled manual weights and constructs `1/N` directly.
- Manual values such as `50,35,15` are converted once to decimal weights with accurate sum validation.
- Input changes and failed runs now remove prior metrics, charts, reports, and exports instead of displaying stale analysis.

### Documentation

- Added permanent project history, decision, roadmap, changelog, and documentation-governance records.
- Added a chronological engineering journal and living architecture reference with verified module contracts and system diagrams.
- Reinforced documentation rules for product-direction, architecture, methodology, course-derived work, and coding-agent changes.

## Dashboard hardening — 2026-07-31

Commits: `a080c52`, `33ed9f0`, `f74a683`

### Added

- Offline Streamlit entrypoint smoke tests.
- Strategy warm-up and common strategy/buy-and-hold evaluation period.
- Actual trading dates for historical stress windows.
- Semantic percentage, ratio, count, and currency formatting for reports.

### Changed

- Reports now use the active custom shocks, selected rebalancing method, and actual aligned analysis dates.
- Optional allocation failures now produce individual warnings instead of aborting all construction results.
- Historical stress uses the same constant-weight daily return model as the main analysis.
- Streamlit navigation uses state-aware lazy tab rendering and bounded market-data caching.

### Fixed

- Included initial wealth when calculating portfolio and relative drawdowns.
- Reported historical VaR and CVaR as nonnegative loss magnitudes.
- Corrected target downside-deviation handling in Sortino.
- Rejected insufficient momentum history instead of returning a silent all-cash result.
- Required one explicit finite shock for every holding.
- Prevented invalid or nonconverged optimizer output from being shown as valid.
- Corrected report and UI units for percentages and unitless ratios.

### Documentation

- Updated methodology for drawdown, tail risk, Sortino, optimization failure, strategy warm-up, stress assumptions, and report state.

## Initial application — 2026-07-31

Commit: `c3cd9c6`

### Added

- Streamlit controls, tabbed analysis workflow, charts, tables, and downloads.
- README with purpose, architecture, installation, testing, deployment, limitations, and interview explanation.
- Methodology and limitations guide.
- Repository ignore rules.

## Core analytics engine — 2026-07-31

Commit: `3b7ed4d`

### Added

- Validated adjusted-price loading and common-date alignment.
- Portfolio performance, risk, benchmark, attribution, construction, optimization, rebalancing, strategy, stress, reporting, and formatting modules.
- Deterministic synthetic unit and integration tests.
- Bounded Python dependencies and pytest configuration.
