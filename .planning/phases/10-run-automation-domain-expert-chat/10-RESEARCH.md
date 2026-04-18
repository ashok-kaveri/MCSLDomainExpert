# Phase 10: Run Automation + Domain Expert Chat - Research

**Researched:** 2026-04-18
**Domain:** Subprocess test execution, Playwright CLI output parsing, Streamlit chat UI, RAG-backed chatbot
**Confidence:** HIGH

## Summary

Phase 10 has two independent deliverables. The first is the Run Automation tab in `pipeline_dashboard.py` — it enumerates spec files from the mcsl-test-automation repo grouped by folder, runs selected specs via `subprocess` calling `npx playwright test`, streams output, parses JSON reporter results, and surfaces pass/fail/duration with a "Post to Slack" button. The second is a standalone `ui/chat_app.py` Streamlit app — a Domain Expert Chat backed by the existing `rag/vectorstore.py` (`search()`) and `rag/code_indexer.py` (`search_code()`) collections, with Quick Questions sidebar buttons, a Knowledge Base refresh trigger, and source attribution per response.

The Playwright JSON reporter (`--reporter=json`) is the correct output format to parse — it yields a structured `{ suites, stats }` object with per-test `status`, `duration`, and error messages. The existing `SlackClient` in `pipeline/slack_client.py` already supports channel posting; the "Post to Slack" flow reuses `post_content_to_slack_channel()` with formatted test results. The Domain Expert Chat follows exactly the same RAG pattern already established in `pipeline/domain_validator.py` and `pipeline/bug_reporter.py` — build context from `search()` + `search_code()`, format a prompt, call `ChatAnthropic`.

**Primary recommendation:** Run `npx playwright test --reporter=json` in a background thread, capture stdout, parse JSON into a `TestRunResult` dataclass, then render in the tab. For chat, create `ui/chat_app.py` as a fresh Streamlit page using `st.chat_input` / `st.chat_message` with RAG context injection — no new libraries needed.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| RUN-01 | Run selected Playwright spec files from UI, show pass/fail/duration results | Playwright JSON reporter, subprocess pattern, tab_run replacement in pipeline_dashboard.py |
| CHAT-01 | RAG-backed chatbot for MCSL app knowledge (label gen, carrier config, special services, etc.) | Existing vectorstore.search() + code_indexer.search_code() + ChatAnthropic, ui/chat_app.py |
| CHAT-02 | Quick Questions sidebar buttons, Knowledge Base refresh, source attribution | Streamlit sidebar buttons, ingest/run_ingest.py trigger, Document.metadata source display |
</phase_requirements>

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| subprocess (stdlib) | Python 3.x | Run `npx playwright test` and capture output | No extra deps; already used in `rag/code_indexer.py` `_git()` helper |
| streamlit | already installed | Run Automation tab UI + chat_app.py | Project standard — entire pipeline_dashboard.py is Streamlit |
| langchain_anthropic.ChatAnthropic | already installed | Domain Expert Chat LLM calls | Used throughout pipeline/ for all Claude calls |
| rag.vectorstore.search | local module | RAG retrieval for KB docs | Established in Phase 1, used in domain_validator + bug_reporter |
| rag.code_indexer.search_code | local module | RAG retrieval for automation + codebase | Established in Phase 1, used in domain_validator + bug_reporter |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| json (stdlib) | Python 3.x | Parse Playwright `--reporter=json` output | Parsing test results |
| pathlib.Path (stdlib) | Python 3.x | Enumerate spec files from MCSL_AUTOMATION_REPO_PATH | Spec file discovery |
| threading (stdlib) | Python 3.x | Run tests in background so UI stays responsive | Same pattern as Release QA AI QA Agent thread |
| dataclasses (stdlib) | Python 3.x | `TestRunResult`, `SpecResult` dataclasses | Typed result container |
| pipeline.slack_client | local module | Post test results to Slack | "Post to Slack" button in Run Automation tab |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `--reporter=json` | Parse `--reporter=list` text output | JSON is structured and reliable; text parsing is fragile |
| Separate chat_app.py | Add chat as 8th tab in pipeline_dashboard.py | Roadmap specifies `ui/chat_app.py` as separate app (see ROADMAP.md plan 10-02); keep dashboard at 7 tabs |
| `st.chat_input` / `st.chat_message` | st.text_input + st.write | `st.chat_*` widgets are the Streamlit-native chat pattern (Streamlit 1.23+) |

**Installation:** No new packages needed. Everything is already installed in `.venv`.

---

## Architecture Patterns

### Recommended Project Structure
```
pipeline/
  test_runner.py          # run_release_tests() + TestRunResult + SpecResult
ui/
  chat_app.py             # Standalone Streamlit Domain Expert Chat
pipeline_dashboard.py     # tab_run replaces stub with test runner UI
```

### Pattern 1: Playwright JSON Reporter Subprocess

**What:** Run `npx playwright test <spec_files> --reporter=json` capturing stdout, parse JSON.

**When to use:** Whenever running Playwright tests programmatically and needing structured pass/fail/duration.

**How Playwright JSON reporter works:**
- `npx playwright test tests/folder/spec.ts --reporter=json` writes JSON to stdout
- JSON top-level keys: `{ "suites": [...], "stats": { "expected": N, "unexpected": M, "duration": X } }`
- Each suite has `specs` — each spec has `tests` — each test has `results[0].status` ("passed"/"failed"/"timedOut"/"skipped") and `results[0].duration` (ms)
- Exit code 0 = all passed, non-zero = failures/errors

```python
# Source: project pattern (subprocess is stdlib, Playwright JSON reporter is documented)
import subprocess, json, os
from pathlib import Path

def run_playwright_specs(
    repo_path: str,
    spec_files: list[str],   # relative paths from repo root, e.g. ["tests/orderGrid/tags/addTags.spec.ts"]
    project: str = "Google Chrome",
) -> dict:
    cmd = [
        "npx", "playwright", "test",
        "--reporter=json",
        "--project", project,
        *spec_files,
    ]
    result = subprocess.run(
        cmd,
        cwd=repo_path,
        capture_output=True,
        text=True,
        timeout=600,
        env={**os.environ},
    )
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        data = {}
    return {
        "raw": data,
        "exit_code": result.returncode,
        "stderr": result.stderr[:2000],
    }
```

### Pattern 2: Spec File Enumeration Grouped by Folder

**What:** Walk `MCSL_AUTOMATION_REPO_PATH/tests/` and collect `.spec.ts` files, group by immediate parent folder name.

**When to use:** When building the checkbox UI for Run Automation tab.

```python
# Source: verified from mcsl-test-automation repo structure (58 spec files)
from pathlib import Path
from collections import defaultdict

def enumerate_specs(repo_path: str) -> dict[str, list[str]]:
    """Returns {folder_name: [relative_spec_paths]} sorted alphabetically."""
    root = Path(repo_path) / "tests"
    groups: dict[str, list[str]] = defaultdict(list)
    for spec in sorted(root.rglob("*.spec.ts")):
        rel = str(spec.relative_to(Path(repo_path)))
        # Group by top-level subfolder under tests/
        parts = spec.relative_to(root).parts
        folder = parts[0] if len(parts) > 1 else "root"
        groups[folder].append(rel)
    return dict(sorted(groups.items()))
```

**Known folders from mcsl-test-automation/tests/:**
automationRules, carrierOtherDetails, cod, externallyFulfilled, labelBatch, onboardingFlow, orderGrid, orderSummary, packagingTypes, shopifyUI, specialServices (11 folders, 58 spec files total)

### Pattern 3: Background Thread for Test Runs (same as AI QA Agent pattern)

**What:** Launch `run_release_tests()` in a `threading.Thread`; write results to `st.session_state`; poll with `st.rerun()`.

**When to use:** Any long-running operation in Streamlit.

```python
# Source: established project pattern (see DASH-02, Phase 7 per-card threads)
import threading

def _run_tests_thread(repo_path, spec_files, state_key_result, state_key_running):
    try:
        result = run_release_tests(repo_path, spec_files)
        st.session_state[state_key_result] = result
    finally:
        st.session_state[state_key_running] = False

if st.button("Run Selected"):
    st.session_state["run_running"] = True
    st.session_state["run_result"] = None
    t = threading.Thread(
        target=_run_tests_thread,
        args=(repo_path, selected_specs, "run_result", "run_running"),
        daemon=True,
    )
    t.start()
```

### Pattern 4: Domain Expert Chat with RAG

**What:** Accept user question, retrieve from both vectorstores, format context + question into a Claude prompt, stream or return response, display with `st.chat_message`.

**When to use:** `ui/chat_app.py` — the standalone Domain Expert Chat app.

```python
# Source: established project pattern (domain_validator.py, bug_reporter.py)
from rag.vectorstore import search
from rag.code_indexer import search_code
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
import config

def ask_domain_expert(question: str, k: int = 5) -> dict:
    kb_docs   = search(question, k=k)
    code_docs = search_code(question, k=3)
    kb_ctx    = "\n\n".join(d.page_content for d in kb_docs)
    code_ctx  = "\n\n".join(d.page_content for d in code_docs)
    prompt = f"""You are an MCSL multi-carrier Shopify app domain expert.
Answer the following question in ≤200 words using ONLY the context provided.
If the context is insufficient, say so clearly.

KB Context:
{kb_ctx}

Code Context:
{code_ctx}

Question: {question}"""
    llm = ChatAnthropic(
        model=config.DOMAIN_EXPERT_MODEL,
        api_key=config.ANTHROPIC_API_KEY,
        max_tokens=512,
    )
    resp = llm.invoke([HumanMessage(content=prompt)])
    sources = [d.metadata.get("source", d.metadata.get("file_path", "")) for d in kb_docs + code_docs]
    return {"answer": resp.content, "sources": sources}
```

### Pattern 5: Quick Questions Sidebar Buttons

**What:** Predefined question strings as `st.sidebar.button()` calls that set `st.session_state["chat_prefill"]`. On next render, if prefill is set, treat it as the user's question.

**When to use:** `ui/chat_app.py` sidebar.

```python
# Source: Streamlit session_state button pattern — standard
QUICK_QUESTIONS = [
    "How do I generate a FedEx label?",
    "How do I configure a UPS carrier account?",
    "What are the DHL special services?",
    "How does the label batch page work?",
    "How do I set up dry ice shipping?",
    "What is the MCSL automation rule priority?",
]

with st.sidebar:
    st.subheader("Quick Questions")
    for q in QUICK_QUESTIONS:
        if st.button(q, key=f"qq_{q[:20]}"):
            st.session_state["chat_prefill"] = q
            st.rerun()
```

### Pattern 6: Knowledge Base Refresh Button

**What:** Sidebar button that calls `ingest/run_ingest.py` via subprocess OR calls the ingest functions directly (preferred — avoids subprocess overhead).

**When to use:** When user clicks "Refresh Knowledge Base" in chat sidebar.

**Recommended approach:** Call `index_codebase()` from `rag/code_indexer.py` and the relevant ingest functions directly — same pattern as the sidebar sync buttons in the Release QA KB section.

```python
# Source: existing pattern in pipeline_dashboard.py sidebar (Phase 5)
from rag.code_indexer import index_codebase, sync_from_git
import config

if st.sidebar.button("Refresh Automation KB"):
    with st.sidebar.spinner("Re-indexing automation repo..."):
        result = sync_from_git(
            config.MCSL_AUTOMATION_REPO_PATH,
            source_type="automation",
        )
    if result.get("error"):
        st.sidebar.error(result["error"])
    else:
        st.sidebar.success(f"Updated {result['chunks_updated']} chunks")
```

### Pattern 7: Playwright JSON Result Parsing

**What:** Walk the JSON tree from `--reporter=json` to extract per-spec pass/fail/duration.

**The JSON structure** (confirmed from Playwright docs and mcsl-test-automation reporter config):
```
{
  "suites": [
    {
      "title": "spec file title",
      "file": "tests/orderGrid/tags/addTags.spec.ts",
      "specs": [
        {
          "title": "test name",
          "tests": [
            {
              "results": [{ "status": "passed|failed|timedOut|skipped", "duration": 1234 }]
            }
          ]
        }
      ]
    }
  ],
  "stats": { "expected": N, "unexpected": M, "duration": X, "startTime": "..." }
}
```

```python
# Source: Playwright JSON reporter format (verified from playwright.dev docs)
def parse_playwright_json(data: dict) -> list[dict]:
    """Returns list of {file, title, status, duration_ms}."""
    results = []
    for suite in data.get("suites", []):
        _parse_suite(suite, results)
    return results

def _parse_suite(suite: dict, results: list) -> None:
    file_name = suite.get("file", suite.get("title", ""))
    for spec in suite.get("specs", []):
        for test in spec.get("tests", []):
            for r in test.get("results", [])[:1]:  # take first result
                results.append({
                    "file": file_name,
                    "title": spec.get("title", ""),
                    "status": r.get("status", "unknown"),
                    "duration_ms": r.get("duration", 0),
                })
    # Recurse into nested suites
    for child in suite.get("suites", []):
        _parse_suite(child, results)
```

### Anti-Patterns to Avoid

- **Parsing `--reporter=list` text output:** Fragile — spacing and formatting varies. Always use `--reporter=json`.
- **Running all specs by default:** Users must select specific specs — running all 58 specs can take 10–30 minutes.
- **Blocking the Streamlit main thread:** Always wrap `subprocess.run()` in a `threading.Thread` with session state flags.
- **Spawning chat_app.py as a subprocess from pipeline_dashboard.py:** Keep them as two separate `streamlit run` commands. They share the same RAG collections on disk.
- **Embedding the Domain Expert Chat as a tab in pipeline_dashboard.py:** Roadmap specifies `ui/chat_app.py` as a separate app. Adding an 8th tab would break the `test_ui01_tab_stubs` test that asserts 7 tabs.
- **Calling `ingest/run_ingest.py` via subprocess for KB refresh:** Import and call the ingest functions directly to avoid subprocess env/path issues.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| JSON reporter parsing | Custom regex on `--reporter=list` text | `--reporter=json` + `json.loads(stdout)` | Playwright JSON is structured; text output format is unstable |
| RAG retrieval | New vector search code | `rag.vectorstore.search()` + `rag.code_indexer.search_code()` | Phase 1 established; already handles errors, empty collections |
| Slack posting | New HTTP requests | `pipeline.slack_client.post_content_to_slack_channel()` | Phase 8 established; handles webhook + bot token, chunking |
| LLM chat calls | Raw Anthropic SDK | `langchain_anthropic.ChatAnthropic` | Project standard; already used everywhere |
| Spec file tree | Manual `os.walk` + regex | `pathlib.Path.rglob("*.spec.ts")` | Clean, handles nested folders naturally |

**Key insight:** All infrastructure for Phase 10 already exists — this phase is assembly, not invention.

---

## Common Pitfalls

### Pitfall 1: Playwright JSON on stdout — but reporters also write to stderr

**What goes wrong:** With multiple reporters in `playwright.config.ts` (list + html + slack + ai), stdout may include reporter initialization warnings. The JSON output from `--reporter=json` goes to **stdout**, but some non-JSON lines (npm warnings, TS compile messages) may prefix it.

**Why it happens:** `npx` may print npm warnings before the JSON; `playwright.config.ts` loads custom reporters that may print to stdout.

**How to avoid:** Use `json.loads()` with a fallback that strips leading non-JSON lines. Look for the first `{` character in stdout before parsing. Better: pass `--reporter=json` which overrides the config reporters when used with the `--reporter` flag in newer Playwright versions — but verify this behavior.

**Warning signs:** `json.JSONDecodeError` — log `result.stdout[:500]` for debugging.

```python
# Safe JSON extraction
import re
def _extract_json(stdout: str) -> dict:
    match = re.search(r'\{', stdout)
    if match:
        try:
            return json.loads(stdout[match.start():])
        except Exception:
            pass
    return {}
```

### Pitfall 2: mcsl-test-automation requires browser auth state

**What goes wrong:** Running specs without a valid `auth-chrome.json` fails with login redirect. Playwright projects have `dependencies: ['setup-chrome']` which requires a login step first.

**Why it happens:** Shopify detects headless and requires manual login to produce the auth state file.

**How to avoid:** The Run Automation tab should show a warning if `auth-chrome.json` does not exist. Do NOT auto-run the login setup — it requires a headed browser and human interaction. Display: "Auth state required — run `npx playwright test tests/setup/login.setup.ts` first."

**Warning signs:** All tests fail immediately with "storage state file not found" or login redirect errors.

### Pitfall 3: MCSL_AUTOMATION_REPO_PATH not set or invalid

**What goes wrong:** `config.MCSL_AUTOMATION_REPO_PATH` defaults to `~/Documents/mcsl-test-automation` but the env var may not be set. `enumerate_specs()` crashes if the path doesn't exist.

**How to avoid:** Defensive check at tab render time — if path doesn't exist or is not a git repo, show a warning and a path input widget instead of the spec tree. Same pattern as the sidebar KB section.

### Pitfall 4: Playwright reporter conflict with `--reporter=json`

**What goes wrong:** `playwright.config.ts` already defines 4 reporters (list, html, playwright-smart-reporter, slack reporter). When `--reporter=json` is passed on CLI, it may ADD to the existing reporters or REPLACE them, depending on Playwright version.

**How to avoid:** Pass `--reporter=json` and also pass `--output=/dev/null` for HTML reporter to avoid conflicts, or use `PLAYWRIGHT_JSON_OUTPUT_FILE` env var with `--reporter=json` to write JSON to a file instead of stdout (more reliable than stdout capture with multiple reporters).

**Recommended approach:** Write to a temp file:
```python
import tempfile, os
with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
    json_path = f.name
env = {**os.environ, "PLAYWRIGHT_JSON_OUTPUT_FILE": json_path}
result = subprocess.run(
    ["npx", "playwright", "test", "--reporter=json", *spec_files],
    cwd=repo_path, env=env, capture_output=True, text=True, timeout=600,
)
data = json.loads(Path(json_path).read_text()) if Path(json_path).exists() else {}
os.unlink(json_path)
```

### Pitfall 5: chat_app.py RAG initialization cold-start

**What goes wrong:** First question to the Domain Expert Chat triggers Ollama embedding + ChromaDB load. On a cold start this can take 5–10 seconds, making the UI appear frozen.

**How to avoid:** Call `get_vectorstore()` eagerly at module load time (or in `st.cache_resource`) so it's warm before the first user question.

```python
# Source: Streamlit cache_resource pattern
@st.cache_resource
def _load_vectorstore():
    from rag.vectorstore import get_vectorstore
    return get_vectorstore()
```

### Pitfall 6: Session state key collisions between pipeline_dashboard.py and chat_app.py

**What goes wrong:** Both apps use `st.session_state` — but they are separate Streamlit processes so there is NO collision. However, within `pipeline_dashboard.py` tab_run must use distinct session state keys from other tabs.

**How to avoid:** Prefix all tab_run keys with `run_` (e.g., `run_running`, `run_result`, `run_selected_specs`). This is consistent with existing naming: `auto_result`, `auto_running` etc.

---

## Code Examples

### TestRunResult dataclass
```python
# Source: project pattern (AutomationResult in automation_writer.py)
from dataclasses import dataclass, field

@dataclass
class SpecResult:
    file: str
    title: str
    status: str          # "passed" | "failed" | "timedOut" | "skipped"
    duration_ms: int

@dataclass
class TestRunResult:
    specs: list[SpecResult] = field(default_factory=list)
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    duration_ms: int = 0
    error: str = ""
```

### Post to Slack — test results formatter
```python
# Source: established pattern (post_content_to_slack_channel in slack_client.py)
from pipeline.slack_client import post_content_to_slack_channel

def _format_results_for_slack(result: TestRunResult, run_name: str) -> str:
    lines = [f"*Automation Run: {run_name}*", ""]
    lines.append(f"Total: {result.total} | Passed: {result.passed} | Failed: {result.failed} | Skipped: {result.skipped}")
    lines.append(f"Duration: {result.duration_ms/1000:.1f}s")
    lines.append("")
    for s in result.specs:
        icon = "✅" if s.status == "passed" else ("❌" if s.status == "failed" else "⏭️")
        lines.append(f"{icon} `{s.file}` — {s.title} ({s.duration_ms}ms)")
    return "\n".join(lines)
```

### chat_app.py skeleton
```python
# Source: Streamlit chat widget docs + project RAG pattern
import streamlit as st
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(raise_error_if_not_found=False), override=True)

st.set_page_config(page_title="MCSL Domain Expert", layout="wide")
st.title("MCSL Domain Expert Chat")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Render history
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Prefill from Quick Question
prefill = st.session_state.pop("chat_prefill", None)

if question := (st.chat_input("Ask about MCSL...") or prefill):
    st.session_state["messages"].append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)
    with st.chat_message("assistant"):
        with st.spinner("Searching knowledge base..."):
            result = ask_domain_expert(question)
        st.write(result["answer"])
        if result["sources"]:
            with st.expander("Sources"):
                for s in result["sources"]:
                    st.caption(s)
    st.session_state["messages"].append({"role": "assistant", "content": result["answer"]})
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Parse `--reporter=list` text | `--reporter=json` structured output | Playwright 1.20+ | Reliable pass/fail/duration extraction |
| `st.text_input` for chat | `st.chat_input` + `st.chat_message` | Streamlit 1.23 (2023) | Native chat UI with role-based bubbles |
| Subprocess blocking UI | `threading.Thread` + session state polling | Phase 4 of this project | Responsive UI during long test runs |

**Deprecated/outdated:**
- `PLAYWRIGHT_JSON_OUTPUT_NAME`: Older env var; use `PLAYWRIGHT_JSON_OUTPUT_FILE` with modern Playwright.

---

## Open Questions

1. **Does `--reporter=json` override or add to config-defined reporters?**
   - What we know: Playwright CLI `--reporter` flag behavior changed between versions; mcsl-test-automation uses Playwright configured via `playwright.config.ts` with 4 reporters
   - What's unclear: Whether passing `--reporter=json` CLI flag suppresses the 4 config reporters in the version installed in mcsl-test-automation
   - Recommendation: Use `PLAYWRIGHT_JSON_OUTPUT_FILE` temp file approach (Pattern 4 above) — this always works regardless of reporter override behavior

2. **Which Playwright project to run by default?**
   - What we know: Config defines "Google Chrome", "Safari", "Firefox" projects; "Google Chrome" uses `auth-chrome.json`
   - What's unclear: Whether Safari/Firefox auth state files exist
   - Recommendation: Default to "Google Chrome"; add a project selector dropdown in the UI

3. **Should chat_app.py be launchable from pipeline_dashboard.py?**
   - What we know: Roadmap says `ui/chat_app.py` is separate; pipeline_dashboard.py must remain 7 tabs
   - What's unclear: Whether users want a link/button in the dashboard to open the chat app
   - Recommendation: Add a `st.link_button("Open Domain Expert Chat", "http://localhost:8502")` in tab_run or sidebar as a convenience — no functional coupling

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (already configured) |
| Config file | none (uses pyproject defaults) |
| Quick run command | `.venv/bin/python -m pytest tests/ -q --tb=short` |
| Full suite command | `.venv/bin/python -m pytest tests/ -q --tb=short` |

Current baseline: **129 passed, 7 skipped** in 3.54s

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| RUN-01 | `enumerate_specs()` returns grouped spec paths | unit | `.venv/bin/python -m pytest tests/test_run_automation.py::test_run01_enumerate_specs -x` | ❌ Wave 0 |
| RUN-01 | `TestRunResult` dataclass has correct fields | unit | `.venv/bin/python -m pytest tests/test_run_automation.py::test_run01_test_run_result_dataclass -x` | ❌ Wave 0 |
| RUN-01 | `parse_playwright_json()` extracts pass/fail/duration from fixture JSON | unit | `.venv/bin/python -m pytest tests/test_run_automation.py::test_run01_parse_playwright_json -x` | ❌ Wave 0 |
| RUN-01 | `run_release_tests()` calls subprocess with correct args | unit (mock) | `.venv/bin/python -m pytest tests/test_run_automation.py::test_run01_run_release_tests_calls_subprocess -x` | ❌ Wave 0 |
| CHAT-01 | `ask_domain_expert()` returns answer and sources | unit (mock RAG) | `.venv/bin/python -m pytest tests/test_chat_app.py::test_chat01_ask_domain_expert -x` | ❌ Wave 0 |
| CHAT-01 | `ask_domain_expert()` handles empty RAG gracefully | unit | `.venv/bin/python -m pytest tests/test_chat_app.py::test_chat01_empty_rag_returns_fallback -x` | ❌ Wave 0 |
| CHAT-02 | Quick Questions list has ≥5 entries | unit | `.venv/bin/python -m pytest tests/test_chat_app.py::test_chat02_quick_questions_list -x` | ❌ Wave 0 |
| CHAT-02 | `chat_app.py` module importable (no crash on load) | unit | `.venv/bin/python -m pytest tests/test_chat_app.py::test_chat02_module_importable -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `.venv/bin/python -m pytest tests/ -q --tb=short`
- **Per wave merge:** `.venv/bin/python -m pytest tests/ -q --tb=short`
- **Phase gate:** Full suite green (≥129 passed + new tests) before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_run_automation.py` — covers RUN-01 (pipeline/test_runner.py unit tests)
- [ ] `tests/test_chat_app.py` — covers CHAT-01, CHAT-02 (ui/chat_app.py unit tests)
- [ ] `ui/__init__.py` — make `ui/` a Python package so `ui.chat_app` is importable in tests

---

## Sources

### Primary (HIGH confidence)
- Direct codebase inspection — `rag/vectorstore.py`, `rag/code_indexer.py`, `pipeline/slack_client.py`, `pipeline/automation_writer.py`, `pipeline_dashboard.py`
- Direct inspection — `mcsl-test-automation/playwright.config.ts`, `mcsl-test-automation/tests/` folder tree (58 spec files, 11 folders)
- Direct inspection — `tests/` (129 passed, 7 skipped baseline), `tests/conftest.py`, `config.py`

### Secondary (MEDIUM confidence)
- Playwright JSON reporter format — documented at playwright.dev; structure confirmed by `playwright.config.ts` which already uses `html` reporter (same output pipeline)
- `PLAYWRIGHT_JSON_OUTPUT_FILE` env var — Playwright docs; used to write JSON to file rather than stdout

### Tertiary (LOW confidence)
- Whether `--reporter=json` CLI flag suppresses config-defined reporters in the exact Playwright version installed in mcsl-test-automation — not verified without running it

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all libraries already installed and in use; no new dependencies
- Architecture: HIGH — patterns directly inherited from existing pipeline/ modules; Playwright JSON format confirmed
- Pitfalls: HIGH for auth state / path checks (confirmed from codebase); MEDIUM for reporter conflict (depends on Playwright version)

**Research date:** 2026-04-18
**Valid until:** 2026-05-18 (stable stack; Streamlit chat API unlikely to change)
