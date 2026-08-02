# Streamlit Community Cloud deployment

This checklist covers the supported deployment path for PortfolioLens. A hosted deployment is not considered complete until its public URL has been opened in a signed-out browser and the workflow below has passed.

Current verified application URL: [portfolio-lens.streamlit.app](https://portfolio-lens.streamlit.app/)

The PortfolioLens deployment moved to its verified product-aligned URL on 2026-08-02. Repository links and automated health checks must use this canonical address.

## 1. Prerequisites

- A GitHub account with access to `Jams411/portfoliolens`
- A Streamlit Community Cloud account connected to GitHub
- The repository pushed to a clean `main` branch
- Python 3.11 selected where the Cloud runtime offers a version choice

No API keys, secrets, database, paid services, or system packages are required.

## Automated independent verification

Two GitHub Actions workflows separate code verification from hosted-service health:

- `.github/workflows/ci.yml` runs on pushes and pull requests involving `main`, plus manual dispatch. It installs Python 3.11 dependencies, runs all pytest tests, compiles/imports the application, validates Streamlit configuration, exercises the entrypoint through non-socket `AppTest`, validates local Markdown targets, and runs `git diff --check`.
- `.github/workflows/deployment-health.yml` runs after pushes to `main`, once daily at 07:17 UTC, and manually. It follows ordinary redirects with a 15-second request timeout and reports a successful response, recognized Streamlit authentication redirect, DNS failure, timeout, server error, or other HTTP/connection failure in the Actions job summary.

An authentication redirect is a successful reachability observation, not proof that the public application rendered. DNS, timeout, and server failures fail the health workflow but must be investigated as operational evidence before being attributed to application code. Neither workflow uses credentials.

Run and inspect the workflows manually with:

```bash
gh workflow run ci.yml --ref main
gh workflow run deployment-health.yml --ref main
gh run list --workflow ci.yml --limit 5
gh run list --workflow deployment-health.yml --limit 5
gh run view RUN_ID --log
```

Some managed coding environments, including Codex/Herdr, reject local socket binding with `PermissionError: [Errno 1] Operation not permitted`. This is a sandbox policy outside the application process. Do not change Streamlit server code, ports, or financial behavior to work around it; use `AppTest` and GitHub Actions instead.

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

- Repository: `Jams411/portfoliolens`
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
2. Run `SPY, QQQ, TLT, GLD` with weights `35, 30, 20, 15`, benchmark `VTI`, dates `2020-01-01` to `2025-12-31`, $100,000, 4% risk-free rate, 0.10% transaction cost, 5% drift threshold, and 50/200 moving averages.
3. Open all ten analysis tabs.
4. Verify the risk-contribution and total-return reconciliation captions.
5. Verify the efficient frontier/GMV/tangency/CAL, construct a feasible target-return portfolio, run one constrained allocation, and inspect the validation summary.
6. Compare buy-and-hold, monthly, quarterly, annual, and threshold policies; download daily policy and trade histories.
7. Download strategy, stress, performance, asset, comparison, frontier, policy, insight, and returns CSVs plus the HTML report.
8. Confirm the methodology disclaimer is visible and no browser console or application-log error appears.

Only after this check should the verified hosted URL be added to the README and GitHub repository homepage.

## 11. Browser-test limitation

A Playwright deployment test is intentionally not installed. The current endpoint can redirect anonymous clients through Streamlit authentication, which makes a title assertion dependent on external account and visibility state. The lightweight health workflow records that redirect without credentials; the signed-out checklist above remains the authoritative UI-level deployment test until the endpoint consistently serves the public page directly.
