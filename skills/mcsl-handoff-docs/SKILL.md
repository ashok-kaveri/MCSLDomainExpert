---
name: mcsl-handoff-docs
description: Use when working inside the MCSLDomainExpert project after cards are approved and the user wants professional release handoff documents like the dashboard Handoff Docs tab: Support Guide, Business Brief, or both, generated from approved US/AC, TCs, AI QA evidence, release/card metadata, toggles, and member ownership. If the user requests only one document, generate only that document and PDF.
---

# MCSL Handoff Docs

Use this skill to generate professional handoff documents for approved PluginHive MCSL release cards across Shopify, WooCommerce, BigCommerce, Magento, and PrestaShop.

It mirrors the dashboard `Handoff Docs` tab:

- Combined release Support Guide
- Combined release Business Brief
- Optional single-card Support Guide / Business Brief for quick review
- Markdown + PDF output
- Trello/Slack-ready artifacts when requested

Default release delivery is one combined PDF per document type. If the user asks for only one document type, generate only that combined document. Use single-card documents only when the user explicitly asks for one card.

## First Reads

Before generating:

1. Read `AGENTS.md`.
2. Read:
   - `skills/mcsl-handoff-docs/references/handoff_doc_formats.md`
3. Inspect only directly relevant project files:
   - `pipeline/handoff_docs.py`
   - `pipeline_dashboard.py`

Use `mcsl-domain-core` research when local context is incomplete or customer-facing explanations need current MCSL/PluginHive/Shopify facts.
Use `mcsl-trello-operator` to fetch card details/members or attach/comment PDFs when explicitly requested.
Use `mcsl-slack-operator` to send PDFs or messages to Slack when explicitly requested.

For release packages, always use full live Trello card context when available: description, comments, labels, attachments/checklist summaries, approved AC/TCs, and AI QA evidence. QA comments often contain late caveats and must not be skipped.

Before writing a release Support Guide, do a payload/log audit for every card:

- If the evidence asks support to inspect a carrier request, response, payload, request log, diagnostic log, invoice request, tracking payload, report source field, or automation-rule log, include the exact node/field name support must verify.
- Put the callout immediately after the relevant walkthrough step, using one of these exact bullet labels so the PDF renderer highlights it:
  - `Request node to verify: ...`
  - `Request nodes to verify: ...`
  - `Request/response nodes to verify: ...`
  - `Request/log fields to verify: ...`
- Do not add node callouts to UI-only, report-only, sync-only, or performance cards unless card evidence names an actual request/log field.
- If the exact field is unknown after checking card comments/checklists and code/context, say what log to inspect in troubleshooting and do not invent a node name.

Before writing Support Guide or Business Brief content, do a platform audit for every card:

- Detect the customer/test platform from the title, labels, description, comments, linked ticket, PR notes, AC, TCs, and QA evidence.
- Supported platform names include Shopify, WooCommerce, BigCommerce, Magento, and PrestaShop.
- If no platform is explicit, default the QA/support platform to Shopify.
- If a customer/ticket explicitly names WooCommerce, BigCommerce, Magento, or PrestaShop, use that platform in support steps, prerequisites, and business wording.
- Treat the underlying feature as shared MCSL behavior unless the card limits the implementation scope, but document/test on the customer-reported platform.

## Inputs

Best input package:

- card name/id/url
- release name
- approved US + AC
- reviewed TCs
- AI QA summary/evidence
- support sign-off notes
- developed by / tested by
- toggles/prerequisites
- known limitations
- rollout notes

If some inputs are missing, still generate a useful draft, but mark unknown fields clearly. Do not invent ownership, release numbers, toggles, or unsupported limitations.

## Document Selection

Generate based on user request:

- "support guide", "support doc", "demo doc", "customer support explanation" -> combined release Support Guide only
- "business brief", "business doc", "stakeholder doc", "marketing/sales summary" -> combined release Business Brief only
- "handoff docs", "both docs", "support and business" -> both combined release PDFs
- "single card", "only this card", or a specific card id/name -> single-card document for that card

If unclear, ask which one: Support Guide, Business Brief, or both.

## Support Guide Purpose

The Support Guide is for support/demo teams who need to understand the feature well enough to explain it to customers.

It must be practical, professional, and support-friendly:

- explain what changed
- include where support can see it inside the relevant walkthrough steps
- explain what the merchant should experience
- include walkthrough steps
- include customer-safe explanation
- include troubleshooting questions
- include toggles/prerequisites
- include developed by / tested by

Do not write vague release notes. This should be a real support enablement document.

## Business Brief Purpose

The Business Brief is for non-technical stakeholders: product, sales, marketing, account managers.

It must:

- stay under about 400 words unless user asks otherwise
- use plain business English
- avoid technical terms
- omit developed by / tested by
- omit QA notes and test counts
- mention toggle/availability only if the merchant or rollout team must do something

## PDF Generation

When the user asks for PDF:

1. Generate the markdown first.
2. Save the markdown under `data/handoff_docs/`.
3. Render PDF using:
   `skills/mcsl-handoff-docs/scripts/render_handoff_pdf.py`

For one requested release document, create one combined PDF containing all selected/approved release cards.

For both, create two combined PDFs: one Support Guide package and one Business Brief package.

## Combined Release Package Structure

Combined Support Guide:

```markdown
# <Release> Support Guide

## Included Story Cards
| Story / card | Carrier scope | Toggle / prerequisite signal |
|---|---|---|

## How Support Should Use This Package
...

## <Story ID> - <Card title>
### Feature Summary
...
```

Combined Business Brief:

```markdown
# What's New: <Release>

## Release Overview
...

## Included Updates
| Story / card | Carrier scope | Toggle / prerequisite signal |
|---|---|---|

## <Story ID> - <Card title>
### The Problem We Solved
...
```

## Support Guide Structure

For each card section inside the combined Support Guide, follow the sample release support guide style:

```markdown
# Support Guide: <Story ID or concise feature name>

## Feature Summary
...

## Toggles & Prerequisites
...

## Step-by-Step Support Walkthrough
...

## Expected Behaviour
...

## Merchant-Safe Explanation
...

## Common Questions & Troubleshooting
**Q: ...**
...

## Support Escalation Packet
...
```

## Quality Bar

Before finalizing:

- make it understandable for support people
- remove internal/code jargon unless necessary
- keep merchant-facing wording safe and clear
- do not expose implementation details that customers do not need
- verify every claim comes from card/AC/TC/AI QA evidence or researched domain facts
- verify every live Trello QA comment and checklist has been considered before finalizing a release package
- do not add a generic `Where to Find This in MCSL` section; include exact platform-aware navigation in the relevant walkthrough step instead
- include highlighted exact request/log node names when the card requires request-payload, response, or diagnostic-log verification, such as `discount`, `declarationStatement`, `signature`, `classification_type`, or carrier-specific service fields
- verify no card heading starts at the bottom of a page without its detail table/content following on the same page
- keep the support guide thorough enough for a support call
- keep the business brief short and polished

## Final Response

Return:

- document(s) generated
- markdown path if saved
- PDF path if rendered
- any missing inputs or assumptions

Use absolute file paths in final responses.
