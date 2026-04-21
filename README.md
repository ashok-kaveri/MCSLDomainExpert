# MCSL Domain Expert

Streamlit-based QA orchestration platform for the Shopify MCSL app.

It adapts the FedEx Domain Expert workflow to MCSL without copying FedEx navigation. The platform combines:
- Trello-driven release workflow
- MCSL domain knowledge RAG
- AI-generated user stories, AC, and test cases
- AI QA browser verification
- Google Sheets sync
- Slack notifications
- automation code generation

## Current Dashboard Flow

The main QA flow is split into four tabs to match the latest FedEx operating model:

1. `🧾 Validate AC`
- load Trello board/list and release
- read existing card requirements
- detect toggle prerequisites
- generate or review AI Suggested User Story & AC
- save/comment/skip/share AC
- run domain validation and apply fixes

2. `🧪 Generate TC`
- reuse the loaded release context
- generate test cases
- review and regenerate test cases
- share test cases to Slack

3. `🤖 AI QA Verifier`
- run AI QA using generated test cases
- handle `qa_needed` reruns
- review failed findings and notify devs
- ask domain expert
- final approve and save to Trello + Sheets + RAG

4. `⚙️ Generate Automation Script`
- write automation from approved cards
- bulk approve remaining cards when needed
- run release automation
- post results to Slack

Other tabs:
- `📝 User Story`
- `🔀 Move Cards`
- `📋 History`
- `✅ Sign Off`
- `📘 Handoff Docs`

## MCSL-Specific Behavior

This repo is intentionally MCSL-specific in a few important areas:

- navigation is based on the embedded Shopify MCSL app, not FedEx app routes
- most ordering flows use API order creation, with UI ordering only where checkout/storefront behavior matters
- log verification uses automation-backed navigation plus TC/code/RAG-driven request expectations
- carrier behavior is modeled as multi-carrier knowledge, not single-carrier FedEx knowledge

## Toggle Handling

Toggle flow is different from FedEx.

Current behavior:
- detect toggles from card name, description, and comments
- auto-read store name from MCSL automation config when available
- notify Ashok / developer through Slack with toggle context
- poll for confirmation and unblock QA when confirmed

Planned MCSL improvement:
- capture `storeUUID` and `accountUUID` from the app `orders` API
- read `/toggles` API to verify whether a toggle is already enabled
- send UUID-based toggle context instead of relying only on store URL/store name

## AI QA Design

AI QA is trained with this split:

- automation repo:
  - navigation
  - stable locators
  - shared UI flows
- codebase + wiki + KB + carrier registry:
  - expected request/response behavior
  - setup knowledge
  - domain reasoning
- runtime memory:
  - learned locators
  - setup context
  - observed log evidence

Current AI QA capabilities include:
- TC-first execution
- preflight setup/navigation macros
- automation-locator-first fallback strategy
- learned locator memory
- request/response expectation matching
- direct log-dialog text capture

## Important Files

- [pipeline_dashboard.py](/Users/madan/Documents/MCSLDomainExpert/pipeline_dashboard.py:1)
- [pipeline/smart_ac_verifier.py](/Users/madan/Documents/MCSLDomainExpert/pipeline/smart_ac_verifier.py:1)
- [pipeline/card_processor.py](/Users/madan/Documents/MCSLDomainExpert/pipeline/card_processor.py:1)
- [pipeline/request_expectations.py](/Users/madan/Documents/MCSLDomainExpert/pipeline/request_expectations.py:1)
- [pipeline/carrier_knowledge.py](/Users/madan/Documents/MCSLDomainExpert/pipeline/carrier_knowledge.py:1)
- [pipeline/carrier_request_registry.py](/Users/madan/Documents/MCSLDomainExpert/pipeline/carrier_request_registry.py:1)
- [pipeline/sheets_writer.py](/Users/madan/Documents/MCSLDomainExpert/pipeline/sheets_writer.py:1)

## Run

```bash
cd /Users/madan/Documents/MCSLDomainExpert
PYTHONPATH=. .venv/bin/streamlit run pipeline_dashboard.py
```

## Supporting Docs

- [docs/FEDEX_FLOW_PARITY_NOTES.md](/Users/madan/Documents/MCSLDomainExpert/docs/FEDEX_FLOW_PARITY_NOTES.md:1)
- [docs/MCSL_PLATFORM_ADAPTATION_PLAN.md](/Users/madan/Documents/MCSLDomainExpert/docs/MCSL_PLATFORM_ADAPTATION_PLAN.md:1)
- [docs/MCSL_CARRIER_SUPPORT_REGISTRY.md](/Users/madan/Documents/MCSLDomainExpert/docs/MCSL_CARRIER_SUPPORT_REGISTRY.md:1)
- [docs/MCSL_CARRIER_CAPABILITY_MATRIX.md](/Users/madan/Documents/MCSLDomainExpert/docs/MCSL_CARRIER_CAPABILITY_MATRIX.md:1)
- [docs/MCSL_CARRIER_REQUEST_REGISTRY.md](/Users/madan/Documents/MCSLDomainExpert/docs/MCSL_CARRIER_REQUEST_REGISTRY.md:1)
