---
phase: 03-label-docs-pre-requirements
plan: "02"
subsystem: testing
tags: [pytest, tdd, label-flow, actions-menu, return-label, workflow-guide]

# Dependency graph
requires:
  - phase: 03-label-docs-pre-requirements
    provides: tests/test_label_flows.py Wave 0 scaffold, _MCSL_WORKFLOW_GUIDE 8-step Manual flow

provides:
  - _MCSL_WORKFLOW_GUIDE extended with Actions Menu Label Flow (LABEL-02) section
  - _MCSL_WORKFLOW_GUIDE extended with Return Label Flow (LABEL-04) section with existing_fulfilled warning
  - test_auto_generate_flow active and passing (LABEL-02)
  - test_return_label_flow active and passing (LABEL-04)
affects: [03-03, 03-04, 03-05, 03-06]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "TDD guide content assertion: unskip test → assert string in _MCSL_WORKFLOW_GUIDE → add section to guide → pass"
    - "Actions menu pattern: header checkbox + buttons-row > button:nth-child(4) + Actions search"

key-files:
  created: []
  modified:
    - pipeline/smart_ac_verifier.py
    - tests/test_label_flows.py

key-decisions:
  - "test_auto_generate_flow (not test_actions_menu_label_flow) is the actual stub name in the file — plan referenced a renamed version but behavior is identical"
  - "_PLAN_PROMPT order judgment table already had 'return label' -> existing_fulfilled mapping — no change needed"
  - "Return Label section placed after Actions Menu Label section, both after existing Bulk Labels section"

patterns-established:
  - "Guide section structure: ### Title, bullet locator details, numbered steps, status verification"

requirements-completed: [LABEL-02, LABEL-04]

# Metrics
duration: 7min
completed: 2026-04-16
---

# Phase 03 Plan 02: Actions Menu Label + Return Label Flows Summary

**_MCSL_WORKFLOW_GUIDE extended with Actions Menu Label (LABEL-02) and Return Label (LABEL-04) sections; both tests unskipped and passing**

## Performance

- **Duration:** 7 min
- **Started:** 2026-04-16T10:41:59Z
- **Completed:** 2026-04-16T10:49:15Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- Added "Actions Menu Label Flow" section to _MCSL_WORKFLOW_GUIDE with Actions button locator, Generate Label menu item, and Label Batch page reference
- Added "Return Label Flow" section to _MCSL_WORKFLOW_GUIDE with existing_fulfilled warning, Create Return Label menu item, Submit button, and Return Created status
- Unskipped test_auto_generate_flow (LABEL-02) and test_return_label_flow (LABEL-04) — both pass
- Full suite: 46 passed, 20 skipped, 0 failures

## Task Commits

Each task was committed atomically:

1. **Task 1 RED: unskip test_auto_generate_flow** - `bc3ec2d` (test)
2. **Task 1 GREEN: add Actions Menu Label section** - `2656622` (feat)
3. **Task 2 RED: unskip test_return_label_flow** - `2c5dbaf` (test)
4. **Task 2 GREEN: add Return Label section** - `5e6e5e0` (feat)

_Note: TDD tasks have multiple commits (test → feat)_

## Files Created/Modified
- `pipeline/smart_ac_verifier.py` — _MCSL_WORKFLOW_GUIDE extended with two new sections: Actions Menu Label Flow and Return Label Flow
- `tests/test_label_flows.py` — test_auto_generate_flow and test_return_label_flow unskipped with content assertions

## Decisions Made
- The plan specified unskipping `test_actions_menu_label_flow` but the actual Wave 0 stub was named `test_auto_generate_flow` (same LABEL-02 docstring). Activated the existing stub rather than creating a duplicate.
- _PLAN_PROMPT order judgment table already mapped "return label" to `existing_fulfilled` (from Phase 2). No changes needed there — the guide section references `existing_fulfilled` to match.

## Deviations from Plan

None — plan executed exactly as written. The only minor discrepancy was the test function name (`test_auto_generate_flow` vs `test_actions_menu_label_flow` in plan prose) — resolved by activating the existing stub, which is the correct file state.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- _MCSL_WORKFLOW_GUIDE now covers Manual, Bulk, Actions Menu, and Return Label flows
- test_label_flows.py has 4 active tests (LABEL-01, LABEL-02, LABEL-04, LABEL-05)
- 14 Wave 0 stubs remain for Plans 03-03 through 03-06
- LABEL-02 and LABEL-04 requirements satisfied

---
*Phase: 03-label-docs-pre-requirements*
*Completed: 2026-04-16*
