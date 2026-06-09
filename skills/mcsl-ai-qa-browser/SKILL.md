---
name: mcsl-ai-qa-browser
description: Use when working inside the MCSLDomainExpert project to verify dashboard-generated MCSL test cases in the real browser with Computer Use, following the same AI QA Verifier knowledge as the dashboard: parse TC metadata, reuse automation/codebase/domain knowledge before navigation, safely drive Shopify/MCSL app flows, ask QA when a non-Shopify platform is mentioned, and return pass/fail evidence without breaking current store/app state.
---

# MCSL AI QA Browser

Use this skill when the user gives a dashboard-generated test case, scenario, AC, or bug and wants real verification against the MCSL Shopify app using Codex/Claude app browser control.

Current execution surface: the available live browser flow is Shopify/MCSL.

AC/TC/docs may describe WooCommerce, BigCommerce, Magento, or PrestaShop cards. If a card/test case explicitly names one of those platforms, ask QA whether this shared MCSL behavior should be tested through the available Shopify/MCSL flow. If QA confirms, proceed and keep the reported platform visible in the evidence; if QA does not confirm, return `QA needed`.

The expected mode is:

1. Read the test case.
2. Open or use the real browser with `Computer Use`.
3. Navigate like the dashboard AI QA Verifier would.
4. Use automation repo, codebase, and domain knowledge as guidance.
5. Gather evidence.
6. Return `Pass`, `Fail`, or `Blocked/QA needed`.

This skill is not a generic browser exploration helper. It should behave like the dashboard `AI QA Verifier` translated into Codex/Claude manual-browser execution.

This skill is meant to cover the full Shopify MCSL QA surface, not only one scenario family. It should be used for:

- domestic label generation
- international label generation
- ORDERS / Order Summary label scenarios
- automation-rule label scenarios
- app iframe options and settings
- packaging settings and advanced packaging rules
- pickup scheduling
- return labels
- bulk label generation
- product-level special services
- request/response log validation
- PDF/document validation
- navigation and regression checks
- new or unfamiliar MCSL app scenarios that still fit the project domain

## First reads

Before taking action:

1. Read `AGENTS.md`.
2. Treat `AGENTS.md` as the source of truth for:
   - app architecture
   - ORDERS, Order Summary, settings, logs, and automation flows
   - order decision logic
   - verification strategies
   - known bugs already fixed
3. When the task touches orchestration or behavior, inspect only the files directly involved:
   - `pipeline/smart_ac_verifier.py`
   - `pipeline/order_creator.py`
   - `pipeline_dashboard.py`
   - `pipeline/rag_updater.py`
4. When a generated TC includes `Execution Flow`, use it as the primary route hint:
   - `orders` / `label` → ORDERS tab, Order Id filter, Order Summary, Generate Label
   - `documents` / `logs` → Order Summary Label Summary / Rate Summary / Request Log evidence
   - `settings` → hamburger menu settings persistence flow
   - `order-grid` → ORDERS grid filters/search/status flows
   - `product-admin` → MCSL App Products or Shopify Products
   - `packaging` → packaging settings and more-settings flow
   - `pickup` → pickup request/details flow
   - `return-label` → return label flow
   - `storefront` → checkout/rates flow

## Goal

Given a test case or scenario, do three things well:

1. Understand what the scenario needs.
2. Verify it in the real app using the same reliable flows the team already uses.
3. Return a concise verdict with evidence, blockers, and any durable learning that should be added back into the project.

The expectation is that the skill can handle all normal MCSL app test scenarios by combining:

- the rules in `AGENTS.md`
- the verifier logic in `pipeline/smart_ac_verifier.py`
- the order creation logic in `pipeline/order_creator.py`
- the existing Playwright automation patterns in `mcsl-test-automation`
- the exact generated TC fields: title, type, priority, preconditions, steps, expected result, preferred evidence, and execution flow

Do not narrow the skill to a single bug, a single modal, or a single feature.

## Generated TC Intake

When the user provides one or more generated test cases, parse each case before touching the browser:

- `TC ID`
- title
- type: Positive / Negative / Edge
- priority
- execution flow if present
- preconditions and setup needs
- Given / When / Then steps
- expected result
- preferred evidence

For multiple TCs:

- Run only the case(s) the user selected.
- If the user does not select, start with the highest-priority Positive case that has the clearest browser path.
- Do not treat the compact Trello QA summary as enough for full verification. Ask for the detailed TC markdown if steps are missing.

Before acting, state the concise route you will follow, such as:

`TC-2 -> ORDERS -> Order Id filter -> Order Summary -> Generate Label -> View Log -> verify request payload`.

## Browser surface

For live app verification, prefer the real browser surface the user is already using:

- Use Chrome through `Computer Use` when the task is about the real Shopify admin or the installed MCSL app.
- Always observe the current browser state before clicking.
- Keep using Computer Use for browser navigation/click/type/scroll unless the user explicitly asks for a Playwright/scripted run.
- Use the existing automation repo as the ground truth for stable selectors and working flows.
- Do not invent a brand-new flow if the automation already covers it.

Automation repo reference:

- `$MCSL_AUTOMATION_REPO_PATH`

Important related page objects and specs:

- `$MCSL_AUTOMATION_REPO_PATH/support/pages/basePage.ts`
- `$MCSL_AUTOMATION_REPO_PATH/support/pages/orders/orderGridPage.ts`
- `$MCSL_AUTOMATION_REPO_PATH/support/pages/orders/orderSummaryPage.ts`
- `$MCSL_AUTOMATION_REPO_PATH/support/pages/products/editProductDetails.ts`
- `$MCSL_AUTOMATION_REPO_PATH/support/pages/automationRules/rateAutomationPage.ts`
- `$MCSL_AUTOMATION_REPO_PATH/support/pages/automationRules/labelAutomationPage.ts`
- `$MCSL_AUTOMATION_REPO_PATH/tests/orderGrid/`
- `$MCSL_AUTOMATION_REPO_PATH/tests/orderSummary/`
- `$MCSL_AUTOMATION_REPO_PATH/tests/specialServices/`
- `$MCSL_AUTOMATION_REPO_PATH/tests/automationRules/`

Also inspect matching specs or helpers for the current scenario before inventing a new flow. Search the automation repo first with `rg`.

Search examples:

- scenario keyword: dry ice, HAL, return label, pickup, order grid, documents
- page object: OrderGrid, OrderSummary, MCSLProductsPage, RateAutomationPage, LabelAutomationPage
- evidence action: View Log, Request Log, Print Documents, Download Documents, Label Summary, Rate Summary

## Safety and Store-State Rules

The real Shopify store and MCSL app are shared QA surfaces. Test properly, but do not break current flow.

- Do not change global settings unless the TC requires it.
- If a global setting is changed, record the original value first and restore it before finishing whenever possible.
- For Additional Services toggles such as Dry Ice, carrier-specific special service, Duties & Taxes, use the dashboard cleanup pattern: reopen Settings and reset the toggle after the run when the scenario changed it.
- For product-level special services, reset the product config after verification when the TC changed it.
- For packaging tests, restore advanced packaging / carrier-box / custom-box changes when the TC requires cleanup.
- Do not delete real data, cancel labels, uninstall apps, alter credentials, or make irreversible account/subscription changes unless the user explicitly asks.
- Do not run bulk label generation on large real order sets unless the TC explicitly requires it and the user confirms the scope.
- Prefer existing unfulfilled/fulfilled test orders when the scenario allows.
- If fresh order creation is needed and the browser cannot create the right setup safely, ask QA for an order ID or explicit permission to use the project order helper.

If state was changed, include a cleanup note in the result:

- restored successfully
- not restored because `<reason>`
- QA action needed: `<specific action>`

## Supported scenario families

Treat these as first-class supported use cases:

- ORDERS / Order Summary label generation
- automation-rule label generation
- domestic shipments
- international shipments
- shipment purpose / terms / duties / taxes
- hold at location
- insurance
- COD
- signature options
- dangerous goods related flows already supported in the app
  - dry ice
  - alcohol
  - battery
- packaging settings
  - base packaging setup
  - more settings / advanced packaging
- pickup request creation and verification
- return label flows
- bulk label generation
- order grid / order summary / status validation
- request and response log validation
- label / packing slip / commercial invoice verification
- regressions in app navigation, forms, and generated outputs

If a scenario falls inside the MCSL Shopify app domain but does not exactly match a listed example, still handle it by mapping it to the nearest supported flow.

## Execution workflow

### 1. Parse the scenario

Extract:

- label flow: `manual` or `auto`
- order need: `create_new`, `create_bulk`, `existing_unfulfilled`, `existing_fulfilled`, or `none`
- whether fresh data is required or an existing QA order can be used
- shipping type: domestic, international, Canada, UK
- setup needs: products, carrier settings, app iframe settings, packaging, pickup, return label, docs, logs
- evidence type needed: UI, request JSON, response JSON, ZIP, PDF, rate log, badge, toast
- cleanup needs after verification

Use the rules already documented in `AGENTS.md`. Do not re-invent classification logic.

If the user provides only a plain-language scenario, still classify it into the existing project categories before acting.

### 2. Reuse existing knowledge before acting

If the scenario resembles an existing automated flow, inspect the related spec or page object first and mirror its sequence.

Examples:

- Carrier special service and request-log validation:
  - follow the existing Order Summary / Label Summary / View Log flow used in automation
- Shipment purpose override:
  - prefer exact combobox labels
  - use the same Order Summary setup flow already proven in automation
- Settings navigation:
  - prefer direct app routes or section-local actions over broad sidebar assumptions

For broader flows, also reuse the project’s known patterns for:

- order creation and address inference
- packaging setup and cleanup
- order summary preparation before generation
- request/response log verification
- print-document PDF verification
- return-label generation
- bulk workflow completion polling

### 3. Drive the real app

When verifying in Chrome:

1. Observe the current browser state first.
2. Confirm whether the app content is inside the Shopify app iframe.
3. Use the already known app flow:
   - label generation: ORDERS -> Add filter -> Order Id -> order link -> Prepare Shipment -> Generate Label
   - logs/documents: Order Summary -> expand Rate Summary or Label Summary -> View Log / Print Documents / Download Documents
   - settings: hamburger Menu -> search target section -> open section-local action
4. Prefer stable, visible UI signals:
   - headings
   - exact combobox labels
   - action buttons
   - badge text like `label generated`
5. After each meaningful action, verify the app actually moved to the next expected state.
6. If navigation lands somewhere unexpected, pause and re-orient from visible headings/URL before taking more actions.
7. If the next action could change shared state, confirm it is required by the TC and that cleanup is understood.

Navigation priority:

1. Existing automation/page-object flow.
2. Dashboard verifier deterministic route from `smart_ac_verifier.py`.
3. Visible browser UI with exact accessible labels.
4. Ask QA if none of the above gives a safe path.

### 4. Choose the right verification strategy

Use the lightest strategy that proves the requirement:

1. UI badge or visible state
2. Download documents ZIP for physical docs
3. Order Summary `View Log` dialogs for request/response payloads
4. Rate Summary `View Log` for pre-generation rate validation
5. `Print Documents` for PDF text checks

Do not use PDF text when the needed truth exists only in request JSON.
Do not use request JSON when a simple visible badge is enough.

When a scenario requires multiple proofs, combine them in this order:

1. visible app result
2. generated document or summary evidence
3. request/response payload evidence

## QA Needed Behavior

Ask QA only when genuinely blocked or when proceeding could damage shared state.

Good `qa_needed` questions are specific:

- "Which existing fulfilled order should I use for return-label verification?"
- "Can I enable the Dry Ice toggle temporarily and restore it after the run?"
- "The TC refers to a feature toggle name that is not visible. What exact toggle should be enabled?"
- "The browser is at Shopify account selection. Which store/account should I choose?"

Do not ask QA because of ordinary navigation uncertainty. First use:

- current page observation
- iframe vs Shopify-admin distinction
- automation repo search
- dashboard verifier rules
- exact visible labels/headings

## Lessons from MCSL AI QA debugging

Carry these forward without the user re-explaining them:

### Navigation

- Do not assume a broad app-shell click lands on the correct settings sub-surface.
- If automation already uses a direct route or section-local action, prefer that.
- For long settings pages, scroll the target section into view before asserting.

### App iframe selectors

- Prefer exact accessible labels, roles, and text inside `iframe[name="app-iframe"]`.
- Avoid broad `div` filtering when a label maps to multiple controls.
- Normalize navigation wording before clicking: `Shipping` usually means the ORDERS tab; `All Products` means hamburger menu -> Products.

### Request and label logs

- Expand `View all Rate Summary` before trying to open a rate-log row menu.
- For label request evidence, use the Label Summary row 3-dot menu, then `View Log`.
- For automation rule evidence, use hamburger menu -> Request Log and open the summary row.
- Read `.dialogHalfDivParent` content directly when the log is displayed in a dialog.

### Browser-debug mindset

- If another spec already works, compare the sequence and helper usage before changing locators.
- If a click appears correct but no file appears, question event timing and helper sequencing, not just the locator text.
- Reuse existing passing automation as the first debugging reference.

## Novel scenarios

If the scenario is new and not clearly covered:

1. Use the closest matching pattern from `AGENTS.md`.
2. Verify the scenario in the real app.
3. Report what was reused, what was new, and what was learned.
4. Propose the durable update that should be added to project knowledge.

When new durable knowledge is discovered, capture it in one of these forms:

- update `AGENTS.md` if it is a stable project rule, architecture detail, or known issue fix
- update the relevant verifier logic if the project behavior must change
- add a short “knowledge update plan” in the response if the user has not yet asked for code changes

Do not silently write broad knowledge changes unrelated to the task.

For genuinely new scenarios, the skill should still try to:

- classify the scenario
- choose the nearest proven MCSL app flow
- execute in browser
- gather evidence
- explain what is new versus what was reused
- suggest the minimum durable project update

## Result format

When giving the user the result of a live verification, include:

1. Verdict: `Pass`, `Fail`, or `Blocked`
2. What was verified
3. Evidence used
4. Steps actually executed, briefly
5. Cleanup status if settings/products/orders were changed
6. If failed: exact stuck point and best next fix
7. If blocked: exact QA question or needed input
8. If new learning was found: a short “Knowledge update” note

Keep it concise. The user prefers direct outcomes over long theory.

## Follow-On Skill Handoffs

After browser verification:

- If the user asks to notify the developer, use `mcsl-trello-operator` to resolve card devs and `mcsl-slack-operator` to send the DM.
- If QA reports a product bug that should go to Backlog, use `mcsl-bug`.
- If the run produced useful DOM/locator evidence, save the locator trace for `mcsl-automation-writer`.
- If the run taught a durable product/QA rule, pass it to `mcsl-knowledge-maintainer` after the card cycle.

## Locator Trace Handoff For Automation

When a run may later become automation, preserve the useful DOM/locator evidence for `mcsl-automation-writer`.

Save a locator trace when:

- the TC passed or partially passed
- a new page/section/control was discovered
- exact labels/buttons/toggles/inputs were important
- the flow involved settings, Products, Carriers, Automation, order grid, Order Summary, documents, request logs, pickup, or return labels

Use:

```bash
PYTHONPATH=. .venv/bin/python skills/mcsl-automation-writer/scripts/save_locator_trace.py --card-name "<card>" --card-id "<id>" --tc-id "TC-1" --route "<short route>"
```

Store traces under:

```text
data/ai_qa_locator_traces/
```

Include in the trace:

- card id/name
- TC ids
- browser route
- iframe vs Shopify admin surface
- exact visible element names
- recommended locator ideas only when grounded in observed DOM
- evidence used for pass/fail

Existing automation POM methods still take priority over saved trace locators.

## When to update project knowledge

If the user asks to make the learning permanent, prefer `mcsl-knowledge-maintainer` so the update lands in the right layer. If editing directly is clearly requested, update the relevant project file with the minimum durable change:

- `AGENTS.md` for workflow knowledge
- verifier code for runtime logic
- related docs or helper modules for repeatable patterns

If the finding belongs in the knowledge base but not yet in repo text, recommend the next action clearly:

- update `AGENTS.md`
- add a new test or helper
- run the ingest/update flow later so the RAG reflects the new behavior

## Avoid these mistakes

- Do not treat Shopify admin navigation and app iframe navigation as the same thing.
- Do not invent a second flow when an existing automation flow already works.
- Do not default to broad locators when exact labels exist.
- Do not keep clicking when the page no longer matches the expected flow; re-observe and recover.
- Do not change global settings without cleanup.
- Do not use compact Trello TC summaries as full executable test cases.
- Do not claim a fix is complete unless the scenario was rerun or the evidence clearly proves it.
- Do not overwrite env-driven path behavior with hardcoded fallbacks.
- Do not assume the skill is only for shipment-purpose or label-log bugs; it must support the full MCSL QA domain.
