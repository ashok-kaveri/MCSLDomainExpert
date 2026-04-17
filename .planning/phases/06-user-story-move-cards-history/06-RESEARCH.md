# Phase 6: User Story + Move Cards + History — Research

**Researched:** 2026-04-17
**Domain:** Streamlit UI, Claude API, Trello REST API, RAG retrieval, JSON persistence
**Confidence:** HIGH — all findings verified against live source files in this repo and the FedEx reference implementation

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| US-01 | Generate User Story + AC from plain English description using Claude + RAG | `generate_user_story()` pattern fully extracted from FedEx reference; RAG functions confirmed in `rag/vectorstore.py` and `rag/code_indexer.py` |
| US-02 | Refine generated AC with a change request (iterative loop) | `refine_user_story()` pattern fully extracted; session state key `us_history` tracks iteration chain |
| US-03 | Push generated AC to new or existing Trello card (list selector + member assign) | `TrelloClient.create_card_in_list()`, `get_lists()`, `get_board_members()`, `create_list()` all confirmed in FedEx trello_client.py |
| MC-01 | Move selected cards from source Trello list to target list with audit comment | `TrelloClient.get_cards_in_list()`, move pattern confirmed in FedEx Move Cards tab; `add_comment()` confirmed |
| HIST-01 | Persist all approved pipeline runs to data/pipeline_history.json, show in History tab | `_load_history()` / `_save_history()` pattern confirmed in FedEx dashboard; `data/` directory exists in MCSL repo |
</phase_requirements>

---

## Summary

Phase 6 adds three capabilities to the MCSL pipeline dashboard: writing User Stories, moving Trello cards between lists, and persisting pipeline history. All three have high-fidelity reference implementations in the FedEx pipeline at `/Users/madan/Documents/Fed-Ex-automation/FedexDomainExpert/`. The MCSL version needs three adaptations: (1) prompt text must reference MCSL's multi-carrier nature rather than "PluginHive FedEx"; (2) `trello_client.py` must be created from scratch in `pipeline/` (does not yet exist in MCSL); and (3) `move_card_to_list` should accept a `list_id` directly (the FedEx UI passes an ID despite the method signature saying `list_name` — MCSL should fix this cleanly with a `move_card_to_list_by_id` method or by overloading).

The history persistence pattern is straightforward: `data/pipeline_history.json` with top-level keys being card IDs, each value being a dict with `card_name`, `approved_at`, `card_url`, `release`, `test_cases`, `rag_chunks`. The History tab reads from `st.session_state.pipeline_runs` which is loaded from disk on first render.

**Primary recommendation:** Clone FedEx user_story_writer.py and trello_client.py verbatim, then adapt prompts and client to be MCSL-specific. Do not hand-roll Trello HTTP calls — the full client is available and battle-tested.

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `langchain-anthropic` | installed | `ChatAnthropic` LLM invocation | Same pattern used in `smart_ac_verifier.py` throughout project |
| `langchain-core` | installed | `HumanMessage`, `Document` types | Project standard — in all pipeline modules |
| `requests` | installed | Trello REST API HTTP calls | Used by FedEx trello_client.py; simpler than `urllib.request` for POST/PUT |
| `streamlit` | 1.56.0 | Dashboard UI | Project-wide; confirmed installed |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `json` (stdlib) | — | Read/write pipeline_history.json | History persistence — no extra dep needed |
| `pathlib.Path` (stdlib) | — | File paths for history file | Established project pattern from `config.py` |
| `datetime` (stdlib) | — | `approved_at` timestamps | ISO format strings in history entries |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `requests` for Trello | `urllib.request` (already used in card_processor.py) | `requests` is cleaner for POST/PUT with JSON body; `urllib` only used in card_processor.py for simple GET |
| `json` file for history | SQLite | JSON is simpler, sufficient for this scale, matches FedEx pattern |

**Installation:**
`requests` should already be installed (check `.venv`). No new deps needed — `langchain-anthropic`, `langchain-core`, `streamlit` all confirmed present.

---

## Architecture Patterns

### Recommended Project Structure
```
pipeline/
├── user_story_writer.py   # NEW — generate_user_story(), refine_user_story()
├── trello_client.py       # NEW — TrelloClient class (copy + adapt from FedEx)
├── card_processor.py      # EXISTS — get_ac_text() (unchanged)
├── smart_ac_verifier.py   # EXISTS (unchanged)
└── rag_updater.py         # EXISTS (unchanged)
data/
└── pipeline_history.json  # CREATED by _save_history() on first approval
tests/
└── test_pipeline.py       # NEW — unit tests for user_story_writer + trello_client
```

### Pattern 1: generate_user_story() — RAG-grounded Claude call

**What:** Queries both `mcsl_knowledge` (domain docs) and `mcsl_code_knowledge` (codebase) then sends a structured prompt to Claude Sonnet.
**When to use:** US-01 — initial generation from a plain-English feature request.

```python
# Source: /Users/madan/Documents/Fed-Ex-automation/FedexDomainExpert/pipeline/user_story_writer.py
def generate_user_story(feature_request: str, model: str | None = None) -> str:
    domain_context = _fetch_domain_context(feature_request)   # rag.vectorstore.search()
    code_context   = _fetch_code_context(feature_request)     # rag.code_indexer.search_code()
    prompt = US_WRITER_PROMPT.format(
        feature_request=feature_request.strip(),
        code_context=code_context,
        domain_context=domain_context,
    )
    claude = ChatAnthropic(model=model or config.CLAUDE_SONNET_MODEL,
                           api_key=config.ANTHROPIC_API_KEY,
                           temperature=0.3, max_tokens=2048)
    response = claude.invoke([HumanMessage(content=prompt)])
    return response.content.strip()
```

**MCSL adaptation required in prompt text:** Change "PluginHive FedEx Shopify app" to "MCSL multi-carrier Shopify app (FedEx, UPS, DHL, USPS)".

### Pattern 2: refine_user_story() — no RAG, pure Claude rewrite

**What:** Takes the previous markdown and a change request, returns updated markdown.
**When to use:** US-02 — iterative refinement loop.

```python
# Source: /Users/madan/Documents/Fed-Ex-automation/FedexDomainExpert/pipeline/user_story_writer.py
def refine_user_story(previous_us: str, change_request: str, model: str | None = None) -> str:
    prompt = US_REFINE_PROMPT.format(
        previous_us=previous_us.strip(),
        change_request=change_request.strip(),
    )
    claude = _get_claude(model)
    response = claude.invoke([HumanMessage(content=prompt)])
    return response.content.strip()
```

No RAG call in refine — previous output is already contextual enough.

### Pattern 3: TrelloClient construction and method set

**What:** Thin `requests` wrapper, reads creds from env, raises `ValueError` if any missing.
**When to use:** All Trello operations in tabs US, Move Cards.

```python
# Source: /Users/madan/Documents/Fed-Ex-automation/FedexDomainExpert/pipeline/trello_client.py
class TrelloClient:
    def __init__(self, api_key=None, token=None, board_id=None):
        self.api_key  = api_key  or os.getenv("TRELLO_API_KEY", "")
        self.token    = token    or os.getenv("TRELLO_TOKEN",   "")
        self.board_id = board_id or os.getenv("TRELLO_BOARD_ID","")
        if not all([self.api_key, self.token, self.board_id]):
            raise ValueError("Trello credentials missing. Set TRELLO_API_KEY, TRELLO_TOKEN, TRELLO_BOARD_ID in .env")
```

Key methods confirmed (all in FedEx trello_client.py):
- `get_lists() -> list[TrelloList]`
- `get_list_by_name(name: str) -> TrelloList | None`
- `create_list(name: str, pos: str = "bottom") -> TrelloList`
- `get_board_members() -> list[dict]`  — returns `[{id, fullName, username}]`
- `create_card_in_list(list_id, name, desc="", member_ids=None, list_name="") -> TrelloCard`
- `get_cards_in_list(list_id: str) -> list[TrelloCard]`
- `move_card_to_list(card_id: str, list_name: str) -> None`  — resolves name to ID internally
- `add_comment(card_id: str, text: str) -> None`
- `update_card_description(card_id: str, new_desc: str) -> None`

**MCSL-specific addition needed:** A `move_card_to_list_by_id(card_id: str, list_id: str) -> None` method that does `self._put(f"cards/{card_id}", idList=list_id)` directly, avoiding a round-trip `get_list_by_name`. The FedEx UI has a latent bug passing list IDs to `move_card_to_list` (which expects a name) — MCSL should fix this cleanly.

### Pattern 4: Move Cards UI — source/target selectbox + checkbox per card

**What:** Two selectboxes (source, target), "Load" button populates `dd_cards` in session_state, per-card checkboxes with "Select all", "Move N cards" button calls `move_card_to_list_by_id` + `add_comment`.

```python
# Source: FedEx ui/pipeline_dashboard.py lines 3693–3799
# Key session state keys for Move Cards:
# dd_list_select       — source list name
# dd_move_target       — target list name
# dd_cards             — list[TrelloCard]
# dd_checked           — dict[card_id, bool]
# dd_chk_{card.id}     — per-card checkbox widget key
# dd_select_all        — select-all checkbox
```

### Pattern 5: History persistence — disk-backed dict

**What:** `data/pipeline_history.json` is a JSON object keyed by card ID. Loaded once into `st.session_state.pipeline_runs` on `_init_state()`. Saved to disk after each approval.

```python
# Source: FedEx ui/pipeline_dashboard.py lines 183–206
_HISTORY_FILE = Path(__file__).resolve().parent / "data" / "pipeline_history.json"

def _load_history() -> dict:
    if _HISTORY_FILE.exists():
        return json.loads(_HISTORY_FILE.read_text(encoding="utf-8"))
    return {}

def _save_history(runs: dict) -> None:
    _HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    _HISTORY_FILE.write_text(json.dumps(runs, indent=2, ensure_ascii=False), encoding="utf-8")
```

**MCSL path:** `Path(__file__).resolve().parent / "data" / "pipeline_history.json"` — `pipeline_dashboard.py` is at repo root, so `data/pipeline_history.json`. The `data/` directory already exists (confirmed — contains `chroma_db/`).

### Pattern 6: User Story tab session state flow

```
us_request_input  -> text_area: "What do you want to build?"
us_result         -> str: latest generated/refined markdown
us_history        -> list[str]: all versions (for potential undo)
us_change_input   -> text_area: change request for Refine button
us_card_title     -> text_input: Trello card title
us_list_mode      -> radio: "Existing list" | "Create new list"
us_existing_list  -> selectbox: chosen existing list name
us_new_list_name  -> text_input: name for new list
us_assign_members -> multiselect: board member display names
```

### Anti-Patterns to Avoid

- **Calling Trello inside a background thread:** All Trello calls happen synchronously in the main Streamlit thread — no threading needed for Phase 6.
- **Using `urllib.request` for POST/PUT:** `requests` library is the right tool; `urllib` is for simple GETs only (card_processor.py pattern).
- **Storing full card objects in history JSON:** Store only serializable primitives. `TrelloCard` dataclass is not JSON-serialisable; extract needed fields.
- **Calling `st.rerun()` inside a `with st.spinner()` block:** Rerun must happen after the spinner exits; call `st.rerun()` at block end outside spinner context.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Trello REST calls | Custom `urllib` wrappers for each endpoint | `TrelloClient` from `pipeline/trello_client.py` | Rate-limit handling, auth params, error raising all done |
| RAG context fetch | Direct ChromaDB queries in user_story_writer | `rag.vectorstore.search()` + `rag.code_indexer.search_code()` | Handles empty collection, filters, batching |
| Claude invocation | Direct `anthropic` SDK | `ChatAnthropic` from `langchain_anthropic` | Established project pattern; message formatting handled |
| History file I/O | Custom file format | `json` stdlib + `pathlib.Path` | FedEx-proven pattern; no extra dependencies |

---

## Common Pitfalls

### Pitfall 1: `move_card_to_list` receives a list ID but expects a list name
**What goes wrong:** FedEx UI passes `all_list_ids.get(move_target)` (an ID like `"66a3b..."`) to `move_card_to_list(card_id, list_name)`. The method calls `get_list_by_name(list_name)` which returns `None` for an ID string, raising `ValueError("List '66a3b...' not found on board.")`.
**Why it happens:** The FedEx UI collects `(name, id)` pairs into `all_list_ids` dict, then passes the ID to a method that does name lookup.
**How to avoid:** Add `move_card_to_list_by_id(card_id: str, list_id: str) -> None` to `TrelloClient` and use it in the Move Cards UI. This does a direct `self._put(f"cards/{card_id}", idList=list_id)` — one API call, no name resolution.

### Pitfall 2: `TrelloClient()` raises on missing env vars — must guard in UI
**What goes wrong:** If `TRELLO_API_KEY`, `TRELLO_TOKEN`, or `TRELLO_BOARD_ID` are absent, `TrelloClient.__init__` raises `ValueError`. If called outside a try/except, the Streamlit app crashes.
**How to avoid:** Always wrap `TrelloClient()` instantiation in `try/except Exception as e: st.warning(f"Could not connect to Trello: {e}")`. The `trello_ok` flag (already computed in `main()`) should gate any Trello UI sections.

### Pitfall 3: `us_history` not initialised — `setdefault` needed
**What goes wrong:** If the user clicks Refine before Generate completes (race), `us_history` key may be absent from session state. `st.session_state["us_history"].append(...)` raises `KeyError`.
**How to avoid:** Use `st.session_state.setdefault("us_history", []).append(refined)` in the refine handler, same as FedEx reference.

### Pitfall 4: `_load_history()` called before `data/` exists
**What goes wrong:** On a clean install, `data/pipeline_history.json` doesn't exist. `_load_history()` must handle `FileNotFoundError` gracefully.
**How to avoid:** Check `_HISTORY_FILE.exists()` before reading; return `{}` on any exception. The `_save_history()` function must `mkdir(parents=True, exist_ok=True)` before writing — `data/chroma_db/` exists but `data/` alone may not have the file.

### Pitfall 5: `generate_user_story()` may raise if RAG collection is empty
**What goes wrong:** `rag.vectorstore.search()` returns `[]` when the collection is empty (normal before first ingest). The function should handle this gracefully — not crash.
**How to avoid:** `_fetch_domain_context` and `_fetch_code_context` must catch all exceptions and return `"No context available."` strings. The prompt still works; Claude generates from general knowledge.

### Pitfall 6: Streamlit widget key collisions between Move Cards and other tabs
**What goes wrong:** `dd_chk_{card.id}` keys are dynamic per card. If the same card ID appears in two contexts (e.g., Release QA tab also lists cards), checkbox state bleeds between tabs.
**How to avoid:** Use tab-specific prefixes: `dd_chk_` for Move Cards, keep `rqa_chk_` for Release QA. This is already the FedEx pattern.

---

## Code Examples

### User Story Writer — complete module structure
```python
# pipeline/user_story_writer.py
# Source: /Users/madan/Documents/Fed-Ex-automation/FedexDomainExpert/pipeline/user_story_writer.py (adapted)

US_WRITER_PROMPT = """\
You are a senior Product Owner / Business Analyst for the MCSL multi-carrier Shopify app.
The app integrates FedEx, UPS, DHL, USPS, and other carrier shipping services
(label generation, rate calculation, tracking, returns, signature options, etc.)
into Shopify stores via a Shopify embedded app.
...
"""

def generate_user_story(feature_request: str, model: str | None = None) -> str:
    """Returns markdown: ### User Story + ### Acceptance Criteria + ### Notes"""

def refine_user_story(previous_us: str, change_request: str, model: str | None = None) -> str:
    """Returns updated markdown incorporating change_request."""
```

### TrelloClient — new method for MCSL
```python
# pipeline/trello_client.py — addition to FedEx base
def move_card_to_list_by_id(self, card_id: str, list_id: str) -> None:
    """Move a card to a list by its ID (avoids name-lookup round-trip)."""
    self._put(f"cards/{card_id}", idList=list_id)
    logger.info("Moved card %s to list id %s", card_id, list_id)
```

### History entry schema
```python
# pipeline_dashboard.py — structure written by _save_history()
history_entry = {
    "card_name":  "My Feature Card",       # str
    "approved_at": "2026-04-17T10:30:00",  # ISO datetime string
    "card_url":   "https://trello.com/c/...",  # str
    "release":    "Sprint 42",              # str (from rqa_release session state)
    "test_cases": "TC-01: ...\nTC-02: ...",# str (markdown)
    "rag_chunks": 8,                        # int — number of RAG docs retrieved
}
# Keyed by card_id in the top-level dict:
# { "CARD_ID_1": {...}, "CARD_ID_2": {...} }
```

### _get_board_lists() helper (module-level cache)
```python
# pipeline_dashboard.py
@st.cache_data(ttl=60)
def _get_board_lists() -> list[tuple[str, str]]:
    """Cached fetch of all Trello board lists — (name, id) pairs."""
    from pipeline.trello_client import TrelloClient
    return [(l.name, l.id) for l in TrelloClient().get_lists()]
```
Use `@st.cache_data(ttl=60)` to avoid re-fetching every Streamlit rerun. The FedEx reference uses this but doesn't show the decorator explicitly — add it for MCSL.

### History tab render loop
```python
# pipeline_dashboard.py — with tab_history:
runs = st.session_state.pipeline_runs  # loaded from disk in _init_state()
for card_id, run in runs.items():
    label = f"✅ {run.get('card_name', card_id)}  ·  {run.get('approved_at', '')}"
    with st.expander(label, expanded=False):
        col1, col2 = st.columns(2)
        col1.markdown(f"**Release**  \n{run.get('release', '—')}")
        col2.markdown(f"**Approved at**  \n{run.get('approved_at', '—')}")
        if run.get("card_url"):
            st.markdown(f"[Open in Trello]({run['card_url']})")
```

---

## State of the Art

| Old Approach | Current Approach | Impact |
|--------------|------------------|--------|
| `urllib.request` for all HTTP | `requests` for POST/PUT (Trello mutations) | Cleaner JSON body handling |
| Passing list names to move_card_to_list | Use list IDs directly via `move_card_to_list_by_id` | Avoids extra GET round-trip + bug in FedEx reference |
| Hardcoded MCSL-specific content | No deviations needed for Phase 6 core logic | Phase 6 is stable, well-understood |

---

## Open Questions

1. **Should `pipeline_history.json` record User Story pushes (US-03) or only Release QA approvals?**
   - What we know: HIST-01 says "approved pipeline runs" — in FedEx this means Release QA card approvals
   - What's unclear: Does Phase 6 scope include persisting US pushes to history, or only Phase 7 Release QA events?
   - Recommendation: For Phase 6, write history entries when a US card is pushed to Trello (US-03 action). Reuse same schema. This gives the History tab meaningful entries before Phase 7 is built.

2. **Does `requests` need to be added to requirements.txt / installed in .venv?**
   - What we know: `pipeline/card_processor.py` uses `urllib.request` not `requests`. The `requests` library may not be in `.venv`.
   - Recommendation: Check `.venv` at plan time with `pip show requests`. If absent, add an install step to 06-01.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (confirmed installed — used by all existing test_*.py files) |
| Config file | None — pytest runs via `python -m pytest` from repo root |
| Quick run command | `/Users/madan/Documents/MCSLDomainExpert/.venv/bin/python -m pytest tests/test_pipeline.py -x -q` |
| Full suite command | `/Users/madan/Documents/MCSLDomainExpert/.venv/bin/python -m pytest tests/ -q` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| US-01 | `generate_user_story(text)` returns non-empty markdown string | unit | `pytest tests/test_pipeline.py::test_us01_generate_returns_markdown -x` | ❌ Wave 0 |
| US-01 | `generate_user_story()` handles empty RAG gracefully (no crash) | unit | `pytest tests/test_pipeline.py::test_us01_generate_no_rag -x` | ❌ Wave 0 |
| US-02 | `refine_user_story(prev, change)` returns updated markdown | unit | `pytest tests/test_pipeline.py::test_us02_refine_returns_updated -x` | ❌ Wave 0 |
| US-02 | Refine prompt includes both `previous_us` and `change_request` | unit | `pytest tests/test_pipeline.py::test_us02_refine_prompt_contains_both -x` | ❌ Wave 0 |
| US-03 | `TrelloClient.create_card_in_list()` called with correct args | unit | `pytest tests/test_pipeline.py::test_us03_trello_card_created -x` | ❌ Wave 0 |
| US-03 | `TrelloClient.__init__` raises `ValueError` on missing env vars | unit | `pytest tests/test_pipeline.py::test_us03_trello_missing_creds -x` | ❌ Wave 0 |
| MC-01 | `TrelloClient.move_card_to_list_by_id()` calls PUT with correct idList | unit | `pytest tests/test_pipeline.py::test_mc01_move_card_by_id -x` | ❌ Wave 0 |
| MC-01 | `TrelloClient.add_comment()` called after move | unit | `pytest tests/test_pipeline.py::test_mc01_audit_comment -x` | ❌ Wave 0 |
| HIST-01 | `_save_history()` writes valid JSON to `data/pipeline_history.json` | unit | `pytest tests/test_pipeline.py::test_hist01_save_history -x` | ❌ Wave 0 |
| HIST-01 | `_load_history()` returns `{}` when file absent | unit | `pytest tests/test_pipeline.py::test_hist01_load_empty -x` | ❌ Wave 0 |
| HIST-01 | History entry has required keys: `card_name`, `approved_at`, `card_url` | unit | `pytest tests/test_pipeline.py::test_hist01_entry_schema -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/test_pipeline.py -x -q`
- **Per wave merge:** `pytest tests/ -q`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_pipeline.py` — new file; covers all US/MC/HIST stubs above
- [ ] `pipeline/user_story_writer.py` — does not yet exist
- [ ] `pipeline/trello_client.py` — does not yet exist
- [ ] Verify `requests` in `.venv`: `pip show requests` — if absent: `pip install requests`

---

## Sources

### Primary (HIGH confidence)
- `/Users/madan/Documents/Fed-Ex-automation/FedexDomainExpert/pipeline/user_story_writer.py` — exact signatures, prompts, RAG call pattern
- `/Users/madan/Documents/Fed-Ex-automation/FedexDomainExpert/pipeline/trello_client.py` — full TrelloClient implementation
- `/Users/madan/Documents/Fed-Ex-automation/FedexDomainExpert/ui/pipeline_dashboard.py` lines 4518–4673 — User Story tab UI pattern
- `/Users/madan/Documents/Fed-Ex-automation/FedexDomainExpert/ui/pipeline_dashboard.py` lines 3693–3799 — Move Cards tab UI pattern
- `/Users/madan/Documents/Fed-Ex-automation/FedexDomainExpert/ui/pipeline_dashboard.py` lines 183–206, 3824–3851 — History persistence + History tab render
- `/Users/madan/Documents/MCSLDomainExpert/.claude/worktrees/objective-archimedes/pipeline_dashboard.py` — current MCSL dashboard with tab stubs
- `/Users/madan/Documents/MCSLDomainExpert/.claude/worktrees/objective-archimedes/rag/vectorstore.py` — `search()` function signature confirmed
- `/Users/madan/Documents/MCSLDomainExpert/.claude/worktrees/objective-archimedes/rag/code_indexer.py` — `search_code()` function signature confirmed
- `/Users/madan/Documents/MCSLDomainExpert/.claude/worktrees/objective-archimedes/config.py` — `CLAUDE_SONNET_MODEL`, `ANTHROPIC_API_KEY` key names

### Secondary (MEDIUM confidence)
- `.planning/REQUIREMENTS.md` lines 91–106 — US-01/02/03, MC-01, HIST-01 requirement text
- `.planning/ROADMAP.md` Phase 6 section — 3 plan structure confirmed

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all libraries confirmed present in project
- Architecture: HIGH — exact FedEx reference code available and read
- Pitfalls: HIGH — `move_card_to_list` ID/name bug identified from direct code inspection
- Test stubs: HIGH — test patterns established from `tests/test_dashboard.py`

**Research date:** 2026-04-17
**Valid until:** 2026-05-17 (stable patterns — FedEx reference doesn't change)
