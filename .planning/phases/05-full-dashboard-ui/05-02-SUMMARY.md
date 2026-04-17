---
phase: 05-full-dashboard-ui
plan: 02
subsystem: ui
tags: [streamlit, sidebar, status-badges, session-state, knowledge-base]

# Dependency graph
requires:
  - phase: 05-01
    provides: app shell with MCSL branding, 24-class CSS, 12-key session state
provides:
  - _status_badge() pure helper returning .status-ok/.status-err HTML
  - Full with st.sidebar: block — System Status, Release Progress, KB expanders, Dry Run toggle
  - code_paths_initialized guard seeding MCSL KB paths from config
  - 5 connection check boolean flags (api_ok, trello_ok, slack_ok, sheets_ok, ollama_ok)
affects:
  - 05-03 (tab scaffold uses sidebar already rendering)
  - 06+ (dry_run toggle consumed by pipeline actions)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - _status_badge() pure function returning HTML — single st.markdown() call renders all 5 badges
    - code_paths_initialized guard — one-time session-to-config seed, prevents widget key collision
    - Ollama live HTTP check via urllib.request.urlopen with timeout=2; wrapped in try/except
    - Lazy import of rag.code_indexer inside button handlers — avoids cold-import cost on every reload

key-files:
  created: []
  modified:
    - pipeline_dashboard.py
    - tests/test_dashboard.py

key-decisions:
  - "_status_badge() placed at module level (before main()) so tests can import it directly without calling main()"
  - "Ollama status uses live urllib HTTP check (not hardcoded True) — alerts user when Ollama is offline"
  - "code_paths_initialized guard uses dict-form st.session_state['key'] = x before widget renders — avoids StreamlitAPIException on widget key collision"
  - "test_ui07_dry_run_toggle unskipped in 05-02 (not 05-03 as plan comment said) because dry_run toggle added in Task 2 sidebar block"

patterns-established:
  - "Pattern: All sidebar content inside single with st.sidebar: block in main()"
  - "Pattern: Connection checks computed as boolean flags before sidebar renders — reusable for tab gating"
  - "Pattern: KB expander lazy imports from rag.code_indexer inside button handlers"
  - "Pattern: MCSL source type strings: automation, storepepsaas_server, storepepsaas_client"

requirements-completed: [UI-02, UI-03, UI-04, UI-07]

# Metrics
duration: 1min
completed: 2026-04-17
---

# Phase 5 Plan 02: Sidebar Implementation Summary

**Full sidebar with 5 live status badges, Release Progress section, 3 MCSL Knowledge Base expanders, and Dry Run toggle — 4 tests unskipped and passing (14 passed, 1 skipped)**

## Performance

- **Duration:** 1 min
- **Started:** 2026-04-17T06:25:54Z
- **Completed:** 2026-04-17T06:26:35Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- `_status_badge(label, ok, err_hint)` pure function at module level, returning `.status-ok`/`.status-err` HTML for rendering all 5 service badges in one `st.markdown()` call
- Full `with st.sidebar:` block: System Status (5 live env/HTTP checks), Release Progress (rqa_* session state with counter row and progress bar), 3 KB expanders (automation, storepepsaas_server, storepepsaas_client), Dry Run toggle
- `code_paths_initialized` guard seeds automation_code_path, be_repo_path, fe_repo_path from config before widget keys are registered
- unskipped test_ui02, test_ui03, test_ui04, test_ui07 — all pass; 14 total passing, 1 skipped

## Task Commits

Both tasks implemented in a single commit (sidebar is one cohesive block):

1. **Task 1: _status_badge() + System Status sidebar** - `0e26736` (feat)
2. **Task 2: Release Progress, KB expanders, Dry Run toggle** - `0e26736` (feat)

## Files Created/Modified

- `pipeline_dashboard.py` - Added `_status_badge()` helper, `main()` connection checks, `code_paths_initialized` guard, full `with st.sidebar:` block
- `tests/test_dashboard.py` - Unskipped `test_ui02_status_badges`, `test_ui03_release_progress`, `test_ui04_knowledge_base`, `test_ui07_dry_run_toggle`

## Decisions Made

- `_status_badge()` placed at module level (before `main()`) so tests can import it directly without triggering `main()` execution
- Ollama status uses live urllib HTTP check (not hardcoded True) — alerts user when Ollama is offline
- `code_paths_initialized` guard uses dict-form `st.session_state["key"] = x` before widget renders — avoids `StreamlitAPIException` on widget key collision
- `test_ui07_dry_run_toggle` unskipped in this plan (not 05-03 as the original skip comment said) because the Dry Run toggle was implemented in Task 2

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Sidebar fully implemented; plan 05-03 can add 7-tab scaffold without touching sidebar code
- `dry_run` session state key available for Phase 6+ pipeline action gating
- `api_ok`, `trello_ok`, etc. computed in `main()` scope — available for tab body conditional gating in 05-03

## Self-Check

- [x] `pipeline_dashboard.py` modified with `_status_badge()` and full sidebar
- [x] `tests/test_dashboard.py` modified (4 tests unskipped)
- [x] Commit `0e26736` exists
- [x] No `BACKEND_CODE_PATH` or `FRONTEND_CODE_PATH` in pipeline_dashboard.py
- [x] 14 passed, 1 skipped, 0 failed

## Self-Check: PASSED

---
*Phase: 05-full-dashboard-ui*
*Completed: 2026-04-17*
