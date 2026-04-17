# Phase 3: Label + Docs + Pre-Requirements - Research

**Researched:** 2026-04-16
**Domain:** MCSL label generation flows, document verification strategies, pre-requirement injection and cleanup
**Confidence:** HIGH — all findings sourced directly from the working Phase 2 codebase, MCSL automation spec files, and MCSL POM source code

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| LABEL-01 | Agent handles Manual Label flow (Shopify Orders → order → More Actions → Generate Label → Get Rates → select service → SideDock → Generate) | NOTE: MCSL does NOT use Shopify More Actions. Flow is App order grid → filter by Order ID → Order Summary → Generate Label button. Implementation: _verify_scenario loop with correct nav steps in _MCSL_WORKFLOW_GUIDE |
| LABEL-02 | Agent handles Auto-Generate Label flow (More Actions → Auto-Generate Label) | MCSL auto-generate: Actions menu → "Auto Generate" (or Generate Label from actions). Uses `selectCheckboxAndClickActionsMenu` + `selectAction` pattern. Routes to label batch page (same as bulk). |
| LABEL-03 | Agent handles Bulk Label generation (Orders list → select all → Actions → Generate Labels) | MCSL bulk: header checkbox click (getByRole "row" label) → "Generate labels" button (lowercase l) → Label Batch page → wait for SUCCESS. Full flow in orderGridPage.ts |
| LABEL-04 | Agent handles Return Label flow (Order Summary → Return packages → Generate Return Label) | MCSL return: Actions menu → "Create Return Label" → Return Label modal header → Submit button. Status becomes "Return Created". From createReturnLabel.spec.ts |
| LABEL-05 | Agent creates test orders via Shopify REST API (single + bulk, reads mcsl-test-automation productsconfig.json + addressconfig.json) | order_creator.py already complete (Phase 2). LABEL-05 may need DANGEROUS_PRODUCTS_JSON support for special service pre-reqs (dry ice/battery use dangerous products in test specs) |
| DOC-01 | Agent verifies label existence via "label generated" badge on Order Summary | MCSL: status locator `div[class="order-summary-greyBlock"] > div:nth-child(1) > div:nth-child(1) > div > span` shows LABEL CREATED. Also `appFrame.getByRole('button').nth(2)` shows status text. validateLabelSummaryDisplayed() checks Label Summary table + SUCCESS cell. |
| DOC-02 | Agent verifies physical docs via More Actions → Download Documents (ZIP → read PDFs/files) | FedEx reference: download_zip action with target="Download Documents". MCSL equivalent: look for "Download Documents" in More Actions. Uses `page.expect_download()` → zipfile.ZipFile extraction. Stub in smart_ac_verifier.py must be replaced with full implementation. |
| DOC-03 | Agent verifies JSON request fields via More Actions → How To → Click Here (ZIP → createShipment JSON) | FedEx: More Actions → How To → scroll to bottom → download_zip target="Click Here". MCSL equivalent is the same pattern — click How To link in order summary → scroll to see "Click Here" → download_zip. |
| DOC-04 | Agent verifies visual label codes via Print Documents → switch_tab → screenshot → read codes → close_tab | MCSL: "Print Documents" button opens NEW TAB at PluginHive document viewer (pluginhive.io domain). Must use switch_tab + screenshot + close_tab. NOT a download — do NOT use download_zip for this. |
| DOC-05 | Agent views rate logs via ⋯ → View Logs → screenshot dialog (before label generation) | MCSL: ViewallRateSummary.click() → rateSummaryTableContainer visible → click3DotsOnRateSummary → viewLogButton.click() → rateRequestSummary (.dialogHalfDivParent). Confirmed from orderSummaryPage.ts |
| PRE-01 | Hardcoded pre-requirements injected for dry ice scenarios (AppProducts → Is Dry Ice Needed → weight → Save + cleanup) | _get_preconditions() already has FedEx dry ice branch in smart_ac_verifier.py. Phase 3 expands this to be MCSL-specific: navigate appproducts, find test product, enable toggle, set weight, save, cleanup after label. |
| PRE-02 | Hardcoded pre-requirements injected for alcohol scenarios (AppProducts → Is Alcohol → type → Save + cleanup) | Already in _get_preconditions() FedEx branch. Phase 3 ensures MCSL nav (appproducts hamburger) and MCSL product search pattern are used. |
| PRE-03 | Hardcoded pre-requirements injected for battery scenarios (AppProducts → Is Battery → material/packing → Save + cleanup) | Already in _get_preconditions() FedEx branch. Expand to use MCSL product navigation. |
| PRE-04 | Hardcoded pre-requirements for signature scenarios (AppProducts → Signature field → Save + cleanup) | Already in _get_preconditions() FedEx branch. MCSL field name: "FedEx® Delivery Signature Options". |
| PRE-05 | Hardcoded pre-requirements for HAL scenarios (SideDock → Hold at Location → modal → select → Yes) | In _get_preconditions(): HAL branch uses label_flow[:5] + SideDock steps. Phase 3: expand with correct MCSL SideDock locators. |
| PRE-06 | Hardcoded pre-requirements for insurance scenarios (SideDock → Insurance → pencil → modal) | In _get_preconditions(): insurance branch. Insurance in MCSL is via SideDock. UPS insurance spec verified from insurance.spec.ts using verifyRateRequestXMLForInsurnceNode(). |
</phase_requirements>

---

## Summary

Phase 3 extends the working Phase 2 agentic loop by replacing three stubs with full implementations and adding new label flow navigation paths. The work is concentrated in four areas: (1) replacing the `download_zip` and `download_file` stubs in `_do_action()` with the full FedEx reference implementation adapted for MCSL, (2) expanding `_get_preconditions()` with MCSL-specific product navigation sequences for all six special service types, (3) adding Manual/Auto/Bulk/Return label generation navigation paths to `_MCSL_WORKFLOW_GUIDE`, and (4) writing the Shopify REST order creation path for LABEL-05 (dangerous products support for battery/dry-ice scenarios).

The FedEx reference implementation in `/Users/madan/Documents/Fed-Ex-automation/FedexDomainExpert/pipeline/smart_ac_verifier.py` already contains fully working `download_zip` and `download_file` handlers (lines 1449–1633) using `page.expect_download()`, `zipfile.ZipFile`, and CSV/Excel/binary detection. These port directly to MCSL with one change: the element locator strategy searches the MCSL app iframe first. The Phase 2 stubs at lines 1142–1154 in `pipeline/smart_ac_verifier.py` must be replaced.

The MCSL automation spec files in `mcsl-test-automation/` provide ground-truth locators for every Phase 3 flow. The `orderSummaryPage.ts` POM contains exact CSS selectors for the rate log (`.rate-summary-table tbody tr td:last-child button[aria-haspopup="true"]`), the three-dots menu on Label Summary, the `.dialogHalfDivParent` log dialog, and the `ViewallRateSummary` title locator. The `orderGridPage.ts` POM confirms the bulk label flow (header row label click → `div[class="buttons-row"] > button:nth-child(4)` for Actions menu → Generate labels button), and the return label flow (Actions menu → "Create Return Label" → Submit button in `body > div:nth-child(15)`).

**Primary recommendation:** Replace download stubs with ported FedEx implementation, expand `_get_preconditions()` to include MCSL product navigation locators, add bulk/return/auto-generate to `_MCSL_WORKFLOW_GUIDE`, and ensure `_verify_scenario` correctly propagates `_file_content` alongside `_zip_content` into `zip_ctx` for Claude's context.

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| playwright (Python sync API) | >=1.40 | `page.expect_download()` for ZIP/file intercept, switch_tab, close_tab | Already wired in Phase 2; `expect_download()` is Playwright's built-in download intercept — no alternatives |
| zipfile (stdlib) | — | Extract ZIP downloads from app: JSON, CSV, XML, TXT, log | Built-in; FedEx reference already uses this pattern |
| tempfile (stdlib) | — | Temp directory for downloaded files | Built-in; shutil.rmtree cleanup after read |
| shutil (stdlib) | — | Cleanup temp directories after ZIP extraction | Built-in |
| csv (stdlib) | — | Parse CSV files from download_file handler | Built-in; used in FedEx reference |
| langchain-anthropic + langchain-core | >=0.3.0 | Claude invocation already in Phase 2 | No change from Phase 2 |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| openpyxl | optional | Parse Excel files in download_file handler | Only if Excel downloads are expected; import inside try/except |
| json (stdlib) | — | Parse JSON files from ZIP | Already imported; used in FedEx reference for ZIP JSON extraction |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `page.expect_download()` | `page.route()` intercept | `expect_download()` is simpler and already in FedEx reference; `route()` adds complexity with no benefit |
| zipfile stdlib | py7zr, rarfile | ZIP is the only format used by MCSL Download Documents and How To flows |
| screenshot for DOC-04 | page.pdf() | Print Documents opens a viewer tab, not a PDF download — screenshot is the only option |

**Installation:** All dependencies already installed from Phase 2 requirements.txt. No new packages needed.

---

## Architecture Patterns

### Recommended Project Structure
```
pipeline/
├── smart_ac_verifier.py    # All changes in Phase 3 go here — no new files
tests/
├── test_agent.py           # New test functions appended (Phase 3 stubs → activated)
├── test_label_flows.py     # New: dedicated label flow + pre-reqs unit tests
```

Phase 3 does NOT require new files. All changes extend the existing `pipeline/smart_ac_verifier.py`. New test functions are added to `tests/test_agent.py` and/or a new `tests/test_label_flows.py`.

### Pattern 1: download_zip Full Implementation (replaces Phase 2 stub)
**What:** Intercepts file download triggered by clicking a target element, saves to temp dir, extracts ZIP, reads all files, stores in `action["_zip_content"]`.
**When to use:** DOC-02 (Download Documents), DOC-03 (How To → Click Here)

```python
# Source: FedexDomainExpert/pipeline/smart_ac_verifier.py lines 1449-1528
# MCSL adaptation: search app iframe frame first (same as FedEx reference)
if atype == "download_zip":
    try:
        tmp_dir  = tempfile.mkdtemp(prefix="sav_zip_")
        zip_path = os.path.join(tmp_dir, "mcsl_download.zip")
        frame = _get_app_frame(page)

        el_to_click = None
        for fn in [
            lambda: frame.get_by_role("button", name=target, exact=False),
            lambda: frame.get_by_role("link",   name=target, exact=False),
            lambda: frame.get_by_text(target, exact=False),
            lambda: page.get_by_role("button",  name=target, exact=False),
            lambda: page.get_by_role("link",    name=target, exact=False),
            lambda: page.get_by_text(target, exact=False),
        ]:
            try:
                el = fn()
                if el.count() > 0:
                    el_to_click = el.first
                    break
            except Exception:
                continue

        if el_to_click is None:
            return False

        with page.expect_download(timeout=30_000) as dl_info:
            el_to_click.click(timeout=5_000)

        dl = dl_info.value
        dl.save_as(zip_path)
        page.wait_for_timeout(500)

        extracted: dict = {}
        with zipfile.ZipFile(zip_path, "r") as zf:
            for name in zf.namelist():
                ext = name.rsplit(".", 1)[-1].lower()
                if ext == "json":
                    raw_text = zf.read(name).decode("utf-8", errors="replace")
                    try:
                        extracted[name] = json.loads(raw_text)
                    except Exception:
                        extracted[name] = raw_text
                elif ext in ("csv", "txt", "xml", "log"):
                    extracted[name] = zf.read(name).decode("utf-8", errors="replace")[:3000]
                else:
                    info = zf.getinfo(name)
                    extracted[name] = f"({ext.upper()} binary — {info.file_size:,} bytes)"

        action["_zip_content"] = extracted
        import shutil
        shutil.rmtree(tmp_dir, ignore_errors=True)
        return True
    except Exception as e:
        logger.debug("download_zip failed: %s", e)
        return False
```

### Pattern 2: download_file Full Implementation (replaces Phase 2 stub)
**What:** Intercepts any direct file download (CSV, Excel, PDF, etc.), reads content into `action["_file_content"]`.
**When to use:** DOC-02 reports/CSV files; any non-ZIP direct download

```python
# Source: FedexDomainExpert/pipeline/smart_ac_verifier.py lines 1530-1633
# Key: action["_file_content"] injected; agentic loop should propagate to context
# CSV handling: headers, row_count, sample_rows, raw_preview
# Excel handling: openpyxl (optional import); fallback to size note
# PDF: size note only
# Other: raw bytes decoded as utf-8 up to 2000 chars
```

### Pattern 3: zip_ctx propagation in _verify_scenario
**What:** After `download_zip` sets `action["_zip_content"]`, the loop must propagate the extracted content into `zip_ctx` so Claude can read it on the next step.
**When to use:** _verify_scenario loop — already partially coded in Phase 2 (`if "_zip_content" in action`)

```python
# Source: smart_ac_verifier.py _verify_scenario loop (Phase 2 partial)
# Phase 3: ensure _file_content is also captured
if "_zip_content" in action:
    zip_ctx = _format_zip_for_context(action["_zip_content"])
if "_file_content" in action:
    zip_ctx = _format_file_for_context(action["_file_content"])
```

A helper `_format_zip_for_context(extracted: dict) -> str` should produce a readable summary string for Claude. The FedEx reference formats this as a file listing with content snippets.

### Pattern 4: MCSL Manual Label Flow (already in _MCSL_WORKFLOW_GUIDE — confirm and extend)
**What:** End-to-end label generation from Order Summary.
**Confirmed from:** `orderSummaryPage.ts:clickGenerateLabel()` + `labelGenerationAndFulfillment.spec.ts`

```
1. navigate: "orders"  (ORDERS tab inside app iframe)
2. If order not visible: reload up to 5×
3. Click "Add filter" → menuitem "Order Id" → fill textbox with orderID → press Escape
4. Click order link (getByRole "link", name=orderID) → Order Summary opens
5. If "Prepare Shipment" button visible → click (retry up to 3×)
6. Click "Generate Label" (exact=True) → wait for appFrame.getByRole('button').nth(2) = "LABEL CREATED" (timeout 800s)
7. Verify: status locator div[class="order-summary-greyBlock"] > div:nth-child(1) > div:nth-child(1) > div > span
8. validateLabelSummaryDisplayed: getByText('Label Summary') visible + getByRole('cell', name='SUCCESS').first() visible
```

### Pattern 5: MCSL Bulk Label Flow (LABEL-03)
**Confirmed from:** `orderGridPage.ts:selectAllFilteredOrders()` + `clickGenerateLabelInOrderGrid()`

```
1. navigate: "orders"
2. Create N orders (order_action: create_bulk)
3. Click header checkbox: appFrame.getByRole("row", name="#").locator("label").first()
4. Click "Generate labels" button: appFrame.locator('role=button[name="Generate labels"]')
   → Label Batch page opens
5. Wait for label batch status: waitUntilStatusChangesInLabelBatch → 'SUCCESS'
6. Click "Mark as Fulfilled": appFrame.locator('role=button[name="Mark as Fulfilled"]')
```

NOTE: The "Generate labels" button uses lowercase "l". This is important — `getByRole('button', {name: 'Generate labels'})` must match exactly.

### Pattern 6: MCSL Auto-Generate Label Flow (LABEL-02)
**Confirmed from:** `generateLabelFromActionsMenu.spec.ts` + `orderGridPage.ts:selectCheckboxAndClickActionsMenu()`

```
1. navigate: "orders"
2. Create order (order_action: create_new)
3. Filter by Order ID (Add filter → Order Id → fill → Escape)
4. Click header checkbox label (getByRole "row" name="#" → locator "label" first)
5. Click Actions button: appFrame.locator('div[class="buttons-row"] > button:nth-child(4)')
6. Search in Actions menu → selectAction("Generate Label") (fills search box → clicks menuitem)
   → Label Batch page opens (same as bulk)
7. Wait for SUCCESS → Mark as Fulfilled
```

### Pattern 7: MCSL Return Label Flow (LABEL-04)
**Confirmed from:** `createReturnLabel.spec.ts` + `orderGridPage.ts:generateReturnLabel()`

```
1. Requires an ALREADY FULFILLED order (order_action: existing_fulfilled)
2. navigate: "orders" → filter by Order ID
3. Select checkbox + click Actions button (selectCheckboxAndClickActionsMenu)
4. selectAction("Create Return Label") → Return Label modal opens
5. Modal header: appFrame.locator("body > div:nth-child(15) > div > div:nth-child(1) > div > div > h3") = "Return Label"
6. Click Submit button (getByRole 'button' name='Submit')
7. Verify: order status in grid = "Return Created" (validateStatusInOrderGrid)
```

### Pattern 8: Document Verification Strategies

**DOC-01 — Badge check:**
```
After Generate Label: verify appFrame.getByRole('button').nth(2) shows "LABEL CREATED"
Also: getByText('Label Summary') visible + getByRole('cell', name='SUCCESS').first() visible
```

**DOC-02 — Download Documents ZIP:**
```
On Order Summary (after LABEL CREATED):
1. Click "More Actions" or find "Download Documents" button
2. action=download_zip, target="Download Documents"
3. ZIP extracted → action["_zip_content"] contains PDF size notes + any text files
4. Claude verifies expected files are present
```

**DOC-03 — How To JSON extraction:**
```
On Order Summary (BEFORE or AFTER label generation):
1. Click "How To" (link or button in order summary area)
2. Modal opens with usage instructions
3. Scroll to bottom to find "Click Here" link
4. action=download_zip, target="Click Here"
5. ZIP contains createShipment request JSON → Claude verifies JSON fields
NOTE: This is the ONLY reliable way to verify JSON request fields (dry ice weight, signature type, etc.)
```

**DOC-04 — Print Documents new-tab screenshot:**
```
On Order Summary (after LABEL CREATED):
1. Click "Print Documents" (standalone button — NOT in More Actions)
2. New tab opens at *document-viewer.pluginhive.io* or *.pluginhive.com*
3. action=switch_tab → active_page becomes new tab
4. Take screenshot → Claude reads visible label codes (ICE, ALCOHOL, ELB, ASR, DSR)
5. action=close_tab → returns to Order Summary
NOTE: Do NOT use download_zip here — Print Documents is a NEW TAB, not a download
```

**DOC-05 — Rate log screenshot (BEFORE label generation):**
```
On Order Summary (after rates load, BEFORE clicking Generate Label):
1. Click ViewallRateSummary: appFrame.getByTitle('View all Rate Summary')
   (collapsed by default — must expand first)
2. Click 3-dots on rate summary row:
   appFrame.locator('.rate-summary-table tbody tr td:last-child button[aria-haspopup="true"]')
3. Click viewLogButton: appFrame.locator('div[role="presentation"]>div:nth-child(2)>ul>li:nth-child(1)').first()
4. Log dialog: appFrame.locator('.dialogHalfDivParent') — contains JSON/XML request text
5. Screenshot dialog → Claude verifies required fields present
6. Close: appFrame.getByRole('button', {name: 'Close'})
```

### Pattern 9: _get_preconditions() MCSL-Specific Expansion (PRE-01 through PRE-06)
**What:** Returns ordered list of step strings for agent to execute before label generation.
**Current state (Phase 2):** FedEx-specific branches already exist in `smart_ac_verifier.py` lines 127–292.
**Phase 3 change:** The existing step strings already use MCSL-correct nav (appproducts hamburger, label_flow from app order grid). The Phase 3 planner must ensure these are correct and add cleanup steps as separate browser actions.

Key MCSL product navigation for PRE-01 through PRE-04:
```
Product search in AppProducts: hamburger → Products → find test product by name link
Toggle: get_by_label("Is Dry Ice Needed") or get_by_role("checkbox", name="Is Dry Ice Needed")
Save: get_by_role("button", name="Save")
Success toast: appFrame.locator('.s-alert-box-inner')
```

HAL (PRE-05) — SideDock steps on Order Summary:
```
On Order Summary, BEFORE clicking Generate Label:
- Click 'Hold at Location' in SideDock panel
- Search location field → type location name → select from results
- Click Yes/Confirm
```

Insurance (PRE-06) — SideDock steps on Order Summary:
```
On Order Summary, BEFORE clicking Generate Label:
- Click Insurance pencil icon in SideDock
- Fill declared value modal
- Click Confirm
```

### Anti-Patterns to Avoid
- **Using download_zip for Print Documents (DOC-04):** Print Documents opens a new tab, NOT a file download. Use switch_tab + screenshot + close_tab.
- **Missing ViewallRateSummary click before DOC-05:** The Rate Summary table is collapsed by default. Must click getByTitle('View all Rate Summary') before the 3-dots button is accessible.
- **Return Label on unfulfilled order:** LABEL-04 requires an already-FULFILLED order. Use `order_action: existing_fulfilled` in the plan.
- **Hardcoding zip_path without cleanup:** Always use `tempfile.mkdtemp()` + `shutil.rmtree()` to avoid disk accumulation during extended test runs.
- **Injecting _file_content but not _zip_content into zip_ctx:** Both download handlers must propagate their results into `zip_ctx` via formatting helpers so Claude can read the content in the next step.
- **Using More Actions for label generation:** MCSL label generation uses the app's own "Generate Label" button on Order Summary. The "More Actions" pattern is FedEx-only.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| ZIP download interception | Custom fetch/request intercept | `page.expect_download()` | Playwright's built-in handles async download triggering correctly; custom approach races with click handler |
| ZIP extraction | Manual binary parsing | `zipfile.ZipFile` (stdlib) | Handles all ZIP variants; already in imports |
| CSV parsing from download_file | Manual split/parse | `csv.reader` (stdlib) | Handles quoted fields, encoding; already in FedEx reference |
| format_zip_for_context | Custom JSON serializer | Simple dict-to-string helper | FedEx reference already has this pattern; copy it |
| Rate log dialog locator | Dynamic element search | Hardcoded `.dialogHalfDivParent` | Confirmed stable from orderSummaryPage.ts — same locator used across all log types |
| Print Documents tab detection | URL polling | switch_tab + pluginhive frame filter | `_ax_tree()` already filters pluginhive frames; switch_tab is sufficient |

**Key insight:** The FedEx reference already solves every non-trivial download problem in 200 lines. Phase 3's value is in porting and adapting those 200 lines, not reinventing them.

---

## Common Pitfalls

### Pitfall 1: Print Documents Uses New Tab, Not Download
**What goes wrong:** Claude (or agent) uses `action=download_zip, target="Print Documents"` — this fails silently because Print Documents triggers a new tab, not a file download. The `download_zip` handler looks for a download event that never fires.
**Why it happens:** The FedEx workflow guide notes say "Print Documents opens a new tab" but the agent may still try download_zip based on context.
**How to avoid:** `_MCSL_WORKFLOW_GUIDE` and `_DECISION_PROMPT` must explicitly state: "Print Documents → NEW TAB (use switch_tab + screenshot + close_tab). Do NOT use download_zip."
**Warning signs:** `download_zip` returns False but no exception logged; active_page not changed.

### Pitfall 2: Rate Summary Is Collapsed — Must Click ViewallRateSummary First
**What goes wrong:** Agent clicks the 3-dots button on Rate Summary but it is not visible (table is collapsed).
**Why it happens:** MCSL Rate Summary collapses by default on Order Summary page. The locator `.rate-summary-table tbody tr td:last-child button` returns 0 results until expanded.
**How to avoid:** Rate log flow must ALWAYS click `appFrame.getByTitle('View all Rate Summary')` first and wait for `.rate-summary-table-container` to be visible.
**Warning signs:** `click3DotsOnRateSummary.nth(0).click()` times out immediately.

### Pitfall 3: generate_zip Requires page Not Frame for expect_download
**What goes wrong:** `frame.expect_download()` is called on the app iframe Frame object — this method does not exist on Frame objects, only on Page.
**Why it happens:** `_get_app_frame(page)` returns a Frame; `page.expect_download()` is the correct call.
**How to avoid:** Always call `page.expect_download()` (the full Page object), not `frame.expect_download()`. The `el_to_click.click()` inside the context manager can use the frame locator — only the `expect_download` must use `page`.
**Warning signs:** `AttributeError: 'Frame' object has no attribute 'expect_download'`

### Pitfall 4: Return Label Requires Fulfilled Order
**What goes wrong:** Agent tries return label on a freshly-created unfulfilled order.
**Why it happens:** `order_action: create_new` is used but LABEL-04 needs an existing fulfilled order.
**How to avoid:** `_PLAN_PROMPT` order judgment table must map "return label" → `existing_fulfilled`. The `_MCSL_WORKFLOW_GUIDE` must state this explicitly.
**Warning signs:** Order Summary shows "Generate Label" button (unfulfilled) — return label option not available.

### Pitfall 5: Cleanup Steps Are Part of Preconditions and Must Be Executed
**What goes wrong:** Pre-requirements enable dry ice / alcohol / battery / signature but cleanup never runs because the agent exits after label generation.
**Why it happens:** `_get_preconditions()` includes a `(CLEANUP: ...)` note string but it is a hint to Claude, not an enforced step. The agent may not navigate back to AppProducts after label generation.
**How to avoid:** Phase 3 pre-requirements should be structured as separate BEFORE and AFTER step lists, or the cleanup should be an explicit `_do_after_label_generation()` hook in `_verify_scenario`. Minimally, the cleanup note must be in the `_DECISION_PROMPT` as an explicit instruction: "After reaching LABEL CREATED, revert product settings before calling verify."
**Warning signs:** Dry ice / alcohol / battery toggles left enabled in test store products, causing subsequent unrelated test failures.

### Pitfall 6: _zip_content and _file_content Must Both Flow Into zip_ctx
**What goes wrong:** After `download_file` sets `action["_file_content"]`, `zip_ctx` is not updated, so Claude's next step context is missing the file content.
**Why it happens:** Phase 2 `_verify_scenario` only checks `if "_zip_content" in action`. `_file_content` was added in Phase 3 but the propagation code was not updated.
**How to avoid:** In `_verify_scenario` loop body, check both keys:
```python
if "_zip_content" in action:
    zip_ctx = _format_zip_for_context(action["_zip_content"])
if "_file_content" in action:
    zip_ctx = _format_file_for_context(action["_file_content"])
```
**Warning signs:** Claude sees download_file returned True but next step context shows no file data.

### Pitfall 7: Bulk Label "Generate labels" Uses Lowercase "l"
**What goes wrong:** Agent clicks "Generate Labels" (capital L) — button not found.
**Why it happens:** MCSL UI uses "Generate labels" (lowercase l). `get_by_role("button", name="Generate labels")` is case-sensitive by default in Playwright.
**How to avoid:** Use `exact=False` or confirm the exact casing from `orderGridPage.ts:clickGenerateLabelInOrderGrid()` which uses `role=button[name="Generate labels"]`.
**Warning signs:** Click strategy falls through all 7 attempts and returns False.

---

## Code Examples

### download_zip handler (full implementation)
```python
# Source: FedexDomainExpert/pipeline/smart_ac_verifier.py lines 1449-1528
# MCSL port — use page.expect_download(), not frame.expect_download()
if atype == "download_zip":
    try:
        tmp_dir  = tempfile.mkdtemp(prefix="sav_zip_")
        zip_path = os.path.join(tmp_dir, "mcsl_download.zip")
        frame = _get_app_frame(page)
        target = action.get("target", action.get("selector", "")).strip()

        el_to_click = None
        for fn in [
            lambda: frame.get_by_role("button", name=target, exact=False),
            lambda: frame.get_by_role("link",   name=target, exact=False),
            lambda: frame.get_by_text(target, exact=False),
            lambda: page.get_by_role("button",  name=target, exact=False),
            lambda: page.get_by_role("link",    name=target, exact=False),
            lambda: page.get_by_text(target, exact=False),
        ]:
            try:
                el = fn()
                if el.count() > 0:
                    el_to_click = el.first; break
            except Exception:
                continue

        if el_to_click is None:
            logger.debug("download_zip: target %r not found", target)
            return False

        with page.expect_download(timeout=30_000) as dl_info:
            el_to_click.click(timeout=5_000)

        dl = dl_info.value
        dl.save_as(zip_path)
        page.wait_for_timeout(500)

        extracted: dict = {}
        with zipfile.ZipFile(zip_path, "r") as zf:
            for name in zf.namelist():
                ext = name.rsplit(".", 1)[-1].lower()
                if ext == "json":
                    raw = zf.read(name).decode("utf-8", errors="replace")
                    try:
                        extracted[name] = json.loads(raw)
                    except Exception:
                        extracted[name] = raw
                elif ext in ("csv", "txt", "xml", "log"):
                    extracted[name] = zf.read(name).decode("utf-8", errors="replace")[:3000]
                else:
                    info = zf.getinfo(name)
                    extracted[name] = f"({ext.upper()} binary — {info.file_size:,} bytes)"

        action["_zip_content"] = extracted
        logger.info("download_zip: extracted %d files — %s", len(extracted), list(extracted.keys()))
        import shutil; shutil.rmtree(tmp_dir, ignore_errors=True)
        return True
    except Exception as e:
        logger.debug("download_zip failed: %s", e)
        return False
```

### Order Summary locators (from orderSummaryPage.ts)
```python
# Status span (PROCESSING / LABEL CREATED / FULFILLED):
# appFrame.locator('div[class="order-summary-greyBlock"] > div:nth-child(1) > div:nth-child(1) > div > span')

# Status button (alternative, used for waiting):
# appFrame.getByRole('button').nth(2)

# 3-dots on Label Summary row:
# appFrame.locator('div[class="order-summary-root"]>div>div:nth-child(2)>div>div>div:nth-child(3)>div>div>div:nth-child(2)>div>table>tbody>tr>td:nth-child(8)')

# View Log button (after 3-dots menu opens):
# appFrame.locator('div[role="presentation"]>div:nth-child(2)>ul>li:nth-child(1)').first()

# Log dialog:
# appFrame.locator('.dialogHalfDivParent')

# View all Rate Summary (expand before 3-dots):
# appFrame.getByTitle('View all Rate Summary')

# 3-dots on Rate Summary row:
# appFrame.locator('.rate-summary-table tbody tr td:last-child button[aria-haspopup="true"]')
```

### Return Label flow (from createReturnLabel.spec.ts + orderGridPage.ts)
```python
# 1. Checkbox + Actions menu:
# appFrame.getByRole("row", name="#").locator("label").first().click()
# appFrame.locator('div[class="buttons-row"] > button:nth-child(4)').click()

# 2. Select action:
# appFrame.getByRole("textbox", name="Search").fill("Create Return Label")
# appFrame.getByRole("menuitem", name="Create Return Label").first().click()

# 3. Return Label modal header:
# appFrame.locator("body > div:nth-child(15) > div > div:nth-child(1) > div > div > h3")
# → text = "Return Label"

# 4. Submit:
# appFrame.getByRole("button", name="Submit").click()

# 5. Verify status in grid:
# appFrame.locator("#all-order-table table tbody tr").first().locator("td").nth(10)
# → "Return Created"
```

### Bulk label flow (from orderGridPage.ts)
```python
# 1. Select all filtered orders:
# appFrame.getByRole("row", name="#").locator("label").first().click()  (header checkbox)

# 2. Click Generate labels:
# appFrame.locator('role=button[name="Generate labels"]').click()
# OR
# appFrame.get_by_role("button", name="Generate labels").click()

# 3. Wait for SUCCESS in label batch:
# labelBatchPage.waitUntilStatusChangesInLabelBatch('1', 'Label Status', 'Processing', 'SUCCESS')
# Python equivalent: poll appFrame for cell with text 'SUCCESS' up to timeout

# 4. Mark as Fulfilled:
# appFrame.get_by_role("button", name="Mark as Fulfilled").click()
```

### _get_preconditions() for MCSL dry ice (PRE-01)
```python
# Current in smart_ac_verifier.py (Phase 2, lines ~172-177):
# Already uses MCSL nav (appproducts hamburger, app order grid label flow)
# Phase 3 validates these steps are executable — no rewrite needed, but cleanup must be enforced

steps = product_nav + [
    "Enable 'Is Dry Ice Needed' toggle on the product",
    "Set Dry Ice Weight to a valid value (e.g. 1.0 kg)",
    "Click Save",
    "Verify success toast appears",
] + label_flow + [cleanup_note]

# cleanup_note = "(CLEANUP: After LABEL CREATED, navigate to appproducts, uncheck 'Is Dry Ice Needed', Save)"
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| download_zip stub (log + return False) | Full download_zip with expect_download() + zipfile extraction | Phase 3 | Agent can verify JSON fields in createShipment requests and physical document downloads |
| _get_preconditions() as string block passed to Claude | _get_preconditions() returns list[str] of executable step descriptions | Phase 2 MCSL adaptation | Steps are enumerable; agent can iterate through them |
| FedEx _get_preconditions() (single-carrier) | MCSL _get_preconditions() (multi-carrier, returns list[str]) | Phase 2 | Correct carrier-specific SideDock vs product-nav routing |

**Deprecated/outdated:**
- `download_zip` stub (Phase 2): logs warning + returns False. Must be replaced in Phase 3.
- `download_file` stub (Phase 2): same — must be replaced.

---

## Open Questions

1. **Does MCSL have a "Download Documents" button on Order Summary?**
   - What we know: FedEx uses "More Actions → Download Documents". MCSL's order summary shows a Label Summary table.
   - What's unclear: Whether MCSL has a direct "Download Documents" button or if it's in an actions menu on Order Summary.
   - Recommendation: Plan 03-04 should include a step to capture the Order Summary page AX tree after LABEL CREATED to confirm the exact button/link text for DOC-02.

2. **Does MCSL have a "How To" modal on Order Summary for DOC-03?**
   - What we know: FedEx has a "How To" button in the order summary that opens a modal with a "Click Here" link to download the createShipment ZIP.
   - What's unclear: Whether MCSL's Order Summary has the same pattern, or if the JSON request is only visible via the rate log dialog.
   - Recommendation: Treat DOC-03 as MEDIUM confidence. Plan 03-04 should probe the live app for "How To" before implementing. Fall back to rate log (DOC-05) if not present.

3. **MCSL dangerous products for LABEL-05 (dry ice, battery)**
   - What we know: `order_creator.py` already supports `DANGEROUS_PRODUCTS_JSON` from carrier-env files. The `create_order()` function has `use_dangerous_products=False` parameter.
   - What's unclear: Whether the dry ice / battery scenarios need dangerous products or simple products. FedEx uses `Simple 1` and `BLAZER` products for special services.
   - Recommendation: LABEL-05 is mostly complete from Phase 2. Phase 3 should verify that `use_dangerous_products=True` is passed when the scenario keyword is "battery" or "dangerous goods".

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.3.3 |
| Config file | `/Users/madan/Documents/MCSLDomainExpert/pytest.ini` |
| Quick run command | `PYTHONPATH=. .venv/bin/pytest tests/ -x -q` |
| Full suite command | `PYTHONPATH=. .venv/bin/pytest tests/ -q` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| LABEL-01 | Manual label flow nav steps injected into plan for label scenarios | unit (mock Claude) | `pytest tests/test_label_flows.py::test_manual_label_flow_plan -x` | Wave 0 — create in 03-01 |
| LABEL-02 | Auto-generate label flow: Actions menu → Generate Label → Label Batch | unit (mock page) | `pytest tests/test_label_flows.py::test_auto_generate_flow -x` | Wave 0 |
| LABEL-03 | Bulk label: header checkbox → Generate labels → SUCCESS status | unit (mock page) | `pytest tests/test_label_flows.py::test_bulk_label_flow -x` | Wave 0 |
| LABEL-04 | Return label: Actions → Create Return Label → Submit → Return Created | unit (mock page) | `pytest tests/test_label_flows.py::test_return_label_flow -x` | Wave 0 |
| LABEL-05 | Order creator supports dangerous products via use_dangerous_products param | unit (mock API) | `pytest tests/test_agent.py::test_order_creator -x` | ✅ (extend existing) |
| DOC-01 | Label badge check: LABEL CREATED status confirmed | unit (mock page) | `pytest tests/test_label_flows.py::test_doc01_badge_check -x` | Wave 0 |
| DOC-02 | download_zip handler: intercepts download, extracts ZIP, sets _zip_content | unit (mock page + zipfile) | `pytest tests/test_label_flows.py::test_doc02_download_zip -x` | Wave 0 |
| DOC-03 | How To ZIP download: download_zip target="Click Here" → JSON in _zip_content | unit | `pytest tests/test_label_flows.py::test_doc03_how_to_zip -x` | Wave 0 |
| DOC-04 | Print Documents: switch_tab + screenshot, NOT download_zip | unit (mock page) | `pytest tests/test_label_flows.py::test_doc04_print_documents -x` | Wave 0 |
| DOC-05 | Rate log: ViewallRateSummary click → 3-dots → View Log → dialogHalfDivParent | unit (mock page) | `pytest tests/test_label_flows.py::test_doc05_rate_log -x` | Wave 0 |
| PRE-01 | dry ice preconditions: appproducts nav + enable toggle + cleanup note | unit | `pytest tests/test_label_flows.py::test_pre01_dry_ice_preconditions -x` | Wave 0 |
| PRE-02 | alcohol preconditions: appproducts nav + Is Alcohol + cleanup | unit | `pytest tests/test_label_flows.py::test_pre02_alcohol_preconditions -x` | Wave 0 |
| PRE-03 | battery preconditions: appproducts nav + Is Battery + material/packing | unit | `pytest tests/test_label_flows.py::test_pre03_battery_preconditions -x` | Wave 0 |
| PRE-04 | signature preconditions: appproducts nav + Signature field | unit | `pytest tests/test_label_flows.py::test_pre04_signature_preconditions -x` | Wave 0 |
| PRE-05 | HAL preconditions: label_flow[:5] + SideDock steps | unit | `pytest tests/test_label_flows.py::test_pre05_hal_preconditions -x` | Wave 0 |
| PRE-06 | insurance preconditions: label_flow[:5] + SideDock insurance steps | unit | `pytest tests/test_label_flows.py::test_pre06_insurance_preconditions -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `PYTHONPATH=. .venv/bin/pytest tests/ -x -q`
- **Per wave merge:** `PYTHONPATH=. .venv/bin/pytest tests/ -q`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_label_flows.py` — new file covering LABEL-01 through LABEL-05, DOC-01 through DOC-05, PRE-01 through PRE-06
- [ ] Extend `tests/test_agent.py::test_action_handlers` to assert download_zip and download_file are no longer returning False (once stubs replaced)

*(If test infrastructure is already in place for Phase 2 tests, no framework install needed — same pytest + .venv)*

---

## Sources

### Primary (HIGH confidence)
- `pipeline/smart_ac_verifier.py` — Phase 2 implementation: download stubs at lines 1142–1154, `_get_preconditions()` at lines 127–292, `_MCSL_WORKFLOW_GUIDE` at lines 383–484, `_verify_scenario` at lines 1388–1498
- `/Users/madan/Documents/Fed-Ex-automation/FedexDomainExpert/pipeline/smart_ac_verifier.py` lines 1449–1633 — full download_zip and download_file implementations (read in full)
- `mcsl-test-automation/support/pages/orders/orderSummaryPage.ts` — all DOC-01 through DOC-05 locators confirmed
- `mcsl-test-automation/support/pages/orders/orderGridPage.ts` — LABEL-02, LABEL-03, LABEL-04 flow locators confirmed
- `mcsl-test-automation/tests/orderSummary/labelGenerationFromSummary/labelGenerationAndFulfillment.spec.ts` — LABEL-01 end-to-end flow
- `mcsl-test-automation/tests/orderGrid/actionMenu/createReturnLabel.spec.ts` — LABEL-04 return label flow
- `mcsl-test-automation/tests/orderGrid/actionMenu/generateLabelFromActionsMenu.spec.ts` — LABEL-02 auto/actions menu flow
- `mcsl-test-automation/tests/specialServices/adultsignature.spec.ts` — PRE-04 signature
- `mcsl-test-automation/tests/specialServices/insurance.spec.ts` — PRE-06 insurance
- `mcsl-test-automation/tests/specialServices/dangerousgoods.spec.ts` — PRE-03 battery/dangerous goods
- `.planning/REQUIREMENTS.md` — canonical requirement text

### Secondary (MEDIUM confidence)
- FedexDomainExpert `_MCSL_WORKFLOW_GUIDE` sections for document strategies (lines 302–766) — patterns verified against MCSL POM but exact button text needs live app confirmation for DOC-02/DOC-03
- `pipeline/order_creator.py` — LABEL-05 dangerous products support (needs `use_dangerous_products=True` param verification)

### Tertiary (LOW confidence — needs live app verification)
- DOC-02 "Download Documents" button text and location in MCSL Order Summary
- DOC-03 "How To" modal existence in MCSL (confirmed in FedEx, uncertain in MCSL)
- PRE-05 HAL SideDock exact locators (confirmed flow from spec but exact CSS selectors not in POM files scanned)

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — identical to Phase 2; zipfile/tempfile/shutil are stdlib
- Label flows (LABEL-01 to 04): HIGH — confirmed from automation spec files
- Download handlers (DOC-02, DOC-03): HIGH for pattern; MEDIUM for exact button text in MCSL
- Rate log (DOC-05): HIGH — exact locators from orderSummaryPage.ts
- Print Documents (DOC-04): HIGH — switch_tab + pluginhive confirmed
- Pre-requirements: HIGH for FedEx/UPS dry ice/alcohol/battery/signature; MEDIUM for HAL SideDock locators
- Test architecture: HIGH — same pytest + .venv from Phase 2

**Research date:** 2026-04-16
**Valid until:** 2026-05-16 (30 days — MCSL app UI relatively stable; locators may shift on major releases)
