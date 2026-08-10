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
- index page with `Story ID`, `Story Title`, `Toggle Name`
- brief description
- toggles and prerequisites
- support/demo walkthrough
- expected behavior

Support guide examples from the sample:

- explain background silently operating fixes clearly
- state if no toggle is required
- specify scope such as international-only or domestic-only
- give concrete scenarios with expected support observations

## Support Guide Tone

Professional, practical, support-ready.

Audience:

- support team
- demo team
- implementation/support leads

The support reader should be able to explain the feature to a merchant without asking engineering.

Use:

- clear brief description
- concrete paths and steps
- "what support should observe"

Avoid:

- technical words anywhere in the body — code, class, file, or method names, API or schema jargon, internal engineering terms. Three exemptions: the request/log callouts, the `Technical Cards` section, and toggle keys in the index table and `Toggles & Prerequisites` tables
- deep code/internal implementation details
- vague "works correctly" wording
- unsupported claims
- excessive QA/test-count language

## Combined Support Guide Required Sections

```markdown
# <Release> Support Guide

## Included Story Cards
| Story ID | Story Title | Toggle Name | Trello card link |
|---|---|---|---|

## <Story ID> - <Card title>
### Brief Description
...

## Technical Cards
### <Story ID> - <Card title>
...
```

Do not add a `How Support Should Use This Package` section. The index page is followed directly by the first card section.

Index page rules:

- use exactly four columns: `Story ID`, `Story Title`, `Toggle Name`, `Trello card link`
- `Story ID` is the story/card number only
- `Story Title` is the card title
- `Toggle Name` is the exact toggle name, or `None` when the card needs no toggle. Source it from anywhere in the card evidence — description, comments, checklists, attachments, approved AC, TCs, QA notes — because the exact key is often only in a comment. Comma-separate multiple keys. Never guess a key; write `Not stated` and flag it when a card clearly needs one but names none
- list technical cards in their normal position here even though their body section moves to the end
- `Trello card link` is a markdown link to the card, labelled with the story id, for example `[941](https://trello.com/c/abc123)`; use `-` when no card URL is known

## Per-Card Support Guide Required Sections

```markdown
# Support Guide: <Story ID or concise feature name>

## Brief Description
Very crisp. 1 short paragraph.

## Toggles & Prerequisites
State whether a feature toggle is required.
List prerequisites and scope.

## Step-by-Step Support Walkthrough
Use Scenario A/B/C when useful. Put exact navigation inside the action step, for example ORDERS, hamburger menu > Carriers, hamburger menu > Products, Reports, Shopify Admin Orders, Shopify Admin Products, checkout, or request logs.

## Expected Behaviour
Summarize the key signal.
```

Do not add `Merchant-Safe Explanation`, `Common Questions & Troubleshooting`, or `Support Escalation Packet`. The card section ends after `Expected Behaviour`.

## Technical Cards Section Structure

```markdown
## Technical Cards

### <Story ID> - <Card title>
Two to four lines: what changed, and why it matters.
```

Rules:

- one `## Technical Cards` H2, placed after the last normal card section, and omitted when the release has no technical cards
- a technical card is developer-only work — API-only change, library or version upgrade, refactor, internal clean-up, infrastructure — with nothing support or the merchant can see or do
- a card with both a technical part and a visible part stays a normal card
- each entry is an H3 so the short entries flow together; the renderer already breaks a page before the `## Technical Cards` H2 itself, so never hand-place a break
- no walkthrough, toggles, or expected-behaviour subsections inside these entries
- plain wording still applies; name a version, endpoint, or field only when the entry makes no sense without it

## Combined Business Brief Required Structure

```markdown
# What's New: <Release>

## Release Overview
2-3 sentences describing the release value.

## Included Updates
| Story ID | Story Title | Toggle Name | Trello card link |
|---|---|---|---|

## <Story ID> - <Card title>
Per-card plain-English business brief.
```

## Per-Card Business Brief Required Structure

```markdown
## <Feature Name in Plain English>
*One sentence headline value.*

### Brief Description
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
- Exclude cards labelled `SL: ON Hold`, `SL: Carrier Platform`, `Spill Over`, or `SL: Closed By Support` from both the index table and the body, matching labels case-insensitively. Include one only when the user names it. Report every exclusion and the label behind it; never drop a card silently.
- Run a toggle audit per card across the whole card, not only the description. The exact toggle key is often only in a QA or developer comment. Never guess a key.
- Run a technical-card audit per card and collect developer-only cards into the trailing `Technical Cards` section.
- After a release package is generated, send the consolidated toggle list as a Slack DM to `ashok@pluginhive.com` per the `Toggle List Follow-Up` section of `SKILL.md`. Skip it when no card has a toggle.
- Do not include a generic `Where to Find This in MCSL` section. The detailed walkthrough is the source of truth for where support should go.
- Keep feature-specific paths and carrier-specific steps inside the walkthrough/troubleshooting sections.
- Every story card section starts on a new PDF page, including the first — the index page stands alone. `render_pdf_bytes` inserts a page break before each `<Story ID> - <Title>` heading, so do not add manual page breaks or blank filler.
- Before final PDF generation, verify no card starts at the bottom of a page without the card detail table/content following on the same page.
- Run a card-by-card payload/log audit before final PDF generation:
  - If QA/support must inspect a carrier request, response, payload, request log, invoice request, tracking payload, report source field, or automation-rule log, include the exact node or log field.
  - Put exact nodes/fields in the walkthrough as a highlighted callout using one of these exact labels: `Request node to verify:`, `Request nodes to verify:`, `Request/response nodes to verify:`, or `Request/log fields to verify:`.
  - Keep those node names out of merchant-safe wording.
  - Do not invent fields for UI-only, sync-only, report-only, or performance-only cards.

## PDF Rendering

Use `pipeline.handoff_docs.render_pdf_bytes` through the skill helper script. This gives the same polished dashboard PDF styling.

For release handoff, render one combined Support Guide PDF and one combined Business Brief PDF. Create individual PDFs only for explicit single-card requests.
