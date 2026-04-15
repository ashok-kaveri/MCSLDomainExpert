---
phase: 1
slug: foundation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-15
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest >= 8.3.3 |
| **Config file** | None — Wave 0 creates `pytest.ini` |
| **Quick run command** | `pytest tests/ -x -q --ignore=tests/test_chat.py` |
| **Full suite command** | `pytest tests/ -v` |
| **Estimated runtime** | ~15 seconds (quick), ~45 seconds (full with integration) |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/ -x -q --ignore=tests/test_chat.py`
- **After every plan wave:** Run `pytest tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** ~15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 1-01-01 | 01 | 0 | INFRA-01,03,04 | unit | `pytest tests/test_config.py -x` | ❌ W0 | ⬜ pending |
| 1-01-02 | 01 | 0 | INFRA-02 | integration | `pytest tests/test_vectorstore.py -x` | ❌ W0 | ⬜ pending |
| 1-01-03 | 01 | 1 | INFRA-01 | unit | `pytest tests/test_config.py::test_dotenv_explicit_path -x` | ❌ W0 | ⬜ pending |
| 1-02-01 | 02 | 1 | INFRA-02 | integration | `pytest tests/test_vectorstore.py::test_both_collections -x` | ❌ W0 | ⬜ pending |
| 1-03-01 | 03 | 2 | RAG-01 | unit | `pytest tests/test_kb_loader.py -x` | ❌ W0 | ⬜ pending |
| 1-03-02 | 03 | 2 | RAG-02 | unit | `pytest tests/test_sheets_loader.py -x` | ❌ W0 | ⬜ pending |
| 1-03-03 | 03 | 2 | RAG-03 | unit | `pytest tests/test_wiki_loader.py -x` | ❌ W0 | ⬜ pending |
| 1-03-04 | 03 | 2 | RAG-04 | unit | `pytest tests/test_code_indexer.py::test_storepepsaas -x` | ❌ W0 | ⬜ pending |
| 1-03-05 | 03 | 2 | RAG-05 | unit | `pytest tests/test_code_indexer.py::test_automation -x` | ❌ W0 | ⬜ pending |
| 1-03-06 | 03 | 2 | INFRA-05 | integration | `pytest tests/test_run_ingest.py::test_partial_reingest -x` | ❌ W0 | ⬜ pending |
| 1-04-01 | 04 | 2 | RAG-06 | unit | `pytest tests/test_rag_updater.py -x` | ❌ W0 | ⬜ pending |
| 1-05-01 | 05 | 3 | RAG-07 | integration | `pytest tests/test_chat.py -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/__init__.py` — empty init
- [ ] `tests/conftest.py` — shared fixtures: tmp ChromaDB path, mock embeddings, sample docs
- [ ] `tests/test_config.py` — covers INFRA-01, INFRA-03, INFRA-04
- [ ] `tests/test_kb_loader.py` — covers RAG-01
- [ ] `tests/test_sheets_loader.py` — covers RAG-02 (mock HTTP for CSV fallback)
- [ ] `tests/test_wiki_loader.py` — covers RAG-03
- [ ] `tests/test_code_indexer.py` — covers RAG-04, RAG-05
- [ ] `tests/test_rag_updater.py` — covers RAG-06
- [ ] `tests/test_vectorstore.py` — covers INFRA-02
- [ ] `tests/test_run_ingest.py` — covers INFRA-05
- [ ] `tests/test_chat.py` — covers RAG-07 (integration, requires live Ollama + Anthropic)
- [ ] `pytest.ini` — project root, testpaths=tests
- [ ] Framework install: included in requirements.txt

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Streamlit chat UI renders, accepts questions, shows ≤200-word answers | RAG-07 | Requires browser | Run `streamlit run ui/chat_app.py`, type "How do I add a UPS account?" |
| Full ingest pipeline completes with no ChromaDB errors | RAG-01–05 | Requires live Ollama + all source paths | Run `python ingest/run_ingest.py`, check stdout for "Ingestion complete" |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
