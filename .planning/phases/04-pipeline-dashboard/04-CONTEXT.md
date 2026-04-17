# Phase 4: Pipeline Dashboard - Context

**Gathered:** 2026-04-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Build the Streamlit Pipeline Dashboard that orchestrates Trello → AC writing → AI QA Agent → report. The dashboard is the user-facing control surface — QA engineers interact with it instead of the terminal.

</domain>

<decisions>
## Implementation Decisions

### UI Design — LOCKED
- **Modern, polished UI** — must NOT look like a default Streamlit app. The user explicitly requires modern components and good colours.
- Use a **custom CSS theme** injected via `st.markdown(..., unsafe_allow_html=True)` or `.streamlit/config.toml`
- Colour palette: dark sidebar + rich accent colours (not Streamlit's default grey/red). Suggested: deep navy/charcoal base, teal/green accents for pass, red for fail, amber for partial, blue for qa_needed
- Cards for scenario results — not raw text dumps. Each scenario result rendered as a styled card with a coloured verdict badge
- Pass/fail/partial/qa_needed shown as **coloured pill badges**, not plain text
- Progress bar should be styled (colour matches running state — blue while running, green on complete, red on error)
- Screenshot thumbnails shown inline in the report, expandable on click
- Sidebar for configuration (carrier, headless mode, max scenarios)
- Logo/branding in the header — "MCSL Domain Expert" with a clean title treatment
- Use `st.columns`, `st.expander`, `st.tabs` for layout structure — not just vertical stacking

### Threading — LOCKED
- Background `threading.Thread` for AI QA Agent run
- Session state keys: `sav_running`, `sav_stop` (threading.Event), `sav_result`, `sav_prog`
- Worker thread writes to session_state dict keys directly (never calls st.* from thread)
- Main thread polls with `time.sleep(0.5) + st.rerun()` during active run
- Stop button uses `on_click` callback — not conditional `if st.button()` — to avoid race condition

### card_processor.py — LOCKED
- Must be created in Phase 4 (does not exist yet)
- Contract: `get_ac_text(trello_card_url: str) -> tuple[str, str]` (ac_text, card_name)
- Trello API fetch with graceful fallback to `("", "")` if credentials missing
- Dashboard shows manual AC paste textarea if Trello fetch fails

### Report Display — LOCKED
- Consume `VerificationReport.to_dict()` output (already designed for Phase 4)
- Per-scenario cards with: verdict badge, finding text, screenshot thumbnail
- Summary header: total scenarios, pass count, fail count, duration

### Claude's Discretion
- Exact colour hex values (within the dark/teal/green/red palette constraint)
- Component layout pixel details
- Whether to use streamlit-extras or custom CSS only
- Exact Trello API endpoint (cards/{id}?fields=desc,name)

</decisions>

<specifics>
## Specific Ideas

- Dark theme base: `#0f1117` background (Streamlit dark), accent `#00d4aa` (teal-green)
- Verdict badges: `#22c55e` pass, `#ef4444` fail, `#f59e0b` partial, `#3b82f6` qa_needed
- Scenario result card: white card on dark bg with left border coloured by verdict
- The dashboard file lives at `pipeline_dashboard.py` (project root level for easy `streamlit run`)

</specifics>

<deferred>
## Deferred Ideas

- Trello webhook for real-time card updates
- Multi-card batch runs
- Playwright test auto-generation from verified scenarios (ADV-01, v2)

</deferred>

---
*Phase: 04-pipeline-dashboard*
*Context gathered: 2026-04-16*
