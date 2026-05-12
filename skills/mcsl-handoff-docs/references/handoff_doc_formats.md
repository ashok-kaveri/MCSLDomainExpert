# Handoff Document Formats

This reference is based on:

- `pipeline/handoff_docs.py`
- dashboard `Handoff Docs` tab
- sample support package `docs/MCSL378_Support_Guide.docx`

## Sample Support Guide Style

The attached release package uses:

- branded PluginHive / Shopify MCSL Shipping App release header
- release version and date
- one combined release PDF with card-by-card sections
- support guide label
- release details
- feature summary
- toggles and prerequisites
- where to find the feature
- support/demo walkthrough
- expected behavior
- business-safe customer explanation
- common questions and troubleshooting

Support guide examples from the sample:

- explain background silently operating fixes clearly
- state if no toggle is required
- specify scope such as international-only or domestic-only
- give concrete scenarios with expected support observations
- include merchant-facing explanation in quoted/plain language
- include Q&A for likely support tickets

## Support Guide Tone

Professional, practical, support-ready.

Audience:

- support team
- demo team
- implementation/support leads

The support reader should be able to explain the feature to a merchant without asking engineering.

Use:

- clear feature summary
- concrete paths and steps
- "what support should observe"
- "what to tell the merchant"
- "what to check if it fails"

Avoid:

- deep code/internal implementation details
- vague "works correctly" wording
- unsupported claims
- excessive QA/test-count language

## Combined Support Guide Required Sections

```markdown
# <Release> Support Guide

## Included Story Cards
| Story / card | Carrier scope | Toggle / prerequisite signal |
|---|---|---|

## How Support Should Use This Package

## <Story ID> - <Card title>
### Feature Summary
...
```

## Per-Card Support Guide Required Sections

```markdown
# Support Guide: <Story ID or concise feature name>

## Feature Summary
2-4 paragraphs.

## Toggles & Prerequisites
State whether a feature toggle is required.
List prerequisites and scope.

## Step-by-Step Support Walkthrough
Use Scenario A/B/C when useful. Put exact navigation inside the action step, for example ORDERS, hamburger menu > Carriers, hamburger menu > Products, Reports, Shopify Admin Orders, Shopify Admin Products, checkout, or request logs.

## Expected Behaviour
Summarize the key signal.

## Merchant-Safe Explanation
Use customer-safe wording.

## Common Questions & Troubleshooting
Use Q/A format.

## Support Escalation Packet
Include concise fields support can send to QA/dev when the feature does not behave as expected.
```

## Combined Business Brief Required Structure

```markdown
# What's New: <Release>

## Release Overview
2-3 sentences describing the release value.

## Included Updates
Table of cards.

## <Story ID> - <Card title>
Per-card plain-English business brief.
```

## Per-Card Business Brief Required Structure

```markdown
## <Feature Name in Plain English>
*One sentence headline value.*

### The Problem
2-3 sentences.

### What's New
- 3-5 bullets.

### Who Benefits
2-3 merchant/support scenarios.

### Availability
One line.
```

Rules:

- max about 400 words
- plain business English
- no developer/tester attribution
- no QA notes
- no internal Trello links in body
- no technical terms unless impossible to avoid
- no toggle detail unless merchant/rollout must act

## Release QA Guardrails

- Build release packages from full live Trello card context when available: description, labels, comments, checklists, approved AC/TCs, and AI QA evidence.
- Treat QA comments as required review input because late caveats often appear there.
- Run a platform audit for every card. Detect Shopify, WooCommerce, BigCommerce, Magento, or PrestaShop from the card/ticket evidence. If no platform is explicit, default to Shopify. If a customer/ticket names a non-Shopify platform, use that platform in support steps and business wording while treating the feature as shared MCSL behavior unless the card limits scope.
- Do not include a generic `Where to Find This in MCSL` section. The detailed walkthrough is the source of truth for where support should go.
- Keep feature-specific paths and carrier-specific steps inside the walkthrough/troubleshooting sections.
- Before final PDF generation, verify no card starts at the bottom of a page without the card detail table/content following on the same page.
- Run a card-by-card payload/log audit before final PDF generation:
  - If QA/support must inspect a carrier request, response, payload, request log, invoice request, tracking payload, report source field, or automation-rule log, include the exact node or log field.
  - Put exact nodes/fields in the walkthrough as a highlighted callout using one of these exact labels: `Request node to verify:`, `Request nodes to verify:`, `Request/response nodes to verify:`, or `Request/log fields to verify:`.
  - Keep those node names out of merchant-safe wording.
  - Do not invent fields for UI-only, sync-only, report-only, or performance-only cards.

## PDF Rendering

Use `pipeline.handoff_docs.render_pdf_bytes` through the skill helper script. This gives the same polished dashboard PDF styling.

For release handoff, render one combined Support Guide PDF and one combined Business Brief PDF. Create individual PDFs only for explicit single-card requests.
