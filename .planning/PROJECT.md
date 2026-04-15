# MCSLDomainExpert

## What This Is

MCSLDomainExpert is an AI-powered QA platform for the PluginHive Shopify Multi Carrier Shipping Label (MCSL) App. It mirrors the architecture of FedexDomainExpert but is tailored to a multi-carrier context — supporting FedEx, UPS, USPS, DHL, Canada Post, Aramex, TNT, Australia Post, and more. It provides three core capabilities: a RAG-backed Domain Expert Chat for answering MCSL app questions, an AI QA Agent that autonomously verifies acceptance criteria by operating the real Shopify app in a browser, and a Pipeline Dashboard that orchestrates the full Trello card → AC writing → QA verification → Playwright test generation workflow.

## Core Value

The AI QA Agent must be able to autonomously verify any AC scenario for the MCSL app — across all supported carriers — without human intervention, reporting clear pass/fail per scenario with evidence.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Domain Expert Chat backed by RAG on MCSL knowledge base docs, wiki, codebase, and approved Trello cards
- [ ] AI QA Agent that opens real MCSL Shopify app, verifies every AC scenario, creates orders, configures carrier settings, downloads logs/labels, and reports pass/fail
- [ ] Multi-carrier aware: agent understands FedEx, UPS, USPS, DHL, Canada Post, and other carrier-specific flows
- [ ] MCSL-specific label generation flows (manual + auto + bulk)
- [ ] MCSL-specific document handling: View Logs, Download Documents, Print Documents (new tab viewer)
- [ ] MCSL carrier account configuration flows (connect carrier, negotiated rates, service selection)
- [ ] Packing methods support (custom boxes, dimensional weight, auto packing)
- [ ] International shipping flows (commercial invoice, customs duties)
- [ ] Rate display at checkout configuration
- [ ] Return label generation
- [ ] Pickup scheduling
- [ ] Pipeline Dashboard (Streamlit) orchestrating Trello → AC → QA → Test Gen
- [ ] RAG auto-updates after each approved Trello card cycle
- [ ] TC sheet ingestion from Google Sheets (provided TC sheet URL)

### Out of Scope

- FedEx-only features (dry ice, alcohol, battery, HAL, COD) — MCSL handles these differently via product-level carrier config; handled per-carrier
- Shopify's own discounted carrier accounts — app only supports merchant's own accounts
- Boxify / Shopify native box integration — MCSL has its own box packing

## Context

- **Architecture reference:** FedexDomainExpert at `~/Documents/Fed-Ex-automation/FedexDomainExpert` — full copy of the agent architecture with Playwright browser automation, ChromaDB RAG, Claude AI, Streamlit UI
- **MCSL automation repo:** Separate repo (`mcsl-test-automation`) — path to be confirmed; provides POM files, productsconfig.json, addressconfig.json, and .env for Shopify API access
- **70% automation coverage:** Existing Playwright tests cover most core flows — high value from AI QA Agent since the remaining 30% can be explored
- **TC Sheet:** https://docs.google.com/spreadsheets/d/1oVtOaM2PesVR_TkuVaBKpbp_qQdmq4FQnN43Xew0FuY/edit — primary source for test case definitions to ingest into RAG
- **Knowledge Base:** https://www.pluginhive.com/knowledge-base/shopify-multi-carrier-shipping-label-app-faqs/ — 5 categories: Setting Up, Troubleshooting, Knowledgebase, FAQ, Use Cases
- **Key MCSL difference from FedEx:** MCSL supports multiple carriers — each carrier has its own account config, service list, label format, and special services. The AI QA Agent must be carrier-aware when planning and executing scenarios.

## Key MCSL App Flows (vs FedEx)

### Label Generation
- Manual: Same flow as FedEx but carrier selection happens at account level, not service level
- Auto-generate: Works same as FedEx but carrier is pre-configured
- Bulk: Select all orders → Actions → "Generate Labels" (different button text than FedEx)

### Carrier Account Configuration
- App Settings → Carriers → Add Carrier → select carrier type → enter credentials
- Each carrier has its own rate zones, services, and special services

### Document Handling
- View Logs: App-specific log viewer (different from FedEx's "How To" flow)
- Print Documents: Opens new tab (same as FedEx — NOT a zip download)
- Download Documents: ZIP with label PDF + packing slip + CI (for international)

### Special Services (carrier-specific)
- FedEx: signature, dry ice, alcohol, battery, HAL, insurance
- UPS: signature, insurance, COD
- USPS: signature, registered mail
- DHL: insurance, signature

## Constraints

- **Tech stack:** Python, ChromaDB, Claude claude-sonnet-4-6/claude-haiku-4-5-20251001, Playwright (Python), Streamlit — same as FedexDomainExpert
- **Embeddings:** Ollama `nomic-embed-text` (local)
- **ChromaDB collections:** `mcsl_knowledge`, `mcsl_code_knowledge`
- **Config:** Must use explicit dotenv path (same pattern as FedexDomainExpert `config.py` fix)
- **Automation repo path:** Will be provided once confirmed — needed for code RAG indexing
- **TC sheet:** Google Sheets ID `1oVtOaM2PesVR_TkuVaBKpbp_qQdmq4FQnN43Xew0FuY`

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Clone FedexDomainExpert architecture | 70% of code is reusable; MCSL same platform (Shopify embedded app in iframe) | — Pending |
| Multi-carrier abstraction in AI QA Agent | Single agent must handle all carriers — carrier name injected in planning prompt | — Pending |
| Separate project from FedexDomainExpert | Different ChromaDB collections, different knowledge base, different automation repo | — Pending |
| YOLO execution mode | User preference — auto-approve, fast execution | — Pending |

---
*Last updated: 2026-04-15 after initialization*
