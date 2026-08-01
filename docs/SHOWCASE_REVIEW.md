# Showcase review — 2026-07-31

The app was reviewed locally at a 1512×862 browser viewport using `SPY, QQQ, TLT, GLD`, weights `35, 30, 20, 15`, benchmark `VTI`, and the settings in [DEMO_GUIDE.md](DEMO_GUIDE.md).

## Findings

| Severity | Location | Observed behavior | Expected behavior | Resolution |
|---|---|---|---|---|
| Medium | Sidebar | Strategy parameters occupied persistent vertical space while reviewing unrelated analytics. | Secondary controls should remain available without crowding the primary workflow. | Moved the two controls into a native collapsed expander. |
| Medium | All populated views | The educational-use limitation was available only on the methodology tab. | A concise scope reminder should remain visible during analysis and screenshots. | Added a global historical-research, constant-weight, non-advice caption. |
| Medium | Theme and captures | Rendering inherited the viewer’s light/dark preference, reducing screenshot consistency across machines. | Deployment and showcase captures should have a predictable, readable native theme. | Added a minimal native Streamlit light theme; no custom CSS. |
| Medium | Navigation | Nine tab labels form a dense row and may require horizontal scrolling at narrow widths. | Every section must remain reachable without obscuring content. | Verified Streamlit’s responsive tab scrolling; no architectural navigation rewrite was justified for this phase. |
| Low | Local startup | Streamlit recommends optional Watchdog tooling on macOS. | App should launch without required local-only packages. | No change; Watchdog is an optional development optimization and is not needed on Community Cloud. |
| Deployment blocker | Hosted URL | The candidate Streamlit URL redirected to authentication during review. | A public hosted URL must load in a signed-out browser. | Unresolved pending Streamlit account authorization/public deployment verification; no hosted-link claim was added. |

## Functional results

The realistic portfolio completed all nine tabs with 1,507 common adjusted-price observations. Return attribution reconciled to portfolio total return, volatility contributions were displayed with the Euler formula, historical stress windows appeared only when fully covered, and the HTML report download event completed. No Critical or High defects and no financial-calculation regression were observed during the review.

## Deferred visual change

Replacing tabs with multipage navigation could reduce horizontal density, but it would alter the application structure and demonstration flow without fixing a failed interaction. It is intentionally deferred rather than treated as cosmetic preference.
