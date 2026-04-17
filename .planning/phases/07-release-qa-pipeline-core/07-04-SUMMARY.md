---
phase: 07-release-qa-pipeline-core
plan: 04
subsystem: ui
tags: [streamlit, trello, gspread, google-sheets, release-qa, test-cases]

# Dependency graph
requires:
  - phase: 07-release-qa-pipeline-core
    provides: "Steps 1-2 per-card accordion (validation, AI QA Agent), generate_test_cases, write_test_cases_to_card, append_to_sheet implementations"

provides:
  - "Step 3 per-card TC generation with editable text_area and regenerate support"
  - "Step 4 per-card Approve & Save button: writes to Trello + Google Sheets, sets approved flag, saves history"
  - "append_to_sheet result display: rows_added count, sheet tab name, duplicate warning"
  - "Approved cards show Approved badge; history persisted via _save_history()"

affects: [phase-08-slack-escalation, pipeline_dashboard.py]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Two-step approval flow: TC generation then explicit approval persists to Trello + Sheets atomically"
    - "approved_store[card.id] = True pattern for per-card approval state across Streamlit reruns"
    - "Pre-implementation gate: verify upstream test (test_rqa04_append_to_sheet_returns_meta) GREEN before touching UI"

key-files:
  created: []
  modified:
    - pipeline_dashboard.py

key-decisions:
  - "write_test_cases_to_card and append_to_sheet imported at module top (not lazy) — both are stable, required for Step 4 button handler"
  - "approved_store[card.id] = True (not rqa_approved[card.id]) used inline — synced back to session_state via st.session_state['rqa_approved'] = approved_store"
  - "Error isolation: Trello write and Sheets write each in separate try/except — partial failure shows warnings but still marks card approved and saves history"

patterns-established:
  - "Step 3/4 inserted BEFORE Phase 8 placeholder comment — preserves placeholder for future Slack DM escalation plan"
  - "tc_store updated inline after TC generation and after text_area edit — single source of truth via rqa_test_cases session key"

requirements-completed: [RQA-04]

# Metrics
duration: 7min
completed: 2026-04-17
---

# Phase 7 Plan 04: Release QA Steps 3-4 Summary

**Per-card TC generation (Step 3) + Trello/Google Sheets approval flow (Step 4) completing the full Release QA pipeline in pipeline_dashboard.py**

## Performance

- **Duration:** 7 min
- **Started:** 2026-04-17T17:39:03Z
- **Completed:** 2026-04-17T17:46:00Z
- **Tasks:** 1 (imports + Steps 3-4 implementation as single atomic unit)
- **Files modified:** 1

## Accomplishments
- Added `write_test_cases_to_card` and `append_to_sheet` imports to module top
- Step 3: Generate Test Cases button with spinner, editable text_area (tc_text_{card.id}), Regenerate button, syncs back to rqa_test_cases session state
- Step 4: Approve & Save to Trello + Sheets button — calls write_test_cases_to_card then append_to_sheet, sets approved_store[card.id]=True, calls _save_history(), shows rows_added + tab name + duplicate warnings
- Full test suite: 111 passed, 7 skipped, 0 failures

## Task Commits

1. **Task 1: Steps 3-4 + imports** - `a11cd99` (feat)

**Plan metadata:** (docs commit pending)

## Files Created/Modified
- `/Users/madan/Documents/MCSLDomainExpert/.claude/worktrees/objective-archimedes/pipeline_dashboard.py` - Added imports for write_test_cases_to_card + append_to_sheet; inserted Steps 3-4 in per-card accordion before Phase 8 placeholder

## Decisions Made
- `write_test_cases_to_card` and `append_to_sheet` imported at module top (not lazy) — both called inside Streamlit button handler, not on cold start; no startup cost concern
- Error isolation: Trello write and Sheets write each wrapped in separate try/except — partial failures show warnings but card still marked approved and history saved
- Pre-implementation gate passed: `test_rqa04_append_to_sheet_returns_meta` GREEN before any UI changes

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
- None.

## User Setup Required
None - no external service configuration required (existing Trello + Sheets credentials from env).

## Next Phase Readiness
- Full Release QA pipeline complete: Steps 1-4 per-card accordion fully implemented
- Phase 8 placeholder comments preserved at correct insertion point for Slack DM / toggle escalation
- 111 tests green, ready for Phase 8

---
*Phase: 07-release-qa-pipeline-core*
*Completed: 2026-04-17*
