---
name: mcsl-ac-writer-reviewer
description: Use when working inside the MCSLDomainExpert project and the user gives a Trello card, feature request, bug/customer issue, PR note, or rough requirement and wants dashboard-style User Story plus Acceptance Criteria markdown generated, reviewed, rewritten, checked for toggle prerequisites, and prepared for Trello comment posting only. Can prepare or, with explicit approval and Slack credentials, send the existing dashboard toggle-enable DM to Ashok Kumar N.
---

# MCSL AC Writer Reviewer

Use this skill to create the dashboard-style User Story and Acceptance Criteria output for PluginHive MCSL across Shopify, WooCommerce, BigCommerce, Magento, and PrestaShop.

This is the Codex/Claude equivalent of the dashboard `Validate AC` generation and review flow, with one publishing rule:

- Generated User Story + AC must be posted to Trello comments only.
- Do not update, overwrite, or merge into the Trello card description.

1. Understand the card/request.
2. Gather only relevant project/domain context.
3. Generate story + AC markdown in the same structure as `pipeline/card_processor.py`.
4. Review the AC for gaps, unsupported claims, duplicate scenarios, and missing toggle prerequisites.
5. Rewrite once if review findings require it.
6. Detect feature toggles and prepare the Ashok enablement note.
7. Send the Slack DM only when the user explicitly asks and credentials are available.

## Trello Publishing Rule

When the user asks to add/save/post the generated US + AC to Trello:

- add it as a new Trello comment only
- do not call `update_card_description`
- do not replace the card description
- do not merge AC into the existing description

Use `mcsl-trello-operator` for actual Trello reads/writes when the user asks to fetch or post. If Trello credentials/tools are unavailable, return a paste-ready Trello comment.

## First Reads

Before writing:

1. Read `AGENTS.md`.
2. Use the MCSL domain core research workflow when the card needs domain facts beyond local context:
   - `skills/mcsl-domain-core/SKILL.md`
   - `skills/mcsl-domain-core/references/research_workflow.md`
3. Read the exact generation/review rules when needed:
   - `skills/mcsl-ac-writer-reviewer/references/ac_generation_review.md`
4. If toggle notification is requested, read:
   - `skills/mcsl-ac-writer-reviewer/references/toggle_slack.md`
5. Inspect only directly relevant project files:
   - `pipeline/card_processor.py`
   - `pipeline/domain_validator.py`
   - `pipeline/slack_client.py`
   - `pipeline/requirement_research.py`

## Input

Best inputs:

- Trello card title, description, comments, checklists, attachments
- raw feature request
- bug/customer issue details
- existing draft AC to review/rewrite
- PR/implementation notes

If the user gives only a Trello URL and no card content is available in the conversation, use `mcsl-trello-operator` to fetch the real card title, description, comments, checklists, and attachments before generating. If Trello access is unavailable, ask the user to paste the card content.

## Context To Use

Ground the output in:

- `AGENTS.md`
- card text and comments
- linked references / PRs / Zendesk / wiki notes provided by the user
- related automation patterns from the automation repo when relevant
- backend/frontend/code context only when it helps avoid wrong AC
- known dashboard rules for AI QA, TC generation, and automation coverage

Do not invent carrier limits, unsupported cases, API behavior, UI paths, or toggle names.

## Platform Scope

Before writing AC, classify the card's customer/test platform from the card title, labels, description, comments, linked ticket, PR notes, and existing AC:

- Shopify
- WooCommerce
- BigCommerce
- Magento
- PrestaShop
- shared MCSL / platform not explicit, which defaults to Shopify for QA/support wording

Use the detected platform in `Domain Rules / MCSL Constraints`, AC preconditions, `Test Scope`, and navigation wording.

Rules:

- If the card/ticket says WooCommerce, BigCommerce, Magento, or PrestaShop, write AC around that platform's admin/storefront/checkout flow.
- If the code change is shared across platforms but the customer card is platform-specific, say implementation is shared, but QA/support validates on the customer-reported platform.
- If no platform is explicit, use Shopify as the default QA/support platform.

If local project knowledge is incomplete, browse/research official MCSL, PluginHive, or Shopify sources before generating final AC. Use the research to improve Domain Rules, AC edge cases, and Scenario Source Attribution.

## Output Structure

Return clean markdown in this structure:

```markdown
## User Story
As a [type of user], I want [goal], so that [benefit].

## Domain Rules / MCSL Constraints
...

## Acceptance Criteria
Scenario 1: <short scenario name>
Given ...
When ...
Then ...

Scenario 2: ...

## Priority
High / Medium / Low - <one sentence justification>

## Scenario Source Attribution
- Scenario 1 -> Card request; Zendesk/wiki; Related Backlog Card; MCSL docs; PluginHive/app behaviour

## Test Scope
...

## Out of Scope
- Mobile / responsive / viewport testing (we test web/desktop only).

## References
- [label](URL)
```

Omit `References` only when no links or useful source references exist.

## AC Requirements

Acceptance Criteria must:

- use Given / When / Then
- cover happy path, edge cases, error states, and regression/customer-impact cases where relevant
- state exact prerequisites for order state, product setup, store state, settings, or toggles
- state the customer/test platform prerequisite when detected
- include toggle/feature-flag enablement as a prerequisite when detected
- avoid mobile/responsive/viewport AC
- avoid unit-test/backend-only AC
- include concrete expected outcomes that later TC generation and AI QA browser verification can test

For bug/customer cards, include:

- broken current behavior
- corrected behavior
- regression scenario proving older working behavior is preserved

## Review Pass

Before finalizing, self-review using the dashboard review criteria:

- duplicate or overlapping scenarios
- vague expected results
- missing prerequisites/setup
- unsupported claims
- missing customer-impact/regression coverage
- missing toggle prerequisites
- weak source attribution

If any issue is found, rewrite the AC before returning it.

If the user asks to post to Trello, post only after this review/rewrite pass is complete.

## Toggle Handling

Detect toggles from card title, description, and comments using the same patterns as `pipeline.slack_client.detect_toggles`:

- `toggle: <name>`
- Shopify webhook/feature keys such as `shopify.webhook...enabled`
- phrases like `enable <name> toggle`, `<name> flag`, `<name> feature flag`

If toggles are detected:

1. Include them in `Domain Rules / MCSL Constraints`.
2. Include a Given prerequisite in relevant AC scenarios.
3. Add a short section after the AC:

```markdown
## Toggle Enablement
- Detected toggle(s): ...
- Store: <store if known, otherwise needs confirmation>
- Slack notification: prepared / sent / not sent
```

Do not send Slack automatically. Sending a DM is an external action and requires explicit user approval.

## Slack Notification To Ashok

If the user explicitly asks to send Ashok the toggle enablement message:

1. Confirm toggles were detected.
2. Resolve store name from user input or automation `.env` `STORE`.
3. Use `scripts/notify_toggle_ashok.py` or `mcsl-slack-operator` if a generic Slack DM is requested.
4. If sandbox/network blocks Slack, rerun with escalation.
5. Report success with Slack timestamp/channel, or the exact error.

Required env/config:

- project `.env` must load successfully
- `SLACK_BOT_TOKEN` must be set
- Slack search must find Ashok Kumar N
- store name should be known or confirmed

## Final Response

For normal generation, return:

- final story + AC markdown
- review notes, only if useful
- detected toggles and Slack status
- Trello target: comment only, not description

For Slack send requests, return:

- whether the DM was sent
- recipient resolved
- toggle names
- store
- timestamp/channel or error
