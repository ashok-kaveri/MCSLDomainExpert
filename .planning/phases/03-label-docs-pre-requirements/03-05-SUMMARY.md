---
phase: 03-label-docs-pre-requirements
plan: "05"
subsystem: testing
tags: [pytest, tdd, download-zip, download-file, playwright, zipfile, csv]

# Dependency graph
requires:
  - phase: 03-label-docs-pre-requirements
    plan: "01"
    provides: tests/test_label_flows.py Wave 0 stubs
  - phase: 03-label-docs-pre-requirements
    plan: "04"
    provides: DOC-02 guide content in _MCSL_WORKFLOW_GUIDE
provides:
  - download_zip full handler replacing Phase 2 stub (zipfile extraction, page.expect_download)
  - download_file full handler replacing Phase 2 stub (CSV/Excel/binary dispatch)
  - _format_zip_for_context and _format_file_for_context helpers
  - _verify_scenario propagates both _zip_content and _file_content into zip_ctx
  - tests/test_label_flows.py with test_doc02_download_zip_handler, test_doc03_how_to_zip, test_doc02_download_file_csv active and passing
affects: [03-06]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "download handler mock pattern: tempfile for real ZIP/CSV bytes, mock_download.save_as copies bytes to handler's tmp path"
    - "6-strategy element search: iframe frame first (button/link/text), then page fallback"
    - "page.expect_download() context manager — NOT frame.expect_download() (frame objects lack this method)"

key-files:
  created: []
  modified:
    - pipeline/smart_ac_verifier.py
    - tests/test_label_flows.py

key-decisions:
  - "download_zip uses page.expect_download() — frame objects do not have expect_download(), only Page does"
  - "test_doc02_download_zip already existed as guide content test (from 03-04); added test_doc02_download_zip_handler and test_doc03_how_to_zip as handler-level tests"
  - "_format_file_for_context and _format_zip_for_context added near _get_app_frame — before _do_action for logical grouping"
  - "download_file detects file extension from download.suggested_filename to dispatch CSV/Excel/PDF/text handling"

patterns-established:
  - "Download handler mock: create real bytes in tempfile, use save_as side_effect to copy to handler's own tmp path"
  - "Both _zip_content and _file_content are propagated into zip_ctx in _verify_scenario using the same pattern"

requirements-completed: [DOC-02]

# Metrics
duration: 7min
completed: 2026-04-16
---

# Phase 03 Plan 05: Download Handlers (download_zip + download_file) Summary

**Full download_zip and download_file handlers replacing Phase 2 stubs, with zipfile/CSV extraction, page.expect_download(), _format_zip_for_context + _format_file_for_context helpers, and zip_ctx propagation for both content types in _verify_scenario**

## Performance

- **Duration:** 7 min
- **Started:** 2026-04-16T11:34:23Z
- **Completed:** 2026-04-16T11:41:40Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- Replaced download_zip stub (logged warning, returned False) with full Playwright-based implementation using page.expect_download(), 6-strategy element search, zipfile extraction (JSON parsed, CSV/TXT/XML/log as text[:3000], binary as size note)
- Replaced download_file stub with full implementation dispatching on file extension: CSV via csv.reader (headers/row_count/sample_rows), Excel via openpyxl (with graceful fallback), PDF/binary as size note, other text as raw utf-8[:2000]
- Added _format_zip_for_context(extracted: dict) -> str and _format_file_for_context(content: dict | str) -> str helpers
- Wired both _zip_content and _file_content into zip_ctx in _verify_scenario loop (previously only _zip_summary was attempted — a broken reference)
- Added 3 new active tests: test_doc02_download_zip_handler, test_doc03_how_to_zip, test_doc02_download_file_csv
- Full test suite: 55 passed, 13 skipped, 0 failures

## Task Commits

Each task was committed atomically:

1. **Task 1 RED: add test_doc02_download_zip_handler and test_doc03_how_to_zip** - `56132b8` (test)
2. **Task 1 GREEN: replace download_zip stub + add format helpers** - `8c6aa35` (feat)
3. **Task 1 GREEN: wire _zip_content → zip_ctx propagation** - `8428f87` (feat)
4. **Task 2 RED: unskip test_doc02_download_file_csv** - `d15572b` (test)
5. **Task 2 GREEN: replace download_file stub with CSV/Excel/binary implementation** - `a4151dc` (feat)
6. **Task 2 GREEN: wire _file_content → zip_ctx propagation** - `e2a5161` (feat)

_Note: TDD tasks have multiple commits (test → feat)_

## Files Created/Modified
- `pipeline/smart_ac_verifier.py` — download_zip full handler (lines ~1263-1318); download_file full handler (lines ~1319-1408); _format_zip_for_context helper (lines ~1171-1185); _format_file_for_context helper (lines ~1186-1204); _verify_scenario zip_ctx propagation for both _zip_content and _file_content (lines ~1744-1747)
- `tests/test_label_flows.py` — test_doc02_download_zip_handler and test_doc03_how_to_zip added (in-memory ZIP mocks); test_doc02_download_file_csv unskipped and implemented (real CSV temp file mock)

## Decisions Made
- download_zip uses `page.expect_download()` (not frame.expect_download) — Frame objects in Playwright do not expose expect_download(); only the Page object does
- test_doc02_download_zip was already active as a guide content test from 03-04 — added handler tests with distinct names (test_doc02_download_zip_handler, test_doc03_how_to_zip) rather than replacing the existing guide test
- _verify_scenario previously had a broken reference `action.get("_zip_summary", "")` — replaced with proper `_format_zip_for_context(action["_zip_content"])` call
- download_file extension detection uses `download.suggested_filename` attribute from Playwright's Download object

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed broken _zip_content → zip_ctx propagation**
- **Found during:** Task 1 GREEN (wiring zip_ctx)
- **Issue:** _verify_scenario had `action.get("_zip_summary", "")` — this always returned empty string because `_zip_summary` is never set; the correct key is `_zip_content` which must be formatted via `_format_zip_for_context`
- **Fix:** Replaced with `_format_zip_for_context(action["_zip_content"])`
- **Files modified:** pipeline/smart_ac_verifier.py
- **Commit:** 8428f87

**2. [Rule 1 - Minor] Added test_doc02_download_zip_handler instead of replacing test_doc02_download_zip**
- **Found during:** Task 1 RED
- **Issue:** test_doc02_download_zip already existed as an active guide content test (from 03-04); plan expected it to be a Wave 0 stub to unskip
- **Fix:** Added test_doc02_download_zip_handler and test_doc03_how_to_zip as new handler-level tests; kept guide test intact
- **Files modified:** tests/test_label_flows.py
- **Commit:** 56132b8

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- download_zip and download_file are fully functional — DOC-02 scenarios can be verified end-to-end
- zip_ctx propagation works for both content types — Claude gets file content context on the next step
- Ready for 03-06 (Pre-requirement strategies)
- 55 tests pass, 13 skipped (Wave 0 stubs for PRE-01 through PRE-06)

---
*Phase: 03-label-docs-pre-requirements*
*Completed: 2026-04-16*
