---
name: mcsl-dashboard-tc-publisher
description: Use when working inside the MCSLDomainExpert project and the user wants QA test cases generated from a Trello card URL or card content, then published to the Trello card comment AND appended to the Ai sheet tab in Google Sheets. Uses the same pipeline as the dashboard: full Trello card data (name, desc, comments, labels, checklists, attachments) + RAG vectorstore + carrier research context + code context + feedback context → generate_test_cases() → write_test_cases_to_card() + append_to_sheet().
---

# MCSL Dashboard TC Publisher

This skill mirrors the dashboard's `🧪 Generate TC` tab exactly.

It is separate from `mcsl-ai-qa-testcase-prep`:
- `mcsl-ai-qa-testcase-prep` creates rich test cases for AI QA Agent / Chrome verification.
- `mcsl-dashboard-tc-publisher` uses the project pipeline to generate, post to Trello, and append to the Ai Google Sheet.

## First Reads

Before doing anything:

1. Read `/Users/madan/Documents/MCSLDomainExpert/AGENTS.md`.
2. Read `/Users/madan/Documents/MCSLDomainExpert/skills/mcsl-dashboard-tc-publisher/references/dashboard_tc_formats.md` when exact formats are needed.

## Execution Path

### Step 1 — Fetch full Trello card data

Use `pipeline/trello_client.py` to fetch:
- `card.name`
- `card.desc`
- `card.comments` (full list — all comments, not just latest)
- `card.labels`
- `card.checklists`
- `card.attachments`

Do not rely on browser-scraped content. Always use the project Trello client so the same data the dashboard sees is used.

If a Trello URL is provided, extract the card ID from the URL slug (e.g. `https://trello.com/c/CARD_ID/...` → `CARD_ID`).

Also extract:
- `release` — from the board/list name or card labels (e.g. `PROD MCSL 371A`, `PROD MCSL 1.0.371`)
- `card_url` — full Trello card URL for the sheet header row

### Step 2 — Generate test cases using the project pipeline

Run a Python script using `.venv/bin/python3` that calls:

```python
from pipeline.card_processor import generate_test_cases
from pipeline.trello_client import TrelloClient

trello = TrelloClient()
card = trello.get_card(card_id)  # full card object with name, desc, comments, labels

# This internally builds:
# - dev_comments_section  (from card.comments)
# - carrier_context       (from carrier_knowledge.carrier_research_context)
# - rag_context_section   (from rag.vectorstore.search — similar past TCs)
# - code_context_section  (from rag.code_indexer.search_code)
# - feedback_context_section (from prior QA feedback)
# - platform_context      (Shopify / WooCommerce / BigCommerce / Magento / PrestaShop)
# Then invokes TEST_CASE_PROMPT and reviews/rewrites using TEST_CASE_REVIEW_PROMPT

test_cases_markdown = generate_test_cases(card, ac_text=ac_text)
```

`ac_text` is the current approved AC draft if one exists in the conversation. If no AC draft, pass `None` and `generate_test_cases` will use `card.desc`.

This is the **same prompt, same context, same review loop** as the dashboard.

### Step 3 — Post Trello QA comment

```python
from pipeline.card_processor import write_test_cases_to_card

write_test_cases_to_card(
    card_id=card.id,
    test_cases=test_cases_markdown,
    trello=trello,
    release=release,
    card_name=card.name,
)
```

This formats the comment using `format_qa_comment()` which groups all Positive / Negative / Edge cases with BDD scenario blocks and posts to the card.

Show the user the formatted comment text before posting (one-line confirmation). Then post.

### Step 4 — Append positive cases to release tab

**Derive the tab name from the release label** — strip the `PROD ` prefix if present:

```python
# e.g. "PROD MCSL 371A" → "MCSL 371A"
#      "PROD MCSL 1.0.371" → "MCSL 1.0.371"
#      "MCSL 379" → "MCSL 379"
tab_name = release.replace("PROD ", "").strip()
```

**Create the tab if it does not exist** — this writes the 9-column header row:

```python
from pipeline.sheets_writer import create_new_tab

create_new_tab(tab_name)
# Creates: SI No | Epic | Scenario | Description | Comments | Priority | Details | Pass/Fail | Release
```

**Append TCs to the release tab:**

```python
from pipeline.sheets_writer import append_to_sheet

result = append_to_sheet(
    card_name=card.name,
    test_cases_markdown=test_cases_markdown,
    epic=card.name,
    tab_name=tab_name,
    release=release,
    card_url=card_url,
)
```

`append_to_sheet` detects this is a non-Ai tab and uses `_build_default_row` which outputs the 9-column format:
`SI No | Epic | Scenario | Description (BDD steps) | Comments (Preconditions) | Priority | Details | Pass/Fail | Release`

It also inserts a coloured card-header row before the TCs linking to the Trello card. Positive-only rows are appended (`positive_only=True` inside `append_to_sheet`).

### Step 5 — Sync to RAG

After successful publish, upsert the card artifacts into `mcsl_knowledge` so future TC generation benefits from this card's knowledge:

```python
from pipeline.rag_updater import update_rag_from_card

update_rag_from_card(
    card_id=card.id,
    card_name=card.name,
    description=card.desc,
    acceptance_criteria=ac_text or card.desc,
    test_cases=test_cases_markdown,
    release=release,
)
```

## What the Sheet Gets

- **Tab:** Release name with `PROD ` stripped — e.g. `MCSL 371A`, `MCSL 1.0.371`, `MCSL 379`
- **Tab created automatically** if it does not exist (9-column header: SI No, Epic, Scenario, Description, Comments, Priority, Details, Pass/Fail, Release)
- **Rows:** Positive cases only (filtered by `append_to_sheet`)
- **Format:** 9-column default layout (not the 12-column Ai layout)
- **Card header row:** coloured row before TCs linking back to the Trello card
- **Never use the `Ai` tab** unless the user explicitly asks for legacy Ai tab output

## What the Trello Comment Gets

All Positive, Negative, and Edge cases as BDD scenario blocks grouped by type — formatted by `format_qa_comment()`.

## Platform Scope

Before generating, detect the customer/test platform from card title, labels, description, comments, and linked tickets:

- Shopify (default when not explicit)
- WooCommerce
- BigCommerce
- Magento
- PrestaShop
- Shared MCSL

The detected platform flows into `generate_test_cases()` via `platform_scope_brief()` — no manual platform injection needed.

## Supported Requests

Use this skill when the user provides a Trello card URL/ID and asks for:

- "generate TCs for this card"
- "write test cases and add to Trello"
- "add TCs to sheet"
- "publish TCs" / "same as dashboard"
- "generate and publish"

## Fallback — No Pipeline Available

If `.venv` or project pipeline is unavailable:

1. Ask the user to paste the full card content (desc + comments).
2. Generate TCs manually using the `TEST_CASE_PROMPT` rules below.
3. Produce paste-ready Trello comment and CSV output instead of live publish.

### Manual TC Format (fallback only)

```markdown
### TC-{n}: <short title>
**Type:** Positive | Negative | Edge Case
**Priority:** High | Medium | Low
**Preconditions:** <clear setup>

**Steps:**
Given <state>
When <action>
And <additional action>
Then <expected result>
And <additional expected result>
```

Rules (same as `TEST_CASE_PROMPT` in `card_processor.py`):
- At least 4 test cases.
- At least 2 Positive, 1 Negative, 1 Edge when the feature supports it.
- Cover every AC item at least once.
- No mobile / responsive / unit-test / mock / backend-only cases.
- Steps must be Given/When/And/Then — no numbered or bulleted steps.
- Reference real MCSL field names, request log fields, and carrier API nodes when known.
- Use Trello comments for rollout notes and toggle details only when they don't conflict with the current AC scope.

### Manual CSV Output (fallback only)

Positive cases only → tab named after the release (e.g. `MCSL 371A`):

```csv
SI No,Epic,Scenario,Description,Comments,Priority,Details,Pass/Fail,Release
```

This matches the 9-column format of `create_new_tab` and `_build_default_row`. Start `SI No` from the tab's last existing row + 1 — check with gspread before generating.

## Final Response

After each step, confirm to the user:
- ✓ TCs generated — N positive, N negative, N edge
- ✓ Trello comment posted to `card.name`
- ✓ N rows added to AI sheet tab (Sl no X–Y)
- ✓ RAG synced for `card.id`
