# MCSL Domain Expert Adaptation Plan

This file is now a current-state adaptation map, not an old gap tracker.

## Goal

Keep the FedEx-style workflow pattern where it improves throughput, while grounding reasoning and execution in MCSL truth:
- MCSL carriers
- MCSL Shopify embedded app
- MCSL automation repo
- MCSL logs and request expectations
- MCSL toggle and store context

## Current Platform Status

The repo is past first-pass planning. Core workflow layers are already implemented.

Already implemented:
- split QA workflow tabs
- Trello-driven release loading
- AC generation and validation
- release intelligence
- TC generation, review, feedback regeneration, share, and publish
- TC-first AI QA execution
- failed-finding review and developer notification
- approval and sign-off flow
- automation writing, run, docs, and manual bug reporter flow
- MCSL toggle and store-state capture
- carrier knowledge and request registry support

## Current Workflow Model

### 1. Validate AC
- load release cards from Trello
- run MCSL validation, diagnosis, and release analysis automatically
- review card requirements
- handle MCSL toggle prerequisites
- generate or review AI AC
- validate, fix, and revalidate AC

### 2. Generate TC
- generate test cases from the current AC draft
- review, regenerate, edit, and re-review
- share to Slack
- publish Trello summary and positive cases to Sheets

### 3. AI QA Verifier
- execute ranked reviewed test cases
- gather evidence from live app behavior
- support reruns and `qa_needed`
- review findings and bugs

### 4. Generate Automation Script
- detect existing-vs-new automation targets
- generate or update automation
- run automation
- post results
- generate docs
- raise manual QA bugs

## MCSL-Specific Operating Rules

### Navigation
- MCSL is a Shopify embedded app
- navigation should use MCSL app paths and automation knowledge, not FedEx routes

### Verification
- many scenarios use API order creation
- some scenarios still require Shopify storefront or admin verification
- request and log verification should be based on MCSL request expectations

### Toggle Handling
- live app or API state should be preferred when available
- `store_uuid`, `account_uuid`, and toggle state are part of the active workflow
- Slack escalation remains part of orchestration

### Analysis
- validation, diagnosis, and release intelligence must stay MCSL-native
- FedEx is a workflow reference only

## Important Current Files

- [pipeline_dashboard.py](/Users/madan/Documents/MCSLDomainExpert/pipeline_dashboard.py:1)
- [pipeline/card_processor.py](/Users/madan/Documents/MCSLDomainExpert/pipeline/card_processor.py:1)
- [pipeline/smart_ac_verifier.py](/Users/madan/Documents/MCSLDomainExpert/pipeline/smart_ac_verifier.py:1)
- [pipeline/automation_writer.py](/Users/madan/Documents/MCSLDomainExpert/pipeline/automation_writer.py:1)
- [pipeline/feature_detector.py](/Users/madan/Documents/MCSLDomainExpert/pipeline/feature_detector.py:1)
- [pipeline/toggle_state.py](/Users/madan/Documents/MCSLDomainExpert/pipeline/toggle_state.py:1)
- [pipeline/bug_tracker.py](/Users/madan/Documents/MCSLDomainExpert/pipeline/bug_tracker.py:1)

## Current Improvement Areas

The highest-value remaining work is:
- more live end-to-end validation against Trello, Slack, Sheets, and app data
- wording and layout cleanup where QA wants tighter FedEx familiarity
- deeper MCSL troubleshooting knowledge ingestion if support-history reasoning needs to improve

## Documentation Rule

If workflow changes again, update this file together with:
- [README.md](/Users/madan/Documents/MCSLDomainExpert/README.md:1)
- [CLAUDE.md](/Users/madan/Documents/MCSLDomainExpert/CLAUDE.md:1)
- [docs/FEDEX_FLOW_PARITY_NOTES.md](/Users/madan/Documents/MCSLDomainExpert/docs/FEDEX_FLOW_PARITY_NOTES.md:1)
