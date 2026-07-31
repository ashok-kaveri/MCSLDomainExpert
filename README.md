# MCSL Domain Expert

Streamlit-based QA orchestration for the Shopify Multi-Carrier Shipping Label app.

This repo follows the FedEx workflow shape where that improves QA throughput, but all reasoning, validation, and execution stay MCSL-native.

## What This App Does

The dashboard helps QA move a release through these stages:
1. load Trello release cards
2. validate and refine AC
3. generate and publish test cases
4. run AI QA verification
5. generate or update automation
6. run automation, post results, generate docs, and raise bugs
7. prepare sign-off and handoff output

Entrypoint:
- [pipeline_dashboard.py](pipeline_dashboard.py:1)

## Current Dashboard Tabs

Top-level tabs:
1. `📝 User Story`
2. `🔀 Move Cards`
3. `🧾 Validate AC`
4. `🧪 Generate TC`
5. `🤖 AI QA Verifier`
6. `⚙️ Generate Automation Script`
7. `📋 History`
8. `✅ Sign Off`
9. `📘 Handoff Docs`

Planned next major workflow:
- `🚚 New Carrier Validation`
  - create store
  - install app
  - manual carrier registration checkpoint
  - create required Shopify products
  - generate carrier env file with product IDs
  - run smoke / sanity / regression
  - publish readiness report

## Current QA Flow

Shared release state is loaded in `🧾 Validate AC` and reused in downstream tabs.
QA can narrow the loaded cards before `Load Cards`, then adjust the active-card subset from any pipeline tab without reloading the Trello list.

## Codex / Claude Skill Bundle

Repo-local MCSL skills live under [skills](skills:1). They mirror the FedEx Domain Expert skill pipeline but use MCSL-native app paths, evidence rules, automation repo paths, labels, and support-doc structure.

Core cycle:
1. `mcsl-domain-core`
2. `mcsl-trello-operator`
3. `mcsl-ac-writer-reviewer`
4. `mcsl-dashboard-tc-publisher`
5. `mcsl-ai-qa-testcase-prep`
6. `mcsl-ai-qa-browser`
7. `mcsl-automation-writer`
8. `mcsl-bug`
9. `mcsl-signoff-message`
10. `mcsl-handoff-docs`

Maintenance and external workflow helpers:
- `mcsl-rag-sync`
- `mcsl-knowledge-maintainer`
- `mcsl-slack-operator`

When dashboard behavior changes materially, update the matching skill alongside [AGENTS.md](AGENTS.md:1) and this README.

### `🧾 Validate AC`
- select Trello board, list, and release label
- optionally select a subset of cards from the chosen list
- click `Load Cards`
- auto-run per-card MCSL validation and diagnosis
- auto-run release-level `Release Intelligence`
- show `Step 1: Card Requirements`
- run MCSL-specific toggle/store-state handling when needed
- generate or review `AI Suggested User Story & AC`
- save, comment, skip, or share AC
- run `Domain Validation`
- apply fixes and re-validate

Important current behavior:
- there is no separate manual `Analyze loaded cards` step
- active-card subset editing stays available after load across Validate AC, Generate TC, AI QA, and Automation
- generated AC is revalidated immediately
- fix and revalidate preserve requirement research context

### `🧪 Generate TC`
- generate test cases from the current AC draft in session
- reuse saved TCs when present
- regenerate with reviewer feedback
- support manual edits and explicit re-review
- share to Slack DM or channel
- publish full QA summary to Trello
- publish positive TCs to Google Sheets
- perform duplicate checks before sheet write

Important current behavior:
- TC generation does not rely only on stale `card.desc` when a newer AC draft exists
- retry after partial publish failure should not duplicate the Trello summary comment

### `🤖 AI QA Verifier`
- runs TC-first AI QA against the live app
- uses the current Shopify/MCSL browser flow by default; if a card names WooCommerce, BigCommerce, Magento, or PrestaShop, ask QA first and run it only when QA confirms the shared MCSL behavior should be tested through the available flow
- reuses generated and reviewed test cases
- normalizes navigation wording to MCSL destinations such as `orders`, `appproducts`, `shippingrates`, and `automation`
- uses existing automation page-object patterns for iframe navigation, Order Id filtering, Actions menu, request logs, label generation, and document checks
- supports `qa_needed` follow-up and reruns
- supports failed-finding review and notify-dev flow
- supports ask-domain-expert
- persists final approval for downstream automation and sign-off

### `⚙️ Generate Automation Script`
- `① Write Automation Code`
- current Playwright generation targets the Shopify MCSL automation repo only
- cards explicitly scoped to WooCommerce, BigCommerce, Magento, or PrestaShop should not generate automation yet
- detect existing-vs-new automation targets with `feature_detector` and `find_pom`
- optional Chrome-agent exploration for locator grounding
- auto-fix loop for generated code
- `② Run Automation & Post to Slack`
- `③ Generate Documentation`
- `🐛 Bug Reporter` for manual QA-found bugs

## MCSL-Specific Rules

### Validation And Analysis

These stay MCSL-native:
- `validate_card(...)`
- `diagnose_customer_ticket(...)`
- `analyse_release(...)`
- `build_requirement_research_context(...)`

FedEx parity work should change workflow shape and UX order, not replace MCSL rules with FedEx rules.

### Toggle Flow

MCSL toggle handling is intentionally different from FedEx.

Current behavior:
- detect toggle details from card title, description, and comments
- derive default store and app URL from MCSL carrier knowledge
- capture live store and toggle state from the app when QA refreshes it
- extract `store_uuid`, `account_uuid`, and toggle state from app or API responses
- compute missing-vs-enabled toggles before notifying
- notify Ashok or the assigned developer through Slack
- poll for confirmation and unblock QA when confirmed

Key files:
- [pipeline/toggle_state.py](pipeline/toggle_state.py:1)
- [tests/test_toggle_state.py](tests/test_toggle_state.py:1)

### Automation Matching

Automation generation should prefer updating existing MCSL automation when a matching area already exists.

Key files:
- [pipeline/automation_writer.py](pipeline/automation_writer.py:1)
- [pipeline/feature_detector.py](pipeline/feature_detector.py:1)

## Important Files

- [pipeline_dashboard.py](pipeline_dashboard.py:1)
- [pipeline/card_processor.py](pipeline/card_processor.py:1)
- [pipeline/smart_ac_verifier.py](pipeline/smart_ac_verifier.py:1)
- [pipeline/domain_validator.py](pipeline/domain_validator.py:1)
- [pipeline/automation_writer.py](pipeline/automation_writer.py:1)
- [pipeline/feature_detector.py](pipeline/feature_detector.py:1)
- [pipeline/doc_generator.py](pipeline/doc_generator.py:1)
- [pipeline/bug_tracker.py](pipeline/bug_tracker.py:1)
- [pipeline/request_expectations.py](pipeline/request_expectations.py:1)
- [pipeline/carrier_knowledge.py](pipeline/carrier_knowledge.py:1)

## Local References

Expected local comparison repo:
- `../Fed-Ex-automation/FedexDomainExpert`

Expected local automation repo:
- `config.MCSL_AUTOMATION_REPO_PATH`

## Run Locally

```bash
cd "$MCSL_REPO"  # path to your MCSLDomainExpert clone
PYTHONPATH=. .venv/bin/streamlit run pipeline_dashboard.py
```

## Slack QA Bot

Ask QA questions from Slack and get answers in-thread. Backed by
`pipeline/slack_qa_bot.py` (Socket Mode daemon), `pipeline/qa_question_router.py`
(routing), and `pipeline/qa_metrics.py` (deterministic counts).

The bot answers only when **explicitly addressed**, so multiple domain-expert bots
(MCSL, FedEx, AUPost) can share a channel without all of them replying:
- **DM** the bot — every DM is answered.
- **@mention** the app in a channel (real Slack mention → `app_mention`, routed only
  to this app).
- **Trigger keyword** in an allowlisted channel (`SLACK_QA_CHANNELS`), e.g.
  `@mcslbot how many cases ran?`. Keywords come from `SLACK_QA_TRIGGERS`
  (default `mcslbot`); a leading `@` is optional. Un-addressed chatter is ignored.

It can also **generate MCSL support guides** (PDF) from Trello:
- `@mcslbot generate support guide for <card url/id>` → one card → PDF
- `@mcslbot generate support guide for lane "<name>"` → one combined PDF
- `@mcslbot generate per-card support guides for lane "<name>"` → one PDF per card

Routing:
- Metric intents → exact counts (no LLM). e.g. *"how many cases automated"* →
  spec/`test()` counts; *"how many cases ran in the release"* → latest
  `reports/ai-summary.json` from the automation repo.
- Support-guide intents → Trello fetch + `handoff_docs` PDF (needs `files:write` scope + `reportlab`).
- Everything else → RAG over **both** the wiki/KB collection and the
  automation/code collection.

> To make the real autocomplete mention read `@mcslBot`, rename the app's bot user
> in Slack (App → **App Home** → *Edit* the display name / default username). The
> `SLACK_QA_TRIGGERS` keyword works regardless of the app's display name.

### One-time Slack app setup

1. **Socket Mode** → enable → create an **App-Level Token** with `connections:write`
   → put it in `.env` as `SLACK_APP_TOKEN=xapp-...`.
2. **Event Subscriptions** → subscribe to bot events: `app_mention`, `message.im`,
   and `message.groups` (private channels) / `message.channels` (public channels).
3. **OAuth scopes**: `app_mentions:read`, `chat:write`, `im:history`, `im:read`,
   `im:write`, and `groups:history` (for private channels) / `channels:history`
   (for public). Reinstall the app if you add scopes. Invite the bot to the channel.

### Env

```bash
SLACK_BOT_TOKEN=xoxb-...                 # already used by the rest of the app
SLACK_APP_TOKEN=xapp-...                 # Socket Mode app-level token
SLACK_QA_CHANNELS=qa_members_internal    # optional; comma-separated names or IDs
SLACK_QA_TRIGGERS=mcslbot                 # optional; channel address keyword(s), default 'mcslbot'
```

### Run

```bash
scripts/run_slack_bot.sh --check    # verify tokens/config
scripts/run_slack_bot.sh            # start the daemon (leave running)
```

## Focused Validation Commands

```bash
python3 -m py_compile pipeline_dashboard.py pipeline/card_processor.py
pytest -q tests/test_dashboard.py::test_dash01_scaffold
pytest -q tests/test_dashboard.py::test_ui10b_validate_ac_matches_fedex_auto_analysis_flow
pytest -q tests/test_dashboard.py::test_ui10c_generate_tc_uses_current_ac_and_avoids_duplicate_trello_publish
pytest -q tests/test_toggle_state.py
pytest -q tests/test_qa_question_router.py
```

## Supporting Docs

- [CLAUDE.md](CLAUDE.md:1)
- [docs/FEDEX_FLOW_PARITY_NOTES.md](docs/FEDEX_FLOW_PARITY_NOTES.md:1)
- [docs/MCSL_PLATFORM_ADAPTATION_PLAN.md](docs/MCSL_PLATFORM_ADAPTATION_PLAN.md:1)
- [docs/MCSL_CARRIER_KNOWLEDGE_RESEARCH.md](docs/MCSL_CARRIER_KNOWLEDGE_RESEARCH.md:1)
- [docs/MCSL_CARRIER_SUPPORT_REGISTRY.md](docs/MCSL_CARRIER_SUPPORT_REGISTRY.md:1)
- [docs/MCSL_CARRIER_CAPABILITY_MATRIX.md](docs/MCSL_CARRIER_CAPABILITY_MATRIX.md:1)
- [docs/MCSL_CARRIER_REQUEST_REGISTRY.md](docs/MCSL_CARRIER_REQUEST_REGISTRY.md:1)
- [docs/NEW_CARRIER_VALIDATION_PLAN.md](docs/NEW_CARRIER_VALIDATION_PLAN.md:1)
