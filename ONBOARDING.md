# MCSL Domain Expert — Onboarding

QA orchestration for the PluginHive **Multi-Carrier Shipping Label (MCSL)** Shopify app. It takes a
Trello release card and carries it to shipped: acceptance criteria, test cases, verification against
the live app, automation, sign-off, and the support handoff PDF.

This guide gets you productive. [README.md](README.md) is the command reference once you are.

---

## 1. The one-paragraph version

A Trello release card goes in. Claude writes the acceptance criteria and test cases from that card
plus real context — the codebase, carrier knowledge, past approved cards. An agentic browser layer
then verifies those test cases against the live MCSL app, and out come automation scripts, a QA
sign-off message, and a release support guide PDF.

What makes this repo different from the FedEx sibling is **carriers, plural**. MCSL fronts many of
them, so a large part of the platform exists to reason about carrier differences: what each carrier
supports, what its requests look like, and whether a brand-new carrier is ready to ship.

---

## 2. Read this before you change anything

From [CLAUDE.md](CLAUDE.md) — the repo's own standing rule, and the one that matters most here:

> Reuse the FedEx workflow *shape* where it helps QA flow. Keep validation, diagnosis, automation
> targeting, and request reasoning **MCSL-native**. Do not copy FedEx navigation assumptions into
> MCSL. Do not replace MCSL rules with FedEx rules.

The two repos look alike on purpose, and that similarity is a trap. Workflow structure ports across;
navigation, carrier behaviour, and request expectations do not. Prefer the dashboard code over the
older planning notes in `docs/` whenever they disagree.

---

## 3. Mental model

```
        Trello release card
                │
                ▼
   ┌────────────────────────────────────────────────┐
   │  pipeline_dashboard.py  (Streamlit, 10 tabs)   │
   │                                                │
   │  Validate AC → Generate TC → AI QA Verifier →  │
   │  Generate Automation → Sign Off → Handoff Docs │
   │                                                │
   │  ┌──────────────────────────────────────────┐  │
   │  │ 🚚 New Carrier Validation                │  │
   │  │    onboard a carrier end to end          │  │
   │  └──────────────────────────────────────────┘  │
   └───────────────┬────────────────────────────────┘
                   │  leans on
      ┌────────────┼─────────────┬──────────────────┐
      ▼            ▼             ▼                  ▼
  RAG knowledge  Carrier      Live toggle       Slack QA bot
  (ChromaDB)     registries   state             (QA in Slack)
```

Shared release state lives in Streamlit session and is reused across tabs — board, list, release
label, loaded cards, validations, diagnoses, release analysis, AC drafts, test cases, AI QA reports,
approvals, automation outputs. Don't duplicate it per tab.

### The dashboard tabs

`📝 User Story` · `🔀 Move Cards` · `🧾 Validate AC` · `🧪 Generate TC` · `🤖 AI QA Verifier` ·
`⚙️ Generate Automation Script` · `📋 History` · `✅ Sign Off` · `📘 Handoff Docs` ·
`🚚 New Carrier Validation`

The four in the middle — Validate AC, Generate TC, AI QA Verifier, Generate Automation Script — are
the release path, and `CLAUDE.md` asks you to keep that split unless told otherwise.

---

## 4. Get it running

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

There is **no `.env.example` in this repo** — create `.env` yourself. `config.py` reads:
`ANTHROPIC_API_KEY`, `CLAUDE_SONNET_MODEL`, `CLAUDE_HAIKU_MODEL`, `DOMAIN_EXPERT_MODEL`,
`OLLAMA_BASE_URL`, `EMBEDDING_MODEL`, plus `STORE`, `SHOPIFY_ACCESS_TOKEN` and
`SHOPIFY_API_VERSION` for store actions. Trello and Slack credentials are read where they're used —
grep for `getenv` if something comes back empty. The Slack QA bot also wants `SLACK_APP_TOKEN`
(see `README.md`).

```bash
PYTHONPATH=. .venv/bin/streamlit run pipeline_dashboard.py
```

Two things to note, because they differ from the sibling repos:

- **The dashboard entrypoint is at the repo root**, not under `ui/`.
- **`PYTHONPATH=.` is not optional** — modules import each other as top-level packages.

---

## 5. Where things live

```
pipeline_dashboard.py     the dashboard — repo root, not ui/
pipeline/
  smart_ac_verifier.py      agentic browser verification
  card_processor.py         AC writer + test case generator
  carrier_knowledge.py      what each carrier supports
  carrier_request_registry.py   what each carrier's requests look like
  request_expectations.py   expected request shape per scenario
  new_carrier_validation.py     the New Carrier Validation flow
  new_carrier_onboarding.py     store + app + product provisioning
  new_carrier_runner.py         smoke / sanity / regression runs
  toggle_state.py           live toggle state (store_uuid, account_uuid)
  ticket_diagnoser.py       diagnose a customer ticket
  locator_knowledge.py      automation locator memory
  qa_metrics.py             QA throughput metrics
  slack_qa_bot.py           QA from inside Slack
  handoff_docs.py           support guide / business brief + PDF renderer
  trello_client.py · slack_client.py · sheets_writer.py
rag/          vectorstore.py · chain.py · code_indexer.py · prompts.py
ingest/       knowledge ingestion
skills/       15 mcsl-* Claude Code skills — the CLI half of the product
docs/         carrier registries + adaptation plans (see below)
config.py     settings, env-driven
```

### The skills are half the product

`skills/` holds 15 Claude Code skills that do the same jobs from the terminal: `mcsl-domain-core`,
`mcsl-ac-writer-reviewer`, `mcsl-ai-qa-testcase-prep`, `mcsl-ai-qa-browser`, `mcsl-automation-writer`,
`mcsl-handoff-docs`, `mcsl-toggle-enable-list`, `mcsl-signoff-message`, `mcsl-bug`,
`mcsl-trello-operator`, `mcsl-slack-operator`, `mcsl-shopify-store-actions`,
`mcsl-dashboard-tc-publisher`, `mcsl-rag-sync`, `mcsl-knowledge-maintainer`.

They encode house rules — read the `SKILL.md` before hand-rolling the same job. `mcsl-handoff-docs`
is the most rule-dense.

### The carrier docs are load-bearing

`docs/` is not just history here. When carrier reasoning changes, `CLAUDE.md` asks you to update
`MCSL_CARRIER_KNOWLEDGE_RESEARCH.md`, `MCSL_CARRIER_SUPPORT_REGISTRY.md`,
`MCSL_CARRIER_CAPABILITY_MATRIX.md`, and `MCSL_CARRIER_REQUEST_REGISTRY.md`. Treat them as part of
the code.

---

## 6. Things that will bite you

**Toggles: live state wins.** The toggle flow captures live `store_uuid`, `account_uuid`, and toggle
state from the app or API responses, and computes enabled vs missing from that. If you touch it, keep
live state as the source of truth — do not regress to store-name-only logic.

**New Carrier Validation does not create orders.** The automation repo already creates them from
env-backed product IDs. What this flow provisions is *products*, populating `SIMPLE_PRODUCTS_JSON`,
`VARIABLE_PRODUCTS_JSON`, `DIGITAL_PRODUCTS_JSON` and `DANGEROUS_PRODUCTS_JSON` from deterministic
templates — not a random catalog. The flow also stops deliberately for manual carrier registration.

**There are vendored dependency shims in the repo root.** `streamlit.py`, `langchain_anthropic/`,
`langchain_core/`, `langchain_chroma/`, `langchain_ollama/`, `langchain_text_splitters/`, `chromadb/`
exist for local test and import stability. They look like stray junk. They are not — don't delete
them without checking test coverage and `.venv` behaviour first.

**Don't import FedEx navigation.** Worth repeating, because it is the single easiest mistake to make
in this repo. See section 2.

---

## 7. Housekeeping worth knowing

- **`CLAUDE.md` and `AGENTS.md` are near-duplicates** — the same project context for Claude and for
  Codex. Update both, or they drift.
- **Planning notes vs reality:** `docs/FEDEX_FLOW_PARITY_NOTES.md` and
  `docs/MCSL_PLATFORM_ADAPTATION_PLAN.md` describe intent. The dashboard code is the truth.

---

## 8. First week suggestions

1. Open the dashboard and walk **Validate AC → Generate TC** on a real past release list. Don't run
   the browser verifier yet — compare the generated AC and TCs against the Trello card.
2. Read `pipeline/carrier_knowledge.py` and the carrier registry docs together. Carrier reasoning is
   the thing that makes this repo MCSL rather than a FedEx clone.
3. Read one skill end to end. `mcsl-handoff-docs` is the best single window into the house rules.
4. Generate a support guide for an already-shipped release and diff it against the committed one in
   `data/handoff_docs/`. You'll learn the conventions faster from the diff than from the docs.
5. Only then run the AI QA Verifier on a single test case, reading `pipeline/smart_ac_verifier.py`
   alongside it.
