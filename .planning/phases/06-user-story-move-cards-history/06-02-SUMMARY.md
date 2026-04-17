---
phase: 06-user-story-move-cards-history
plan: 02
subsystem: pipeline_dashboard
tags: [user-story, trello, history, tdd, streamlit]
dependency_graph:
  requires: ["06-01"]
  provides: ["tab_us UI", "_load_history", "_save_history", "_HISTORY_FILE"]
  affects: ["06-03 History tab (consumes _load_history/_HISTORY_FILE)"]
tech_stack:
  added: []
  patterns: ["TDD RED-GREEN", "lazy imports inside button handlers", "session_state defaults in _init_state"]
key_files:
  created: []
  modified:
    - pipeline_dashboard.py
    - tests/test_dashboard.py
decisions:
  - "_save_history() only called when dry_run is False — consistent with all other Trello/write operations"
  - "History helpers added at module level so 06-03 History tab can import them directly"
  - "_init_state() loads history from disk only when pipeline_runs is empty — avoids overwriting in-session state"
metrics:
  duration: 2 min
  completed: "2026-04-17"
  tasks: 2
  files: 2
---

# Phase 6 Plan 02: User Story Tab UI + History Helpers Summary

**One-liner:** Full generate→refine→push-to-Trello UI in tab_us with module-level history persistence helpers (_load_history, _save_history) wired to data/pipeline_history.json.

## Tasks Completed

| Task | Type | Description | Commit |
|------|------|-------------|--------|
| 1 | TDD RED | 4 failing tests for US-01/US-02/US-03 | aa56511 |
| 2 | TDD GREEN | Full tab_us implementation + history helpers | 9bc52f3 |

## Implementation Details

### History Helpers (module level)

Added to `pipeline_dashboard.py` above `_CSS`:

- `_HISTORY_FILE`: `Path(__file__).resolve().parent / "data" / "pipeline_history.json"`
- `_load_history() -> dict`: reads JSON from disk, returns `{}` on absence or parse error
- `_save_history(runs: dict) -> None`: creates `data/` directory if missing, writes JSON with indent=2

### _init_state() Extensions

Added 8 User Story session state keys:
- `us_request_input`, `us_result`, `us_history`, `us_card_title`
- `us_list_mode` (default: "Existing list"), `us_existing_list`, `us_new_list_name`, `us_assign_members`

Added post-loop history load: `if not st.session_state.get("pipeline_runs"): st.session_state["pipeline_runs"] = _load_history()`

### tab_us Implementation

Replaced `st.info("User Story generation coming in Phase 6.")` stub with:

1. **Generate section** — `st.text_area` (key=`us_request_input`), "✨ Generate" button calling `generate_user_story()` lazily, stores result to `us_result` + appends to `us_history`
2. **Refine section** — renders only when `us_result` is set; "🔁 Refine" button calls `refine_user_story()` and appends refined version to `us_history`
3. **Push to Trello section** — card title input, list mode radio (Existing/Create new), Trello list selectbox or new list name input, member multiselect, "📌 Create Trello Card" button
4. **History save** — on successful push: builds history entry with card id, name, url, approved_at, release; calls `_save_history(runs)` if `not dry_run`

TrelloClient() wrapped in try/except — gracefully degrades when Trello env vars missing.

## Test Results

| Suite | Before | After |
|-------|--------|-------|
| tests/test_dashboard.py | 15 passed | 19 passed |
| tests/ (full) | 87 passed, 7 skipped | 91 passed, 7 skipped |

New tests:
- `test_us_tab_generate_calls_writer` — asserts `generate_user_story` in source
- `test_us_tab_refine_calls_refiner` — asserts `refine_user_story` + `us_history` in source
- `test_us_tab_push_calls_trello` — asserts `create_card_in_list` + `us_card_title` + `us_assign_members` in source
- `test_us_tab_history_saved_on_push` — asserts `_save_history`/`_load_history`/`_HISTORY_FILE` in source and callable on module

## Deviations from Plan

None — plan executed exactly as written.

## Self-Check

### Files Exist
- pipeline_dashboard.py: modified in place
- tests/test_dashboard.py: modified in place

### Commits Exist
- aa56511 (RED tests)
- 9bc52f3 (GREEN implementation)

## Self-Check: PASSED
