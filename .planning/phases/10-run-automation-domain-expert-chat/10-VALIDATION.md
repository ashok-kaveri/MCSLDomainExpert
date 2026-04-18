---
phase: 10
slug: run-automation-domain-expert-chat
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-18
---

# Phase 10 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (existing — tests/ directory) |
| **Config file** | none — pytest discovered automatically |
| **Quick run command** | `PYTHONPATH=. .venv/bin/python -m pytest tests/ -q --tb=short` |
| **Full suite command** | `PYTHONPATH=. .venv/bin/python -m pytest tests/ -q --tb=short` |
| **Estimated runtime** | ~5 seconds |
| **Current baseline** | 129 passed, 7 skipped |

---

## Sampling Rate

- **After every task commit:** Run `PYTHONPATH=. .venv/bin/python -m pytest tests/ -q --tb=short`
- **After every plan wave:** Run `PYTHONPATH=. .venv/bin/python -m pytest tests/ -q --tb=short`
- **Before `/gsd:verify-work`:** Full suite must be green (≥137 passed)
- **Max feedback latency:** ~5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 10-01-01 | 01 | 1 | RUN-01 | unit | `PYTHONPATH=. .venv/bin/pytest tests/test_run_automation.py::test_run01_enumerate_specs -x` | ❌ W0 | ⬜ pending |
| 10-01-02 | 01 | 1 | RUN-01 | unit | `PYTHONPATH=. .venv/bin/pytest tests/test_run_automation.py::test_run01_test_run_result_dataclass -x` | ❌ W0 | ⬜ pending |
| 10-01-03 | 01 | 1 | RUN-01 | unit | `PYTHONPATH=. .venv/bin/pytest tests/test_run_automation.py::test_run01_parse_playwright_json -x` | ❌ W0 | ⬜ pending |
| 10-01-04 | 01 | 1 | RUN-01 | unit | `PYTHONPATH=. .venv/bin/pytest tests/test_run_automation.py::test_run01_run_release_tests_calls_subprocess -x` | ❌ W0 | ⬜ pending |
| 10-02-01 | 02 | 2 | CHAT-01 | unit | `PYTHONPATH=. .venv/bin/pytest tests/test_chat_app.py::test_chat01_ask_domain_expert -x` | ❌ W0 | ⬜ pending |
| 10-02-02 | 02 | 2 | CHAT-01 | unit | `PYTHONPATH=. .venv/bin/pytest tests/test_chat_app.py::test_chat01_empty_rag_returns_fallback -x` | ❌ W0 | ⬜ pending |
| 10-02-03 | 02 | 2 | CHAT-02 | unit | `PYTHONPATH=. .venv/bin/pytest tests/test_chat_app.py::test_chat02_quick_questions_list -x` | ❌ W0 | ⬜ pending |
| 10-02-04 | 02 | 2 | CHAT-02 | unit | `PYTHONPATH=. .venv/bin/pytest tests/test_chat_app.py::test_chat02_module_importable -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_run_automation.py` — new file with RUN-01 stubs (4 test functions)
- [ ] `tests/test_chat_app.py` — new file with CHAT-01 / CHAT-02 stubs (4 test functions)
- [ ] `ui/__init__.py` — make `ui/` a Python package so `ui.chat_app` is importable in tests
- [ ] `pipeline/test_runner.py` — does not exist yet
- [ ] `ui/chat_app.py` — does not exist yet

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Run Automation tab renders spec file tree with checkboxes | RUN-01 | Requires live Streamlit + mcsl-test-automation repo on disk | `streamlit run pipeline_dashboard.py` → Run Automation tab → verify spec groups and checkboxes appear |
| Run selected specs end-to-end | RUN-01 | Requires live Shopify store + auth-chrome.json | Select 1 spec, click Run, verify pass/fail results appear |
| Domain Expert Chat answers MCSL questions | CHAT-01 | Requires indexed RAG + ANTHROPIC_API_KEY | `streamlit run ui/chat_app.py` → ask "How do I generate a FedEx label?" → verify relevant answer |
| Quick Questions buttons pre-fill chat input | CHAT-02 | Requires live Streamlit session | Click a Quick Question button → verify chat input is filled and answer returned |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
