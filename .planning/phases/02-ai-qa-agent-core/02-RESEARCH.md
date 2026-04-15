# Phase 2: AI QA Agent Core - Research

**Researched:** 2026-04-15
**Domain:** Agentic browser automation, multi-carrier planning, Claude AI loop, Playwright Python
**Confidence:** HIGH — architecture directly cloned from a working reference implementation (FedexDomainExpert/pipeline/smart_ac_verifier.py, 2840 lines, fully operational)

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| AGENT-01 | Agent extracts testable scenarios from AC text as JSON array | _extract_scenarios() pattern from FedEx — Claude + _EXTRACT_PROMPT, returns list[str] |
| AGENT-02 | Agent queries Domain Expert RAG for expected behaviour, API signals, key checks per scenario | _ask_domain_expert() pattern — queries mcsl_knowledge + mcsl_code_knowledge, synthesises ≤200-word answer |
| AGENT-03 | Agent generates JSON execution plan (nav_clicks, look_for, api_to_watch, order_action, carrier) | _plan_scenario() + _PLAN_PROMPT — carrier field added to schema vs FedEx |
| AGENT-04 | Agent runs agentic browser loop (up to 15 steps): observe/click/fill/scroll/navigate/switch_tab/close_tab/download_zip/download_file/verify/qa_needed | _verify_scenario() loop — direct port, MCSL nav map replaces FedEx nav map |
| AGENT-05 | Agent captures AX tree (depth 6, 250 lines) + screenshot (base64 PNG) + filtered network calls per step | _ax_tree() + _screenshot() + _network() — iframe filter pattern updated for MCSL |
| AGENT-06 | Agent reports pass/fail/partial/qa_needed verdict per scenario with finding text and screenshot evidence | ScenarioResult + VerificationReport dataclasses — direct port |
| AGENT-07 | Agent supports stop button (threading-based, stop flag checked at each loop iteration) | stop_flag callable checked in verify_ac() loop before each scenario |
| CARRIER-01 | Agent is carrier-aware — carrier name injected into planning prompt from AC text detection | carrier detection regex + _PLAN_PROMPT carrier injection — new MCSL layer |
| CARRIER-02 | Agent handles carrier account configuration flow (App Settings → Carriers → Add/Edit) | MCSL-specific nav: Settings → Carriers tab — workflow guide section needed |
| CARRIER-03 | Agent handles FedEx-specific flows (signature, dry ice, alcohol, battery, HAL, insurance) | _get_preconditions() ported from FedEx — same fields, MCSL label flow differs |
| CARRIER-04 | Agent handles UPS-specific flows (signature, insurance, COD) | New _get_preconditions() branches for UPS — verify JSON fields differ from FedEx |
| CARRIER-05 | Agent handles USPS-specific flows (signature, registered mail) | New _get_preconditions() branches — USPS-stamps store has separate carrier-env |
| CARRIER-06 | Agent handles DHL-specific flows (insurance, signature, international) | New _get_preconditions() branches — international flow uses commercial invoice |
</phase_requirements>

---

## Summary

Phase 2 builds the AI QA Agent core by cloning and adapting FedexDomainExpert's `pipeline/smart_ac_verifier.py` (2840 lines, fully working) into an MCSL-aware equivalent. The FedEx version handles a single-carrier app; the MCSL version must handle 43 carriers with per-carrier account configuration, service codes, and special service flows.

The architecture is a five-stage pipeline per scenario: (1) scenario extraction from raw AC text using Claude + `_EXTRACT_PROMPT`, (2) domain expert RAG query for expected behaviour and API signals, (3) JSON execution plan generation with carrier-specific nav path, (4) agentic browser loop up to 15 steps using Playwright capturing AX tree + screenshot + network calls at each step, and (5) pass/fail/partial/qa_needed verdict with screenshot evidence. Every stage has a working reference implementation that needs targeted MCSL adaptations rather than a ground-up rewrite.

The two most significant MCSL differences from FedEx are: (a) the MCSL app has its own order grid and navigates to Order Summary via the app rather than Shopify More Actions for some flows — see PROJECT.md section 1 for the exact locators, and (b) carrier awareness requires a new `carrier` field in the plan JSON and a `_MCSL_WORKFLOW_GUIDE` that replaces `_APP_WORKFLOW_GUIDE` with MCSL-specific navigation paths for each carrier and flow type.

**Primary recommendation:** Port smart_ac_verifier.py from FedexDomainExpert, then adapt the workflow guide, nav URL map, preconditions resolver, and carrier detection layer for MCSL. Do not rewrite the agentic loop, action handlers, data models, or Claude invocation patterns — they are proven and stable.

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| playwright (Python sync API) | >=1.40 | Browser automation, iframe interaction | Already used in FedexDomainExpert; sync_playwright is simplest for agent loop |
| langchain-anthropic | >=0.3.0 | ChatAnthropic wrapper for Claude | Already in requirements.txt; handles multi-modal messages (screenshot + text) |
| langchain-core | >=0.3.0 | HumanMessage, Document types | Already in requirements.txt |
| requests | >=2.32.3 | Shopify REST API order creation | Already in requirements.txt |
| python-dotenv | >=1.0.1 | Explicit dotenv path loading | Already in requirements.txt; INFRA-01 pattern |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| zipfile (stdlib) | — | Extract ZIP downloads from app | download_zip action handler |
| base64 (stdlib) | — | Encode screenshots for Claude vision | _screenshot() |
| tempfile (stdlib) | — | Temp storage for downloaded files | download_zip / download_file handlers |
| threading (stdlib) | — | Stop flag check; async-safe boolean | AGENT-07 stop button |
| re (stdlib) | — | JSON parsing fallback, carrier detection | _parse_json(), _detect_carrier() |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| playwright sync API | playwright async | Async adds complexity with no benefit for sequential agent loop |
| LangChain ChatAnthropic | Raw anthropic SDK | LangChain already wired in; multi-modal HumanMessage is cleaner |
| in-process stop_flag callable | threading.Event | Callable is simpler and already works in FedEx; Event is equally valid |

**Installation:** Playwright already in requirements.txt; add `playwright` if missing:
```bash
pip install playwright
playwright install chromium
```

---

## Architecture Patterns

### Recommended Project Structure
```
pipeline/
├── smart_ac_verifier.py    # Main entry: verify_ac(), scenario loop, prompts, action handlers
├── order_creator.py        # Shopify REST API order creation (single + bulk)
agent/                      # (Optional split — keep in smart_ac_verifier.py if preferred)
├── browser_loop.py
├── action_handlers.py
├── planner.py
```

The FedEx reference keeps everything in `smart_ac_verifier.py` (single 2840-line file). This is acceptable — the planner should mirror that structure with MCSL adaptations inside `pipeline/smart_ac_verifier.py`.

### Pattern 1: Five-Stage Scenario Pipeline

**What:** For each extracted scenario, run five sequential stages before entering the agentic browser loop.
**When to use:** Every scenario — this is the fixed pipeline shape.

```python
# Source: FedexDomainExpert/pipeline/smart_ac_verifier.py, verify_ac() lines 2745-2784
for idx, scenario in enumerate(scenarios):
    if stop_flag and stop_flag():
        break
    expert_insight = _ask_domain_expert(scenario, card_name, claude)
    code_ctx       = _code_context(scenario, card_name)
    plan_data      = _plan_scenario(scenario, app_url, code_ctx, expert_insight, claude)
    sv = _verify_scenario(
        page, scenario, card_name, app_base, plan_data,
        ctx=code_ctx, claude=claude, first_scenario=(idx==0),
        expert_insight=expert_insight,
    )
    report.scenarios.append(sv)
```

### Pattern 2: Agentic Browser Loop with Active Page Tracking

**What:** Loop up to MAX_STEPS=15, capture state (AX tree + screenshot + network), ask Claude for next action, execute, break on verify/qa_needed.
**When to use:** `_verify_scenario()` — the innermost loop.

```python
# Source: FedexDomainExpert/pipeline/smart_ac_verifier.py lines 2569-2668
active_page = page
zip_ctx = ""
for step_num in range(1, MAX_STEPS + 1):
    ax  = _ax_tree(active_page)
    scr = _screenshot(active_page)
    net = _network(active_page, api_endpoints)
    effective_ctx = f"{zip_ctx}{ctx}" if zip_ctx else ctx
    action = _decide_next(claude, scenario, active_page.url, ax, net_seen,
                          result.steps, effective_ctx, step_num, scr=scr,
                          expert_insight=expert_insight)
    atype = action.get("action", "observe")
    step.success = _do_action(active_page, action, app_base)
    if atype == "verify":
        result.status = action.get("verdict", "partial"); break
    if atype == "qa_needed":
        result.status = "qa_needed"; break
    if "_new_page" in action:          # switch_tab / close_tab
        active_page = action["_new_page"]
    if "_zip_content" in action:       # download_zip result
        zip_ctx = format_zip_for_context(action["_zip_content"])
```

### Pattern 3: Dual-Frame AX Tree Capture (MCSL iframe-aware)

**What:** Capture accessibility tree from both the Shopify admin page and the embedded app iframe.
**When to use:** Every step — the MCSL app content lives inside `iframe[name="app-iframe"]`.

```python
# Source: FedexDomainExpert/pipeline/smart_ac_verifier.py lines 1245-1300, adapted for MCSL
def _ax_tree(page) -> str:
    lines: list[str] = []
    # 1. Main Shopify admin page (sidebar, headers)
    ax = page.accessibility.snapshot(interesting_only=True)
    if ax: _walk(ax, lines)
    # 2. MCSL app iframe — all app UI is here
    for frame in page.frames:
        if frame is page.main_frame: continue
        frame_url = frame.url or ""
        # MCSL iframe filter: match app-iframe or pluginhive domains
        if not frame_url or ("shopify" not in frame_url
                             and "pluginhive" not in frame_url
                             and "apps" not in frame_url):
            continue
        frame_ax = frame.accessibility.snapshot(interesting_only=True)
        if frame_ax:
            lines.append(f"\n--- [APP IFRAME: {frame_url[:60]}] ---")
            _walk(frame_ax, lines)
    return "\n".join(lines) or "(no interactive elements)"
```

**MCSL-specific:** `iframe[name="app-iframe"]` — same selector as FedEx (confirmed in config.py INFRA-04). Frame filter already matches pluginhive.io (used by Print Documents tab).

### Pattern 4: Carrier-Aware Plan Prompt

**What:** Detect carrier name from AC text, inject it into the planning prompt.
**When to use:** `_plan_scenario()` — CARRIER-01 requirement.

```python
# New MCSL layer — does not exist in FedexDomainExpert
CARRIER_CODES = {
    "fedex": ("FedEx", "C2"),
    "ups":   ("UPS",   "C3"),
    "dhl":   ("DHL",   "C1"),
    "usps":  ("USPS",  "C22"),
    "stamps":("USPS Stamps", "C22"),
    "easypost": ("EasyPost", "C22"),
}

def _detect_carrier(ac_text: str) -> tuple[str, str]:
    """Returns (carrier_name, carrier_code) from AC text. Defaults to ('', '')."""
    lower = ac_text.lower()
    for keyword, (name, code) in CARRIER_CODES.items():
        if keyword in lower:
            return name, code
    return "", ""

# Inject into _PLAN_PROMPT:
# CARRIER: {carrier_name} (internal code: {carrier_code})
# Use carrier-specific navigation and service codes when planning.
```

### Pattern 5: MCSL Nav URL Map

**What:** Direct URL navigation for each known app section — replaces FedEx `_APP_URL_MAP`.
**When to use:** `_verify_scenario()` nav_clicks execution.

```python
# MCSL URL map — adapted from FedexDomainExpert lines 2487-2508
# App URL: https://admin.shopify.com/store/{store}/apps/mcsl-qa
_MCSL_URL_MAP = {
    "shipping":    f"{app_base}/shopify",       # MCSL Orders grid (app sidebar)
    "appproducts": f"{app_base}/products",      # MCSL app Products (carrier settings)
    "settings":    f"{app_base}/settings/0",    # App Settings
    "carriers":    f"{app_base}/settings/0",    # Carriers tab is in Settings
    "pickup":      f"{app_base}/pickup",        # Pickups list
    "faq":         f"{app_base}/faq",
    "rates log":   f"{app_base}/rateslog",
    # Shopify admin (outside iframe)
    "orders":          f"https://admin.shopify.com/store/{store}/orders",
    "shopifyproducts": f"https://admin.shopify.com/store/{store}/products",
}
# NOTE: MCSL label generation uses the app's own order grid flow (see PROJECT.md §1),
# NOT the Shopify More Actions flow used by FedEx.
```

### Pattern 6: MCSL Order Creator

**What:** Create test orders via Shopify REST API reading from MCSL carrier-env files.
**When to use:** `order_creator.py` — AGENT-01 order_action=create_new/create_bulk.

```python
# MCSL differs from FedEx: no productsconfig.json file found in mcsl-test-automation.
# Products are defined inline in carrier-env files (SIMPLE_PRODUCTS_JSON, etc.)
# Approach: read active carrier-env file or fall back to config.py STORE + SHOPIFY_ACCESS_TOKEN

# From carrier-envs/ups.env:
# SIMPLE_PRODUCTS_JSON='[{"product_id":8250672349345,"variant_id":44995757244577},...]'
# SHOPIFY_ACCESS_TOKEN=REDACTED_SHOPIFY_TOKEN
# SHOPIFY_API_VERSION=2023-01
# SHOPIFY_STORE_NAME=mcsl-automation
```

### Pattern 7: MCSL-Specific Preconditions

**What:** Hardcoded pre-requirement sequences for special service scenarios.
**When to use:** `_get_preconditions()` — CARRIER-03 through CARRIER-06.

MCSL preconditions differ from FedEx in the label generation flow after product setup:
- FedEx: Shopify Orders → More Actions → Generate Label → SideDock → Get Rates → Generate
- MCSL: App → click Account Card → filter by Order ID → click order → Generate Label button → waits for LABEL CREATED status

### Anti-Patterns to Avoid
- **Using Shopify More Actions for MCSL label generation:** MCSL uses the app's own order grid (click Account Card, filter by Order ID, navigate to Order Summary, click Generate Label). The FedEx More Actions flow does NOT apply to MCSL.
- **Hardcoding the store app URL suffix:** MCSL app slug is `mcsl-qa` (confirmed from carrier-env APPURL). FedEx uses `testing-553`. Do not copy the FedEx app URL suffix.
- **Single-carrier workflow guide:** Do not write `_MCSL_WORKFLOW_GUIDE` assuming FedEx-only flows. All flow descriptions must be carrier-neutral at the top level, with carrier-specific subsections.
- **page.wait_for_load_state("networkidle"):** Shopify has constant background XHR. Always use `"domcontentloaded"` + small timeout, never `networkidle`.
- **Capturing only the main frame:** MCSL app UI is entirely in the iframe. Calling `page.accessibility.snapshot()` alone gives only Shopify admin chrome. Must also capture `frame.accessibility.snapshot()` for the app iframe.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| JSON extraction from Claude response | Custom parser | `_parse_json()` from FedexDomainExpert | Handles markdown fences, prefix text, list vs dict — 3 fallback strategies |
| Playwright multi-strategy click | Single locator | 8-strategy fallback chain in `_do_action()` | App UI uses buttons, links, text, role — no single strategy is reliable |
| ZIP download interception | Manual fetch | `page.expect_download()` context manager | Playwright's built-in download intercept handles async download triggering |
| AX tree walking | Custom recursion | `_walk()` from FedexDomainExpert | Handles depth limit (6), line limit (250), checked/value attributes |
| Bot detection bypass | Custom headers | `_ANTI_BOT_ARGS` list + `channel="chrome"` | Shopify blocks standard headless Chromium; must use `--disable-blink-features=AutomationControlled` |
| Order strategy inference | Heuristic rules | `infer_order_decision()` + `_validate_order_action()` | Catches Claude mismatches; keyword lists for bulk/fulfilled/unfulfilled signals |

**Key insight:** 80% of the agentic loop code in FedexDomainExpert is carrier-neutral. The MCSL adaptation work is concentrated in (1) `_MCSL_WORKFLOW_GUIDE`, (2) `_detect_carrier()`, (3) `_get_preconditions()` carrier branches, (4) `_MCSL_URL_MAP`, and (5) MCSL-specific order flow in `order_creator.py`. Everything else ports directly.

---

## Common Pitfalls

### Pitfall 1: MCSL Label Flow vs FedEx Label Flow
**What goes wrong:** Agent navigates to Shopify Orders → More Actions → Generate Label (FedEx flow) but MCSL app uses its own order grid and Order Summary.
**Why it happens:** The FedEx workflow guide is embedded in `_APP_WORKFLOW_GUIDE`. If it is ported unchanged, the agent tries FedEx-specific steps that don't exist in MCSL.
**How to avoid:** Write `_MCSL_WORKFLOW_GUIDE` from scratch using PROJECT.md §1 as the authoritative source. Key MCSL flow: App → Account Card click → filter by Order ID (Add filter → Order Id → paste → Escape) → wait for order row → click Order ID link → Order Summary → Generate Label button.
**Warning signs:** Agent step log shows "More Actions" click followed by failures; OR agent looks for "Auto-Generate Label" in More Actions menu.

### Pitfall 2: App Slug is Different
**What goes wrong:** `get_auto_app_url()` constructs URL with FedEx app slug `testing-553`.
**Why it happens:** FedEx hardcodes `apps/testing-553` in `_APP_URL_MAP`.
**How to avoid:** MCSL app slug is `mcsl-qa` (from carrier-envs/ups.env APPURL: `.../apps/mcsl-qa`). Use this or read from env.
**Warning signs:** `page.goto()` lands on 404 or Shopify app store page instead of app.

### Pitfall 3: Order Status Mismatch
**What goes wrong:** Agent waits for FULFILLED status but MCSL status flow is INITIAL → PROCESSING → LABEL CREATED → FULFILLED.
**Why it happens:** FedEx and MCSL share status names but MCSL has an intermediate LABEL CREATED state and an optional PREPARE SHIPMENT button before Generate Label.
**How to avoid:** MCSL status locator: `div[class="order-summary-greyBlock"] > div:nth-child(1) > div:nth-child(1) > div > span`. Workflow: optionally click "Prepare Shipment" → click "Generate Label" → wait for LABEL CREATED → click "Mark As Fulfilled".
**Warning signs:** Agent clicks "Generate Label" but expects immediate FULFILLED; times out.

### Pitfall 4: Rate Log / View Log Flow
**What goes wrong:** Agent tries FedEx "⋯ → View Logs" pattern during label generation, but MCSL uses "View all Rate Summary" first.
**Why it happens:** MCSL Rate Summary is collapsed by default (PROJECT.md §3). Must click "View all Rate Summary" link before the 3-dots button is accessible.
**How to avoid:** MCSL rate log flow: click "View all Rate Summary" (getByTitle) → Rate Summary table expands → click 3-dots on rate row → click "View Log". Log dialog locator: `.dialogHalfDivParent`.
**Warning signs:** Agent cannot find 3-dots button or View Log menu item on Order Summary.

### Pitfall 5: Carrier Account Config — Settings Tab
**What goes wrong:** Agent navigates to Settings but doesn't find a "Carriers" tab.
**Why it happens:** CARRIER-02 requires App Settings → Carriers → Add/Edit. The tab name and locator need to be verified in the live MCSL app.
**How to avoid:** Nav URL `{app_base}/settings/0` lands on General tab. Carriers tab likely at `/settings/1` or via tab click. Add workflow guide section for carrier account config that exactly matches the MCSL app tab structure.
**Warning signs:** Agent sees Settings page but reports no Carriers tab.

### Pitfall 6: iframe Filter for MCSL app
**What goes wrong:** Network calls captured are empty or from wrong frame.
**Why it happens:** MCSL app API calls originate from the iframe, not the main Shopify page. The iframe URL filter must match MCSL app domains.
**How to avoid:** MCSL app iframe URL contains `mcsl-qa` or `pluginhive`. Update the frame filter in `_ax_tree()` and `_network()` to match. The current FedEx filter checks for `pluginhive` which should already match — verify with a live test.
**Warning signs:** `api_to_watch` shows no network calls even when label generation happens.

### Pitfall 7: Carrier-Specific Store Auth
**What goes wrong:** Agent runs against UPS carrier tests but authenticates with FedEx store session.
**Why it happens:** MCSL has separate Shopify stores per carrier (mcsl-automation for UPS, mcsl-automation-usps-ship for USPS, etc. — confirmed in carrier-envs/).
**How to avoid:** The MCSL config.py and order_creator.py should read the active carrier store credentials. For Phase 2, scope to `mcsl-automation` store (UPS + FedEx). Carrier account config flow tests carrier settings within the same store.
**Warning signs:** Login fails or agent lands in wrong Shopify admin.

---

## Code Examples

### Scenario Extraction
```python
# Source: FedexDomainExpert/pipeline/smart_ac_verifier.py lines 2093-2104
_EXTRACT_PROMPT = dedent("""\
    Extract each testable scenario from the acceptance criteria below.
    Return ONLY a JSON array of concise scenario title strings. No explanation.
    Example: ["User can enable Hold at Location", "Success toast shown after Save"]

    Acceptance Criteria:
    {ac}
""")

def _extract_scenarios(ac: str, claude: ChatAnthropic) -> list[str]:
    resp = claude.invoke([HumanMessage(content=_EXTRACT_PROMPT.format(ac=ac))])
    data = _parse_json(resp.content.strip())
    if isinstance(data, list):
        return data
    # fallback: parse line-by-line
    return [ln.strip("- ").strip() for ln in ac.splitlines()
            if ln.strip().startswith(("Given", "When", "Scenario", "Then", "-"))][:12]
```

### Plan JSON Schema (MCSL Extended)
```python
# MCSL extends FedEx plan schema with carrier field — CARRIER-01
# Claude must return:
{
    "app_path": "",
    "look_for": ["UI element or behaviour that proves scenario is implemented"],
    "api_to_watch": ["API endpoint path fragment to watch in network calls"],
    "nav_clicks": ["Shipping | Settings | AppProducts | Orders | Carriers | ..."],
    "plan": "one sentence: how you will verify this scenario",
    "order_action": "none | existing_fulfilled | existing_unfulfilled | create_new | create_bulk",
    "carrier": "FedEx | UPS | DHL | USPS | (empty if not carrier-specific)"
}
```

### Stop Flag Integration
```python
# Source: FedexDomainExpert/pipeline/smart_ac_verifier.py lines 2747-2749
# stop_flag is a callable() → bool — checked before each scenario
for idx, scenario in enumerate(scenarios):
    if stop_flag and stop_flag():
        logger.info("SmartVerifier: stopped by user after %d scenarios", idx)
        break
    # ... scenario processing
```

### Auth JSON Loading (Playwright)
```python
# Source: FedexDomainExpert/pipeline/smart_ac_verifier.py lines 1234-1242
def _auth_ctx_kwargs() -> dict:
    kw: dict = {"viewport": {"width": 1400, "height": 1000}}
    auth_json = Path(config.MCSL_AUTOMATION_REPO_PATH) / "auth.json"
    if auth_json.exists():
        try:
            json.loads(auth_json.read_text(encoding="utf-8"))
            kw["storage_state"] = str(auth_json)
        except Exception:
            pass
    return kw
# MCSL auth.json is at /Users/madan/Documents/mcsl-test-automation/auth.json
# (confirmed — file exists and contains valid session state)
```

### Download ZIP Action Handler
```python
# Source: FedexDomainExpert/pipeline/smart_ac_verifier.py lines 1449-1528
# Key pattern — use page.expect_download() to intercept ZIP:
with page.expect_download(timeout=30_000) as dl_info:
    el_to_click.click(timeout=5_000)
dl = dl_info.value
dl.save_as(zip_path)

# Unzip and read all files
with zipfile.ZipFile(zip_path, "r") as zf:
    for name in zf.namelist():
        ext = name.rsplit(".", 1)[-1].lower()
        if ext == "json":
            extracted[name] = json.loads(zf.read(name).decode("utf-8"))
        elif ext in ("csv", "txt", "xml", "log"):
            extracted[name] = zf.read(name).decode("utf-8")[:3000]
        else:
            info = zf.getinfo(name)
            extracted[name] = f"({ext.upper()} binary — {info.file_size:,} bytes)"
action["_zip_content"] = extracted
```

### MCSL Order Grid Navigation (key difference from FedEx)
```python
# Source: PROJECT.md §1 — VERIFIED from mcsl-test-automation spec files
# Flow: App URL → click Account Card → filter by Order ID → click Order ID link → Order Summary

# From labelGenerationAndFulfillment.spec.ts:
# await pages.orderGridPage.navigateToAppAndFilterOrder(orderID);
# await pages.orderGridPage.clickOrderId(orderID);
# await pages.orderSummaryPage.clickGenerateLabel();
# Status locator: div[class="order-summary-greyBlock"] > div:nth-child(1) > ... > span
# Generate Label button: getByRole('button', { name: 'Generate Label', exact: true })
```

### MCSL Label Summary Log Access (3-dots → View Log)
```python
# Source: PROJECT.md §2 — MCSL-specific (NOT FedEx How To flow)
# Three-dots button on label row:
# appFrame.locator('div[class="order-summary-root"]>div>div:nth-child(2)>div>div>div:nth-child(3)>div>div>div:nth-child(2)>div>table>tbody>tr>td:nth-child(8)')
# View Log menu item:
# appFrame.locator('div[role="presentation"]>div:nth-child(2)>ul>li:nth-child(1)').first()
# Dialog: .dialogHalfDivParent
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Screenshot-only QA explorer (chrome_agent.py) | Full agentic loop with AX tree + screenshot + network (smart_ac_verifier.py) | FedexDomainExpert Phase 2 | True pass/fail verdicts per scenario; can navigate multi-step flows |
| Separate agent/ directory (browser_loop.py, action_handlers.py, planner.py) | Single smart_ac_verifier.py file | Collapsed in FedexDomainExpert | Simpler; all state in one file; phase 2 should maintain this |
| TypeScript Playwright test execution | Python playwright sync API | FedexDomainExpert design decision | Python stays in same process as Claude + RAG; no cross-language subprocess |

**Deprecated/outdated:**
- `chrome_agent.py` (FedexDomainExpert): Single-step exploration tool; replaced by smart_ac_verifier.py's full agentic loop. Do NOT port chrome_agent.py to MCSL.

---

## MCSL-Specific Workflow Guide Sections Needed

The `_MCSL_WORKFLOW_GUIDE` must include these sections (replacing FedEx equivalents):

### Required Sections
1. **MCSL App URL Map** — `{app_base}/shopify`, `/products`, `/settings/0`, `/pickup`, `/rateslog`; Shopify orders at `admin.shopify.com/store/{store}/orders`
2. **MCSL Order Grid Navigation** — App URL → Account Card click → filter by Order ID → click row → Order Summary
3. **MCSL Generate Label flow** — PROCESSING → optional Prepare Shipment → Generate Label → LABEL CREATED → Mark As Fulfilled
4. **MCSL View Rate Summary** — must expand "View all Rate Summary" first (collapsed by default); 3-dots → View Log → `.dialogHalfDivParent`
5. **MCSL View Label Log** — 3-dots on Label Summary table row → View Log → `.dialogHalfDivParent`
6. **MCSL Bulk Label** — Order Grid → header checkbox label → "Generate labels" button (lowercase l) → Label Batch page
7. **MCSL Print Documents** — Opens new tab at pluginhive document viewer (switch_tab + screenshot + close_tab)
8. **MCSL Carrier Account Config** — Settings → Carriers → Add/Edit (CARRIER-02)
9. **Carrier-Specific Special Services** — FedEx HAL/dry-ice/alcohol/battery; UPS COD; DHL international; USPS registered mail

### Nav Clicks Accepted Values (MCSL)
`"Shipping"` | `"Settings"` | `"AppProducts"` | `"Orders"` | `"PickUp"` | `"ShopifyProducts"` | `"Rates Log"` | `"Carriers"`

---

## MCSL Order Creator Design

MCSL order_creator.py differs from FedEx because there is no `productsconfig.json` file in `mcsl-test-automation/` (no testData/products/ directory found). Product IDs are defined inline in carrier-env files as JSON env vars:

```
# From carrier-envs/ups.env
SIMPLE_PRODUCTS_JSON='[{"product_id":8250672349345,"variant_id":44995757244577},...]'
DANGEROUS_PRODUCTS_JSON='[{"product_id":7729648284034,"variant_id":45382308954273}]'
SHOPIFY_ACCESS_TOKEN=REDACTED_SHOPIFY_TOKEN
```

**order_creator.py approach for MCSL:**
1. Read from `config.MCSL_AUTOMATION_REPO_PATH + /carrier-envs/ups.env` (default carrier) or from `config.SHOPIFY_ACCESS_TOKEN` + `config.STORE`
2. Parse `SIMPLE_PRODUCTS_JSON`, `DANGEROUS_PRODUCTS_JSON` from env vars
3. Shipping address: use inline default (221B Baker Street, LA, CA, US, 90001 — from UPS carrier-env)
4. Shopify REST API: same pattern as FedEx order_creator.py (`POST /admin/api/{version}/orders.json`)
5. Store: `mcsl-automation.myshopify.com`, API version 2023-01

---

## Open Questions

1. **MCSL Carrier Account Config Locators**
   - What we know: Flow is App Settings → Carriers → Add/Edit (PROJECT.md §10). Tab name in Settings is "Carriers".
   - What's unclear: Exact CSS/role locators for the Carriers tab and Add Carrier button. Need live app verification.
   - Recommendation: Plan 02-04 should include a step to capture these locators from the live app using the auth.json session before writing the workflow guide section.

2. **MCSL App Slug Verification**
   - What we know: carrier-envs/ups.env shows APPURL ending in `/apps/mcsl-qa`. This is the MCSL app slug for the `mcsl-automation` store.
   - What's unclear: Whether other carrier stores (usps-ship, stamps) use the same `mcsl-qa` slug.
   - Recommendation: Use `mcsl-qa` as the default. Make it configurable via `config.py` (add `MCSL_APP_SLUG = os.getenv("MCSL_APP_SLUG", "mcsl-qa")`).

3. **DHL International Flow Locators**
   - What we know: DHL handles insurance, signature, international (CARRIER-06). International requires commercial invoice.
   - What's unclear: Whether DHL uses a separate MCSL store or the same mcsl-automation store. DHL carrier code is C1.
   - Recommendation: Start CARRIER-06 implementation using the same mcsl-automation store; capture DHL-specific UI locators from live app.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.3.3 |
| Config file | `/Users/madan/Documents/MCSLDomainExpert/pytest.ini` |
| Quick run command | `pytest tests/test_smart_ac_verifier.py -x -q` |
| Full suite command | `pytest tests/ -q` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| AGENT-01 | Extracts JSON array of scenarios from AC text | unit | `pytest tests/test_smart_ac_verifier.py::test_extract_scenarios -x` | Wave 0 |
| AGENT-02 | Queries domain expert RAG, returns ≤200-word answer | unit (mock RAG) | `pytest tests/test_smart_ac_verifier.py::test_ask_domain_expert -x` | Wave 0 |
| AGENT-03 | Generates valid JSON plan with required keys | unit (mock Claude) | `pytest tests/test_smart_ac_verifier.py::test_plan_scenario -x` | Wave 0 |
| AGENT-04 | Agentic loop runs up to 15 steps, breaks on verify | unit (mock Playwright) | `pytest tests/test_smart_ac_verifier.py::test_verify_scenario_loop -x` | Wave 0 |
| AGENT-05 | AX tree captured from both main page and iframe | unit (mock page) | `pytest tests/test_smart_ac_verifier.py::test_ax_tree_captures_iframe -x` | Wave 0 |
| AGENT-06 | Verdict pass/fail/partial/qa_needed returned per scenario | unit | `pytest tests/test_smart_ac_verifier.py::test_verdict_types -x` | Wave 0 |
| AGENT-07 | Stop flag halts loop before next scenario | unit | `pytest tests/test_smart_ac_verifier.py::test_stop_flag -x` | Wave 0 |
| CARRIER-01 | Carrier detected from AC text, injected into plan | unit | `pytest tests/test_smart_ac_verifier.py::test_carrier_detection -x` | Wave 0 |
| CARRIER-02 | Carrier account config flow nav succeeds | manual / smoke | manual — requires live MCSL app | N/A |
| CARRIER-03 | FedEx preconditions return correct JSON field assertions | unit | `pytest tests/test_smart_ac_verifier.py::test_preconditions_fedex -x` | Wave 0 |
| CARRIER-04 | UPS preconditions return correct flow steps | unit | `pytest tests/test_smart_ac_verifier.py::test_preconditions_ups -x` | Wave 0 |
| CARRIER-05 | USPS preconditions return correct flow steps | unit | `pytest tests/test_smart_ac_verifier.py::test_preconditions_usps -x` | Wave 0 |
| CARRIER-06 | DHL preconditions return correct flow steps | unit | `pytest tests/test_smart_ac_verifier.py::test_preconditions_dhl -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/test_smart_ac_verifier.py -x -q`
- **Per wave merge:** `pytest tests/ -q`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_smart_ac_verifier.py` — covers AGENT-01 through AGENT-07, CARRIER-01, CARRIER-03 through CARRIER-06
- [ ] `tests/test_order_creator.py` — covers order creation unit logic (mock Shopify API)
- [ ] Playwright dependency: `pip install playwright && playwright install chromium` (if not already installed)

---

## Sources

### Primary (HIGH confidence)
- `/Users/madan/Documents/Fed-Ex-automation/FedexDomainExpert/pipeline/smart_ac_verifier.py` — full agentic loop architecture, all prompts, action handlers, data models (read in full, 2840 lines)
- `/Users/madan/Documents/Fed-Ex-automation/FedexDomainExpert/pipeline/order_creator.py` — Shopify REST API order creation pattern
- `/Users/madan/Documents/Fed-Ex-automation/FedexDomainExpert/pipeline/chrome_agent.py` — older exploration pattern (NOT to be ported)
- `/Users/madan/Documents/MCSLDomainExpert/.planning/PROJECT.md` — MCSL-specific flows verified from code + wiki
- `/Users/madan/Documents/MCSLDomainExpert/config.py` — confirmed MCSL config structure, MCSL_AUTOMATION_REPO_PATH, APP_IFRAME_SELECTOR
- `/Users/madan/Documents/mcsl-test-automation/carrier-envs/ups.env` — MCSL store credentials, product IDs, app URL slug
- `/Users/madan/Documents/mcsl-test-automation/tests/orderSummary/labelGenerationFromSummary/labelGenerationAndFulfillment.spec.ts` — MCSL label generation flow locators

### Secondary (MEDIUM confidence)
- `/Users/madan/Documents/MCSLDomainExpert/.planning/REQUIREMENTS.md` — requirement text for all 13 Phase 2 requirements
- `/Users/madan/Documents/MCSLDomainExpert/.planning/ROADMAP.md` — plan structure (7 plans for Phase 2)
- `/Users/madan/Documents/mcsl-test-automation/.env` — multi-carrier store config (UPS, USPS-ship, USPS-stamps)

### Tertiary (LOW confidence — requires live app verification)
- MCSL Carriers tab locators in Settings — not found in automation code; needs live app capture
- DHL store configuration — carrier-env file for DHL not found; assumed same mcsl-automation store

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — identical to FedexDomainExpert; requirements.txt already has all dependencies
- Architecture: HIGH — direct port of proven 2840-line implementation with documented MCSL adaptation points
- MCSL nav flows: HIGH — sourced from PROJECT.md (verified from code + wiki) and live automation specs
- Carrier account config locators: LOW — requires live app verification; noted in Open Questions
- Pitfalls: HIGH — sourced from actual code examination and PROJECT.md difference table

**Research date:** 2026-04-15
**Valid until:** 2026-05-15 (30 days — Shopify app UI is relatively stable; carrier-env credentials may rotate)
