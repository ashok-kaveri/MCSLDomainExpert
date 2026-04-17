---
phase: 03-label-docs-pre-requirements
plan: "03"
subsystem: testing
tags: [pytest, tdd, label-flow, bulk-label, shopify-order-grid, mcsl-workflow-guide]

# Dependency graph
requires:
  - phase: 03-label-docs-pre-requirements
    plan: "01"
    provides: tests/test_label_flows.py Wave 0 stubs, _MCSL_WORKFLOW_GUIDE 8-step Manual Label flow
  - phase: 03-label-docs-pre-requirements
    plan: "02"
    provides: Actions Menu Label + Return Label sections in _MCSL_WORKFLOW_GUIDE
provides:
  - _MCSL_WORKFLOW_GUIDE with full 7-step Bulk Label Flow (LABEL-03) including filter step and lowercase warning
  - test_bulk_label_flow active and passing (unskipped from Wave 0 stub)
affects: [03-04, 03-05, 03-06]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "TDD: unskip Wave 0 stub → assert guide content → expand guide section"
    - "Guide content assertions: assert exact casing strings + warning words present in _MCSL_WORKFLOW_GUIDE"

key-files:
  created: []
  modified:
    - tests/test_label_flows.py
    - pipeline/smart_ac_verifier.py

key-decisions:
  - "test_bulk_label_flow asserts 'lowercase' keyword in guide — forces explicit casing warning, not just correct button text"
  - "Bulk Label section expanded from 5-line stub to full 7-step LABEL-03 section with filter step, selector details, and explicit capital-L failure warning"
  - "_PLAN_PROMPT order judgment table already had 'bulk labels → create_bulk' mapping — no change required"

patterns-established:
  - "Wave 0 stub activation: add content assertions first (RED), then expand guide section (GREEN)"

requirements-completed: [LABEL-03]

# Metrics
duration: 8min
completed: 2026-04-16
---

# Phase 03 Plan 03: Bulk Label Flow (LABEL-03) Summary

**_MCSL_WORKFLOW_GUIDE Bulk Label section expanded to full 7-step flow with lowercase "Generate labels" warning and Fulfillment Status filter step; test_bulk_label_flow unskipped and passing**

## Performance

- **Duration:** 8 min
- **Started:** 2026-04-16T11:00:00Z
- **Completed:** 2026-04-16T11:08:00Z
- **Tasks:** 1 (TDD: 2 commits — test RED + feat GREEN)
- **Files modified:** 2

## Accomplishments
- Unskipped test_bulk_label_flow (LABEL-03) with 5 content assertions on _MCSL_WORKFLOW_GUIDE
- Expanded "Bulk Labels" stub (5 lines) to full "Bulk Label Flow (LABEL-03)" section (7 steps)
- Added explicit lowercase warning: `'Generate labels' — NOTE: lowercase "l" is EXACT, not "Generate Labels" (capital L fails all click attempts)`
- Added filter step: `Add filter → Fulfillment Status → Unfulfilled so only test orders are visible`
- Added header checkbox selector: `getByRole "row" name="#" → locator "label" → first click`
- Full test suite: 47 passed, 19 skipped (Wave 0 stubs)

## Task Commits

Each task was committed atomically:

1. **Task 1 RED: unskip test_bulk_label_flow** - `655f83f` (test)
2. **Task 1 GREEN: expand Bulk Label section in _MCSL_WORKFLOW_GUIDE** - `c4e4366` (feat)

_Note: TDD tasks have multiple commits (test → feat)_

## Files Created/Modified
- `tests/test_label_flows.py` — test_bulk_label_flow unskipped with 5 guide-content assertions
- `pipeline/smart_ac_verifier.py` — Bulk Labels section replaced with full Bulk Label Flow (LABEL-03)

## Decisions Made
- test_bulk_label_flow asserts the word "lowercase" appears in the guide — this forces an explicit warning to the agent, not just having the correct button text. Without the word "lowercase", the agent could still use "Generate Labels" (capital L).
- _PLAN_PROMPT order judgment table already mapped "bulk labels, batch label, select all orders" → create_bulk at line 710; no change needed.

## Deviations from Plan

None — plan executed exactly as written. The existing Bulk Labels stub already had "Generate labels" (lowercase l), "header checkbox", "Label Batch", and "Mark as Fulfilled", causing the initial test unskip to pass immediately. Added the "lowercase" warning assertion and "Unfulfilled" filter step assertion to produce a proper RED state before expanding the guide section.

## Issues Encountered
Initial unskip produced trivially GREEN test (guide stub had partial content). Added stronger assertions for explicit "lowercase" warning and filter step to achieve correct RED state before GREEN implementation.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- test_bulk_label_flow (LABEL-03) is active and passing
- _MCSL_WORKFLOW_GUIDE now covers all 4 label flows: Manual (LABEL-01), Actions Menu (LABEL-02), Bulk (LABEL-03), Return (LABEL-04)
- 03-04 can activate DOC-* tests for document download flows

---
*Phase: 03-label-docs-pre-requirements*
*Completed: 2026-04-16*
