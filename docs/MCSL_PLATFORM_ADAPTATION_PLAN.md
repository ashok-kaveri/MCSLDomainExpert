# MCSL Domain Expert Adaptation Plan

## Goal

Adapt the FedEx-style AI QA platform pattern to the MCSL (Multi-Carrier Shipping Label) app without copying FedEx navigation.

FedEx and MCSL should share:
- workflow stages
- Trello movement flow
- AC and TC generation flow
- AI QA execution pattern
- automation-writing assistance
- sign-off and release support

MCSL must differ in:
- domain knowledge
- app navigation
- prerequisite planning
- supported carrier coverage
- Shopify verification flow
- multi-source troubleshooting and code-aware reasoning
- toggle deployment context

## Current Implementation Status

The current repo is no longer at planning-only stage. The following pieces are already implemented:

- split QA workflow tabs:
  - `🧾 Validate AC`
  - `🧪 Generate TC`
  - `🤖 AI QA Verifier`
  - `⚙️ Generate Automation Script`
- FedEx-style AC save/comment/skip/share actions
- domain validation with fix/revalidate loop
- TC review and regeneration loop
- TC-first AI QA execution
- failed-finding review and dev notification
- test-case publish and final approval to Trello + Sheets + RAG
- release-level automation generation, run, and Slack posting
- handoff docs generation
- carrier knowledge registry and carrier request registry
- locator learning and locator memory
- AI QA request/response expectation matching

So the remaining work is refinement and MCSL-specific depth, not first-pass platform construction.

---

## What Already Exists In This Repo

The current repo already has the base platform pieces:
- RAG ingestion for KB, wiki, sheets, app code, automation code
- domain expert chat
- user story writer
- domain validator
- Trello client
- AI QA verifier scaffold
- Streamlit pipeline dashboard
- automation writer scaffolding

This means the main task is adaptation and extension, not a full rebuild.

---

## Confirmed MCSL Operating Model

Based on the current MCSL repo, your notes, and the `mcsl-test-automation` project:

### Entry and auth

- MCSL testing starts from Shopify admin, not from many direct app URLs.
- Shopify auth should reuse saved browser auth first.
- If auth is missing, setup login must run first.
- The automation repo already follows this pattern with `auth-{browser}.json` and `support/setup/login.setup.ts`.

### Core MCSL navigation

- MCSL is a Shopify embedded app with internal navigation.
- Main tabs include `ORDER`, `LABELS`, `PICKUP`, plus hamburger-menu flows.
- Important internal areas include:
  - carrier setup
  - automation rules
  - packaging settings
  - request logs
  - product settings
  - order summary

### Ordering model

- Most test scenarios can use Shopify API order creation.
- API order creation depends on `product_id` and `variant_id`.
- If the agent creates a new Shopify product, it must fetch and store the new `product_id` and `variant_id` for later ordering.
- Shopify storefront ordering is still needed for some rate and automation-rule scenarios.

### Shopify verification model

- Shopify Orders URL is used for post-fulfillment verification.
- Shopify Products URL is used when a new product must be created.
- After MCSL fulfillment, the agent should verify Shopify fulfillment status and tracking number behavior where relevant.

### Log verification model

- Rate request and label request validation should follow the same idea as the FedEx flow, but using MCSL request-log paths and MCSL-specific automation helpers.
- The automation repo confirms request-log validation patterns in `tests/automationRules/...`.

---

## Required MCSL-Specific Capability Expansion

The final MCSL domain expert should support all of the following:

### 1. Product/domain expertise

It should know:
- all major MCSL features
- all supported carriers
- carrier onboarding/configuration paths
- packaging methods
- automation rules
- request log and label log verification
- fulfillment and tracking behavior
- order flows
- pickup flows
- special services
- customs/commercial invoice behavior
- Shopify sync behavior

### 2. Support and troubleshooting expertise

It should answer:
- what the customer issue likely is
- what feature or config causes it
- which logs or settings should be checked
- whether the issue is likely data, config, code, or carrier-side

This requires more than KB ingestion. It needs support-ticket style knowledge and troubleshooting patterns.

### 3. Code-aware issue analysis

Given a customer problem or requirement, it should be able to:
- search MCSL frontend/backend code
- search automation code
- identify likely impacted module/flow
- explain probable root cause or risky area

### 4. Requirement-to-delivery workflow

It should:
- turn raw request into user story
- generate acceptance criteria
- validate AC against domain truth
- generate test cases
- help create or update Trello cards
- assign cards to developers
- move cards through Dev -> QA -> Release-style lists

### 5. AI QA agent execution

For a selected test case, the AI QA agent should:
- ask the domain expert for prerequisites
- prepare product/settings/carrier data
- create or locate order data
- navigate the MCSL app correctly
- verify label/rate/log behavior
- verify Shopify fulfillment/tracking when required
- capture evidence

### 6. QA automation support

It should:
- generate automation candidates from approved TCs
- help write Playwright automation in MCSL style
- help write manual test cases
- add TC details to Trello
- add TC details to sheets when needed

---

## Current Gaps In The MCSL Repo

### Gap 1: Prompting is still too narrow

Current prompts assume a simplified MCSL view:
- limited navigation assumptions
- no support-ticket reasoning
- no explicit customer-issue diagnosis mode
- no structured prerequisite planner
- no explicit root-cause analysis mode using code + domain + automation context

### Gap 2: Knowledge ingestion is incomplete for your requirement

Current ingestion covers:
- KB snapshots
- wiki
- Google sheet
- app code
- automation repo

Still missing or not explicit:
- customer/support tickets
- approved MCSL Trello cards/history as a searchable source
- carrier/API reference notes per carrier
- browser-observed navigation/playbooks
- MCSL feature inventory and navigation map

### Gap 3: Navigation intelligence is not MCSL-accurate enough

The current browser agent and verifier still contain hardcoded flow assumptions such as:
- direct app URL style
- simplified destination mapping
- limited menu resolution

MCSL needs a deterministic navigation layer for:
- home tabs
- hamburger menu sections
- order summary actions
- request log views
- product settings
- automation rules
- packaging settings
- Shopify orders/products verification pages

### Gap 4: Prerequisite planning is under-modeled

Your requirement depends heavily on setup steps before execution:
- add/edit carrier
- add/edit product
- set packaging
- set automation rules
- create order via API or UI
- fetch product/variant ids
- choose domestic/international address type
- verify tracking/fulfillment after action

That logic is only partially represented in the current verifier.

### Gap 5: Multi-carrier coverage is too shallow

The current verifier has some carrier keyword handling, but not a durable carrier capability map.

Needed:
- supported carrier matrix
- carrier setup steps
- carrier-specific special services
- carrier-specific request/label verification expectations
- known limitations and prerequisites

### Gap 6: Ticket-to-root-cause flow is not built

Your requirement says the expert should inspect docs, browser behavior, and code to explain what issue is likely happening.

That requires a new analysis layer that combines:
- domain RAG
- code RAG
- automation RAG
- optional ticket text/history

### Gap 7: Trello flow needs MCSL-specific operationalization

Trello client exists, but the business flow needs to be defined end to end for MCSL:
- which lists map to Dev / QA / Release
- when AC/TC comments are posted
- how QA evidence is attached or linked
- how automation/test-case output is written back

### Gap 8: No explicit MCSL source-of-truth document inside this repo

The repo needs one place that defines:
- navigation map
- supported source systems
- deterministic helpers
- scenario setup strategies
- Shopify verification rules

Without that, prompts and agent behavior will drift.

### Gap 9: MCSL toggle identity is still under-modeled

FedEx can often work with store URL/store name.

MCSL needs stronger deployment identifiers:
- `storeUUID`
- `accountUUID`
- live `/toggles` API state

These values are available from the MCSL app APIs and should become the source of truth for toggle requests and toggle-status checks.

---

## Recommended Architecture Changes

### A. Add a project truth layer for MCSL

Create internal source-of-truth docs for:
- navigation map
- scenario categories
- setup strategies
- verification strategies
- supported carrier inventory
- Shopify side-verification rules

These docs should become first-class RAG inputs.

### B. Split knowledge into functional buckets

Recommended knowledge buckets:
- `kb_articles`
- `wiki`
- `sheets`
- `trello_cards`
- `support_tickets`
- `storepepsaas_server`
- `storepepsaas_client`
- `automation`
- `playbooks`

### C. Add a prerequisite-planning module

Before AI QA execution, generate a structured plan:
- scenario type
- setup actions needed
- order creation mode: API vs UI
- product source: existing vs create-new
- required Shopify verification
- required request/log verification
- cleanup needed

### D. Add an issue-analysis mode

New mode for prompts/pipeline:
- input: ticket text, screenshots, logs, code references, AC, card
- output:
  - likely issue summary
  - impacted area
  - likely root cause
  - how to reproduce
  - what logs to inspect
  - what code modules to inspect

### E. Add deterministic MCSL helpers before agentic fallback

High-value helpers:
- open MCSL embedded app from Shopify admin
- ensure auth or run setup
- search hamburger menu item
- open request log
- open product settings
- create Shopify product and capture ids
- create Shopify order by product/variant ids
- verify order fulfillment in Shopify
- verify tracking number presence
- open rate log / label log

---

## Recommended Build Order

### Phase 1: MCSL foundation docs and prompt correction

Deliverables:
- MCSL navigation map
- MCSL scenario taxonomy
- MCSL verification playbook
- prompt updates for domain expert, user story writer, validator, AI QA planner

### Phase 2: Knowledge expansion

Deliverables:
- add support-ticket ingestion path
- add Trello card/history ingestion path
- add internal playbook docs to ingestion
- add carrier capability docs

### Phase 3: Deterministic execution helpers

Deliverables:
- login/auth bootstrap
- app open helper
- menu/search navigation helpers
- Shopify product creation helper
- API order helper wrapper
- Shopify order verification helper
- request/log verification helpers

### Phase 4: Prerequisite planner + AI QA flow rewrite

Deliverables:
- structured prerequisite planner
- scenario setup execution
- API-vs-UI ordering selection
- cleanup planning
- evidence model for MCSL logs and Shopify status

### Phase 5: Ticket analysis and root-cause assistant

Deliverables:
- ticket triage prompt flow
- code-aware issue analyzer
- likely-root-cause report
- affected module suggestions

### Phase 6: Trello and QA delivery completion

Deliverables:
- create/update MCSL cards with AC and TCs
- assign dev
- move cards across lists
- add QA findings
- attach automation/test-case references

---

## Immediate Next Changes To Implement In This Repo

1. Add MCSL internal playbook docs to `docs/` and ingest them.
2. Update prompts to support:
   - support-ticket reasoning
   - prerequisite planning
   - code-aware root-cause analysis
   - MCSL-specific navigation language
3. Expand config and ingest pipeline for:
   - Trello historical cards
   - support-ticket source
   - playbook docs
4. Replace simplified browser-navigation assumptions with deterministic MCSL helpers.
5. Add a prerequisite planner that chooses:
   - existing product vs new product
   - API order vs storefront order
   - request log vs label log vs Shopify verification

---

## Recommended Questions To Finalize Before Implementation

These answers will remove ambiguity before wiring the next phase:

- Which Trello board/list names are the exact MCSL equivalents of Dev, QA, Release?
- Where should support tickets come from for ingestion: Trello, Slack, email exports, sheet, or another system?
- Which MCSL frontend/backend code paths are the real source repos to index in addition to the paths already configured?
- Do you want the AI QA agent to create Shopify products directly, or should it call existing automation helpers first?
- Which carrier list should be treated as officially supported for v1 of this expert?
- What is the expected output format for developer-facing issue analysis: summary only, full bug report, or Trello-ready card body?

---

## Bottom Line

The MCSL repo already contains the reusable platform skeleton. The missing work is the MCSL truth layer:
- better knowledge sources
- better navigation modeling
- prerequisite planning
- support-ticket and code-aware diagnosis
- deterministic Shopify + MCSL execution helpers

That is the correct adaptation path. Copying FedEx app navigation would be the wrong implementation.
