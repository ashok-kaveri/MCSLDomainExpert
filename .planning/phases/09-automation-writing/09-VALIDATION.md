---
phase: 9
slug: automation-writing
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-18
---

# Phase 9 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (existing — tests/test_pipeline.py) |
| **Config file** | none — pytest discovered via conftest.py |
| **Quick run command** | `PYTHONPATH=. .venv/bin/python -m pytest tests/test_pipeline.py -k "auto" -x -q` |
| **Full suite command** | `PYTHONPATH=. .venv/bin/python -m pytest tests/ -x -q` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `PYTHONPATH=. .venv/bin/python -m pytest tests/test_pipeline.py -k "auto" -x -q`
- **After every plan wave:** Run `PYTHONPATH=. .venv/bin/python -m pytest tests/ -x -q`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 9-01-01 | 01 | 1 | AUTO-01 | unit | `PYTHONPATH=. .venv/bin/pytest tests/test_pipeline.py -k "auto01" -x -q` | ❌ W0 | ⬜ pending |
| 9-01-02 | 01 | 1 | AUTO-01 | unit | `PYTHONPATH=. .venv/bin/pytest tests/test_pipeline.py -k "auto01_spec_structure" -x -q` | ❌ W0 | ⬜ pending |
| 9-01-03 | 01 | 1 | AUTO-01 | unit | `PYTHONPATH=. .venv/bin/pytest tests/test_pipeline.py -k "auto01_pom_structure" -x -q` | ❌ W0 | ⬜ pending |
| 9-01-04 | 01 | 1 | AUTO-01 | unit | `PYTHONPATH=. .venv/bin/pytest tests/test_pipeline.py -k "auto01_no_api_key" -x -q` | ❌ W0 | ⬜ pending |
| 9-02-01 | 02 | 2 | AUTO-02 | unit | `PYTHONPATH=. .venv/bin/pytest tests/test_pipeline.py -k "auto02_explore_error" -x -q` | ❌ W0 | ⬜ pending |
| 9-03-01 | 03 | 3 | AUTO-03 | unit | `PYTHONPATH=. .venv/bin/pytest tests/test_pipeline.py -k "auto03_git_push" -x -q` | ❌ W0 | ⬜ pending |
| 9-03-02 | 03 | 3 | AUTO-03 | unit | `PYTHONPATH=. .venv/bin/pytest tests/test_pipeline.py -k "auto03_git_error" -x -q` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_pipeline.py` — add AUTO-01 stubs: `test_auto01_write_automation_returns_result`, `test_auto01_spec_structure`, `test_auto01_pom_structure`, `test_auto01_no_api_key`
- [ ] `tests/test_pipeline.py` — add AUTO-02 stub: `test_auto02_explore_error`
- [ ] `tests/test_pipeline.py` — add AUTO-03 stubs: `test_auto03_git_push`, `test_auto03_git_error`

*All tests added to existing `tests/test_pipeline.py` — consistent with Phase 6-8 pattern. No new test files needed.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Write Automation tab renders correctly in Streamlit | AUTO-03 | UI rendering requires live Streamlit session | Run `streamlit run pipeline_dashboard.py`, navigate to Write Automation tab, verify feature name input + TC textarea + Generate button appear |
| Chrome Agent explores live MCSL Shopify app | AUTO-02 | Requires live Shopify store credentials + running browser | Set SHOPIFY_STORE_URL in .env, run explore_feature() with a real feature name, verify selectors are returned |
| Generated TypeScript compiles without errors | AUTO-01 | tsc validation requires Node.js + automation repo | Copy generated .ts files to mcsl-test-automation, run `npx tsc --noEmit`, verify no type errors |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
