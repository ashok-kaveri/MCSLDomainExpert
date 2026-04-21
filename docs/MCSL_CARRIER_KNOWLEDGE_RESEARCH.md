# MCSL Carrier Knowledge Research

## What I verified

The current MCSL expert already has strong source coverage:

- `docs/kb_snapshots/`
  - PluginHive KB articles for setup, troubleshooting, carriers, packaging, checkout rates, customs, alcohol/signature, etc.
- `docs/tc_snapshots/mcsl-regression-master-sheet.md`
  - broad regression coverage for orders, products, packaging, carriers, fulfillment, tracking, automation, and Shopify sync
- local wiki at `~/Documents/mcsl-wiki/wiki`
  - product, support, architecture, modules, operations, zendesk summaries
- automation repo at `~/Documents/mcsl-test-automation`
  - Playwright tests, auth, test data, automation rules, and carrier envs
- code search across:
  - backend/shared source
  - frontend/client source
  - automation source

## Carrier coverage confirmed from automation envs

The automation repo currently has carrier env files for:

- Amazon Shipping
- Australia Post
- Blue Dart
- FedEx
- MyPost
- UPS
- USPS
- USPS Stamps

There are also KB/doc references for additional carriers and carrier families such as:

- DHL
- Canada Post
- Purolator
- PostNord
- EasyPost / USPS via EasyPost

## Important product rule

Cards should be interpreted using this rule:

- if the card clearly mentions a carrier, treat it as `carrier-specific`
- if the card does not mention a carrier, treat it as `generic`
- generic cards should use a stable default carrier path for execution planning unless the retrieved context says the scenario must be carrier-neutral or multi-carrier

This matters because many MCSL features are shared platform behaviors:

- order import / order grid
- label generation flow
- packaging settings
- Shopify fulfillment / tracking sync
- rate automation / request log
- product settings
- generic settings flows

## MCSL navigation facts confirmed

The MCSL app is easier to model than FedEx because many flows are shared:

- top tabs:
  - `ORDERS`
  - `LABELS`
  - `PICKUP`
  - also `MANIFEST`, `TRACKING` in verifier navigation
- hamburger-menu flows:
  - `Products`
  - `Carriers`
  - `General Settings`
  - shipping / packaging / automation areas
- Shopify admin verification:
  - Orders page for fulfillment/tracking verification
  - Products page for product creation / verification

## Current implementation changes made

I added a shared carrier knowledge layer in:

- `pipeline/carrier_knowledge.py`

It now provides:

- supported carrier profiles
- alias matching
- carrier-specific vs generic card detection
- default generic-carrier guidance
- carrier env path resolution for automation order creation

It is now used by:

- `pipeline/user_story_writer.py`
- `pipeline/domain_validator.py`
- `pipeline/smart_ac_verifier.py`
- `pipeline/order_creator.py`
- `pipeline/handoff_docs.py`

## What still needs to happen

The next high-value work is ingestion and retrieval quality, not dashboard wiring.

We should add:

1. a carrier capability matrix document
- carrier name
- internal code
- available env
- main setup path
- known special services
- request-log / label-log verification notes

2. wiki/source ingestion refresh discipline
- re-run ingest regularly for:
  - `kb_articles`
  - `wiki`
  - `automation`
  - backend
  - frontend

3. ticket diagnosis guidance
- for each new customer issue, classify likely cause as:
  - generic platform
  - carrier setup
  - packaging/data
  - Shopify sync
  - request/label API issue
  - code defect

4. QA planning guidance
- if card has carrier info:
  - use that carrier first
- if card is generic:
  - use generic flow and stable default carrier path unless knowledge says otherwise

## Practical conclusion

The MCSL expert does not need a different tab structure first.
It needs a better source-of-truth layer for multi-carrier knowledge.

The repo already has the right source inputs.
The important work now is to make carrier knowledge explicit and consistently used across:

- user story writing
- domain validation
- AI QA planning
- issue diagnosis
- handoff documentation
