---
phase: 10-run-automation-domain-expert-chat
plan: 02
subsystem: ui
tags: [streamlit, rag, langchain, chat, tdd]

# Dependency graph
requires:
  - phase: 01-foundation
    provides: rag.chain.ask + build_chain + SimpleConversationalChain
  - phase: 10-run-automation-domain-expert-chat
    provides: ui/chat_app.py Streamlit UI with QUICK_ASKS list
provides:
  - ask_domain_expert() function exported at module level in ui/chat_app.py
  - 4 unit tests for CHAT-01 (RAG-backed answers + fallback) and CHAT-02 (QUICK_ASKS + importability)
affects: [10-run-automation-domain-expert-chat, future-chat-integrations]

# Tech tracking
tech-stack:
  added: []
  patterns: [patch module-level bindings (ui.chat_app.build_chain) not source module (rag.chain.build_chain)]

key-files:
  created:
    - tests/test_chat_app.py
  modified:
    - ui/chat_app.py

key-decisions:
  - "patch target is ui.chat_app.build_chain (module binding), not rag.chain.build_chain — from-import pattern requires patching at use site"
  - "ask_domain_expert() placed after imports but BEFORE st.set_page_config() so it is importable in tests without triggering page config"

patterns-established:
  - "Stateless one-shot RAG helper pattern: build_chain() + ask(question, chain) with try/except fallback returning {answer, sources}"
  - "TDD RED stubs fail on ImportError (function not yet exported); patch targets fixed in GREEN commit"

requirements-completed: [CHAT-01, CHAT-02]

# Metrics
duration: 2min
completed: 2026-04-18
---

# Phase 10 Plan 02: Domain Expert Chat ask_domain_expert() + CHAT Tests Summary

**ask_domain_expert() stateless RAG wrapper added to ui/chat_app.py with 4 unit tests covering CHAT-01 fallback behavior and CHAT-02 module importability**

## Performance

- **Duration:** ~2 min
- **Started:** 2026-04-18T09:56:53Z
- **Completed:** 2026-04-18T09:58:21Z
- **Tasks:** 2 (TDD RED + GREEN)
- **Files modified:** 2

## Accomplishments
- Created tests/test_chat_app.py with 4 unit tests confirming RED (3 fail, 1 pass before implementation)
- Added ask_domain_expert() at module level in ui/chat_app.py — stateless one-shot RAG query with exception fallback
- Full test suite: 137 passed, 7 skipped, 0 regressions (was 129 before this phase)
- QUICK_ASKS already had 7 entries — verified ≥5 satisfied without changes

## Task Commits

1. **Task 1: RED — failing CHAT-01/CHAT-02 test stubs** - `58b91cc` (test)
2. **Task 2: GREEN — add ask_domain_expert() + fix patch targets** - `0303709` (feat)

_Note: TDD tasks have two commits (test RED → feat GREEN)_

## Files Created/Modified
- `tests/test_chat_app.py` - 4 unit tests: test_chat01_ask_domain_expert, test_chat01_empty_rag_returns_fallback, test_chat02_quick_questions_list, test_chat02_module_importable
- `ui/chat_app.py` - Added ask_domain_expert() function (15 lines) after logger, before st.set_page_config()

## Decisions Made
- Patch targets corrected to `ui.chat_app.build_chain` and `ui.chat_app.ask` (not `rag.chain.*`) — `from rag.chain import ask, build_chain` creates module-level bindings; patching the source module has no effect after import
- ask_domain_expert() positioned before st.set_page_config() so it can be imported in a non-Streamlit test environment without triggering page config side effects

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed incorrect patch targets in test stubs**
- **Found during:** Task 2 (GREEN — running tests after implementation)
- **Issue:** Test stubs used `patch("rag.chain.build_chain")` and `patch("rag.chain.ask")` but ui/chat_app.py uses `from rag.chain import ask, build_chain` — module-level bindings require patching at the use site (`ui.chat_app.build_chain`)
- **Fix:** Changed both patch targets in test_chat01_ask_domain_expert and test_chat01_empty_rag_returns_fallback to `ui.chat_app.*`
- **Files modified:** tests/test_chat_app.py
- **Verification:** All 4 tests pass after fix
- **Committed in:** 0303709 (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 bug — wrong patch target)
**Impact on plan:** Necessary for test correctness. No scope creep.

## Issues Encountered
- Wrong patch targets in initial RED stubs (patched source module instead of use-site binding). Fixed during GREEN phase per Rule 1.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- ui/chat_app.py now exports ask_domain_expert() and QUICK_ASKS at module level
- Tests for CHAT-01 and CHAT-02 are GREEN (4/4)
- Ready for 10-03 if planned, or phase completion

---
*Phase: 10-run-automation-domain-expert-chat*
*Completed: 2026-04-18*
