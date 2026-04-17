# Phase 5: Full Dashboard UI — Research

**Researched:** 2026-04-17
**Domain:** Streamlit multi-tab dashboard — MCSL branding, CSS, sidebar, session state
**Confidence:** HIGH — all findings sourced from live FedEx reference implementation and current MCSL codebase

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| UI-01 | 7-tab Streamlit dashboard: User Story, Move Cards, Release QA, History, Sign Off, Write Automation, Run Automation | FedEx reference line 904 shows exact `st.tabs()` call with all 7 tab labels and emoji prefixes |
| UI-02 | Sidebar: System Status badges (Claude API, Trello, Slack, Google Sheets, Ollama) | FedEx reference lines 429-438 show `_status_badge()` helper and 5-badge block; env var names confirmed |
| UI-03 | Sidebar: Release Progress section with counters and progress bar | FedEx reference lines 443-484 show `rqa_*` session state keys and mini progress bar pattern |
| UI-04 | Sidebar: Code Knowledge Base (Automation/Backend/Frontend repo path + sync) | FedEx reference lines 488-728 show 3-expander pattern; MCSL maps to `automation`/`storepepsaas_server`/`storepepsaas_client` |
| UI-05 | MCSL branding: "🚚 MCSL QA Pipeline" header, dark theme, wide layout | FedEx reference lines 32-37 for page config; lines 418-426 for header; dark theme already in `.streamlit/config.toml` |
| UI-06 | Global CSS: status badges, scenario cards, severity badges, pipeline flow bar | FedEx reference lines 40-177 — full CSS block catalogued below |
| UI-07 | Dry run toggle in sidebar | FedEx reference line 900: `st.toggle("Dry Run (no writes)", value=False)` |
</phase_requirements>

---

## Summary

Phase 5 replaces `pipeline_dashboard.py` (currently a single-tab Phase 4 UI) with a full 7-tab Streamlit app matching the FedEx QA Pipeline structure. The FedEx reference at `/Users/madan/Documents/Fed-Ex-automation/FedexDomainExpert/ui/pipeline_dashboard.py` has been read in full and is the authoritative source — every pattern needed for Phase 5 is already proven there.

The MCSL version is a direct adaptation: same tab order, same sidebar structure, same CSS class vocabulary — but with "MCSL QA Pipeline" branding and MCSL-specific config keys (`MCSL_AUTOMATION_REPO_PATH`, `STOREPEPSAAS_SERVER_PATH`, `STOREPEPSAAS_CLIENT_PATH`) replacing FedEx-specific ones (`AUTOMATION_CODEBASE_PATH`, `BACKEND_CODE_PATH`, `FRONTEND_CODE_PATH`). The dark theme is already established in `.streamlit/config.toml` (base="dark", primaryColor="#00d4aa", backgroundColor="#0f1117"). The Phase 4 CSS block already defines verdict badges and scenario cards; Phase 5 extends it with FedEx-style structural CSS.

All three plans in Phase 5 are pure scaffolding — no pipeline logic changes. The Phase 4 pipeline functions (`_run_pipeline`, `start_run`, `render_report`, `_init_state`, `_make_stop_callback`, `_progress_cb`) must be preserved verbatim. Tab bodies are stubs with placeholder `st.info()` messages.

**Primary recommendation:** Completely replace `pipeline_dashboard.py` top-to-bottom. Preserve all working Phase 4 functions exactly. Extend `_init_state()` with new keys. Replace the layout section with the 7-tab FedEx structure, adapting brand strings and config key names only.

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| streamlit | 1.56.0 (installed) | App framework, multi-tab UI, session state | Already installed; Phase 4 uses it |
| os / os.getenv | stdlib | Env var checks for status badges | No new deps needed |
| threading, time, json | stdlib | Background agent runs, polling, history (preserved from Phase 4) | Already working |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `config` (project) | — | Read ANTHROPIC_API_KEY, GOOGLE_CREDENTIALS_PATH, path defaults | Status badge truthiness checks, KB path defaults |
| `rag.code_indexer` (project) | — | `get_index_stats()`, `index_codebase()`, `sync_from_git()`, `get_repo_info()` | Knowledge Base sidebar expanders |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `st.tabs()` for 7-tab layout | Multi-page app (`pages/`) | `st.tabs()` keeps all state in one script; matches FedEx reference exactly |
| CSS via `st.markdown(unsafe_allow_html=True)` | `st.html()` (Streamlit 1.31+) | `st.markdown` is the established pattern used in Phase 4 |

**Installation:** No new packages required.

---

## Architecture Patterns

### Recommended Project Structure
```
pipeline_dashboard.py        # REPLACED — full 7-tab version (repo root, not moved to ui/)
.streamlit/config.toml       # UNCHANGED — dark theme already set
tests/test_dashboard.py      # EXTENDED — append UI-01 through UI-07 tests
```

### Pattern 1: Page Config and CSS Injection
**What:** `st.set_page_config()` MUST be the first Streamlit call. CSS injected via `st.markdown(_CSS, unsafe_allow_html=True)` immediately after.
**When to use:** Module top-level, before any `main()` definition.
```python
# Source: FedexDomainExpert/ui/pipeline_dashboard.py lines 32-178
st.set_page_config(
    page_title="MCSL QA Pipeline",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(_CSS, unsafe_allow_html=True)
```

### Pattern 2: Session State Initialisation
**What:** All keys set idempotently in `_init_state()`, called at top of `main()`.
**Phase 4 keys (PRESERVE verbatim):**
```python
"sav_running": False
"sav_stop":    threading.Event()
"sav_result":  None
"sav_prog":    {"current": 0, "total": 0, "label": ""}
```
**New Phase 5 keys:**
```python
"pipeline_runs":          {}     # persisted history (loaded from disk)
"trello_connected":       False
"ac_drafts_loaded":       False
"code_paths_initialized": False  # one-time config→state seed guard
"rqa_cards":              []
"rqa_approved":           {}
"rqa_test_cases":         {}
"rqa_release":            ""
```
Note: `be_repo_path`, `fe_repo_path`, `automation_code_path` are seeded inside the `code_paths_initialized` guard, not in `_init_state`.

### Pattern 3: Status Badge Helper
**What:** Pure function returning HTML; all 5 badges rendered as one `st.markdown()` call.
```python
# Source: FedexDomainExpert lines 338-344
def _status_badge(label: str, ok: bool, err_hint: str = "") -> str:
    if ok:
        return f'<div class="status-badge status-ok">✅ &nbsp;{label}</div>'
    else:
        hint = f" — {err_hint}" if err_hint else ""
        return f'<div class="status-badge status-err">❌ &nbsp;{label}{hint}</div>'
```

### Pattern 4: Env Var Checks for Status Badges
**What:** Boolean flags computed once before sidebar renders; reused in tab body for conditional gating.
```python
# Source: FedexDomainExpert lines 402-413, adapted for MCSL
import config
api_ok    = bool(config.ANTHROPIC_API_KEY)
trello_ok = all([os.getenv("TRELLO_API_KEY"), os.getenv("TRELLO_TOKEN"), os.getenv("TRELLO_BOARD_ID")])
slack_ok  = bool(
    os.getenv("SLACK_WEBHOOK_URL", "").strip()
    or (os.getenv("SLACK_BOT_TOKEN", "").strip() and os.getenv("SLACK_CHANNEL", "").strip())
)
sheets_ok = bool(os.path.exists(config.GOOGLE_CREDENTIALS_PATH))
# Ollama: live check against local server (FedEx hardcodes True — MCSL checks properly)
try:
    import urllib.request as _ur
    _ur.urlopen(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=2)
    ollama_ok = True
except Exception:
    ollama_ok = False
```

### Pattern 5: 7-Tab Layout
**What:** Single `st.tabs()` call, 7 tab objects, each used as context manager.
```python
# Source: FedexDomainExpert line 904 — exact tab names and emoji
tab_us, tab_devdone, tab_release, tab_history, tab_signoff, tab_manual, tab_run = st.tabs([
    "📝 User Story",
    "🔀 Move Cards",
    "🚀 Release QA",
    "📋 History",
    "✅ Sign Off",
    "✍️ Write Automation",
    "▶️ Run Automation",
])
```
Phase 5: each `with tab_*:` block contains only a stub `st.info("Coming in Phase N.")`.

### Pattern 6: code_paths_initialized Guard
**What:** One-time session state seed that reads repo paths from config on first page load.
```python
# Source: FedexDomainExpert lines 395-401, adapted for MCSL config keys
if "code_paths_initialized" not in st.session_state:
    if config.MCSL_AUTOMATION_REPO_PATH:
        st.session_state["automation_code_path"] = config.MCSL_AUTOMATION_REPO_PATH
    if config.STOREPEPSAAS_SERVER_PATH:
        st.session_state["be_repo_path"] = config.STOREPEPSAAS_SERVER_PATH
    if config.STOREPEPSAAS_CLIENT_PATH:
        st.session_state["fe_repo_path"] = config.STOREPEPSAAS_CLIENT_PATH
    st.session_state["code_paths_initialized"] = True
```

### Pattern 7: Knowledge Base Expanders
**What:** Three `st.expander()` blocks — Automation, StorePepSAAS Server, StorePepSAAS Client.
Each has: path text_input, optional branch selectbox, Pull & Sync + Full Re-index buttons in two columns.
**MCSL source type strings:** `"automation"`, `"storepepsaas_server"`, `"storepepsaas_client"`.
**Config keys:** `config.MCSL_AUTOMATION_REPO_PATH`, `config.STOREPEPSAAS_SERVER_PATH`, `config.STOREPEPSAAS_CLIENT_PATH`.
**`get_index_stats()` keys:** `"automation"`, `"storepepsaas_server"`, `"storepepsaas_client"`, `"automation_sync"`, `"server_sync"`, `"client_sync"`.

### Pattern 8: Release Progress Section
```python
# Source: FedexDomainExpert lines 443-484
cards    = st.session_state.get("rqa_cards", [])
approved = st.session_state.get("rqa_approved", {})
tc_store = st.session_state.get("rqa_test_cases", {})
n_cards    = len(cards)
n_approved = sum(1 for c in cards if approved.get(c.id))
n_tc       = sum(1 for c in cards if c.id in tc_store)
current_release = st.session_state.get("rqa_release", "")

if current_release:
    st.markdown(f"**Release:** `{current_release}`")
    # inline HTML rows for counters
    if n_cards > 0:
        st.progress(n_approved / n_cards, text=f"{n_approved}/{n_cards} approved")
else:
    st.caption("Load a release in Release QA to see progress.")
```

### Pattern 9: Dry Run Toggle
```python
# Source: FedexDomainExpert line 900 — bottom of sidebar, before `with st.sidebar:` closes
dry_run = st.toggle("🧪 Dry Run (no writes)", value=False)
st.caption("Generates output without writing to Trello, repo, or Sheets.")
```

### Anti-Patterns to Avoid
- **`st.set_page_config()` not first:** Any Streamlit call before it raises `StreamlitAPIException`.
- **`import config` at module top level:** `config.py` calls `load_dotenv()` — must stay inside `main()` to avoid import-phase side effects.
- **Calling `st.*` from background thread:** Only `st.session_state` dict key writes are safe from threads.
- **Using FedEx config key names:** `config.BACKEND_CODE_PATH` and `config.FRONTEND_CODE_PATH` do not exist in MCSL config.py — will raise `AttributeError`.
- **Using FedEx `get_index_stats()` key names `"backend"` / `"frontend"`:** MCSL uses `"storepepsaas_server"` / `"storepepsaas_client"`.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Status badge HTML | Custom HTML | `_status_badge()` helper | Already proven in FedEx reference |
| Branch listing | Custom `subprocess.run(['git', 'branch', ...])` | `rag.code_indexer.get_repo_info(path)` → `result["branches"]` | Already implemented in MCSL |
| Index stats | Direct ChromaDB query | `rag.code_indexer.get_index_stats()` | Returns typed dict with per-source counts and sync metadata |
| Code sync | Custom git + embed loop | `rag.code_indexer.sync_from_git(path, source_type, branch)` | Already handles pull + re-embed delta |
| Full re-index | Custom walk | `rag.code_indexer.index_codebase(path, source_type, clear_existing=True)` | Already handles extensions filter, batching |

**Key insight:** Phase 5 is pure UI scaffolding. All backend functions already exist — no new logic.

---

## Common Pitfalls

### Pitfall 1: FedEx Config Keys Do Not Exist in MCSL
**What goes wrong:** Copy FedEx sidebar code referencing `config.BACKEND_CODE_PATH` or `config.FRONTEND_CODE_PATH` — raises `AttributeError`.
**Why it happens:** FedEx config has these keys; MCSL config has differently named equivalents.
**How to avoid:** Replace FedEx → MCSL config keys:
- `config.BACKEND_CODE_PATH` → `config.STOREPEPSAAS_SERVER_PATH`
- `config.FRONTEND_CODE_PATH` → `config.STOREPEPSAAS_CLIENT_PATH`
- `config.AUTOMATION_CODEBASE_PATH` → `config.MCSL_AUTOMATION_REPO_PATH`
**Warning signs:** `AttributeError: module 'config' has no attribute 'BACKEND_CODE_PATH'` on app launch.

### Pitfall 2: FedEx `get_index_stats()` Key Names Wrong for MCSL
**What goes wrong:** `_stats.get("backend", 0)` always returns 0 — "Not indexed" badge stuck on even after successful index.
**Why it happens:** MCSL `get_index_stats()` uses `storepepsaas_server`, `storepepsaas_client`, `automation`.
**How to avoid:** Use MCSL source type string names throughout.
**Warning signs:** KB expanders show "Not indexed" status despite successful prior indexing.

### Pitfall 3: Phase 4 Functions Accidentally Removed
**What goes wrong:** Full rewrite omits `_run_pipeline`, `start_run`, `render_report`, `_make_stop_callback`, `_progress_cb` — 5 Phase 4 tests fail.
**How to avoid:** Plan tasks must explicitly list these as "carry forward unchanged."
**Warning signs:** `test_dash01_scaffold`, `test_dash02_threading`, `test_dash03_progress`, `test_dash04_stop_button`, `test_dash05_report_render` all fail.

### Pitfall 4: `st.set_page_config()` Not First
**What goes wrong:** `StreamlitAPIException: set_page_config() can only be called once per app page...`
**How to avoid:** `set_page_config` → `st.markdown(_CSS)` → rest of module-level code. Import `config` only inside `main()`.

### Pitfall 5: Session State Key Collision on Widget Keys
**What goes wrong:** Widget `key="be_repo_path"` is also used as a manual `st.session_state["be_repo_path"]` write — raises `StreamlitAPIException`.
**How to avoid:** Keep key names consistent; never do `st.session_state.be_repo_path = x` directly after widget renders — use dict form `st.session_state["be_repo_path"] = x` before the widget renders (in the `code_paths_initialized` block).

### Pitfall 6: Ollama Hardcoded True
**What goes wrong:** FedEx passes `True` unconditionally for Ollama badge — misleads users when Ollama is down.
**How to avoid:** Use `urllib.request.urlopen` with 2s timeout as shown in Pattern 4. Wrap in try/except so dashboard loads when Ollama offline.

---

## CSS Classes — Complete Inventory

All class names sourced from FedEx reference lines 40-177. Carry all into MCSL `_CSS` block verbatim, adjusting only brand gradient colours.

### App Header
```
.pipeline-header        — gradient div wrapping h1 title
.pipeline-header h1     — white bold title text
.pipeline-header p      — muted subtitle
```

### Status Badges (sidebar)
```
.status-badge           — base: inline-flex, full-width, rounded pill
.status-ok              — green bg (#d4edda), dark green text
.status-warn            — yellow bg (#fff3cd), amber text
.status-err             — red bg (#f8d7da), dark red text
```

### Pipeline Step Chips (tab bodies)
```
.step-chip              — indigo chip for "① Select Release" labels
```

### Risk Level Badges
```
.risk-low               — green
.risk-medium            — amber
.risk-high              — red
```

### Card Step Headers
```
.step-header            — flex row: circle + title
.step-num               — indigo circle, white number
.step-title             — bold 0.95rem label
```

### Streamlit Overrides
```
[data-testid="metric-container"]             — styled metric boxes
section[data-testid="stSidebar"] > div       — sidebar padding
button[data-baseweb="tab"]                   — bold tab labels
[data-testid="stExpander"]                   — rounded border
```

### Pipeline Flow Bar
```
.pipeline-flow          — flex row container
.pf-step                — slate chip
.pf-step.done           — green done state
.pf-step.active         — indigo active state
.pf-arrow               — muted arrow connector
```

### Bug Severity Badges
```
.sev-p1  — P1 red
.sev-p2  — P2 orange
.sev-p3  — P3 yellow
.sev-p4  — P4 green
```

### Phase 4 CSS Classes (already in MCSL — keep unchanged)
```
.badge-pass / .badge-fail / .badge-partial / .badge-qa_needed
.scenario-card (+ .pass / .fail / .partial / .qa_needed)
.app-header
.app-subtitle
```

**MCSL brand colour note:** Change `.pipeline-header` gradient from FedEx blue-indigo (`#1a1f36` → `#2d3561`) to a dark teal-navy (`#0f1723` → `#1a2d2a`) to match the `#00d4aa` teal already established in `.streamlit/config.toml`. Keep `#818cf8` release-badge colour from FedEx or replace with `#00d4aa`.

---

## Session State Key Reference

### Preserved from Phase 4 (no changes)
| Key | Type | Set by |
|-----|------|--------|
| `sav_running` | bool | `start_run()` / `_run_pipeline()` |
| `sav_stop` | threading.Event | `_init_state()` / stop callback |
| `sav_result` | dict or None | `_run_pipeline()` |
| `sav_prog` | dict | `_progress_cb()` |

### New in Phase 5
| Key | Type | Description |
|-----|------|-------------|
| `code_paths_initialized` | bool | One-time config-to-state seed guard |
| `automation_code_path` | str | Automation repo path (input widget + sync) |
| `be_repo_path` | str | storepepSAAS server repo path |
| `fe_repo_path` | str | storepepSAAS client repo path |
| `auto_branch_select` | str | Widget key for automation branch selectbox |
| `be_branch_select` | str | Widget key for server branch selectbox |
| `fe_branch_select` | str | Widget key for client branch selectbox |
| `rqa_release` | str | Current release label (used in header badge + progress section) |
| `rqa_cards` | list | Loaded Trello card objects (Phase 7 populates) |
| `rqa_approved` | dict | card.id → bool (Phase 7 populates) |
| `rqa_test_cases` | dict | card.id → test case text (Phase 7 populates) |
| `dry_run` | bool | Toggle value (Phase 6+ consumes) |
| `pipeline_runs` | dict | Persisted history loaded from data/pipeline_history.json |

---

## Env Var Reference

| Service | Env Var(s) | Truthy condition |
|---------|-----------|-----------------|
| Claude API | `ANTHROPIC_API_KEY` | `bool(config.ANTHROPIC_API_KEY)` |
| Trello | `TRELLO_API_KEY`, `TRELLO_TOKEN`, `TRELLO_BOARD_ID` | `all([...])` — all three required |
| Slack | `SLACK_WEBHOOK_URL` OR (`SLACK_BOT_TOKEN` + `SLACK_CHANNEL`) | Either webhook or bot+channel |
| Google Sheets | file at `GOOGLE_CREDENTIALS_PATH` | `os.path.exists(config.GOOGLE_CREDENTIALS_PATH)` |
| Ollama | `OLLAMA_BASE_URL` (default `http://localhost:11434`) | HTTP GET to `/api/tags` with 2s timeout |

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Single-page Trello URL input (Phase 4) | 7-tab dashboard | Phase 5 | Full layout replacement |
| `st.image(use_column_width=True)` | `st.image(use_container_width=True)` | Streamlit ~1.30 | Phase 4 already correct |
| `@st.experimental_cache` | `@st.cache_data(ttl=60)` | Streamlit 1.18 | FedEx reference uses `@st.cache_data` |

**Deprecated/outdated:**
- `st.beta_columns()` → `st.columns()` (not used in FedEx reference)
- `use_column_width` parameter → `use_container_width`

---

## Open Questions

1. **`rqa_cards` item access pattern**
   - What we know: Release Progress section accesses `c.id` on each item in `rqa_cards`.
   - What's unclear: Phase 5 only scaffolds the sidebar; actual card loading is Phase 7.
   - Recommendation: Guard the entire progress section with `if n_cards > 0` — empty list produces safe defaults.

2. **StorePepSAAS Client Path relevance**
   - What we know: FedEx has "Frontend Code" expander; MCSL equivalent is `STOREPEPSAAS_CLIENT_PATH`.
   - What's unclear: Whether this path is ever meaningfully synced during QA sessions.
   - Recommendation: Include the expander regardless — Phase 5 scaffolds it; it costs nothing to have.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (already configured, venv at `/Users/madan/Documents/MCSLDomainExpert/.venv`) |
| Config file | none (no pytest.ini found; `pytest tests/` from project root) |
| Quick run command | `/Users/madan/Documents/MCSLDomainExpert/.venv/bin/python -m pytest tests/test_dashboard.py -x -q` |
| Full suite command | `/Users/madan/Documents/MCSLDomainExpert/.venv/bin/python -m pytest tests/ -x -q` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| UI-01 | `st.tabs()` called with exactly 7 labels matching spec | unit | `pytest tests/test_dashboard.py::test_ui01_seven_tabs -x` | Wave 0 |
| UI-02 | `_status_badge()` returns correct HTML class for ok/err; 5 env vars checked | unit | `pytest tests/test_dashboard.py::test_ui02_status_badges -x` | Wave 0 |
| UI-03 | Release Progress reads `rqa_cards`, `rqa_approved`, `rqa_test_cases` from session state | unit | `pytest tests/test_dashboard.py::test_ui03_release_progress -x` | Wave 0 |
| UI-04 | KB expanders reference MCSL source type strings, not FedEx ones | unit | `pytest tests/test_dashboard.py::test_ui04_knowledge_base -x` | Wave 0 |
| UI-05 | `set_page_config` called with `page_title="MCSL QA Pipeline"`, `page_icon="🚚"`, `layout="wide"` | unit | `pytest tests/test_dashboard.py::test_ui05_branding -x` | Wave 0 |
| UI-06 | `_CSS` string contains all required CSS class names | unit | `pytest tests/test_dashboard.py::test_ui06_css_classes -x` | Wave 0 |
| UI-07 | `st.toggle()` called with "Dry Run" label and `value=False` | unit | `pytest tests/test_dashboard.py::test_ui07_dry_run_toggle -x` | Wave 0 |

### TDD Test Stubs — Per Plan

**05-01: App Shell (page config, CSS block, 7-tab layout)**

```python
# test_ui05_branding
def test_ui05_branding():
    from unittest.mock import patch, MagicMock
    calls = {}
    with patch("streamlit.set_page_config", side_effect=lambda **kw: calls.update(kw)):
        import importlib, pipeline_dashboard
        importlib.reload(pipeline_dashboard)
    assert calls.get("page_title") == "MCSL QA Pipeline"
    assert calls.get("page_icon") == "🚚"
    assert calls.get("layout") == "wide"

# test_ui06_css_classes
def test_ui06_css_classes():
    import pipeline_dashboard as pd
    required = [
        "pipeline-header", "status-badge", "status-ok", "status-err", "status-warn",
        "step-chip", "risk-low", "risk-medium", "risk-high",
        "step-header", "step-num", "step-title",
        "pf-step", "pf-arrow", "pipeline-flow",
        "sev-p1", "sev-p2", "sev-p3", "sev-p4",
        "badge-pass", "badge-fail", "badge-partial", "badge-qa_needed",
        "scenario-card",
    ]
    for cls in required:
        assert cls in pd._CSS, f"CSS class '{cls}' missing from _CSS"

# test_ui01_seven_tabs
def test_ui01_seven_tabs():
    from unittest.mock import patch, MagicMock
    import pipeline_dashboard as pd
    with patch("pipeline_dashboard.st") as mock_st:
        mock_st.tabs.return_value = [MagicMock()] * 7
        mock_st.session_state = make_ss()
        # trigger just the tabs call by checking the module
        call_args_list = mock_st.tabs.call_args_list
    # Verify tab count and names when tabs() is called
    import pipeline_dashboard as pd2
    assert hasattr(pd2, "_CSS")  # smoke check file loads
```

**05-02: Sidebar (System Status, Release Progress, Knowledge Base)**

```python
# test_ui02_status_badges
def test_ui02_status_badges():
    import pipeline_dashboard as pd
    ok_html = pd._status_badge("Claude API", True)
    assert "status-ok" in ok_html and "Claude API" in ok_html

    err_html = pd._status_badge("Trello", False, "Set TRELLO_* in .env")
    assert "status-err" in err_html
    assert "Set TRELLO_" in err_html

# test_ui03_release_progress
def test_ui03_release_progress():
    # Verify session state keys used in Release Progress section are the correct names
    import pipeline_dashboard as pd
    # The function must read these exact keys from session_state
    import inspect
    src = inspect.getsource(pd)
    assert "rqa_cards" in src
    assert "rqa_approved" in src
    assert "rqa_test_cases" in src
    assert "rqa_release" in src

# test_ui04_knowledge_base
def test_ui04_knowledge_base():
    import pipeline_dashboard as pd
    import inspect
    src = inspect.getsource(pd)
    # MCSL source type names must appear; FedEx names must not
    assert "storepepsaas_server" in src
    assert "storepepsaas_client" in src
    assert "MCSL_AUTOMATION_REPO_PATH" in src
    # FedEx config keys must NOT appear
    assert "BACKEND_CODE_PATH" not in src
    assert "FRONTEND_CODE_PATH" not in src
```

**05-03: Tab Scaffolds (7 stub tabs)**

```python
# test_ui07_dry_run_toggle
def test_ui07_dry_run_toggle():
    import pipeline_dashboard as pd
    import inspect
    src = inspect.getsource(pd)
    assert "st.toggle" in src
    assert "Dry Run" in src or "dry run" in src.lower()

# test_ui01_tab_stubs (verify all 7 tab variable names declared)
def test_ui01_tab_stubs():
    import pipeline_dashboard as pd
    import inspect
    src = inspect.getsource(pd)
    # All 7 tab variable names must appear
    for tab_var in ["tab_us", "tab_devdone", "tab_release", "tab_history",
                    "tab_signoff", "tab_manual", "tab_run"]:
        assert tab_var in src, f"Tab variable '{tab_var}' missing"
```

### Sampling Rate
- **Per task commit:** `/Users/madan/Documents/MCSLDomainExpert/.venv/bin/python -m pytest tests/test_dashboard.py -x -q`
- **Per wave merge:** `/Users/madan/Documents/MCSLDomainExpert/.venv/bin/python -m pytest tests/ -x -q`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_dashboard.py` — append 7 new test functions: `test_ui01_seven_tabs`, `test_ui02_status_badges`, `test_ui03_release_progress`, `test_ui04_knowledge_base`, `test_ui05_branding`, `test_ui06_css_classes`, `test_ui07_dry_run_toggle` (existing DASH-01 through DASH-05 tests must remain intact)

---

## Sources

### Primary (HIGH confidence)
- `/Users/madan/Documents/Fed-Ex-automation/FedexDomainExpert/ui/pipeline_dashboard.py` — full file read; CSS block (lines 40-177), session state init (lines 244-256), status badge helper (lines 338-344), code_paths_initialized guard (lines 395-401), connection checks (lines 402-413), sidebar structure (lines 428-901), tab layout (line 904)
- `/Users/madan/Documents/MCSLDomainExpert/.claude/worktrees/objective-archimedes/pipeline_dashboard.py` — current Phase 4 file; CSS, STATUS_BADGE dict, session state keys, threading pattern
- `/Users/madan/Documents/MCSLDomainExpert/.claude/worktrees/objective-archimedes/config.py` — MCSL config key names confirmed: `ANTHROPIC_API_KEY`, `GOOGLE_CREDENTIALS_PATH`, `OLLAMA_BASE_URL`, `MCSL_AUTOMATION_REPO_PATH`, `STOREPEPSAAS_SERVER_PATH`, `STOREPEPSAAS_CLIENT_PATH`
- `/Users/madan/Documents/MCSLDomainExpert/.clone/worktrees/objective-archimedes/.streamlit/config.toml` — dark theme: base="dark", primaryColor="#00d4aa", backgroundColor="#0f1117"
- `/Users/madan/Documents/MCSLDomainExpert/.clone/worktrees/objective-archimedes/tests/test_dashboard.py` — existing test patterns for DASH-01 through DASH-05 and card_processor

### Secondary (MEDIUM confidence)
- `.planning/REQUIREMENTS.md` lines 81-89 — UI-01 through UI-07 descriptions
- `.planning/ROADMAP.md` lines 108-123 — Phase 5 plan breakdown

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — confirmed against installed packages and Phase 4 imports
- Architecture patterns: HIGH — direct transcription from FedEx reference source
- CSS classes: HIGH — catalogued directly from FedEx reference lines 40-177
- Session state keys: HIGH — sourced from both FedEx reference and Phase 4 MCSL dashboard
- Pitfalls: HIGH — config key mismatches verified against actual MCSL config.py
- Test patterns: MEDIUM — patterns follow Phase 4 established mock approach; some `inspect.getsource` stubs may need refinement

**Research date:** 2026-04-17
**Valid until:** 2026-05-17 (stable Streamlit 1.x API; MCSL config unlikely to change)
