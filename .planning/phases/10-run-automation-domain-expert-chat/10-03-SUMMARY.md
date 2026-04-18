---
phase: 10-run-automation-domain-expert-chat
plan: 03
subsystem: ui
tags: [streamlit, playwright, test-runner, threading, slack]

# Dependency graph
requires:
  - phase: 10-run-automation-domain-expert-chat
    provides: pipeline/test_runner.py (enumerate_specs, run_release_tests, TestRunResult, SpecResult)
  - phase: 08-slack-sign-off
    provides: pipeline/slack_client.py post_content_to_slack_channel()
provides:
  - Full tab_run implementation in pipeline_dashboard.py replacing the st.info() stub
  - Spec file tree with folder groupings (enumerate_specs), per-spec checkboxes, browser project selector
  - Background thread execution of Playwright specs via run_release_tests()
  - Pass/fail/duration results table with color-coded icons and 4-metric header row
  - Post to Slack button posting formatted run results after completion
  - Warnings when MCSL_AUTOMATION_REPO_PATH unset or auth-chrome.json missing
affects: [future-run-automation-extensions, phase-10-complete]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - run_* session state prefix (run_running, run_result, run_selected_specs) established for Run Automation tab
    - Default-arg thread closure pattern (rp=repo_path, specs=selected, proj=project) prevents late-binding bugs
    - Lazy import of pipeline.test_runner inside tab_run block — avoids cold-start cost on every Streamlit reload

key-files:
  created: []
  modified:
    - pipeline_dashboard.py

key-decisions:
  - "run_* session state keys (run_running, run_result, run_selected_specs) added to _init_state() under Phase 10 comment block"
  - "Default-arg lambda closure for _run_tests_thread captures repo_path/specs/project at call time — prevents late-binding bugs in Streamlit reruns"
  - "Lazy import from pipeline.test_runner inside tab_run — consistent with card_processor lazy import pattern from Phase 4"
  - "Post to Slack lazy-imports post_content_to_slack_channel inside button handler — no cold-start cost"
  - "Auth-chrome.json warning is st.warning (not st.error) — lets user decide to proceed without blocking the UI"

patterns-established:
  - "run_* key prefix scoped to Run Automation tab — avoids collision with sav_* (Phase 4), auto_* (Phase 9)"
  - "Default-arg thread closure: def _run_tests_thread(rp=repo_path, specs=selected, proj=project)"

requirements-completed: [RUN-01]

# Metrics
duration: ~5min
completed: 2026-04-18
---

# Phase 10 Plan 03: Run Automation Tab Full Implementation Summary

**Full tab_run implemented in pipeline_dashboard.py: spec file tree with folder-grouped checkboxes, background Playwright thread execution, 4-metric results header, per-spec pass/fail icons, Post to Slack button; 137 tests GREEN**

## Performance

- **Duration:** ~5 min
- **Started:** 2026-04-18T09:58:00Z
- **Completed:** 2026-04-18T10:05:00Z
- **Tasks:** 2 (Task 1 implementation + Task 2 human-verify approved)
- **Files modified:** 1

## Accomplishments
- Replaced tab_run st.info() stub with full Run Automation UI in pipeline_dashboard.py
- Spec file tree: enumerate_specs() groups .spec.ts files by folder with st.expander + per-spec st.checkbox
- Background thread launch via threading.Thread with default-arg closure (run_running flag, run_result store)
- Results display: 4-column metrics row (Total/Passed/Failed/Duration) + per-spec rows with status icons
- Post to Slack button formats and posts run results to configured SLACK_CHANNEL after run completes
- Warning shown when MCSL_AUTOMATION_REPO_PATH unset/missing or auth-chrome.json absent
- Full suite remains GREEN: 137 passed, 7 skipped, 0 regressions

## Task Commits

1. **Task 1: Add run_* session state keys to _init_state() and implement tab_run UI** - `0c814b6` (feat)
2. **Task 2: Human verify — Run Automation tab and Domain Expert Chat UI** - checkpoint approved

## Files Created/Modified
- `pipeline_dashboard.py` - tab_run block fully implemented; 3 new _init_state() keys (run_running, run_result, run_selected_specs)

## Decisions Made
- run_* prefix chosen for Run Automation session state keys — distinct from sav_* (Phase 4 SAV runner), auto_* (Phase 9 automation writer)
- Default-arg closure `def _run_tests_thread(rp=repo_path, specs=selected, proj=project)` captures mutable loop variables at call time — established pattern from Phase 7
- Lazy import of pipeline.test_runner inside tab_run block — avoids cold-start cost on every Streamlit reload (consistent with card_processor pattern)
- auth-chrome.json check uses st.warning not st.error — non-blocking, user may choose to proceed

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Phase 10 complete: RUN-01, CHAT-01, CHAT-02 all implemented and GREEN
- pipeline_dashboard.py has all 7 tabs fully implemented end-to-end
- ui/chat_app.py has ask_domain_expert() and QUICK_ASKS for Domain Expert Chat
- All 137 tests passing, 7 skipped (wave-gated stubs)

---
*Phase: 10-run-automation-domain-expert-chat*
*Completed: 2026-04-18*
