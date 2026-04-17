# Phase 8: Slack + Sign Off — Research

**Researched:** 2026-04-17
**Domain:** Slack Web API (Python/requests), Streamlit Sign Off tab, Trello QA-done workflow
**Confidence:** HIGH — primary source is the FedEx reference implementation which is fully implemented and production-tested

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| SLACK-01 | Send AC/TCs via Slack DM (user search) or post to channel | `send_ac_dm()` + `post_content_to_slack_channel()` from FedEx slack_client.py are direct ports |
| SLACK-02 | Bug notifications: auto-DM developer when AI QA Agent finds a bug | `notify_devs_of_bug()` from FedEx bug_reporter.py is a direct port (needs MCSL QA team list + `get_card_members` added to MCSL TrelloClient) |
| SIGNOFF-01 | Compose Slack sign-off message with card checklist, bugs, QA lead mention | `post_signoff_message()` + Sign Off tab UI — full reference in FedEx ui/pipeline_dashboard.py lines 4078–4368 |
| SIGNOFF-02 | Mark all approved cards as QA-done in Trello after sign-off | `add_comment()` already on MCSL TrelloClient; pattern is to add sign-off comment per approved+verified card |
</phase_requirements>

---

## Summary

Phase 8 introduces Slack integration and the Sign Off tab to the MCSL QA Pipeline dashboard. The FedEx version is a complete, production-tested reference implementation. The key work is:

1. **Port `pipeline/slack_client.py`** — the FedEx version is a 1053-line module covering DM, channel posting, sign-off messages, user search, and channel listing. The MCSL version needs: webhook + bot-token dual mode, `send_dm()`, `search_users()`, `send_ac_dm()`, `post_content_to_slack_channel()`, `post_signoff_message()`, `list_slack_channels()`, and the module-level convenience helpers (`send_ac_dm`, `post_signoff`, `slack_configured`, etc.).

2. **Port `pipeline/bug_reporter.py`** — FedEx version is ~470 lines. For MCSL: replace `_QA_NAMES` set with the MCSL team, update prompt branding from "FedEx Shopify App" to "MCSL Shopify App", update code RAG source types from `backend/frontend` to `storepepsaas_server/storepepsaas_client`. Also add `get_card_members()` to MCSL `TrelloClient` (it exists in FedEx TrelloClient at line 401 but is missing from MCSL).

3. **Implement `tab_signoff` in `pipeline_dashboard.py`** — the FedEx UI dashboard lines 4078–4368 contain the full Sign Off tab. The MCSL version replaces the Phase 8 stub comment at line 1347 with the ported content. Key UI sections: metrics row, card checkboxes (from `rqa_cards`/`rqa_approved`), bug textarea (from `bugs_for_{card.id}` session keys), mentions/CC/QA-lead inputs, live message preview, Send Sign-Off button, Mark Cards Done in Trello button.

All required env vars (`SLACK_BOT_TOKEN`, `SLACK_WEBHOOK_URL`, `SLACK_CHANNEL`) are already present in `.env`. The `requests` library is already a project dependency.

**Primary recommendation:** Port FedEx `slack_client.py` and `bug_reporter.py` verbatim with MCSL-specific naming substitutions; implement Sign Off tab by replacing the stub in `pipeline_dashboard.py`.

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| requests | already installed | Slack Web API HTTP calls | Project dependency; FedEx reference uses it throughout |
| slack_sdk | NOT used | — | FedEx reference deliberately uses raw `requests` — do not add slack_sdk |
| langchain_anthropic | already installed | Claude calls in bug_reporter locate_bug_in_code + ask_domain_expert | Phase 2+ dependency |

### Slack API Endpoints Used
| Endpoint | Method | Purpose | Auth |
|----------|--------|---------|------|
| `chat.postMessage` | POST | Post to channel or DM channel | Bot token |
| `conversations.open` | POST | Open/get DM channel ID | Bot token |
| `users.list` | GET | Search workspace members | Bot token + `users:read` scope |
| `conversations.list` | GET | List channels | Bot token + `channels:read` scope |
| Incoming Webhook URL | POST | Post to fixed channel | No auth header (URL is the secret) |

### Required Bot Token Scopes
| Scope | Required For |
|-------|-------------|
| `chat:write` | Post messages to channels and DMs |
| `im:write` | Open DM conversations |
| `users:read` | Search users by name |
| `channels:read` | List public channels |
| `groups:read` | List private channels (only those bot is invited to) |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| raw `requests` | `slack_sdk` | slack_sdk is cleaner but adds a dependency; FedEx reference uses requests throughout — keep consistent |
| Webhook-only | Bot token only | Webhook cannot open DMs; bot token is required for user search and DMs |

---

## Architecture Patterns

### Recommended Project Structure
```
pipeline/
├── slack_client.py       # SlackClient class + module-level helpers (port of FedEx)
├── bug_reporter.py       # notify_devs_of_bug + ask_domain_expert (port of FedEx)
└── trello_client.py      # add get_card_members() method (missing from MCSL)

pipeline_dashboard.py     # Replace tab_signoff stub (line 1347) with full UI
tests/
└── test_pipeline.py      # Add SLACK-01/02 + SIGNOFF-01/02 test stubs
```

### Pattern 1: Dual Delivery Mode (Webhook Preferred, Bot Token Fallback)
**What:** `SlackClient._post()` tries webhook URL first, falls back to `chat.postMessage` with bot token.
**When to use:** Always — this is the constructor/post pattern.
```python
# Source: FedEx pipeline/slack_client.py lines 84-112
def _post(self, payload: dict) -> dict:
    if self.webhook_url:
        resp = requests.post(self.webhook_url, json=payload, timeout=15)
        resp.raise_for_status()
        return {"ok": True, "ts": ""}  # webhook returns plain "ok", not JSON
    payload["channel"] = self.channel
    resp = requests.post(f"{SLACK_API}/chat.postMessage",
                         headers={"Authorization": f"Bearer {self.token}", ...},
                         json=payload, timeout=15)
    data = resp.json()
    if not data.get("ok"):
        raise RuntimeError(f"Slack API error: {data.get('error')}")
    return data
```

### Pattern 2: DM Flow (conversations.open + chat.postMessage)
**What:** Opening a DM requires `conversations.open` first to get the DM channel ID, then `chat.postMessage` to that channel ID.
**When to use:** All DM operations (send AC to user, bug notification to dev).
```python
# Source: FedEx pipeline/slack_client.py lines 205-244
def send_dm(self, user_id: str, text: str) -> str:
    open_resp = requests.post(f"{SLACK_API}/conversations.open",
                              headers=self._bot_headers(),
                              json={"users": user_id}, timeout=15)
    dm_channel = open_resp.json()["channel"]["id"]
    msg_resp = requests.post(f"{SLACK_API}/chat.postMessage",
                             headers=self._bot_headers(),
                             json={"channel": dm_channel, "text": text, "mrkdwn": True},
                             timeout=15)
    return msg_resp.json().get("ts", "")
```

### Pattern 3: User Search with Pagination
**What:** `users.list` is paginated (max 200/page); must follow `response_metadata.next_cursor`.
**When to use:** `search_users()` for user lookup before DM.
```python
# Source: FedEx pipeline/slack_client.py lines 128-203
# Key: filter deleted=True, is_bot=True, id=="USLACKBOT" members
# Match on real_name, display_name, username, first_name, last_name
```

### Pattern 4: Sign Off Tab Session State Integration
**What:** Sign Off tab reads from `rqa_cards`, `rqa_approved`, `rqa_test_cases`, `rqa_release`, and per-card `bugs_for_{card.id}` keys. All populated by Phase 7 Release QA tab.
**When to use:** Tab render — pull state at top of `with tab_signoff:` block.
```python
# Source: FedEx ui/pipeline_dashboard.py lines 4092-4095
so_cards    = st.session_state.get("rqa_cards", [])
so_release  = st.session_state.get("rqa_release", "")
so_approved = st.session_state.get("rqa_approved", {})
so_tc_store = st.session_state.get("rqa_test_cases", {})
```

### Pattern 5: Bug Aggregation from Session State
**What:** Collect bugs from `bugs_for_{card.id}` (rich dicts: `{"name", "url", "severity"}`) for all cards in the current release. Deduplicate by name.
**When to use:** Building the backlog list in the Sign Off tab.
```python
# Source: FedEx ui/pipeline_dashboard.py lines 4099-4117
_seen_bug_names: set[str] = set()
so_bugs_with_urls: list[dict] = []
for card in so_cards:
    for bug in st.session_state.get(f"bugs_for_{card.id}", []):
        bname = bug.get("name", "")
        if bname and bname not in _seen_bug_names:
            _seen_bug_names.add(bname)
            so_bugs_with_urls.append(bug)
```

### Pattern 6: Sign-Off Message Format
**What:** Standard team sign-off format used in production.
**When to use:** `post_signoff_message()` and the live preview in the UI.
```
@here  @alice  @bob

We've completed testing  *RELEASE*  and it's good for the release ✅

*Cards Verified:*

Card Name
https://trello.com/c/xxx

*Cards added to backlog (N):*

Bug title 1
Bug title 2

*QA Signed off* :tada:

CC: @manager
_Signed by: QA Lead_
```

### Anti-Patterns to Avoid
- **`slack_sdk` dependency:** Don't add it — the project uses raw `requests` throughout. Adding `slack_sdk` would introduce an unnecessary dependency.
- **Channel name instead of ID:** Use channel ID (C...) not name when posting — name resolution can fail if bot is not in channel.
- **`webhook_url` for DMs:** Webhooks cannot open DMs. `SLACK_BOT_TOKEN` is required for any DM operation. Check `dm_token_configured()` before offering DM UI.
- **Blocking DM on main thread during AI QA Agent:** Bug DMs in `notify_devs_of_bug()` are called from the Streamlit UI button handler (not from the agent thread), so no threading concern.
- **`get_card_members()` missing from MCSL TrelloClient:** The FedEx version has it at `GET /1/cards/{card_id}/members`. MCSL TrelloClient does NOT have this method yet. `bug_reporter.py` calls it — must add it in Plan 08-01 or 08-02.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Slack mrkdwn message formatting | Custom markdown converter | Pass `"mrkdwn": True` in payload + write Slack mrkdwn directly | Slack's mrkdwn is a fixed subset; FedEx reference already handles it |
| User search across pages | Single-page request | Paginated `users.list` loop with cursor | Workspaces can have 1000+ members; single request truncates |
| Channel list | Hardcoded list | `list_slack_channels()` with cursor pagination | Channel IDs change; hardcoding breaks |
| Block text limits | Allow unlimited text | Split at 2900 chars for Slack block limit | Slack block `text` field max is 3000 chars |

**Key insight:** The Slack Web API is straightforward for this use case. The complexity is in pagination and the dual webhook/token delivery modes, both already solved in the FedEx reference.

---

## Common Pitfalls

### Pitfall 1: Webhook Returns "ok" Text Not JSON
**What goes wrong:** `resp.json()` raises `JSONDecodeError` when using Incoming Webhook.
**Why it happens:** Webhook endpoint returns the plain text string `"ok"`, not `{"ok": true}`.
**How to avoid:** Check `if self.webhook_url:` first and return `{"ok": True, "ts": ""}` directly without parsing response as JSON.
**Warning signs:** `JSONDecodeError` or `ts` returning `None` in webhook mode.

### Pitfall 2: Bot Not in Channel (not_in_channel Error)
**What goes wrong:** `chat.postMessage` returns `{"ok": false, "error": "not_in_channel"}`.
**Why it happens:** Bot must be invited to a channel before posting.
**How to avoid:** `post_content_to_slack_channel()` catches this error and returns a human-readable message. Show it in the UI with `st.error()`.
**Warning signs:** Channel visible in `conversations.list` but posting fails.

### Pitfall 3: missing_scope Error for users:read
**What goes wrong:** `users.list` returns `{"ok": false, "error": "missing_scope"}`.
**Why it happens:** Bot token installed before `users:read` scope was added.
**How to avoid:** `search_users()` raises `RuntimeError` with clear instructions to add scope and reinstall. Surface this in UI.
**Warning signs:** DM search never returns results.

### Pitfall 4: get_card_members Missing from MCSL TrelloClient
**What goes wrong:** `bug_reporter.get_card_devs()` calls `client.get_card_members(card_id)` which doesn't exist on MCSL `TrelloClient`.
**Why it happens:** MCSL TrelloClient was built for Phase 6/7 operations; `GET /1/cards/{card_id}/members` was never added.
**How to avoid:** Add `get_card_members(self, card_id: str) -> list[dict]` to `pipeline/trello_client.py` in Plan 08-02 (bug_reporter plan). Pattern from FedEx TrelloClient lines 401-418.
**Warning signs:** `AttributeError: 'TrelloClient' object has no attribute 'get_card_members'`.

### Pitfall 5: `bugs_for_{card.id}` Keys Not Yet Set in MCSL Session State
**What goes wrong:** Sign Off tab bug aggregation loop finds no bugs even when the Release QA tab found some.
**Why it happens:** Phase 7 Release QA tab in MCSL may not be writing `bugs_for_{card.id}` to session state yet — this is a FedEx pattern that may not have been ported in Phase 7.
**How to avoid:** In Plan 08-03 (Sign Off tab), check whether `bugs_for_{card.id}` is populated. If not, provide a manual text_area fallback (already in FedEx pattern). The text_area is the primary input anyway.
**Warning signs:** Bug list is always empty in Sign Off even after AI QA Agent run.

### Pitfall 6: Sign Off Tab Shows Empty When rqa_cards Not Loaded
**What goes wrong:** Sign Off tab shows "Load a release from the Release QA tab first" even after loading.
**Why it happens:** `rqa_cards` is not set, or Sign Off tab rendered before Phase 7 work completes.
**How to avoid:** Show the warning message gracefully as FedEx does (`if not so_cards: st.info(...)`). No crash, just instructional message.

### Pitfall 7: Slack Block Text 3000-char Limit
**What goes wrong:** `chat.postMessage` returns `invalid_blocks` error when AC or TC text exceeds 3000 chars.
**Why it happens:** Slack's Block Kit `text` field has a 3000-character limit.
**How to avoid:** Split content at 2900 chars, add a second `section` block for overflow. FedEx reference handles this in `post_content_to_slack_channel()` lines 690-696.

---

## Code Examples

### SlackClient Constructor + Validation
```python
# Source: FedEx pipeline/slack_client.py lines 64-82
class SlackClient:
    def __init__(self, token=None, channel=None, webhook_url=None):
        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL", "")
        self.token       = token       or os.getenv("SLACK_BOT_TOKEN", "")
        self.channel     = channel     or os.getenv("SLACK_CHANNEL", "")
        self.mention_on_fail = os.getenv("SLACK_MENTION_ON_FAIL", "")
        # Webhook is preferred; DM-only usage needs token alone
        if not self.webhook_url and not self.token:
            raise ValueError("Slack credentials missing. Set SLACK_WEBHOOK_URL OR SLACK_BOT_TOKEN in .env")
```

### Module-Level Convenience Helpers (used by dashboard)
```python
# Source: FedEx pipeline/slack_client.py lines 484-565
def slack_configured() -> bool: ...          # Used by sidebar badge + signoff button guard
def dm_token_configured() -> bool: ...       # Used before showing DM UI sections
def search_slack_users(query) -> tuple: ...  # (results, error_msg)
def list_slack_channels() -> tuple: ...      # (channels, error_msg, note)
def send_ac_dm(user_ids, card_name, ac_text, content_label) -> dict: ...
def post_content_to_slack_channel(channel_id, card_name, content_text, ...) -> dict: ...
def post_signoff(release, verified_cards, backlog_cards, mentions, ...) -> dict: ...
```

### TrelloClient.get_card_members (to add to MCSL)
```python
# Source: FedEx pipeline/trello_client.py lines 401-418
def get_card_members(self, card_id: str) -> list[dict]:
    """Return members assigned to a card. Each dict: {id, fullName, username}"""
    try:
        raw = self._get(f"cards/{card_id}/members")
        return [{"id": m.get("id",""), "fullName": m.get("fullName",""),
                 "username": m.get("username","")} for m in raw]
    except Exception as exc:
        logger.warning("get_card_members failed for %s: %s", card_id, exc)
        return []
```

### Sign Off Tab Button Pattern
```python
# Source: FedEx ui/pipeline_dashboard.py lines 4265-4317
col_send, col_trello = st.columns(2)
with col_send:
    if slack_configured():
        if st.button("📣 Send Sign-Off to Slack", type="primary", ...):
            with st.spinner("Posting sign-off to Slack…"):
                result = post_signoff(release=so_release_input,
                                      verified_cards=verified_cards,
                                      backlog_cards=backlog_cards,
                                      mentions=mentions_list,
                                      cc=cc_raw.strip(),
                                      qa_lead=qa_lead_name.strip(),
                                      backlog_links=so_bugs_with_urls or None)
            if result["ok"]:
                st.session_state["signoff_sent"] = True
                st.rerun()
            else:
                st.error(f"❌ Slack error: {result['error']}")
with col_trello:
    if st.button("✅ Mark Cards Done in Trello", ...):
        for card in so_cards:
            if so_approved.get(card.id) and any(v["name"]==card.name for v in verified_cards):
                trello_cl.add_comment(card.id,
                    f"✅ QA Signed off — {so_release_input} · Signed by: {qa_lead_name}")
```

### Bug Reporter — MCSL QA Team List Change
```python
# Source: FedEx pipeline/bug_reporter.py lines 32-42 — CHANGE THESE for MCSL
_QA_NAMES: set[str] = {
    "anuja b", "arshiya sayed", "ashok kumar n", "basavaraj",
    "inderbir singh", "keerthanaa elangovan", "madan kumar as",
    "preethi k k", "shahitha s",
}
# NOTE: Same team for MCSL — keep identical.
```

### Bug Reporter — Code RAG Source Types for MCSL
```python
# Source: FedEx pipeline/bug_reporter.py lines 99-106 — CHANGE source types
# FedEx uses: "backend", "frontend"
# MCSL uses:  "storepepsaas_server", "storepepsaas_client"
for stype, label in [("storepepsaas_server", "Backend"), ("storepepsaas_client", "Frontend")]:
    docs = search_code(query, k=3, source_type=stype)
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Incoming Webhook only | Dual mode: webhook preferred + bot token fallback | FedEx Phase 8 | DMs now possible alongside channel posts |
| Manual bug reporting | Auto-DM developer via Trello card member + Slack name search | FedEx Phase 8 | Zero-touch bug notification |

---

## Open Questions

1. **Does MCSL Phase 7 write `bugs_for_{card.id}` to session state?**
   - What we know: FedEx Release QA tab writes `bugs_for_{card.id}` when a bug is raised via the "Notify Dev of Bug" button
   - What's unclear: MCSL Phase 7 (07-03 plan) may or may not have ported this session key writing
   - Recommendation: In Plan 08-03 (Sign Off tab), check `pipeline_dashboard.py` for `bugs_for_` key writes. If absent, the text_area fallback in Sign Off is the primary input and functions correctly without this key.

2. **`trello_api_ok` variable scope in Sign Off tab**
   - What we know: FedEx Sign Off tab references `trello_api_ok` (line 4301) which is set in the sidebar section
   - What's unclear: MCSL `pipeline_dashboard.py` sets `trello_ok` in the sidebar at line ~388; variable may be named differently
   - Recommendation: Plan 08-03 must verify the exact variable name used in MCSL sidebar for Trello connectivity status.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (existing) |
| Config file | pytest.ini or conftest.py at project root |
| Quick run command | `python -m pytest tests/test_pipeline.py -x -q` |
| Full suite command | `python -m pytest tests/ -x -q` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SLACK-01 | `send_ac_dm()` sends DM and returns ok=True/sent count | unit | `pytest tests/test_pipeline.py::test_slack01_send_ac_dm -x` | ❌ Wave 0 |
| SLACK-01 | `post_content_to_slack_channel()` posts and returns ok=True | unit | `pytest tests/test_pipeline.py::test_slack01_post_to_channel -x` | ❌ Wave 0 |
| SLACK-02 | `notify_devs_of_bug()` calls send_dm for dev user | unit | `pytest tests/test_pipeline.py::test_slack02_notify_devs -x` | ❌ Wave 0 |
| SLACK-02 | `notify_devs_of_bug()` returns ok=False when no devs on card | unit | `pytest tests/test_pipeline.py::test_slack02_no_devs -x` | ❌ Wave 0 |
| SIGNOFF-01 | `post_signoff_message()` formats and posts sign-off text | unit | `pytest tests/test_pipeline.py::test_signoff01_post_message -x` | ❌ Wave 0 |
| SIGNOFF-02 | Mark Cards Done calls `add_comment` for each approved card | unit | `pytest tests/test_pipeline.py::test_signoff02_trello_done -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `python -m pytest tests/test_pipeline.py -x -q`
- **Per wave merge:** `python -m pytest tests/ -x -q`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_pipeline.py` — add stubs for SLACK-01, SLACK-02, SIGNOFF-01, SIGNOFF-02 test IDs listed above (file exists, append new test functions)
- [ ] No new test files needed — all Phase 8 tests go in the existing `test_pipeline.py`

---

## Sources

### Primary (HIGH confidence)
- `/Users/madan/Documents/Fed-Ex-automation/FedexDomainExpert/pipeline/slack_client.py` — full implementation (1053 lines), read directly
- `/Users/madan/Documents/Fed-Ex-automation/FedexDomainExpert/pipeline/bug_reporter.py` — full implementation (474 lines), read directly
- `/Users/madan/Documents/Fed-Ex-automation/FedexDomainExpert/ui/pipeline_dashboard.py` lines 4078–4368 — Sign Off tab implementation, read directly
- `/Users/madan/Documents/MCSLDomainExpert/pipeline/trello_client.py` — MCSL TrelloClient current state, read directly
- `/Users/madan/Documents/MCSLDomainExpert/pipeline_dashboard.py` — MCSL dashboard, `tab_signoff` stub at line 1347, session state keys confirmed

### Secondary (MEDIUM confidence)
- Slack Web API documentation pattern for `conversations.open` + `chat.postMessage` DM flow — verified against FedEx implementation which is known to work in production

### Tertiary (LOW confidence)
- None

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — FedEx reference is production code; env vars confirmed present in .env
- Architecture: HIGH — FedEx Sign Off tab is a complete reference; session state keys (`rqa_cards`, `rqa_approved`, etc.) confirmed in MCSL `_init_state()`
- Pitfalls: HIGH — sourced from FedEx implementation's own error handling (missing_scope, not_in_channel, webhook JSON parse)

**Research date:** 2026-04-17
**Valid until:** 2026-05-17 (Slack Web API is stable; FedEx reference is frozen)
