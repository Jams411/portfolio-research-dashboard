# Streamlit Community Cloud deployment

This checklist covers the supported deployment path for the Portfolio Research Dashboard. A hosted deployment is not considered complete until its public URL has been opened in a signed-out browser and the workflow below has passed.

## 1. Prerequisites

- A GitHub account with access to `Jams411/portfolio-research-dashboard`
- A Streamlit Community Cloud account connected to GitHub
- The repository pushed to a clean `main` branch
- Python 3.11 selected where the Cloud runtime offers a version choice

No API keys, secrets, database, paid services, or system packages are required.

## 2. GitHub repository requirements

The repository must contain `app.py`, `requirements.txt`, the `portfolio_dashboard/` package, and `.streamlit/config.toml`. Do not commit `.venv`, downloaded prices, generated reports, caches, or `.streamlit/secrets.toml`.

Before deployment:

```bash
git status --short
git rev-list --left-right --count origin/main...main
.venv/bin/pytest -q
```

Expected: a clean status, `0 0`, and a passing test suite.

## 3. Community Cloud setup

1. Sign in at [share.streamlit.io](https://share.streamlit.io/).
2. Select **Create app** and **Deploy a public app from GitHub**.
3. Authorize the Streamlit GitHub application if prompted.
4. Choose the repository and settings below.

## 4. Repository and branch

- Repository: `Jams411/portfolio-research-dashboard`
- Branch: `main`

## 5. Entry file

Set the main file path to `app.py`. Do not use a local absolute path.

## 6. Dependencies

Community Cloud installs the bounded Python packages in `requirements.txt`. The project has no `packages.txt` because it requires no operating-system dependencies. Choose Python 3.11 if the advanced settings expose a runtime selector. `runtime.txt` is intentionally omitted because it is not required by this deployment path.

## 7. Expected startup behavior

The landing page loads without downloading market data. It explains the workflow and waits for **Run analysis**. yfinance is contacted only after the user submits validated inputs.

## 8. Common failures

- **Module not found:** Confirm the deployment root is the repository root and `requirements.txt` is present.
- **Unsupported Streamlit API:** Reboot the app so the current bounded requirements are installed.
- **Ticker download failure:** Retry later or use liquid ETF tickers; yfinance availability is external to the app.
- **Private or authorization screen:** Confirm the app is public and the Streamlit GitHub application can read the repository.
- **Resource limit or slow first run:** Use the demo date range and four-ticker sample; cached downloads speed later runs.

## 9. Troubleshooting

Open **Manage app → Logs** and find the first Python exception. Reproduce it locally with the same Python version and requirements. Do not add credentials or suppress broad exceptions. If a dependency resolution fails, validate with a fresh virtual environment before changing version bounds.

## 10. Post-deployment verification

In a signed-out browser:

1. Open the hosted URL and confirm no login is required.
2. Run `SPY, QQQ, TLT, GLD` with weights `35, 30, 20, 15`, benchmark `VTI`, dates `2020-01-01` to `2025-12-31`, $100,000, 4% risk-free rate, 0.10% transaction cost, and 50/200 moving averages.
3. Open all nine analysis tabs.
4. Verify the risk-contribution and total-return reconciliation captions.
5. Download the rebalancing, strategy, stress, performance, asset, and returns CSVs plus the HTML report.
6. Confirm the methodology disclaimer is visible and no browser console or application-log error appears.

Only after this check should the verified hosted URL be added to the README and GitHub repository homepage.
