---
phase: 01-foundation
plan: "01"
subsystem: infra
tags: [python, chromadb, langchain, pytest, dotenv, config]

# Dependency graph
requires: []
provides:
  - "config.py: explicit dotenv path, mcsl_knowledge + mcsl_code_knowledge collection names, all MCSL env vars"
  - "requirements.txt: all Phase 1 Python dependencies (langchain, chromadb, streamlit, pytest, etc.)"
  - ".env.template: developer env var reference"
  - "pytest.ini: test discovery config with testpaths=tests"
  - "tests/conftest.py: shared fixtures (tmp_chroma_path, sample_kb_doc, sample_wiki_doc, sample_code_doc, mock_embeddings)"
  - "Wave 0 test stub files: 10 test files, 25 tests (4 real + 21 skipped stubs)"
  - "Module skeleton: ingest/, rag/, pipeline/, ui/ with empty __init__.py"
affects: [01-02, 01-03, 01-04, 01-05, all-future-plans]

# Tech tracking
tech-stack:
  added: [python-dotenv, pytest, langchain-core (planned), chromadb (planned), streamlit (planned)]
  patterns:
    - "Explicit dotenv: load_dotenv(dotenv_path=Path(__file__).parent / '.env', override=True)"
    - "Two ChromaDB collections: mcsl_knowledge (KB+wiki) and mcsl_code_knowledge (source code)"
    - "Lazy import in conftest.py fixtures to avoid hard dependency on langchain_core until installed"
    - "Wave-based test stubs: tests written with @pytest.mark.skip(reason='Wave N: ...') until implementation ready"

key-files:
  created:
    - config.py
    - requirements.txt
    - .env.template
    - pytest.ini
    - ingest/__init__.py
    - rag/__init__.py
    - pipeline/__init__.py
    - ui/__init__.py
    - tests/__init__.py
    - tests/conftest.py
    - tests/test_config.py
    - tests/test_vectorstore.py
    - tests/test_kb_loader.py
    - tests/test_sheets_loader.py
    - tests/test_wiki_loader.py
    - tests/test_code_indexer.py
    - tests/test_rag_updater.py
    - tests/test_run_ingest.py
    - tests/test_chat.py
  modified: []

key-decisions:
  - "Explicit dotenv path (Path(__file__).parent / '.env') prevents silent load failure when CWD is not project root"
  - "ChromaDB collection names mcsl_knowledge and mcsl_code_knowledge — never reuse FedEx names"
  - "conftest.py fixtures use lazy imports so test_config.py runs without langchain_core installed"
  - "Wave-based skip reasons (Wave 1/2/3) make test intent clear and enable progressive activation"

patterns-established:
  - "config.py is single source of truth: all paths, collection names, model names, credentials via explicit dotenv"
  - "Test stubs use @pytest.mark.skip with wave reason — activated in-place by later plans"
  - "conftest.py lazy imports: heavy dependencies imported inside fixture body, not at module level"

requirements-completed: [INFRA-01, INFRA-02, INFRA-03, INFRA-04]

# Metrics
duration: 19min
completed: 2026-04-15
---

# Phase 1 Plan 01: Project Scaffold Summary

**Python project skeleton with explicit-path dotenv config.py, mcsl_knowledge + mcsl_code_knowledge ChromaDB collections, and 10 Wave 0 test stub files covering all future implementation targets**

## Performance

- **Duration:** 19 min
- **Started:** 2026-04-15T10:02:33Z
- **Completed:** 2026-04-15T10:21:29Z
- **Tasks:** 2 completed
- **Files modified:** 19

## Accomplishments
- config.py with explicit `load_dotenv(dotenv_path=Path(__file__).parent / ".env", override=True)` pattern — no CWD-dependent silent failures
- MCSL ChromaDB collection names established: `mcsl_knowledge` and `mcsl_code_knowledge` (no fedex_* names anywhere)
- All MCSL-specific env vars in config: STORE, SHOPIFY_ACCESS_TOKEN, SHOPIFY_API_VERSION, MCSL_AUTOMATION_REPO_PATH, WIKI_PATH, STOREPEPSAAS_SHARED_PATH, GOOGLE_SHEETS_ID, APP_IFRAME_SELECTOR
- 10 Wave 0 test stub files: 4 real test_config.py tests passing, 21 skipped stubs ready for activation in later waves
- pytest discovers all 25 tests from 10 files in under 1 second

## Task Commits

Each task was committed atomically:

1. **Task 1: Create directory skeleton, config.py, requirements.txt, .env.template, pytest.ini** - `38fa825` (feat)
2. **Task 2: Create all Wave 0 test stub files** - `ff59f8a` (feat)

**Plan metadata:** _(to be added after final commit)_

## Files Created/Modified
- `config.py` - Project-wide constants: explicit dotenv, collection names, model names, MCSL paths
- `requirements.txt` - All Phase 1 Python dependencies (langchain stack, chromadb, streamlit, pytest)
- `.env.template` - Developer env var reference with defaults
- `pytest.ini` - testpaths=tests, addopts=-q
- `ingest/__init__.py` - Empty package marker
- `rag/__init__.py` - Empty package marker
- `pipeline/__init__.py` - Empty package marker
- `ui/__init__.py` - Empty package marker
- `tests/__init__.py` - Empty package marker
- `tests/conftest.py` - Shared fixtures: tmp_chroma_path, sample_kb_doc, sample_wiki_doc, sample_code_doc, mock_embeddings (lazy imports)
- `tests/test_config.py` - 4 real tests: dotenv_explicit_path, collection_names, mcsl_env_vars, app_iframe_selector
- `tests/test_vectorstore.py` - 3 Wave 1 stubs
- `tests/test_kb_loader.py` - 3 Wave 2 stubs
- `tests/test_sheets_loader.py` - 3 Wave 2 stubs
- `tests/test_wiki_loader.py` - 3 Wave 2 stubs
- `tests/test_code_indexer.py` - 3 Wave 2 stubs
- `tests/test_rag_updater.py` - 2 Wave 2 stubs
- `tests/test_run_ingest.py` - 2 Wave 2 stubs
- `tests/test_chat.py` - 2 Wave 3 stubs

## Decisions Made
- Used explicit `Path(__file__).parent / ".env"` pattern — critical for running tests from any working directory
- conftest.py fixtures use lazy imports (inside function body) so test_config.py runs without full langchain stack installed
- Wave-based skip reasons (`Wave 1: requires vectorstore.py implementation`) document intent and activation plan
- GOOGLE_SHEETS_ID defaulted to MCSL TC sheet ID `1oVtOaM2PesVR_TkuVaBKpbp_qQdmq4FQnN43Xew0FuY`

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed test_dotenv_explicit_path mkdir/chdir ordering**
- **Found during:** Task 2 (test_config.py execution)
- **Issue:** Test called `monkeypatch.chdir(tmp_path / "subdir")` before `mkdir` — FileNotFoundError
- **Fix:** Swapped order: `mkdir` before `monkeypatch.chdir`
- **Files modified:** tests/test_config.py
- **Verification:** All 4 test_config.py tests pass
- **Committed in:** ff59f8a (Task 2 commit)

**2. [Rule 1 - Bug] Fixed conftest.py top-level langchain_core import**
- **Found during:** Task 2 (pytest collection)
- **Issue:** Original conftest.py had `from langchain_core.documents import Document` at module level — fails before langchain is installed, blocking all test collection
- **Fix:** Moved import inside each fixture body (lazy import)
- **Files modified:** tests/conftest.py
- **Verification:** pytest collects all 25 tests, 4 pass, 21 skipped
- **Committed in:** ff59f8a (Task 2 commit)

---

**Total deviations:** 2 auto-fixed (both Rule 1 - Bug)
**Impact on plan:** Both fixes essential for correct test operation. No scope creep.

## Issues Encountered
- `python` command not found on macOS (uses `python3`) — used `python3` for all commands
- `python-dotenv` not installed system-wide — installed with `--break-system-packages` (PEP 668 environment)

## User Setup Required
None - no external service configuration required for this scaffold plan.

## Next Phase Readiness
- All Wave 0 infrastructure in place — 01-02 can start implementing vectorstore.py and activating Wave 1 tests
- requirements.txt ready for `pip install -r requirements.txt` once virtual environment is set up
- config.py is the single source of truth — all future plans import from it, no duplication
- Blocker noted: langchain, chromadb not yet installed system-wide — 01-02 should install or create venv

---
*Phase: 01-foundation*
*Completed: 2026-04-15*
