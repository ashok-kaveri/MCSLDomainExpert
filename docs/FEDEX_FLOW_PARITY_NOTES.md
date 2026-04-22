# FedEx Flow Parity Notes

This document tracks workflow parity only. It is not a claim that MCSL and FedEx share the same domain logic.

Comparison repo:
- `../Fed-Ex-automation/FedexDomainExpert`

MCSL source of truth:
- [pipeline_dashboard.py](/Users/madan/Documents/MCSLDomainExpert/pipeline_dashboard.py:1)

## What Parity Means

Parity means:
- similar QA stage order
- similar release-state progression
- similar user affordances around generation, validation, publish, review, automation, docs, and sign-off

Parity does not mean:
- copying FedEx navigation
- copying FedEx carrier assumptions
- replacing MCSL rules with FedEx logic

## Current Parity Status By Stage

### Validate AC

MCSL now follows the FedEx-style sequence:
- `Load Cards`
- auto-run validation, diagnosis, and release analysis
- show `Release Intelligence`
- show `Step 1: Card Requirements`
- show `AI Suggested User Story & AC`
- show `Domain Validation`
- allow fix and revalidate

Important MCSL-specific difference:
- toggle flow is richer and app-state-aware, and should stay different from FedEx

### Generate TC

MCSL supports the same core flow shape:
- generate test cases
- review and regenerate with feedback
- manual edit and re-review
- Slack share
- publish to Trello and Sheets
- duplicate review before sheet write

Current correctness behavior:
- generation uses the current AC draft, not only stale Trello description
- existing saved TCs are also reviewed against the current AC draft
- partial publish retry should not duplicate the Trello summary comment

Remaining differences:
- mostly wording and layout
- not a major flow gap

### AI QA Verifier

MCSL already has the main FedEx-style AI QA flow:
- TC-first execution
- reruns and `qa_needed`
- failed-finding review
- ask-domain-expert
- final approval and save

Intentional MCSL difference:
- execution and reasoning use MCSL automation, MCSL request expectations, and MCSL carrier knowledge

### Generate Automation Script

MCSL now includes the main FedEx-style automation stages:
- `① Write Automation Code`
- `② Run Automation & Post to Slack`
- `③ Generate Documentation`
- `🐛 Bug Reporter`

Additional parity already present:
- existing-vs-new feature detection
- `find_pom`-style automation matching
- per-card run breakdown
- failed-test detail
- richer generation summary

## Intentional MCSL Differences That Must Stay

- Shopify embedded-app navigation
- multi-carrier expectation logic
- MCSL toggle and store-state capture
- MCSL automation repo structure
- MCSL request and log verification rules

## Remaining Work

Most remaining parity work is now:
- wording and layout cleanup where QA wants closer FedEx familiarity
- live Trello, Slack, and app validation of the newest flows
- small parity fixes only when they improve MCSL workflow without damaging MCSL-specific behavior
