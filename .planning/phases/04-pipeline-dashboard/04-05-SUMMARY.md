---
phase: 04-pipeline-dashboard
plan: "05"
subsystem: pipeline
tags: [trello, card_processor, urllib, dotenv, streamlit, dashboard]

# Dependency graph
requires:
  - phase: 04-pipeline-dashboard
    provides: pipeline_dashboard.py scaffold, start_run(), render_report(), threading, progress, stop button
  - phase: 02-ai-qa-agent-core
    provides: verify_ac() with VerificationReport.to_dict() for pipeline wiring

provides:
  - pipeline/card_processor.py with get_ac_text(trello_card_url) -> tuple[str, str]
  - Trello REST API fetch using stdlib urllib.request (no requests library)
  - Graceful fallback to ("", "") when TRELLO_API_KEY or TRELLO_TOKEN absent
  - Run button handler wired: URL input -> get_ac_text -> start_run -> render_report
  - Manual AC textarea fallback with warning on failed Trello fetch
  - Full end-to-end pipeline: Trello URL -> card_processor -> smart_ac_verifier -> report

affects:
  - pipeline-dashboard
  - trello integration
  - card_processor

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Lazy import of get_ac_text inside Run button handler (avoids startup cost)
    - stdlib urllib.request for HTTP — no requests library (not in requirements.txt)
    - Explicit dotenv load via Path(__file__).parent.parent / ".env" (config.py pattern)
    - TDD: RED (ImportError) -> GREEN (implementation) for card_processor

key-files:
  created:
    - pipeline/card_processor.py
  modified:
    - pipeline_dashboard.py
    - tests/test_dashboard.py

key-decisions:
  - "card_processor uses os.environ.get() (not os.getenv()) so tests can mock via patch"
  - "Lazy import from pipeline.card_processor inside Run handler — not at module top level"
  - "Run handler checks fetched_ac truthiness (not card_name) to decide whether to use Trello result"

patterns-established:
  - "card_processor: stdlib-only HTTP (urllib.request) — no third-party HTTP library"
  - "Fallback to ('', '') on any error — no exception leaks from get_ac_text()"

requirements-completed: [DASH-01, DASH-02, DASH-03, DASH-04, DASH-05]

# Metrics
duration: 7min
completed: 2026-04-17
---

# Phase 4 Plan 05: Trello card_processor and Run button wiring Summary

**Trello card_processor with urllib.request fallback and full Run handler wiring: URL -> get_ac_text -> start_run -> render_report, all 7 dashboard tests green**

## Performance

- **Duration:** 7 min
- **Started:** 2026-04-17T08:03:22Z
- **Completed:** 2026-04-17T08:09:38Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments

- Created `pipeline/card_processor.py` with `get_ac_text()` using stdlib `urllib.request` only — extracts card ID from Trello URL via regex, fetches name + desc from Trello REST API
- Graceful credential fallback: returns `("", "")` when `TRELLO_API_KEY` or `TRELLO_TOKEN` absent, when URL is invalid, and on any HTTP/network error
- Wired Run button handler in `pipeline_dashboard.py` to call `get_ac_text()` for Trello URLs, show spinner during fetch, show warning on empty result, and pass `(card_name, ac_text)` to `start_run()`
- Full test suite: 68 passed, 7 skipped, 0 failures

## Task Commits

Each task was committed atomically:

1. **Task 1: Create pipeline/card_processor.py** - `b6f5ebd` (feat — TDD RED+GREEN)
2. **Task 2: Wire get_ac_text() into Run button handler** - `1a0a25d` (feat)

**Plan metadata:** (docs commit — see below)

_Note: Task 1 is TDD — tests added first (RED ImportError), then implementation (GREEN pass)_

## Files Created/Modified

- `pipeline/card_processor.py` - Trello card AC text extractor; `get_ac_text(url) -> (card_name, ac_text)`
- `pipeline_dashboard.py` - Run handler updated to call `get_ac_text()` with spinner, warning fallback
- `tests/test_dashboard.py` - Added `test_card_processor_missing_creds` and `test_card_processor_valid_url`

## Decisions Made

- `card_processor` uses `os.environ.get()` rather than reading env at module-load time, so test mocking with `patch("pipeline.card_processor.os.environ.get")` works correctly after `importlib.reload()`
- Lazy import `from pipeline.card_processor import get_ac_text` inside the Run handler — avoids Trello SDK cold-import cost on every Streamlit reload
- Truthiness check on `fetched_ac` (not `fetched_name`) decides whether to use the Trello result, since a card can have no name but still have AC text

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

To use Trello card fetching, add to `.env`:

```
TRELLO_API_KEY=<your Trello API key>
TRELLO_TOKEN=<your Trello token>
```

Without these, the dashboard falls back gracefully to manual AC paste — no error raised.

## Next Phase Readiness

- Phase 4 (Pipeline Dashboard) is now complete — all 5 plans executed
- Full pipeline wired: Trello URL input -> card_processor -> smart_ac_verifier -> styled report
- `streamlit run pipeline_dashboard.py` starts without import errors
- 68 tests pass across the full suite

---
*Phase: 04-pipeline-dashboard*
*Completed: 2026-04-17*

## Self-Check: PASSED

- pipeline/card_processor.py: FOUND
- 04-05-SUMMARY.md: FOUND
- Commit b6f5ebd (Task 1): FOUND
- Commit 1a0a25d (Task 2): FOUND
