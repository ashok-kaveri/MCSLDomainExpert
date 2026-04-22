# MCSL Carrier Knowledge Research

This file describes the current carrier-knowledge inputs used by the MCSL expert. It is not a future backlog.

## Current Source Coverage

The repo already has broad MCSL source coverage from:
- `docs/kb_snapshots/`
- `docs/tc_snapshots/mcsl-regression-master-sheet.md`
- local wiki at `~/Documents/mcsl-wiki/wiki`
- local automation repo at `~/Documents/mcsl-test-automation`
- code search across backend, frontend, and automation source

## Carrier Coverage Confirmed

The automation repo currently includes carrier env coverage for:
- Amazon Shipping
- Australia Post
- Blue Dart
- FedEx
- MyPost
- UPS
- USPS
- USPS Stamps

The broader documentation set also includes support material for additional carriers and carrier families such as:
- DHL
- Canada Post
- Purolator
- PostNord
- EasyPost or USPS via EasyPost

## Operating Rule For Card Interpretation

Cards should be interpreted with this rule:
- if the card clearly mentions a carrier, treat it as carrier-specific
- if the card does not mention a carrier, treat it as generic
- generic cards should use a stable default carrier path unless retrieved context says the scenario must stay carrier-neutral or explicitly multi-carrier

This matters because many MCSL features are shared platform behaviors:
- order import and order grid
- label generation
- packaging settings
- Shopify fulfillment and tracking sync
- rate automation and request log
- product settings
- general settings flows

## Navigation Facts

Common navigation patterns in MCSL:
- top tabs such as `ORDERS`, `LABELS`, and `PICKUP`
- hamburger-menu flows such as `Products`, `Carriers`, and `General Settings`
- Shopify admin verification for orders, fulfillment, tracking, and products when needed

## Current Implementation

Shared carrier knowledge is implemented in:
- [pipeline/carrier_knowledge.py](/Users/madan/Documents/MCSLDomainExpert/pipeline/carrier_knowledge.py:1)

It provides:
- supported carrier profiles
- alias matching
- carrier-specific vs generic card detection
- default generic-carrier guidance
- carrier env path resolution for automation order creation

It is currently used by:
- [pipeline/user_story_writer.py](/Users/madan/Documents/MCSLDomainExpert/pipeline/user_story_writer.py:1)
- [pipeline/domain_validator.py](/Users/madan/Documents/MCSLDomainExpert/pipeline/domain_validator.py:1)
- [pipeline/smart_ac_verifier.py](/Users/madan/Documents/MCSLDomainExpert/pipeline/smart_ac_verifier.py:1)
- [pipeline/order_creator.py](/Users/madan/Documents/MCSLDomainExpert/pipeline/order_creator.py:1)
- [pipeline/handoff_docs.py](/Users/madan/Documents/MCSLDomainExpert/pipeline/handoff_docs.py:1)

## Practical Conclusion

The repo already has the right source inputs for multi-carrier reasoning.

The important rule for future agents is:
- keep carrier knowledge explicit
- keep it reused across validation, QA planning, automation setup, issue diagnosis, and handoff output
- do not downgrade the repo back to single-carrier assumptions just to mirror FedEx
