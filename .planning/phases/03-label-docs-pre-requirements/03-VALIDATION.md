---
phase: 3
slug: label-docs-pre-requirements
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-16
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.3.3 |
| **Config file** | `pytest.ini` |
| **Quick run command** | `PYTHONPATH=. .venv/bin/pytest tests/ -x -q` |
| **Full suite command** | `PYTHONPATH=. .venv/bin/pytest tests/ -q` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `PYTHONPATH=. .venv/bin/pytest tests/ -x -q`
- **After every plan wave:** Run `PYTHONPATH=. .venv/bin/pytest tests/ -q`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 3-01-01 | 03-01 | 1 | LABEL-01 | unit (mock Claude) | `PYTHONPATH=. .venv/bin/pytest tests/test_label_flows.py::test_manual_label_flow_plan -x` | ❌ W0 | ⬜ pending |
| 3-02-01 | 03-02 | 1 | LABEL-02 | unit (mock page) | `PYTHONPATH=. .venv/bin/pytest tests/test_label_flows.py::test_auto_generate_flow -x` | ❌ W0 | ⬜ pending |
| 3-02-02 | 03-02 | 1 | LABEL-04 | unit (mock page) | `PYTHONPATH=. .venv/bin/pytest tests/test_label_flows.py::test_return_label_flow -x` | ❌ W0 | ⬜ pending |
| 3-03-01 | 03-03 | 1 | LABEL-03 | unit (mock page) | `PYTHONPATH=. .venv/bin/pytest tests/test_label_flows.py::test_bulk_label_flow -x` | ❌ W0 | ⬜ pending |
| 3-04-01 | 03-04 | 2 | DOC-01 | unit (mock page) | `PYTHONPATH=. .venv/bin/pytest tests/test_label_flows.py::test_doc01_badge_check -x` | ❌ W0 | ⬜ pending |
| 3-04-02 | 03-04 | 2 | DOC-02 | unit (mock page + zipfile) | `PYTHONPATH=. .venv/bin/pytest tests/test_label_flows.py::test_doc02_download_zip -x` | ❌ W0 | ⬜ pending |
| 3-04-03 | 03-04 | 2 | DOC-03 | unit | `PYTHONPATH=. .venv/bin/pytest tests/test_label_flows.py::test_doc03_how_to_zip -x` | ❌ W0 | ⬜ pending |
| 3-04-04 | 03-04 | 2 | DOC-04 | unit (mock page) | `PYTHONPATH=. .venv/bin/pytest tests/test_label_flows.py::test_doc04_print_documents -x` | ❌ W0 | ⬜ pending |
| 3-04-05 | 03-04 | 2 | DOC-05 | unit (mock page) | `PYTHONPATH=. .venv/bin/pytest tests/test_label_flows.py::test_doc05_rate_log -x` | ❌ W0 | ⬜ pending |
| 3-05-01 | 03-05 | 2 | DOC-02/03 | unit (mock page + zipfile) | `PYTHONPATH=. .venv/bin/pytest tests/test_label_flows.py::test_doc02_download_zip tests/test_label_flows.py::test_doc03_how_to_zip -x` | ❌ W0 | ⬜ pending |
| 3-05-02 | 03-05 | 2 | LABEL-05 | unit (mock API) | `PYTHONPATH=. .venv/bin/pytest tests/test_agent.py::test_order_creator -x` | ✅ (extend) | ⬜ pending |
| 3-06-01 | 03-06 | 3 | PRE-01 | unit | `PYTHONPATH=. .venv/bin/pytest tests/test_label_flows.py::test_pre01_dry_ice_preconditions -x` | ❌ W0 | ⬜ pending |
| 3-06-02 | 03-06 | 3 | PRE-02 | unit | `PYTHONPATH=. .venv/bin/pytest tests/test_label_flows.py::test_pre02_alcohol_preconditions -x` | ❌ W0 | ⬜ pending |
| 3-06-03 | 03-06 | 3 | PRE-03 | unit | `PYTHONPATH=. .venv/bin/pytest tests/test_label_flows.py::test_pre03_battery_preconditions -x` | ❌ W0 | ⬜ pending |
| 3-06-04 | 03-06 | 3 | PRE-04 | unit | `PYTHONPATH=. .venv/bin/pytest tests/test_label_flows.py::test_pre04_signature_preconditions -x` | ❌ W0 | ⬜ pending |
| 3-06-05 | 03-06 | 3 | PRE-05 | unit | `PYTHONPATH=. .venv/bin/pytest tests/test_label_flows.py::test_pre05_hal_preconditions -x` | ❌ W0 | ⬜ pending |
| 3-06-06 | 03-06 | 3 | PRE-06 | unit | `PYTHONPATH=. .venv/bin/pytest tests/test_label_flows.py::test_pre06_insurance_preconditions -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_label_flows.py` — new file covering LABEL-01 through LABEL-05, DOC-01 through DOC-05, PRE-01 through PRE-06 (16 test stubs)
- [ ] Extend `tests/test_agent.py` — assert `download_zip` and `download_file` are no longer returning `False` (stubs replaced with real implementations)

*Existing pytest infrastructure from Phase 2 — no framework install needed.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| DOC-02 "Download Documents" button exists in MCSL | DOC-02 | UI button text uncertain — FedEx pattern confirmed, MCSL may differ | Navigate to Order Summary, confirm "Download Documents" button is present before implementing ZIP intercept |
| DOC-03 "How To" modal in MCSL | DOC-03 | "How To" modal with "Click Here" ZIP link not confirmed in MCSL UI | Check if MCSL has a How To modal on Order Summary; if absent, DOC-03 maps to a different element |
| DOC-04 Print Documents opens pluginhive.io tab | DOC-04 | New tab navigation — must screenshot correct tab | Confirm Print Documents button opens pluginhive.io in new tab; screenshot confirms visual label codes |
| PRE-05 HAL SideDock exact CSS selectors | PRE-05 | HAL flow confirmed but exact SideDock locators not in scanned POMs | Inspect SideDock element tree during dry run before committing HAL precondition steps |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
