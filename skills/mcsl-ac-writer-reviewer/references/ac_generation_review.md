# AC Generation And Review Rules

This reference mirrors the dashboard flow in `pipeline/card_processor.py` and `pipeline/domain_validator.py`.

Codex/Claude publishing rule:

- Generated User Story + Acceptance Criteria are for Trello comment posting only.
- Do not update the Trello card description.
- Do not use the dashboard's older card-description update behavior for this skill flow.

## Generation Intent

Act as a senior QA engineer and product owner for PluginHive MCSL across Shopify, WooCommerce, BigCommerce, Magento, and PrestaShop.

Work research-first, not card-text-first. Ground the final card in:

- card type
- customer/test platform scope
- linked references
- customer issue / Zendesk signals
- toggle / feature-flag prerequisites
- known prerequisites and risks
- research source priority
- MCSL / PluginHive / Shopify / app behavior facts

## Required Markdown Structure

```markdown
## User Story
As a [type of user], I want [goal], so that [benefit].

## Domain Rules / MCSL Constraints
Summarize concrete MCSL, PluginHive, Shopify, API, carrier, or app limitations.

## Acceptance Criteria
Scenario 1: <short title>
Given ...
When ...
Then ...

## Priority
High / Medium / Low - justify in one sentence.

## Scenario Source Attribution
- Scenario 1 -> Card request; Zendesk/wiki; Related Backlog Card; MCSL docs; PluginHive/app behaviour

## Test Scope
List app sections and automation areas that need coverage.

## Out of Scope
- Mobile / responsive / viewport testing (we test web/desktop only).

## References
- [label or URL](URL)
```

## Platform Scope Rules

Classify the platform from card title, labels, description, comments, linked ticket, PR notes, and existing AC:

- Shopify
- WooCommerce
- BigCommerce
- Magento
- PrestaShop
- shared MCSL / platform not explicit, which defaults to Shopify for QA/support wording

Use that platform in Domain Rules, Given prerequisites, Test Scope, and navigation. If the implementation is shared but the customer card is platform-specific, AC should say the shared behavior is validated on the reported platform. If no platform is explicit, use Shopify as the default QA/support platform.

## Domain Rules

Include concrete limits, constraints, prerequisites, unsupported cases, required fields, special service rules, app behavior, and carrier behavior when supported by context.

Use official MCSL findings as authoritative for carrier/API limits. Use PluginHive/app findings for app behavior.

If a limit is unclear, mark it as an open question instead of inventing it.

## Acceptance Criteria Rules

Cover:

- happy path
- edge cases
- error states
- MCSL/PluginHive limitation cases found in context
- regression scenarios for bug/customer issue cards
- setup prerequisites for store/order/product/settings/toggles
- customer/test platform prerequisites and any cross-platform scope notes

If a toggle or feature flag is required:

- do not assume it is enabled
- add it as a Domain Rule prerequisite
- add it in Given steps where relevant
- include Toggle Enablement section in final output

Do not write ACs for:

- mobile viewports
- responsive breakpoints
- `isMobileView`
- unit tests
- backend helper/function calls
- mocks/stubs

## Test Scope Areas

Reference existing areas where relevant:

- Single Label
- Rate Domestic/International
- Label Domestic/International
- Orders Grid
- Settings
- Pickup
- Return Labels
- Notifications
- Print Settings
- Locations
- Bulk Orders
- Products
- Packaging
- Additional Services

## Review Criteria

Before finalizing, check:

- duplicate or overlapping scenarios
- vague expected results
- missing prerequisites or setup assumptions
- unsupported claims not grounded in card/research
- platform drift, such as Shopify Admin assumptions on WooCommerce, BigCommerce, Magento, or PrestaShop cards
- missing customer-impact/regression coverage for bug or Zendesk-driven cards
- missing toggle prerequisites
- missing or weak scenario source attribution

If any review issue exists, rewrite before returning final markdown.

## Domain Validation Style

If validating an existing draft, produce concise findings:

- overall status: PASS / NEEDS_REVIEW / FAIL
- summary
- requirement gaps
- AC gaps
- accuracy issues
- suggestions
- rewrite instructions
- KB/domain insights

Then provide the revised AC if requested or clearly needed.
