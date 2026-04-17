---
phase: 04-pipeline-dashboard
plan: "02"
subsystem: ui
tags: [streamlit, threading, dashboard, verify_ac]

# Dependency graph
requires:
  - phase: 04-01
    provides: pipeline_dashboard.py scaffold with session state keys (sav_running, sav_stop, sav_result, sav_prog)
provides:
  - start_run() daemon thread launcher in pipeline_dashboard.py
  - _run_pipeline() background worker with result-before-flag ordering
  - Run button wired in main Streamlit script body
affects:
  - 04-03 (progress polling loop reads sav_prog and sav_running)
  - 04-04 (render_report consumes sav_result populated by _run_pipeline)
  - 04-05 (card_processor enriches card_name before start_run call)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Result-before-flag ordering: sav_result assigned before sav_running=False in worker thread"
    - "Module-level worker function: _run_pipeline defined at top level (not nested) to allow threading"
    - "Lazy import: verify_ac imported inside _run_pipeline to keep startup fast"

key-files:
  created: []
  modified:
    - pipeline_dashboard.py
    - tests/test_dashboard.py

key-decisions:
  - "_run_pipeline() accesses st.session_state dict keys directly — never calls any st.* render functions"
  - "sav_result = report.to_dict() assigned before sav_running = False to avoid polling race condition"
  - "Exception handler stores error dict with same schema as VerificationReport.to_dict() for uniform render_report handling"

patterns-established:
  - "Worker thread: write result FIRST (sav_result), clear flag SECOND (sav_running=False)"
  - "No st.* calls in _run_pipeline — st.session_state dict writes are allowed (not render calls)"

requirements-completed:
  - DASH-02

# Metrics
duration: 8min
completed: 2026-04-17
---

# Phase 4 Plan 02: Threading — start_run() and _run_pipeline() Worker

**Daemon-thread launcher (start_run) and background worker (_run_pipeline) with result-before-flag ordering and no st.* render calls**

## Performance

- **Duration:** 8 min
- **Started:** 2026-04-17T07:49:00Z
- **Completed:** 2026-04-17T07:57:00Z
- **Tasks:** 2 (Task 1 TDD + Task 2 wiring)
- **Files modified:** 2

## Accomplishments
- Implemented `_run_pipeline()` worker at module level — calls `verify_ac()`, writes `sav_result` before `sav_running=False`, catches exceptions with uniform error dict
- Implemented `start_run()` — sets session state flags, clears stop event, launches `daemon=True` thread
- Wired Run button in main Streamlit script body with input validation and `st.rerun()` after launch
- `test_dash02_threading` passes; full suite shows 2 passed, 3 skipped, 0 errors

## Task Commits

Each task was committed atomically:

1. **Task 1 (TDD RED): Unskip test_dash02_threading** - `87850fb` (test)
2. **Task 1 (TDD GREEN): Implement _run_pipeline() and start_run()** - `29620c6` (feat)
3. **Task 2: Wire Run button to start_run()** - `4a66985` (feat)

_Note: TDD task has RED commit then GREEN commit_

## Files Created/Modified
- `pipeline_dashboard.py` — Added `_run_pipeline()` worker and full `start_run()` implementation; added Run button handler block
- `tests/test_dashboard.py` — Removed `@pytest.mark.skip(reason="wave:04-02")` from `test_dash02_threading`

## Decisions Made
- `_run_pipeline()` uses `st.session_state` dict writes only — no `st.write`, `st.progress`, or other render calls — per CONTEXT.md threading contract
- Error handler stores `{"error": str(exc), "card_name": ..., "total": 0, "summary": {...}, ...}` — same shape as `VerificationReport.to_dict()` so `render_report()` needs no special-case for errors
- `start_run()` sets `sav_prog["label"] = "Starting\u2026"` immediately so UI shows feedback before first `_progress_cb` call

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- `start_run()` and `_run_pipeline()` fully implemented and tested
- `sav_running`, `sav_result`, `sav_prog` correctly managed by worker thread
- Ready for 04-03: progress polling loop (reads `sav_running` and `sav_prog` on each rerun)
- Ready for 04-04: `render_report()` implementation (consumes `sav_result` populated here)

---
*Phase: 04-pipeline-dashboard*
*Completed: 2026-04-17*
