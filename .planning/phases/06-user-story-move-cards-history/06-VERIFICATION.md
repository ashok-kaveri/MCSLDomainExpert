---
phase: 06-user-story-move-cards-history
verified: 2026-04-17T00:00:00Z
status: passed
score: 8/8 must-haves verified
re_verification: false
---

# Phase 6: User Story + Move Cards + History Verification Report

**Phase Goal:** User Story tab (generate AC from description, refine, push to Trello), Move Cards tab (move between lists), History tab (persisted pipeline runs)
**Verified:** 2026-04-17
**Status:** passed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `generate_user_story(request)` returns non-empty markdown (User Story + AC sections) | VERIFIED | pipeline/user_story_writer.py L105-126; full prompt formatting + Claude invocation |
| 2 | `generate_user_story()` handles empty RAG without crashing — falls back gracefully | VERIFIED | `_fetch_domain_context` and `_fetch_code_context` each catch `Exception` and return fallback strings (L83-98) |
| 3 | `refine_user_story(previous, change_req)` returns updated markdown | VERIFIED | pipeline/user_story_writer.py L129-149; prompt formats both arguments, returns `response.content.strip()` |
| 4 | `TrelloClient.move_card_to_list_by_id(card_id, list_id)` calls PUT directly — no name lookup | VERIFIED | trello_client.py L168-176; calls `self._put(f"cards/{card_id}", idList=list_id)` with no `get_list_by_name` call |
| 5 | tab_us has full generate/refine/push UI (not a stub) | VERIFIED | pipeline_dashboard.py L570-709; textarea `us_request_input`, Generate button, Refine section, Push to Trello with `create_card_in_list` |
| 6 | tab_devdone uses `move_card_to_list_by_id` (not name variant); posts audit comment | VERIFIED | pipeline_dashboard.py L817: `tc.move_card_to_list_by_id(card.id, target_id)`; L818: `tc.add_comment(...)`; `grep "move_card_to_list\b"` returns 0 matches |
| 7 | tab_history reads `pipeline_runs` and renders entries with approved_at / card_url / Clear history | VERIFIED | pipeline_dashboard.py L847-869; iterates `pipeline_runs`, shows expandables with `approved_at`, `card_url`, Clear history button |
| 8 | `data/pipeline_history.json` created on first push (path resolves correctly) | VERIFIED | `_HISTORY_FILE = Path(__file__).resolve().parent / "data" / "pipeline_history.json"` (L18); `_save_history` calls `mkdir(parents=True, exist_ok=True)` (L33) before write — file not yet created because no push has run, which is correct |

**Score:** 8/8 truths verified

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `pipeline/user_story_writer.py` | `generate_user_story()`, `refine_user_story()`, `US_WRITER_PROMPT`, `US_REFINE_PROMPT` | VERIFIED | 149 lines; all four exports present at module level |
| `pipeline/trello_client.py` | `TrelloClient` with `move_card_to_list_by_id`, `TrelloCard`, `TrelloList` | VERIFIED | 184 lines; all three exports; `move_card_to_list_by_id` at L168 |
| `pipeline_dashboard.py` | `tab_us`, `tab_devdone`, `tab_history` implemented; `_load_history`, `_save_history`, `_HISTORY_FILE` at module level | VERIFIED | 888 lines; history helpers at L18-34; tab_us at ~L560+; tab_devdone at ~L720+; tab_history at ~L840+ |
| `tests/test_pipeline.py` | 11 tests covering US-01/02/03, MC-01, HIST-01 | VERIFIED | 11 collected, 11 passed (0 skipped — 06-03 completion unblocked the 3 history tests) |
| `tests/test_dashboard.py` | 24 tests (15 original + 4 US tab + 5 MC/HIST) | VERIFIED | 24 collected, 24 passed |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `pipeline_dashboard.py tab_us` | `pipeline.user_story_writer.generate_user_story` | lazy import inside Generate button handler | WIRED | L581: `from pipeline.user_story_writer import generate_user_story` |
| `pipeline_dashboard.py tab_us` | `pipeline.user_story_writer.refine_user_story` | lazy import inside Refine button handler | WIRED | L606: `from pipeline.user_story_writer import refine_user_story` |
| `pipeline_dashboard.py tab_us Push handler` | `_save_history()` | called after `create_card_in_list` succeeds | WIRED | L709: `_save_history(runs)` gated on `not dry_run` |
| `pipeline_dashboard.py tab_devdone Move handler` | `TrelloClient.move_card_to_list_by_id` | lazy import inside Move button handler | WIRED | L817: `tc.move_card_to_list_by_id(card.id, target_id)` |
| `pipeline_dashboard.py tab_devdone Move handler` | `TrelloClient.add_comment` | audit comment after each card move | WIRED | L818-820: `tc.add_comment(card.id, "Moved to {list} by MCSL QA Pipeline")` |
| `pipeline_dashboard.py tab_history` | `st.session_state.pipeline_runs` | loaded from disk by `_init_state()` | WIRED | L177-178: `_init_state` loads `_load_history()` into `pipeline_runs`; L847: `runs = st.session_state.get("pipeline_runs", {})` |
| `pipeline/user_story_writer.py` | `rag.vectorstore.search()` | `_fetch_domain_context()` | WIRED | L78: `from rag.vectorstore import search` |
| `pipeline/user_story_writer.py` | `rag.code_indexer.search_code()` | `_fetch_code_context()` | WIRED | L91: `from rag.code_indexer import search_code` |
| `pipeline/trello_client.py` | `PUT /1/cards/{card_id}` with `idList=list_id` | `move_card_to_list_by_id` body | WIRED | L174: `self._put(f"cards/{card_id}", idList=list_id)` — no name lookup |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| US-01 | 06-01, 06-02 | Generate User Story + AC from plain-English feature description | SATISFIED | `generate_user_story()` in user_story_writer.py; tab_us Generate section wired to it; test_us01_* passes |
| US-02 | 06-01, 06-02 | Refine User Story iteratively | SATISFIED | `refine_user_story()` in user_story_writer.py; tab_us Refine section appends to `us_history`; test_us02_* passes |
| US-03 | 06-01, 06-02 | Push User Story as Trello card (with list/member assignment) | SATISFIED | `TrelloClient.create_card_in_list()` called with `list_id`, `desc=us_result`, `member_ids`; test_us03_* passes |
| MC-01 | 06-01, 06-03 | Move Trello cards between lists using direct-ID method (no name resolution) | SATISFIED | `move_card_to_list_by_id` in trello_client.py; used exclusively in tab_devdone; `grep "move_card_to_list\b"` returns 0 matches; test_mc01_* passes |
| HIST-01 | 06-02, 06-03 | Persist pipeline runs to `data/pipeline_history.json`; History tab shows entries | SATISFIED | `_save_history`/`_load_history` at module level; tab_history renders `pipeline_runs` with expandables; test_hist01_* passes (all 3) |

---

### Anti-Patterns Found

None. No TODO/FIXME/placeholder/stub patterns in any Phase 6 files. No empty handlers. The only `st.info(...)` stubs in `pipeline_dashboard.py` are for Phase 7-10 tabs which are outside this phase's scope.

---

### Human Verification Required

The following behaviors require a running Streamlit environment to verify:

**1. Generate Button Spinner and Result Rendering**
- Test: Launch `streamlit run pipeline_dashboard.py`, navigate to User Story tab, type a feature description, click "Generate".
- Expected: Spinner appears, then generated markdown renders with User Story + Acceptance Criteria sections.
- Why human: Claude API call requires real credentials; UI rendering cannot be verified with grep.

**2. Trello Integration End-to-End**
- Test: With valid TRELLO_API_KEY, TRELLO_TOKEN, TRELLO_BOARD_ID in .env, generate a story and push it to a Trello list.
- Expected: Card appears in Trello, `data/pipeline_history.json` is created, History tab shows the entry.
- Why human: Requires real Trello credentials and board access.

**3. Move Cards Workflow**
- Test: With Trello credentials set, navigate to Move Cards tab, select source "Dev Done", click Load, check cards, click Move.
- Expected: Cards move to target list; audit comment "Moved to ... by MCSL QA Pipeline" appears on each card.
- Why human: Requires live Trello board with cards.

**4. Dry Run Toggle Behavior**
- Test: Enable Dry Run toggle, attempt push in User Story tab and move in Move Cards tab.
- Expected: UI reports success but no actual Trello writes occur; history saved to session state but not to disk.
- Why human: Conditional logic `if not dry_run:` verified by code inspection but effect requires running UI.

---

### Test Suite Summary

| Suite | Collected | Passed | Skipped | Failed |
|-------|-----------|--------|---------|--------|
| tests/test_pipeline.py | 11 | 11 | 0 | 0 |
| tests/test_dashboard.py | 24 | 24 | 0 | 0 |
| tests/ (full) | 103 | 96 | 7 | 0 |

The 7 skipped tests are in `tests/test_agent.py` (Phase 5 pre-existing; unrelated to Phase 6).

---

## Summary

Phase 6 goal is fully achieved. All three feature areas are implemented, tested, and wired:

- **User Story tab:** `generate_user_story()` + `refine_user_story()` in `pipeline/user_story_writer.py` backed by Claude + RAG with graceful fallback; `tab_us` in dashboard replaces Phase 5 stub with generate/refine/push-to-Trello flow; history saved on push.
- **Move Cards tab:** `TrelloClient.move_card_to_list_by_id()` in `pipeline/trello_client.py` uses direct PUT by list ID with no name-lookup risk; `tab_devdone` wires it with per-card checkboxes, select-all, and audit comment; `move_card_to_list` (name variant) has zero occurrences in the dashboard.
- **History tab:** `_load_history`/`_save_history` at module level in `pipeline_dashboard.py`; `_HISTORY_FILE` points to `data/pipeline_history.json` (created lazily on first push); `tab_history` renders all `pipeline_runs` entries with full schema (card_name, approved_at, card_url, release, test_cases) and a Clear history button.

All 5 requirement IDs (US-01, US-02, US-03, MC-01, HIST-01) are satisfied. 96/103 tests pass (7 pre-existing skips in test_agent.py, unrelated to this phase).

---

_Verified: 2026-04-17_
_Verifier: Claude (gsd-verifier)_
