---
phase: 06-user-story-move-cards-history
plan: "03"
subsystem: pipeline_dashboard
tags: [move-cards, history, trello, tdd, streamlit]
dependency_graph:
  requires: ["06-01", "06-02"]
  provides: ["MC-01", "HIST-01"]
  affects: ["pipeline_dashboard.py", "tests/test_dashboard.py"]
tech_stack:
  added: []
  patterns:
    - "TDD RED/GREEN: 5 tests written failing first, then implementation made them pass"
    - "move_card_to_list_by_id (PUT /1/cards/{id} with idList) — direct ID method, no name lookup"
    - "Session state keys dd_list_select/dd_move_target/dd_cards/dd_checked/dd_select_all"
    - "History loaded from disk via _load_history() inside _init_state() on first render"
key_files:
  created: []
  modified:
    - pipeline_dashboard.py
    - tests/test_dashboard.py
decisions:
  - "Use move_card_to_list_by_id exclusively — name variant forbidden; builds name->ID map from get_lists()"
  - "Audit comment posted after each card move via add_comment() with 'Moved to {list} by MCSL QA Pipeline'"
  - "dry_run toggle gates both move_card_to_list_by_id and add_comment calls"
  - "dd_chk_{card.id} per-card widget key prefix scoped to avoid collision with future rqa_chk_ keys in Phase 7"
  - "Card list cleared from session state after successful move to prevent stale UI state"
metrics:
  duration_minutes: 2
  completed_date: "2026-04-17"
  tasks_completed: 2
  files_modified: 2
---

# Phase 6 Plan 03: Move Cards Tab + History Tab Summary

Wire `tab_devdone` (Move Cards) and `tab_history` (Pipeline History) in `pipeline_dashboard.py`, replacing Phase 5 stubs with full TDD-driven implementations using `move_card_to_list_by_id` and `pipeline_runs` session state.

## What Was Built

### tab_devdone — Move Cards
- Source list selectbox (`dd_list_select`, default "Dev Done") and target list selectbox (`dd_move_target`, default "Ready for QA") in a 3-column layout
- Load button fetches cards from source list via `TrelloClient.get_cards_in_list()`, stores in `dd_cards` session state
- Select-all toggle (`dd_select_all`) with per-card checkboxes using `dd_chk_{card.id}` widget key pattern
- Move N cards button calls `TrelloClient.move_card_to_list_by_id(card.id, target_id)` — direct PUT by list ID, no name lookup
- Audit comment posted after each move: `tc.add_comment(card.id, "Moved to {list} by MCSL QA Pipeline")`
- Respects `dry_run` toggle — skips Trello writes when enabled
- Clears card list from session state after successful move

### tab_history — Pipeline History
- Shows `{len(runs)} run(s) recorded` header with Clear history button
- Clear history button wipes `pipeline_runs` from session state and disk via `_save_history({})`
- Per-entry expandables showing card_name, approved_at, release, Trello link (card_url), test_cases preview
- Gracefully shows empty state message when no runs recorded

### _init_state() extension
- Added 5 new session state keys: `dd_list_select`, `dd_move_target`, `dd_cards`, `dd_checked`, `dd_select_all`

## Tests

| Test | Description | Status |
|------|-------------|--------|
| test_mc_tab_source_and_target_present | dd_list_select, dd_move_target, Dev Done, Ready for QA | PASS |
| test_mc_tab_move_uses_by_id | move_card_to_list_by_id, dd_chk_, add_comment | PASS |
| test_mc_tab_select_all | dd_select_all, dd_checked | PASS |
| test_hist_tab_renders_runs | pipeline_runs, approved_at, card_url, Clear history | PASS |
| test_hist_tab_load_from_disk | _load_history callable, _HISTORY_FILE is Path, returns dict | PASS |

**Total: 24 dashboard tests pass; 96 full suite pass (7 skipped)**

## Commits

| Hash | Description |
|------|-------------|
| 51c03e6 | test(06-03): add failing tests for Move Cards and History tabs (RED) |
| 179ead5 | feat(06-03): wire Move Cards (tab_devdone) and History (tab_history) tabs (GREEN) |

## Smoke Checks

- `grep "move_card_to_list_by_id" pipeline_dashboard.py` — 1 match (Move Cards handler)
- `grep "move_card_to_list\b" pipeline_dashboard.py` — 0 matches (name variant not used)

## Deviations from Plan

None — plan executed exactly as written.

## Self-Check: PASSED

- pipeline_dashboard.py modified with all required patterns
- tests/test_dashboard.py has 24 tests (19 existing + 5 new)
- Commits 51c03e6 and 179ead5 exist in git log
- No `move_card_to_list` (name variant) in pipeline_dashboard.py
