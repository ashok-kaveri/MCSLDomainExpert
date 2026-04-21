# CLAUDE.md

Project notes for future Claude/Codex work in this repo.

## Product Context

This project is the MCSL version of the FedEx Domain Expert platform.

Do not copy FedEx app navigation.
Do copy the FedEx workflow pattern where it makes sense:
- Trello-driven release flow
- AC generation and validation
- TC generation and review
- AI QA verification
- approval and sign-off
- automation writing support

## Current QA Tab Split

The old single `Release QA` tab has been replaced with:

1. `🧾 Validate AC`
2. `🧪 Generate TC`
3. `🤖 AI QA Verifier`
4. `⚙️ Generate Automation Script`

Keep this split unless the user explicitly asks to change it.

Shared release state is stored in Streamlit session and reused across the four tabs:
- board
- list
- release label
- loaded cards
- validations
- test cases
- AI QA reports
- approvals

## MCSL Toggle Rules

FedEx toggle flow is not enough for MCSL.

Current implementation:
- detect toggle names from card description, title, and comments
- auto-read store name from automation config if available
- notify Ashok or developer via Slack
- allow reply polling and escalation

Required MCSL direction:
- read `storeUUID` and `accountUUID` from the MCSL home/orders API
- read `/toggles` API to determine actual toggle state
- prefer UUID-based toggle notification payloads over only store URL/store name

If touching toggle flow, keep the current Slack/escalation behavior but move the payload toward live API-derived identifiers.

## AI QA Rules

Use automation for:
- navigation
- locators
- shared repeated flows

Use codebase + wiki + KB + carrier registries for:
- expectation building
- request/response reasoning
- setup guidance

Do not reduce AI QA back to AC-only execution.
Keep TC-first verification as the default path.

Current important AI QA features already in place:
- parsed TC execution
- preflight setup macros
- learned locator memory
- automation-locator-first lookup
- expectation matching against captured logs

## Docs To Keep Updated

When changing workflow or architecture, update:
- `README.md`
- `CLAUDE.md`
- `docs/FEDEX_FLOW_PARITY_NOTES.md`
- `docs/MCSL_PLATFORM_ADAPTATION_PLAN.md`

Update carrier docs too when carrier knowledge changes:
- `docs/MCSL_CARRIER_SUPPORT_REGISTRY.md`
- `docs/MCSL_CARRIER_CAPABILITY_MATRIX.md`
- `docs/MCSL_CARRIER_REQUEST_REGISTRY.md`

If KB-facing docs change, remember they may need re-ingest later.

## Runtime Notes

- Python env is pinned via `.python-version`
- Streamlit entrypoint is `pipeline_dashboard.py`
- automation repo path comes from `config.MCSL_AUTOMATION_REPO_PATH`
- many flows depend on Trello, Slack, Sheets, and local automation code being configured

## Known Next Improvement

Most important open MCSL-specific gap:
- derive toggle/store identity from live MCSL APIs:
  - `storeUUID`
  - `accountUUID`
  - `/toggles` status

That should be implemented before calling the toggle flow fully complete.
