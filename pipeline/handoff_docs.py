from __future__ import annotations

import datetime as _dt
import io
import logging
import os
import re
from dataclasses import dataclass, field

import config
from pipeline.carrier_knowledge import detect_carrier_scope
from pipeline.card_processor import detect_platform_scope

logger = logging.getLogger(__name__)

# Per-request LLM timeout (seconds). Without this a stalled socket hangs the
# generation indefinitely. Matches the convention in card_processor.py.
_LLM_TIMEOUT_SECONDS = int(os.environ.get("MCSL_LLM_TIMEOUT_SECONDS", "90"))

# Max output tokens per doc generation. Detailed cards (multi-part walkthroughs)
# overflow the old 2400 cap and get truncated mid-section.
_LLM_MAX_TOKENS = int(os.environ.get("MCSL_DOC_MAX_TOKENS", "6000"))


STANDARD_MCSL_NAVIGATION: tuple[str, ...] = (
    "Open Shopify Admin > Apps > PH Multi Carrier Shipping Label App.",
    "Use ORDERS for order summary, label generation, request logs, tracking, and report-related checks.",
    "Use the hamburger menu for Products, Carriers, General Settings, packaging, and automation-rule setup.",
    "Use Shopify Admin Orders or Products for cross-checking sync, fulfillment, tracking, and product source data.",
)

PLATFORM_NAVIGATION: dict[str, tuple[str, ...]] = {
    "Shopify": (
        "Shopify Admin > Apps > PH Multi Carrier Shipping Label App",
        "Shopify Admin Orders or Products for cross-checking Shopify source data",
    ),
    "WooCommerce": (
        "WordPress Admin / WooCommerce store admin > PluginHive MCSL app/settings",
        "WooCommerce Orders or Products for cross-checking WooCommerce source data",
    ),
    "BigCommerce": (
        "BigCommerce admin/storefront checkout and the BigCommerce MCSL app/settings",
        "BigCommerce Orders, Products, checkout, or rate automation logs for cross-checking source data",
    ),
    "Magento": (
        "Magento admin > PluginHive Multi Carrier Shipping Label extension/settings",
        "Magento Orders, Products, checkout, or shipping logs for cross-checking source data",
    ),
    "PrestaShop": (
        "PrestaShop admin > PluginHive Multi Carrier Shipping Label module/settings",
        "PrestaShop Orders, Products, checkout, or shipping logs for cross-checking source data",
    ),
}

REQUEST_LOG_CALLOUT_RE = re.compile(
    r"^[-*]\s*(?:Request node|Request nodes|Request/response nodes|Request/log fields) to verify:",
    flags=re.IGNORECASE,
)


def is_request_log_callout(markdown_line: str) -> bool:
    """Return true when a markdown bullet should render as a request/log callout."""
    return bool(REQUEST_LOG_CALLOUT_RE.match((markdown_line or "").strip()))


@dataclass
class HandoffDocContext:
    card_id: str
    card_name: str
    card_url: str = ""
    release_name: str = ""
    approved_at: str = ""
    card_description: str = ""
    card_comments: list[str] = field(default_factory=list)
    card_checklists: list[dict] = field(default_factory=list)
    acceptance_criteria: str = ""
    test_cases: str = ""
    ai_qa_summary: str = ""
    ai_qa_evidence: str = ""
    signoff_summary: str = ""
    developer_names: list[str] = field(default_factory=list)
    tester_names: list[str] = field(default_factory=list)
    toggle_names: list[str] = field(default_factory=list)
    carrier_names: list[str] = field(default_factory=list)
    platform_names: list[str] = field(default_factory=list)
    likely_navigation: list[str] = field(default_factory=list)
    generated_on: str = field(default_factory=lambda: _dt.datetime.now().strftime("%Y-%m-%d %H:%M"))


def split_card_members(members: list[dict]) -> tuple[list[str], list[str]]:
    try:
        from pipeline.bug_reporter import is_qa_name
    except Exception:
        def is_qa_name(_: str) -> bool:
            return False

    testers: list[str] = []
    developers: list[str] = []
    for member in members or []:
        full_name = (member.get("fullName") or member.get("username") or "").strip()
        if not full_name:
            continue
        if is_qa_name(full_name):
            if full_name not in testers:
                testers.append(full_name)
        elif full_name not in developers:
            developers.append(full_name)
    return developers, testers


def detect_toggles(*texts: str) -> list[str]:
    patterns = [
        r"[`\"“”']?([A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)+)[`\"“”']?\s*:\s*(?:true|false)",
        r"\btoggle\b\s*[:=-]\s*([A-Za-z0-9_. -]+)",
        r"\bfeature flag\b\s*[:=-]\s*([A-Za-z0-9_. -]+)",
        r"\brollout\b\s*[:=-]\s*([A-Za-z0-9_. -]+)",
    ]
    found: list[str] = []
    for text in texts:
        for pattern in patterns:
            for match in re.findall(pattern, text or "", flags=re.IGNORECASE):
                value = re.sub(r"\s+", " ", match).strip(" -:")
                if value and value not in found:
                    found.append(value)
    return found


def detect_carriers(*texts: str) -> list[str]:
    return [profile.canonical_name for profile in detect_carrier_scope(*texts).carriers]


def infer_navigation(*texts: str) -> list[str]:
    combined = " ".join(texts).lower()
    nav: list[str] = []
    platforms = detect_platform_scope(*texts)
    for platform in platforms:
        for item in PLATFORM_NAVIGATION.get(platform, ()):
            if item not in nav:
                nav.append(item)
    if any(token in combined for token in ("order", "label generated", "fulfill", "mark as shipped")):
        nav.append("ORDERS tab -> open order -> Prepare Shipment / Generate Label")
    if any(token in combined for token in ("label", "print documents", "tracking", "manifest")) and "ORDERS tab -> open order -> Prepare Shipment / Generate Label" not in nav:
        nav.append("LABELS or order summary flow inside the MCSL app")
    if any(token in combined for token in ("pickup", "schedule pickup")):
        nav.append("PICKUP tab")
    if any(token in combined for token in ("product", "weight", "dimension", "customs value", "dry ice", "alcohol", "battery", "signature")):
        nav.append("Hamburger menu -> Products")
    if any(token in combined for token in ("carrier", "credentials", "production key", "account details")):
        nav.append("Hamburger menu -> Carriers")
    if any(token in combined for token in ("packaging", "box", "packing method")):
        nav.append("Hamburger menu -> Settings / Packaging")
    if any(token in combined for token in ("rate", "checkout", "automation rule", "service selection", "request log")):
        nav.append("Hamburger menu -> Settings / Shipping Rates / Automation or Request Log")
    if "Shopify" in platforms or any(token in combined for token in ("shopify", "product_id", "variant_id", "tracking number")):
        nav.append("Shopify Admin -> Orders or Products for post-verification")
    if not nav:
        nav.append("Shopify Admin > Apps > PH Multi Carrier Shipping Label App")
    return nav


def _checklists_to_text(checklists: list[dict] | None) -> str:
    lines: list[str] = []
    for checklist in checklists or []:
        if not isinstance(checklist, dict):
            continue
        name = (checklist.get("name") or "").strip()
        if name:
            lines.append(name)
        for item in checklist.get("items", []) or []:
            item_name = (item.get("name") or "").strip()
            if item_name:
                state = (item.get("state") or "").strip()
                lines.append(f"- {item_name}" + (f" [{state}]" if state else ""))
    return "\n".join(lines)


def build_handoff_context(
    *,
    card,
    release_name: str = "",
    approved_at: str = "",
    acceptance_criteria: str = "",
    test_cases: str = "",
    ai_qa_summary: str = "",
    ai_qa_evidence: str = "",
    signoff_summary: str = "",
    members: list[dict] | None = None,
) -> HandoffDocContext:
    devs, testers = split_card_members(members or [])
    desc = getattr(card, "desc", "") or ""
    comments = [c for c in (getattr(card, "comments", []) or []) if c]
    checklists = getattr(card, "checklists", []) or []
    comments_text = "\n".join(comments)
    checklist_text = _checklists_to_text(checklists)
    evidence_text = "\n".join([comments_text, checklist_text]).strip()
    toggles = detect_toggles(desc, getattr(card, "name", "") or "", acceptance_criteria, test_cases, evidence_text)
    carriers = detect_carriers(
        desc,
        getattr(card, "name", "") or "",
        acceptance_criteria,
        test_cases,
        ai_qa_summary,
        ai_qa_evidence,
        evidence_text,
    )
    platforms = detect_platform_scope(
        desc,
        getattr(card, "name", "") or "",
        acceptance_criteria,
        test_cases,
        ai_qa_summary,
        ai_qa_evidence,
        evidence_text,
    )
    navigation = infer_navigation(
        desc,
        getattr(card, "name", "") or "",
        acceptance_criteria,
        test_cases,
        ai_qa_summary,
        ai_qa_evidence,
        evidence_text,
    )
    return HandoffDocContext(
        card_id=getattr(card, "id", ""),
        card_name=getattr(card, "name", ""),
        card_url=getattr(card, "url", "") or "",
        release_name=release_name,
        approved_at=approved_at,
        card_description=desc,
        card_comments=comments,
        card_checklists=checklists,
        acceptance_criteria=acceptance_criteria or desc,
        test_cases=test_cases,
        ai_qa_summary=ai_qa_summary,
        ai_qa_evidence=ai_qa_evidence,
        signoff_summary=signoff_summary,
        developer_names=devs,
        tester_names=testers,
        toggle_names=toggles,
        carrier_names=carriers,
        platform_names=platforms,
        likely_navigation=navigation,
    )


_SUPPORT_PROMPT = """You are writing a support-ready story-card guide for PluginHive MCSL across Shopify, WooCommerce, BigCommerce, Magento, and PrestaShop.

This document is used internally by support, QA, account managers, and escalation owners. \
It should match the MCSL 378 Support Guide style: practical, support-facing, card-specific, \
and written so a support engineer can explain, verify, and escalate the change without reading code.

Use this EXACT section order — no other sections:

1. `# Support Guide: <Story ID or concise feature name>`
2. `<Original card title>` as a short subtitle line below the title when available.
3. `## Brief Description` — 1 crisp paragraph explaining what changed, why it matters, \
   and the affected carrier/product area. Keep it support-facing, not marketing-heavy.
4. `## Toggles & Prerequisites` — markdown table with columns \
   `| Toggle / config note | What support should confirm |`. \
   Include detected toggles, release/store prerequisites, carrier account/service prerequisites, \
   detected customer/test platform, and "None detected" only if nothing is known.
5. `## Step-by-Step Support Walkthrough` — numbered support steps to verify or explain the feature. \
   Include the exact app area/path inside the relevant step, such as ORDERS, hamburger menu > Carriers, \
   hamburger menu > Products, Reports, Shopify Admin Orders/Products, WooCommerce Orders/Products, \
   BigCommerce Orders/Products/checkout/rate automation, Magento Orders/Products, PrestaShop Orders/Products, \
   checkout, or request logs. \
   Use the customer/test platform from the card/ticket. Do not default to Shopify Admin when WooCommerce, \
   BigCommerce, Magento, or PrestaShop is detected; if the implementation is shared, say support is validating it on the reported platform. \
   Do not add a separate generic `Where to Find This in MCSL` section.
   If the card requires payload, carrier request, response, or diagnostic log verification, add a highlighted \
   bullet immediately after the relevant step using one of these exact labels: \
   `- Request node to verify: ...`, `- Request nodes to verify: ...`, \
   `- Request/response nodes to verify: ...`, or `- Request/log fields to verify: ...`.
6. `## Expected Behaviour` — markdown table with columns \
   `| What support should observe | How to confirm |`. \
   Include UI result, request/log result, document/report result, or sync result when supported by context.
   Include exact request/log node names when the card or QA evidence requires payload verification.

The document ends after `Expected Behaviour`.

Formatting rules:
- Use markdown tables with pipe syntax — header row, separator row (|---|---|), then data rows.
- Never use giant paragraphs — prefer bullets, numbered lists, and tables.
- Mention MCSL navigation paths naturally: ORDERS tab, hamburger menu > Products, hamburger menu > Carriers, etc.
- Call out carrier names explicitly when the feature is carrier-specific.
- DO NOT add: Merchant-Safe Explanation, Common Questions & Troubleshooting, Support Escalation Packet, \
  The Problem, The Solution, Key Benefits, User Story, Test Scenarios, Acceptance Criteria Checklist, \
  AI Code Analysis, Rollout Notes, or References.
- Use facts from the context only. If a detail is missing, phrase it as "Confirm from live store/card context" rather than inventing.

CONTEXT:
{context}
"""


_BUSINESS_PROMPT = """You are writing a customer-facing, marketing-style Business Brief for a new feature in PluginHive MCSL \
(Multi-Carrier Shipping Labels) across Shopify, WooCommerce, BigCommerce, Magento, and PrestaShop.

Your audience is merchants on the platform identified by the card/ticket, e-commerce store owners, account managers, and product marketing — \
NOT engineers or QA teams. Write as if this will appear on a product update page or be shared with a customer \
success manager explaining the release to a merchant.

Tone: Friendly, benefit-first, real-world focused. No jargon, no API field names, no enum values, no code identifiers.

Use this exact section order:
1. `# What's New: <feature name in plain English>`
2. `## Brief Description`
3. `## What You Can Do Now`
4. `## Real-World Scenarios`
5. `## Who Benefits`
6. `## How to Get Started`
7. `## What Stays the Same`

Section guidelines:
- **Brief Description**: Tell the story from a merchant's perspective. What frustration or blocker did they hit? \
  Use a realistic merchant scenario (e.g. "If your warehouse uses thermal label printers..."). 2-4 sentences max.
- **What You Can Do Now**: Plain-English bullets describing the new capability. No technical terms. \
  Translate any label format names (e.g. STOCK_4X6 → "4×6 inch thermal label") into human-readable equivalents.
- **Real-World Scenarios**: Write 2-3 short named scenarios (### Scenario 1: ...) showing a real merchant \
  benefiting from this feature. Use concrete details: store type, shipment type, what they do, what improves.
- **Who Benefits**: Short bullets — which merchant types, business sizes, or shipping patterns benefit most.
- **How to Get Started**: Simple numbered steps in plain English. Use app navigation in natural language \
  (e.g. "Go to Settings → Carriers → FedEx" not raw path codes). No more than 5 steps.
- **What Stays the Same**: Reassure merchants what hasn't changed. Calm any migration concerns.

Rules:
- Never mention API fields, JSON payloads, enum values, or code identifiers
- Never mention internal QA terms (acceptance criteria, test cases, fallback, regression)
- Use merchant-friendly language throughout: "you can now", "your labels", "your store"
- If the feature is carrier-specific, say the carrier name naturally ("FedEx" not "FedEx REST endpoint")
- If the card/ticket is WooCommerce, BigCommerce, Magento, or PrestaShop, do not call the audience Shopify merchants or give Shopify Admin setup steps.
- If the implementation is shared but the customer card is platform-specific, describe the benefit for that reported platform and avoid unsupported cross-platform promises.
- Keep the whole document skimmable and upbeat

Use facts from the context only. Do not invent features or scenarios not supported by the context.

CONTEXT:
{context}
"""


def _context_text(ctx: HandoffDocContext) -> str:
    checklist_text = _checklists_to_text(ctx.card_checklists)
    parts = [
        f"Card: {ctx.card_name}",
        f"Card URL: {ctx.card_url or '(none)'}",
        f"Release: {ctx.release_name or '(unknown)'}",
        f"Approved at: {ctx.approved_at or '(unknown)'}",
        f"Developed by: {', '.join(ctx.developer_names) if ctx.developer_names else 'Unknown'}",
        f"Tested by: {', '.join(ctx.tester_names) if ctx.tester_names else 'QA Team'}",
        f"Toggles: {', '.join(ctx.toggle_names) if ctx.toggle_names else 'None detected'}",
        f"Carriers: {', '.join(ctx.carrier_names) if ctx.carrier_names else 'Carrier-neutral or not explicitly stated'}",
        f"Customer/test platform: {', '.join(ctx.platform_names) if ctx.platform_names else 'Shopify'}",
        "Likely MCSL navigation:",
        "\n".join(f"- {item}" for item in (ctx.likely_navigation or [])),
        "",
        "CARD DESCRIPTION / CURRENT AC:",
        (ctx.acceptance_criteria or ctx.card_description or "").strip()[:7000],
        "",
        "LIVE TRELLO COMMENTS / QA NOTES:",
        ("\n\n".join(ctx.card_comments or []) or "None").strip()[:7000],
        "",
        "LIVE TRELLO CHECKLISTS:",
        (checklist_text or "None").strip()[:3000],
        "",
        "TEST CASES:",
        (ctx.test_cases or "").strip()[:6000],
        "",
        "AI QA SUMMARY:",
        (ctx.ai_qa_summary or "").strip()[:3000],
        "",
        "AI QA EVIDENCE:",
        (ctx.ai_qa_evidence or "").strip()[:5000],
        "",
        "SIGN-OFF / NOTES:",
        (ctx.signoff_summary or "").strip()[:2000],
    ]
    return "\n".join(parts).strip()


def _invoke_doc_prompt(prompt: str, ctx: HandoffDocContext) -> str:
    if not config.ANTHROPIC_API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY not set")
    from langchain_anthropic import ChatAnthropic
    from langchain_core.messages import HumanMessage

    claude = ChatAnthropic(
        model=config.CLAUDE_SONNET_MODEL,
        api_key=config.ANTHROPIC_API_KEY,
        temperature=0.1,
        max_tokens=_LLM_MAX_TOKENS,
        default_request_timeout=_LLM_TIMEOUT_SECONDS,
    )
    resp = claude.invoke([HumanMessage(content=prompt.format(context=_context_text(ctx)))])
    content = resp.content if isinstance(resp.content, str) else str(resp.content)
    return content.strip()


def _standard_navigation_markdown(extra_navigation: list[str] | None = None) -> str:
    # The release support guide uses one fixed app-orientation block. Keep
    # carrier/card-specific paths in the walkthrough so this section stays
    # predictable across all cards.
    return "\n".join(f"- {item}" for item in STANDARD_MCSL_NAVIGATION)


def _enforce_standard_navigation(markdown_text: str, ctx: HandoffDocContext) -> str:
    """Remove the old generic MCSL location block from support guides.

    Card-specific navigation belongs in the walkthrough, where support sees it
    next to the action they need to perform.
    """
    if not markdown_text or "## Where to Find This in MCSL" not in markdown_text:
        return markdown_text

    pattern = re.compile(
        r"(## Where to Find This in MCSL\s*\n)(.*?)(?=\n## (?:Step-by-Step Support Walkthrough|Expected Behaviour)\b|\Z)",
        flags=re.DOTALL,
    )
    sanitized, count = pattern.subn("", markdown_text, count=1)
    if not count:
        logger.warning("Could not remove generic navigation block for %s", ctx.card_name)
    return sanitized


def _enforce_toggle_scope(markdown_text: str, ctx: HandoffDocContext) -> str:
    if ctx.toggle_names:
        return markdown_text

    sanitized = markdown_text
    sanitized = re.sub(
        r"^\|\s*(?:None detected|No feature toggle(?: found in card notes)?\.?)\s*\|\s*Use live MCSL store/account state as the source of truth\.?\s*\|\s*$",
        "| No toggle | No feature toggle is required for this card; validate release deployment, carrier/account setup, and card-specific prerequisites only. |",
        sanitized,
        flags=re.MULTILINE,
    )
    sanitized = re.sub(
        r"^\s*[-*]\s*Use live MCSL store/account state as the source of truth when a toggle is mentioned\.?\s*$\n?",
        "",
        sanitized,
        flags=re.MULTILINE,
    )
    sanitized = re.sub(
        r"^\s*[-*]\s*Exact toggle/config value if (?:the feature is )?gated\.?\s*$\n?",
        "",
        sanitized,
        flags=re.MULTILINE,
    )
    sanitized = sanitized.replace(
        "first confirm release, store/account, carrier account, and toggle/config state",
        "first confirm release, store/account, carrier account, and card-specific prerequisites",
    )
    return sanitized


def _enforce_support_doc_guardrails(markdown_text: str, ctx: HandoffDocContext) -> str:
    return _enforce_toggle_scope(_enforce_standard_navigation(markdown_text, ctx), ctx)


def _fallback_support_doc(ctx: HandoffDocContext) -> str:
    carriers = ", ".join(ctx.carrier_names) if ctx.carrier_names else "carrier-neutral"
    platform_scope = ", ".join(ctx.platform_names) if ctx.platform_names else "Shopify"
    nav_steps = ctx.likely_navigation or ["MCSL embedded app main flow"]
    story_label = _story_id(ctx) or ctx.card_name
    if ctx.toggle_names:
        toggle_rows = "\n".join(
            f"| {toggle} | Confirm the exact value is enabled for the target store/account before testing. |"
            for toggle in ctx.toggle_names
        )
    else:
        toggle_rows = "| No toggle | No feature toggle is required for this card; validate release deployment, carrier/account setup, and card-specific prerequisites only. |"
    return f"""## Support Guide: {story_label}

{ctx.card_name}

## Brief Description
This update covers the approved card scope for {carriers} behaviour in MCSL. Support should verify it on the customer/test platform from the card: {platform_scope}. Use the card details, approved AC, test evidence, and live store state to explain or verify the visible merchant outcome.

## Toggles & Prerequisites

| Toggle / config note | What support should confirm |
|---|---|
{toggle_rows}
| Release | Confirm the merchant store/account is on {ctx.release_name or 'the target release'} before promising the behavior. |
| Platform | {platform_scope}. If the implementation is shared across MCSL platforms, validate on the customer-reported platform unless the card asks for broader coverage. |
| Carrier/account | Confirm the exact carrier account, service, and order data before testing carrier-specific behavior. |

## Step-by-Step Support Walkthrough

1. Confirm the merchant store, platform, release, carrier account, and order/product/report context.
2. Open the relevant MCSL area: {nav_steps[0]}.
3. Reproduce the workflow described in the approved card scope.
4. Check the visible UI result and any request/log, document, tracking, sync, or report evidence.

## Expected Behaviour

| What support should observe | How to confirm |
|---|---|
| The feature behaves as described in the approved card scope. | Compare the live UI result with the approved AC and AI QA evidence. |
| Existing related MCSL workflows continue to work. | Run the adjacent order/product/carrier flow noted in the card context. |
"""


def _fallback_business_doc(ctx: HandoffDocContext) -> str:
    carriers = ", ".join(ctx.carrier_names) if ctx.carrier_names else "all supported carriers"
    platform_merchants = ", ".join(ctx.platform_names) + " merchants" if ctx.platform_names else "MCSL merchants"
    return f"""# What's New: {ctx.card_name}

## Brief Description
{platform_merchants} using {carriers} through the MCSL app previously encountered a limitation in this area. \
This update removes that blocker so your store can ship more smoothly without workarounds.

## What You Can Do Now
- The new capability is now available directly inside the MCSL app — no additional setup required
- {carriers} users benefit immediately upon updating to this release
- Existing configurations and workflows continue to work exactly as before

## Real-World Scenarios

### Scenario 1: Day-to-day shipping
A merchant shipping orders through {carriers} can now complete their label generation flow \
without hitting the previous limitation, saving time on every shipment.

### Scenario 2: High-volume store
For stores processing many orders per day, this update eliminates a manual workaround step, \
reducing the chance of errors and speeding up fulfilment.

## Who Benefits
- {platform_merchants} using {carriers} for shipping
- Stores that previously hit errors or limitations in this label flow
- Merchants looking for a smoother, more reliable shipping experience

## How to Get Started
1. Open the MCSL app/settings from the platform used by this store
2. Navigate to the relevant settings area for your carrier
3. Configure the new option to match your shipping setup
4. Generate a label from the ORDERS tab to verify everything works
5. Contact PluginHive support if you need help getting set up

## What Stays the Same
- All your existing carrier settings and label configurations are untouched
- Other carriers and shipping flows work exactly as before
- No migration or re-configuration is needed for current setups
"""


def generate_support_guide(ctx: HandoffDocContext) -> str:
    try:
        return _enforce_support_doc_guardrails(_invoke_doc_prompt(_SUPPORT_PROMPT, ctx), ctx)
    except Exception as exc:
        logger.warning("Support guide generation fell back to template: %s", exc)
        return _enforce_support_doc_guardrails(_fallback_support_doc(ctx), ctx)


def generate_business_brief(ctx: HandoffDocContext) -> str:
    try:
        return _invoke_doc_prompt(_BUSINESS_PROMPT, ctx)
    except Exception as exc:
        logger.warning("Business brief generation fell back to template: %s", exc)
        return _fallback_business_doc(ctx)


def _doc_title(ctx: HandoffDocContext) -> str:
    story_id_match = re.search(r"\b([A-Z]{1,4}-\d{1,5})\b", ctx.card_name or "")
    return story_id_match.group(1) if story_id_match else (ctx.card_name or ctx.card_id or "Card")


def _demote_markdown(markdown_text: str) -> str:
    """Nest a single-card document under a release-level package heading."""
    lines: list[str] = []
    for raw in (markdown_text or "").splitlines():
        line = raw.rstrip()
        if line.startswith("### "):
            lines.append("#### " + line[4:].strip())
        elif line.startswith("## "):
            lines.append("### " + line[3:].strip())
        elif line.startswith("# "):
            lines.append("## " + line[2:].strip())
        else:
            lines.append(line)
    return "\n".join(lines).strip()


def _story_id(ctx: HandoffDocContext) -> str:
    """Story/card number only, for the index page `Story ID` column."""
    name = ctx.card_name or ""
    story_id_match = re.search(r"\b([A-Z]{1,4}-\d{1,5})\b", name)
    if story_id_match:
        return story_id_match.group(1)
    leading_number = re.match(r"\s*#?(\d{1,6})\b", name)
    if leading_number:
        return leading_number.group(1)
    return ""


def _story_title(ctx: HandoffDocContext) -> str:
    """Card title with any leading story id stripped, for the `Story Title` column."""
    title = (ctx.card_name or "").strip()
    story_id = _story_id(ctx)
    if story_id and title.startswith(story_id):
        title = title[len(story_id):].lstrip(" -–—:#")
    return title or "(untitled card)"


def _table_cell(value: str) -> str:
    return (value or "").replace("|", "\\|").replace("\n", " ").strip()


def _release_summary_table(contexts: list[HandoffDocContext]) -> str:
    rows = [
        "| Story ID | Story Title | Toggle Name |",
        "|---|---|---|",
    ]
    for ctx in contexts:
        toggles = ", ".join(ctx.toggle_names) if ctx.toggle_names else "None"
        rows.append(
            f"| {_table_cell(_story_id(ctx)) or '-'} | {_table_cell(_story_title(ctx))} | {_table_cell(toggles)} |"
        )
    return "\n".join(rows)


def _card_section_heading(ctx: HandoffDocContext) -> str:
    """`<Story ID> - <Story Title>` heading, without repeating the id inside the title."""
    story_id = _story_id(ctx)
    story_title = _story_title(ctx)
    return f"{story_id} - {story_title}" if story_id else story_title


def generate_combined_support_guide(contexts: list[HandoffDocContext], release_name: str = "") -> str:
    """Generate one release-level Support Guide containing all selected cards."""
    contexts = [ctx for ctx in contexts if ctx]
    release = release_name or (contexts[0].release_name if contexts else "") or "MCSL Release"
    parts = [
        f"# {release} Support Guide",
        "",
        "## Included Story Cards",
        _release_summary_table(contexts),
    ]
    for ctx in contexts:
        parts.extend([
            "",
            f"## {_card_section_heading(ctx)}",
            _demote_markdown(generate_support_guide(ctx)),
        ])
    return "\n".join(part for part in parts if part is not None).strip()


def generate_combined_business_brief(contexts: list[HandoffDocContext], release_name: str = "") -> str:
    """Generate one release-level Business Brief containing all selected cards."""
    contexts = [ctx for ctx in contexts if ctx]
    release = release_name or (contexts[0].release_name if contexts else "") or "MCSL Release"
    carriers = sorted({carrier for ctx in contexts for carrier in ctx.carrier_names})
    carrier_scope = ", ".join(carriers) if carriers else "supported shipping workflows"
    platforms = sorted({platform for ctx in contexts for platform in ctx.platform_names})
    platform_scope = ", ".join(platforms) if platforms else "the platform(s) named by each card"
    parts = [
        f"# What's New: {release}",
        "",
        "## Release Overview",
        f"This release includes {len(contexts)} approved update(s) for PluginHive MCSL across {platform_scope}, covering {carrier_scope}.",
        "",
        "## Included Updates",
        _release_summary_table(contexts),
    ]
    for ctx in contexts:
        parts.extend([
            "",
            f"## {_card_section_heading(ctx)}",
            _demote_markdown(generate_business_brief(ctx)),
        ])
    parts.extend([
        "",
        "## Availability",
        "These updates are available once the merchant store is on the target MCSL release and any listed prerequisite or toggle is confirmed.",
    ])
    return "\n".join(part for part in parts if part is not None).strip()


def _register_fonts() -> tuple[str, str]:
    """Register Arial + Georgia TTF fonts. Returns (sans_family, serif_family)."""
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.pdfbase.pdfmetrics import registerFontFamily

        _SF = "/System/Library/Fonts/Supplemental/"
        pdfmetrics.registerFont(TTFont("Arial",           _SF + "Arial.ttf"))
        pdfmetrics.registerFont(TTFont("Arial-Bold",      _SF + "Arial Bold.ttf"))
        pdfmetrics.registerFont(TTFont("Arial-Italic",    _SF + "Arial Italic.ttf"))
        pdfmetrics.registerFont(TTFont("Arial-BoldItalic",_SF + "Arial Bold Italic.ttf"))
        registerFontFamily("Arial", normal="Arial", bold="Arial-Bold",
                           italic="Arial-Italic", boldItalic="Arial-BoldItalic")

        pdfmetrics.registerFont(TTFont("Georgia",           _SF + "Georgia.ttf"))
        pdfmetrics.registerFont(TTFont("Georgia-Bold",      _SF + "Georgia Bold.ttf"))
        pdfmetrics.registerFont(TTFont("Georgia-Italic",    _SF + "Georgia Italic.ttf"))
        pdfmetrics.registerFont(TTFont("Georgia-BoldItalic",_SF + "Georgia Bold Italic.ttf"))
        registerFontFamily("Georgia", normal="Georgia", bold="Georgia-Bold",
                           italic="Georgia-Italic", boldItalic="Georgia-BoldItalic")
        return "Arial", "Georgia"
    except Exception:
        return "Helvetica", "Times-Roman"


def _md_to_rl(text: str, sans: str = "Arial") -> str:
    """Convert basic markdown inline formatting to ReportLab XML tags."""
    # Markdown links [label](url) → clickable ReportLab anchors. Do this first so the
    # label/url (which never contain markdown emphasis) survive the asterisk handling.
    def _link(m):
        label, url = m.group(1), m.group(2)
        href = url.replace('&', '&amp;')
        return f'<a href="{href}" color="#1155CC">{label}</a>'
    text = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', _link, text)
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<b><i>\1</i></b>', text)
    text = re.sub(r'\*\*(.+?)\*\*',     r'<b>\1</b>', text)
    text = re.sub(r'\*(.+?)\*',         r'<i>\1</i>', text)
    text = re.sub(r'`(.+?)`',           r'<font name="Courier" fontSize="9">\1</font>', text)
    # Strip any unmatched asterisks left over (e.g. from BDD steps bleeding in)
    text = re.sub(r'\*+', '', text)
    return text


def render_pdf_bytes(title: str, markdown_text: str) -> bytes:
    try:
        from reportlab.lib.colors import HexColor
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import (
            HRFlowable, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
        )
    except ModuleNotFoundError as exc:
        raise RuntimeError("PDF rendering requires reportlab to be installed") from exc

    SANS, SERIF = _register_fonts()

    PAGE_W, PAGE_H = A4
    LM = RM = 0.7 * inch
    CW = PAGE_W - LM - RM

    # ── Professional navy / gold colour palette ──────────────────────────────
    C_NAVY      = HexColor("#0d1b3e")   # header background — deep navy
    C_NAVY_MID  = HexColor("#162447")   # header body rows
    C_NAVY_META = HexColor("#1a2f5e")   # metadata strip
    C_GOLD      = HexColor("#c9922a")   # badge label & subtitle — warm gold
    C_BLUE      = HexColor("#1d4ed8")   # section headings — royal blue
    C_ACCENT    = HexColor("#2563eb")   # left accent bar
    C_WHITE     = HexColor("#ffffff")
    C_HDR_DESC  = HexColor("#cbd5e1")   # header description text
    C_META_TXT  = HexColor("#94a3b8")   # metadata strip text
    C_TEXT      = HexColor("#1e293b")   # body text — rich charcoal
    C_GRAY      = HexColor("#475569")   # secondary / quote text
    C_BORDER    = HexColor("#e2e8f0")   # dividers & table borders

    def _ps(name, **kw):
        return ParagraphStyle(name, **kw)

    # Fonts: Georgia for the big title impact, Arial everywhere else
    hdr_badge  = _ps("HBadge", fontName=f"{SANS}-Bold",   fontSize=8.5, leading=11, textColor=C_GOLD,
                               spaceAfter=2, tracking=60)
    hdr_title  = _ps("HTitle", fontName=f"{SERIF}-Bold",  fontSize=26,  leading=32, textColor=C_WHITE,
                               spaceAfter=4)
    hdr_sub    = _ps("HSub",   fontName=f"{SANS}-Bold",   fontSize=10.5,leading=14, textColor=C_GOLD,
                               spaceAfter=0)
    hdr_desc   = _ps("HDesc",  fontName=f"{SANS}-Italic", fontSize=10,  leading=14, textColor=C_HDR_DESC)
    hdr_meta   = _ps("HMeta",  fontName=SANS,             fontSize=8.5, leading=12, textColor=C_META_TXT)
    h2_style   = _ps("H2",     fontName=f"{SANS}-Bold",   fontSize=12,  leading=16, textColor=C_BLUE,
                               spaceBefore=12, spaceAfter=2)
    h3_style   = _ps("H3",     fontName=f"{SANS}-BoldItalic", fontSize=11, leading=14, textColor=C_BLUE,
                               spaceBefore=8, spaceAfter=3)
    body_style = _ps("Body",   fontName=SANS,             fontSize=10.5, leading=16, textColor=C_TEXT,
                               spaceAfter=6)
    bullet_sty = _ps("Bullet", fontName=SANS,             fontSize=10.5, leading=16, textColor=C_TEXT,
                               spaceAfter=4, leftIndent=16)
    num_style  = _ps("Num",    fontName=SANS,             fontSize=10.5, leading=16, textColor=C_TEXT,
                               spaceAfter=4, leftIndent=18)
    quote_sty  = _ps("Quote",  fontName=f"{SERIF}-Italic",fontSize=10.5, leading=16, textColor=C_GRAY,
                               leftIndent=20, rightIndent=20, spaceAfter=8,
                               borderPadding=(6, 10, 6, 14),
                               borderColor=C_GOLD, borderWidth=0)

    # ── H2 with left royal-blue accent bar ──────────────────────────────────
    def _h2_row(text: str):
        bar = Table([[""]], colWidths=[4], rowHeights=[18])
        bar.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), C_ACCENT),
            ("TOPPADDING",    (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("LEFTPADDING",   (0, 0), (-1, -1), 0),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ]))
        p = Paragraph(_md_to_rl(text), h2_style)
        row = Table([[bar, p]], colWidths=[6, CW - 6])
        row.setStyle(TableStyle([
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",    (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("LEFTPADDING",   (0, 0), (-1, -1), 0),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
            ("LEFTPADDING",   (0, 1), (0, 1), 9),
        ]))
        return [row, HRFlowable(width=CW, thickness=0.5, color=C_BORDER, spaceAfter=5)]

    # ── Badge / subtitle detection ───────────────────────────────────────────
    tl = title.lower()
    if any(w in tl for w in ["delay", "fix", "bug", "error", "performance", "slow", "issue"]):
        badge_txt = "PERFORMANCE FIX"
    elif any(w in tl for w in ["new", "feature", "add", "introduc", "launch"]):
        badge_txt = "NEW FEATURE"
    else:
        badge_txt = "UPDATE"

    clean_title = re.sub(r'\[#\d+\]', '', title).strip()
    clean_title = re.sub(r'From SL:\s*[A-Z]+-\d+\s*[—–-]\s*', '', clean_title).strip()

    carriers_found = re.findall(
        r'\b(Australia Post|eParcel|MyPost|FedEx|UPS|DHL|USPS|Stamps)\b', title, re.IGNORECASE,
    )
    platform_names = detect_platform_scope(title, markdown_text)
    subtitle = "PluginHive MCSL"
    if platform_names:
        subtitle = "PluginHive MCSL  ·  " + " / ".join(platform_names)
    if carriers_found:
        carrier_part = "  /  ".join(dict.fromkeys(c.title() for c in carriers_found))
        subtitle = f"{subtitle}  ·  {carrier_part}"

    # ── Parse markdown ───────────────────────────────────────────────────────
    lines = (markdown_text or "").splitlines()
    content_lines: list[str] = []
    desc_text = ""
    skip_h1 = True
    for line in lines:
        if skip_h1 and line.startswith("# "):
            skip_h1 = False
            continue
        content_lines.append(line)
        if not desc_text:
            s = line.strip()
            if s and not s.startswith("#") and not s.startswith("-"):
                desc_text = s[:170] + ("…" if len(s) > 170 else "")

    # ── Canvas footer ────────────────────────────────────────────────────────
    buf = io.BytesIO()

    def _draw_footer(canvas_obj, doc):
        canvas_obj.saveState()
        # Thin gold rule above footer
        canvas_obj.setStrokeColor(C_GOLD)
        canvas_obj.setLineWidth(0.5)
        canvas_obj.line(LM, 26, PAGE_W - RM, 26)
        canvas_obj.setFillColor(C_GRAY)
        canvas_obj.setFont(SANS, 7.5)
        canvas_obj.drawString(LM, 12, f"Generated {_dt.datetime.now().strftime('%B %d, %Y')}  ·  Confidential — PluginHive")
        canvas_obj.drawCentredString(PAGE_W / 2, 12, f"Page {doc.page}")
        canvas_obj.drawRightString(PAGE_W - RM, 12, "pluginhive.com")
        canvas_obj.restoreState()

    doc_obj = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=LM, rightMargin=RM,
        topMargin=0.4 * inch, bottomMargin=0.5 * inch,
        title=title,
    )

    story: list = []

    # ── Header panel (deep navy) ─────────────────────────────────────────────
    badge_p = Paragraph(badge_txt, hdr_badge)
    title_p = Paragraph(clean_title, hdr_title)
    sub_p   = Paragraph(subtitle, hdr_sub)
    desc_p  = Paragraph(_md_to_rl(desc_text), hdr_desc) if desc_text else Spacer(1, 2)

    hdr_tbl = Table([[badge_p], [title_p], [sub_p], [desc_p]], colWidths=[CW])
    hdr_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), C_NAVY_MID),
        ("BACKGROUND",    (0, 0), (0, 0),   C_NAVY),
        ("TOPPADDING",    (0, 0), (0, 0), 18),
        ("BOTTOMPADDING", (0, 0), (0, 0),  4),
        ("TOPPADDING",    (0, 1), (0, 1),  4),
        ("BOTTOMPADDING", (0, 1), (0, 1),  6),
        ("TOPPADDING",    (0, 2), (0, 2),  2),
        ("BOTTOMPADDING", (0, 2), (0, 2),  8),
        ("TOPPADDING",    (0, 3), (0, 3),  2),
        ("BOTTOMPADDING", (0, 3), (0, 3), 18),
        ("LEFTPADDING",   (0, 0), (-1, -1), 22),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 22),
    ]))

    # Gold top-border accent line on header
    hdr_border = Table([[""]], colWidths=[CW], rowHeights=[3])
    hdr_border.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), C_GOLD),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
    ]))

    meta_txt = (
        f"Generated {_dt.datetime.now().strftime('%B %Y')}     ·     "
        f"PluginHive QA Team"
    )
    meta_tbl = Table([[Paragraph(meta_txt, hdr_meta)]], colWidths=[CW])
    meta_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), C_NAVY_META),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 22),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 22),
    ]))

    story += [hdr_border, hdr_tbl, meta_tbl, Spacer(1, 0.25 * inch)]

    # ── Styles for tables and checkboxes ────────────────────────────────────
    tbl_hdr  = _ps("TblHdr",  fontName=f"{SANS}-Bold", fontSize=9,   leading=12,
                               textColor=C_WHITE)
    tbl_cell = _ps("TblCell", fontName=SANS,            fontSize=9,   leading=13,
                               textColor=C_TEXT)
    tbl_cell_sm = _ps("TblSm", fontName=SANS,           fontSize=8.5, leading=12,
                               textColor=C_TEXT)
    chk_sty  = _ps("Chk",     fontName=SANS,            fontSize=10.5, leading=16,
                               textColor=C_TEXT, spaceAfter=3, leftIndent=16)
    node_sty = _ps("NodeCallout", fontName=f"{SANS}-Bold", fontSize=10, leading=14,
                               textColor=HexColor("#1e3a8a"), spaceAfter=0)

    def _flush_table(raw_rows: list[str]) -> None:
        """Parse buffered markdown table lines and append a styled ReportLab Table."""
        parsed: list[list[str]] = []
        for r in raw_rows:
            if re.match(r"^\|[-| :]+\|$", r.strip()):
                continue  # separator row
            cells = [c.strip() for c in r.strip().strip("|").split("|")]
            parsed.append(cells)
        if not parsed:
            return
        n_cols = max(len(r) for r in parsed)
        # Normalise column count
        parsed = [r + [""] * (n_cols - len(r)) for r in parsed]
        # Auto column widths: first col narrower, last col narrower for status cols
        if n_cols == 3:
            col_ws = [0.06 * CW, 0.56 * CW, 0.38 * CW]
        elif n_cols == 2:
            col_ws = [0.32 * CW, 0.68 * CW]
        else:
            unit = CW / n_cols
            col_ws = [unit] * n_cols
        # Build cell paragraphs
        tbl_data: list[list] = []
        for ri, row in enumerate(parsed):
            style = tbl_hdr if ri == 0 else tbl_cell_sm
            tbl_data.append([Paragraph(_md_to_rl(cell), style) for cell in row])
        rl_tbl = Table(tbl_data, colWidths=col_ws, repeatRows=1)
        ts = TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0),   C_NAVY),
            ("TEXTCOLOR",     (0, 0), (-1, 0),   C_WHITE),
            ("FONTNAME",      (0, 0), (-1, 0),   f"{SANS}-Bold"),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1),  [C_WHITE, HexColor("#f1f5f9")]),
            ("GRID",          (0, 0), (-1, -1),  0.4, C_BORDER),
            ("TOPPADDING",    (0, 0), (-1, -1),  5),
            ("BOTTOMPADDING", (0, 0), (-1, -1),  5),
            ("LEFTPADDING",   (0, 0), (-1, -1),  7),
            ("RIGHTPADDING",  (0, 0), (-1, -1),  7),
            ("VALIGN",        (0, 0), (-1, -1),  "TOP"),
        ])
        rl_tbl.setStyle(ts)
        story.append(rl_tbl)
        story.append(Spacer(1, 0.1 * inch))

    # ── Render content (with table buffering) ────────────────────────────────
    table_buf: list[str] = []
    seen_card_marker = False

    def _maybe_flush():
        if table_buf:
            _flush_table(list(table_buf))
            table_buf.clear()

    for line in content_lines:
        clean = line.strip()

        # Table row detection
        if clean.startswith("|"):
            table_buf.append(clean)
            continue
        else:
            _maybe_flush()

        if not clean:
            story.append(Spacer(1, 0.05 * inch))
            continue
        if re.match(r"^CARD\s+\d+/\d+$", clean, flags=re.IGNORECASE):
            if seen_card_marker:
                story.append(PageBreak())
            seen_card_marker = True
            story.append(Paragraph(_md_to_rl(clean), body_style))
            continue
        if clean.startswith("## ") or (clean.startswith("# ") and not skip_h1):
            prefix = "## " if clean.startswith("## ") else "# "
            story.extend(_h2_row(clean[len(prefix):].strip()))
        elif clean.startswith("### "):
            story.append(Paragraph(_md_to_rl(clean[4:].strip()), h3_style))
        elif re.match(r"^- \[[ xX]\]", clean):
            # Checkbox bullet: - [ ] or - [x]
            checked = bool(re.match(r"^- \[[xX]\]", clean))
            raw_text = re.sub(r"^- \[[ xX]\]\s*", "", clean)
            # Strip any leftover ** / * that _md_to_rl couldn't pair-match
            raw_text = re.sub(r"\*+", "", raw_text)
            text = _md_to_rl(raw_text)
            if checked:
                icon = f'<font color="#16a34a" fontName="{SANS}-Bold" fontSize="13">✓</font>'
            else:
                icon = f'<font color="#1d4ed8" fontName="{SANS}-Bold" fontSize="11">✦</font>'
            story.append(Paragraph(f"{icon}  {text}", chk_sty))
        elif is_request_log_callout(clean):
            text = re.sub(r"^[-*]\s*", "", clean).strip()
            node_tbl = Table([[Paragraph(_md_to_rl(text), node_sty)]], colWidths=[CW])
            node_tbl.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, -1), HexColor("#dbeafe")),
                ("BOX",           (0, 0), (-1, -1), 0.7, HexColor("#2563eb")),
                ("LEFTPADDING",   (0, 0), (-1, -1), 10),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
                ("TOPPADDING",    (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]))
            story.append(node_tbl)
            story.append(Spacer(1, 0.08 * inch))
        elif clean.startswith("- ") or clean.startswith("* "):
            text = _md_to_rl(clean[2:].strip())
            story.append(Paragraph(
                f'<font color="#c9922a" fontName="{SANS}-Bold">›</font>  {text}', bullet_sty,
            ))
        elif re.match(r"^\d+\.\s+", clean):
            m = re.match(r"^(\d+)\.\s+(.*)", clean)
            if m:
                n, cnt = m.group(1), _md_to_rl(m.group(2))
                story.append(Paragraph(
                    f'<font color="#1d4ed8" fontName="{SANS}-Bold">{n}.</font>  {cnt}', num_style,
                ))
        elif clean.startswith('"') or clean.startswith('\u201c'):
            q_tbl = Table([[Paragraph(_md_to_rl(clean), quote_sty)]], colWidths=[CW])
            q_tbl.setStyle(TableStyle([
                ("BACKGROUND",   (0, 0), (-1, -1), HexColor("#fefce8")),
                ("LINEAFTER",    (0, 0), (0, -1),  3, C_GOLD),
                ("LINEBEFORE",   (0, 0), (0, -1),  3, C_GOLD),
                ("TOPPADDING",   (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING",(0, 0), (-1, -1), 10),
                ("LEFTPADDING",  (0, 0), (-1, -1), 14),
                ("RIGHTPADDING", (0, 0), (-1, -1), 14),
            ]))
            story.append(q_tbl)
            story.append(Spacer(1, 0.06 * inch))
        else:
            story.append(Paragraph(_md_to_rl(clean), body_style))

    _maybe_flush()
    story.append(Spacer(1, 0.3 * inch))
    doc_obj.build(story, onFirstPage=_draw_footer, onLaterPages=_draw_footer)
    return buf.getvalue()
