---
phase: 03-label-docs-pre-requirements
plan: "01"
subsystem: testing
tags: [pytest, tdd, label-flow, dangerous-products, shopify-api, order-creator]

# Dependency graph
requires:
  - phase: 02-ai-qa-agent-core
    provides: _plan_scenario, _verify_scenario, _MCSL_WORKFLOW_GUIDE, order_creator.py with SIMPLE_PRODUCTS_JSON
provides:
  - tests/test_label_flows.py with 17 functions (1 active, 16 Wave 0 stubs)
  - _MCSL_WORKFLOW_GUIDE expanded to explicit 8-step Manual Label flow
  - create_bulk_orders() with use_dangerous_products param
  - _verify_scenario wired to pass dangerous_products flag from plan_data
affects: [03-02, 03-03, 03-04, 03-05, 03-06]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Wave 0 stub pattern: pytest.mark.skip with 'Wave 0 stub — activated in later plans'"
    - "TDD: test asserts guide content + mock _plan_scenario output shape"
    - "dangerous_products: plan_data key triggers use_dangerous_products=True in order creator"

key-files:
  created:
    - tests/test_label_flows.py
  modified:
    - pipeline/smart_ac_verifier.py
    - pipeline/order_creator.py

key-decisions:
  - "test_manual_label_flow_plan verifies guide content directly (assert 'Add filter' in _MCSL_WORKFLOW_GUIDE) rather than end-to-end Claude call"
  - "_MCSL_WORKFLOW_GUIDE already had explicit filter step — guide expanded to 8 steps for research-spec alignment"
  - "create_bulk_orders gets use_dangerous_products param passing through to create_order"
  - "_verify_scenario reads plan_data['dangerous_products'] boolean to select product source"

patterns-established:
  - "Wave 0 stub pattern: all 16 stubs skip with same reason string for grep-ability"
  - "Label flow test pattern: mock _plan_scenario, assert nav_clicks has Order Id step, look_for has LABEL CREATED"

requirements-completed: [LABEL-01, LABEL-05]

# Metrics
duration: 18min
completed: 2026-04-16
---

# Phase 03 Plan 01: Wave 0 Test Scaffold + Manual Label Flow Summary

**17-function test_label_flows.py scaffold established, _MCSL_WORKFLOW_GUIDE expanded to explicit 8-step Manual Label flow, and create_bulk_orders/create_order wired with use_dangerous_products support**

## Performance

- **Duration:** 18 min
- **Started:** 2026-04-16T00:00:00Z
- **Completed:** 2026-04-16T00:18:00Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments
- Created tests/test_label_flows.py with 17 functions: test_manual_label_flow_plan active, 16 Wave 0 stubs skip cleanly
- Expanded _MCSL_WORKFLOW_GUIDE Label Generation Flow section to explicit 8-step Manual flow (steps 6-7 split, step 8 Label Summary verification added)
- Added use_dangerous_products: bool = False param to create_bulk_orders() and wired dangerous_products flag detection in _verify_scenario

## Task Commits

Each task was committed atomically:

1. **Task 0+1 RED: Wave 0 test scaffold** - `e7931de` (test)
2. **Task 0+1 GREEN: Expand _MCSL_WORKFLOW_GUIDE** - `4a11f5f` (feat)
3. **Task 2 RED: Unskip test_label05_dangerous_products** - `0d082a2` (test)
4. **Task 2 GREEN: add use_dangerous_products param** - `5b9ebcb` (feat)

**Plan metadata:** (docs commit — see below)

_Note: TDD tasks have multiple commits (test → feat)_

## Files Created/Modified
- `tests/test_label_flows.py` — 17-function Wave 0 scaffold: test_manual_label_flow_plan active, 16 stubs skipped
- `pipeline/smart_ac_verifier.py` — _MCSL_WORKFLOW_GUIDE Label Generation Flow expanded to 8 explicit steps; _verify_scenario wired to pass dangerous_products from plan_data
- `pipeline/order_creator.py` — create_bulk_orders() gains use_dangerous_products: bool = False param

## Decisions Made
- test_manual_label_flow_plan asserts on _MCSL_WORKFLOW_GUIDE string content directly (not via Claude prompt end-to-end) — validates guide correctness without network calls
- _MCSL_WORKFLOW_GUIDE already had "Add filter" and "Order Id" content from Phase 2 — guide was expanded (not rewritten) to reach 8-step count per research spec
- _verify_scenario reads plan_data.get("dangerous_products") to detect dangerous product scenarios, keeping the detection in the plan layer where Claude sets it

## Deviations from Plan

None — plan executed exactly as written. The guide already contained the required content, which caused TDD RED to be trivially GREEN for the guide assertions. The create_bulk_orders missing param correctly caused RED for Task 2.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- tests/test_label_flows.py is ready for subsequent plans to unskip stubs (test_auto_generate_flow, test_bulk_label_flow, etc.)
- All 44 tests pass, 22 skipped (Wave 0 stubs + pre-existing skips)
- LABEL-01 and LABEL-05 requirements satisfied

---
*Phase: 03-label-docs-pre-requirements*
*Completed: 2026-04-16*
