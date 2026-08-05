import types
from unittest.mock import patch


def test_support_fallback_uses_story_card_support_format():
    from pipeline.handoff_docs import build_handoff_context, generate_support_guide

    card = types.SimpleNamespace(
        id="c1",
        name="From SL: ZI-058 - eParcel bulk label generation delay",
        desc="Toggle: australiaPost.skip.get.shipment.enabled",
        url="https://trello.com/c/example",
    )
    ctx = build_handoff_context(
        card=card,
        release_name="MCSL 378",
        acceptance_criteria="- Bulk labels complete faster",
        test_cases="## TC-1: Bulk label performance",
    )

    with patch("pipeline.handoff_docs._invoke_doc_prompt", side_effect=RuntimeError("offline")):
        doc = generate_support_guide(ctx)

    assert "## Support Guide: ZI-058" in doc
    assert "## Brief Description" in doc
    assert "## Toggles & Prerequisites" in doc
    assert "## Step-by-Step Support Walkthrough" in doc
    assert "## Expected Behaviour" in doc
    assert "## Feature Summary" not in doc
    assert "## Merchant-Safe Explanation" not in doc
    assert "## Common Questions & Troubleshooting" not in doc
    assert "## Support Escalation Packet" not in doc
    assert "## The Problem" not in doc
    assert "## Test Scenarios" not in doc


def test_support_doc_removes_generic_mcsl_navigation_block():
    from pipeline.handoff_docs import build_handoff_context, generate_support_guide

    card = types.SimpleNamespace(
        id="c1",
        name="From SL: ZI-063 - Custom declaration statement on FedEx commercial invoice not available",
        desc="FedEx REST commercial invoice declarationStatement request log carrier settings",
        url="https://trello.com/c/tHOnnmuh",
    )
    ctx = build_handoff_context(card=card, release_name="MCSL 378")
    generated = """# Support Guide: ZI-063

## Brief Description
FedEx custom declaration statement.

## Where to Find This in MCSL
- Open FedEx REST carrier settings only.
- Go directly to Other Details.

## Step-by-Step Support Walkthrough
1. Open carrier Other Details.
"""

    with patch("pipeline.handoff_docs._invoke_doc_prompt", return_value=generated):
        doc = generate_support_guide(ctx)

    assert "## Where to Find This in MCSL" not in doc
    assert "Open FedEx REST carrier settings only" not in doc
    assert "Go directly to Other Details" not in doc


def test_handoff_context_includes_live_trello_comments_and_checklists():
    from pipeline.handoff_docs import _context_text, build_handoff_context

    card = types.SimpleNamespace(
        id="c1",
        name="From SL: ZI-034 - Discounted price not reflected on commercial invoice",
        desc="UPS commercial invoice discount",
        url="https://trello.com/c/example",
        comments=[
            "QA note: free shipping should apply to shipping amount, not product total.",
            "Toggle: account.ups.rest.commercial.invoice.discount.enabled",
        ],
        checklists=[
            {
                "name": "QA Caveats",
                "items": [{"name": "Verify Amount off products does not fail label generation", "state": "incomplete"}],
            }
        ],
    )

    ctx = build_handoff_context(card=card, release_name="MCSL 378")
    context = _context_text(ctx)

    assert "LIVE TRELLO COMMENTS / QA NOTES:" in context
    assert "free shipping should apply to shipping amount" in context
    assert "LIVE TRELLO CHECKLISTS:" in context
    assert "Verify Amount off products does not fail label generation" in context
    assert "account.ups.rest.commercial.invoice.discount.enabled" in ctx.toggle_names


def test_support_fallback_does_not_add_toggle_language_for_no_toggle_card():
    from pipeline.handoff_docs import build_handoff_context, generate_support_guide

    card = types.SimpleNamespace(
        id="c1",
        name="From SL: ZI-065 - DHL Export Declaration Surcharge incorrectly applied for Japan shipments",
        desc="No toggle. DHL Japan export surcharge should be excluded.",
        url="https://trello.com/c/example",
    )
    ctx = build_handoff_context(card=card, release_name="MCSL 378")

    with patch("pipeline.handoff_docs._invoke_doc_prompt", side_effect=RuntimeError("offline")):
        doc = generate_support_guide(ctx)

    assert "| No toggle |" in doc
    assert "Use live MCSL store/account state as the source of truth" not in doc
    assert "Exact toggle/config value if the feature is gated" not in doc


def test_support_doc_guard_removes_toggle_language_from_model_output_for_no_toggle_card():
    from pipeline.handoff_docs import build_handoff_context, generate_support_guide

    card = types.SimpleNamespace(
        id="c1",
        name="From SL: ZI-065 - DHL Export Declaration Surcharge incorrectly applied for Japan shipments",
        desc="DHL Japan export surcharge should be excluded. No toggle.",
        url="https://trello.com/c/example",
    )
    ctx = build_handoff_context(card=card, release_name="MCSL 378")
    generated = """# Support Guide: ZI-065

## Toggles & Prerequisites
| Toggle / config note | What support should confirm |
|---|---|
| None detected | Use live MCSL store/account state as the source of truth. |

- Use live MCSL store/account state as the source of truth when a toggle is mentioned.

## Where to Find This in MCSL
- Wrong navigation.

## Step-by-Step Support Walkthrough
1. Confirm Japan-origin DHL shipment.
- Exact toggle/config value if the feature is gated.
"""

    with patch("pipeline.handoff_docs._invoke_doc_prompt", return_value=generated):
        doc = generate_support_guide(ctx)

    assert "| No toggle | No feature toggle is required" in doc
    assert "Use live MCSL store/account state as the source of truth" not in doc
    assert "Exact toggle/config value" not in doc
    assert "## Where to Find This in MCSL" not in doc


def test_combined_handoff_docs_include_multiple_cards():
    from pipeline.handoff_docs import (
        build_handoff_context,
        generate_combined_business_brief,
        generate_combined_support_guide,
    )

    cards = [
        types.SimpleNamespace(
            id="c1",
            name="From SL: ZI-058 - eParcel bulk label generation delay",
            desc="Toggle: australiaPost.skip.get.shipment.enabled",
            url="https://trello.com/c/example1",
        ),
        types.SimpleNamespace(
            id="c2",
            name="From SL: ZI-059 - UPS tracking sync",
            desc="Tracking number should sync to Shopify order",
            url="https://trello.com/c/example2",
        ),
    ]
    contexts = [
        build_handoff_context(card=card, release_name="MCSL 378", acceptance_criteria="AC", test_cases="TC")
        for card in cards
    ]

    with patch("pipeline.handoff_docs._invoke_doc_prompt", side_effect=RuntimeError("offline")):
        support_doc = generate_combined_support_guide(contexts, "MCSL 378")
        business_doc = generate_combined_business_brief(contexts, "MCSL 378")

    # "From SL:" boilerplate is stripped from card headings and the index page.
    assert support_doc.startswith("# MCSL 378 Support Guide")
    assert "## Included Story Cards" in support_doc
    assert "## ZI-058 - eParcel bulk label generation delay" in support_doc
    assert "## ZI-059 - UPS tracking sync" in support_doc
    assert "### Brief Description" in support_doc
    index_rows = [ln for ln in support_doc.splitlines() if ln.startswith("| ZI-")]
    assert index_rows and not any("From SL:" in row for row in index_rows)

    assert business_doc.startswith("# What's New: MCSL 378")
    assert "## Included Updates" in business_doc
    assert "## ZI-058 - eParcel bulk label generation delay" in business_doc
    assert "## ZI-059 - UPS tracking sync" in business_doc


def test_release_index_table_uses_story_id_title_and_toggle_columns():
    from pipeline.handoff_docs import build_handoff_context, generate_combined_support_guide

    cards = [
        types.SimpleNamespace(
            id="c1",
            name="ZI-058 - eParcel bulk label generation delay",
            desc="Toggle: australiaPost.skip.get.shipment.enabled",
            url="https://trello.com/c/example1",
        ),
        types.SimpleNamespace(
            id="c2",
            name="ZI-059 - UPS tracking sync",
            desc="Tracking number should sync to Shopify order",
            url="https://trello.com/c/example2",
        ),
    ]
    contexts = [build_handoff_context(card=card, release_name="MCSL 378") for card in cards]

    with patch("pipeline.handoff_docs._invoke_doc_prompt", side_effect=RuntimeError("offline")):
        support_doc = generate_combined_support_guide(contexts, "MCSL 378")

    assert "| Story ID | Story Title | Toggle Name | Trello card link |" in support_doc
    assert (
        "| ZI-058 | eParcel bulk label generation delay "
        "| australiaPost.skip.get.shipment.enabled | [ZI-058](https://trello.com/c/example1) |"
    ) in support_doc
    assert "| ZI-059 | UPS tracking sync | None | [ZI-059](https://trello.com/c/example2) |" in support_doc
    assert "Toggle / prerequisite signal" not in support_doc
    assert "How Support Should Use This Package" not in support_doc


def test_request_log_callout_detector_supports_all_handoff_labels():
    from pipeline.handoff_docs import is_request_log_callout

    assert is_request_log_callout("- Request node to verify: `discount`")
    assert is_request_log_callout("- Request nodes to verify: `signature`, `nsr`")
    assert is_request_log_callout("- Request/response nodes to verify: VAT/tax component")
    assert is_request_log_callout("- Request/log fields to verify: carrier not found")
    assert not is_request_log_callout("- Open the request log and compare the result.")


def test_platform_scope_defaults_to_shopify_and_detects_named_platforms():
    from pipeline.card_processor import detect_platform_scope, platform_scope_brief

    assert detect_platform_scope("FedEx commercial invoice card") == ["Shopify"]
    assert detect_platform_scope("Custom BigCommerce theme blocking checkout rates") == ["BigCommerce"]
    assert detect_platform_scope("WooCommerce Canpar adult signature") == ["WooCommerce"]
    assert detect_platform_scope("Magento order label generation issue") == ["Magento"]
    assert detect_platform_scope("PrestaShop checkout rate issue") == ["PrestaShop"]
    assert "Shopify is the default QA/support platform" in platform_scope_brief("carrier-neutral card")


def test_handoff_context_uses_named_platform_or_shopify_default():
    from pipeline.handoff_docs import build_handoff_context

    default_card = types.SimpleNamespace(
        id="c1",
        name="From SL: ZI-065 - DHL Export Declaration Surcharge incorrectly applied",
        desc="DHL Japan export surcharge should be excluded.",
        url="https://trello.com/c/example",
    )
    bigcommerce_card = types.SimpleNamespace(
        id="c2",
        name="From SL: ZI-360 - Custom BigCommerce theme blocking shipping rate display",
        desc="BigCommerce checkout rates should show after rate automation carrier mapping.",
        url="https://trello.com/c/example2",
    )

    assert build_handoff_context(card=default_card, release_name="MCSL 378").platform_names == ["Shopify"]
    bigcommerce_ctx = build_handoff_context(card=bigcommerce_card, release_name="MCSL 378")
    assert bigcommerce_ctx.platform_names == ["BigCommerce"]
    assert any("BigCommerce" in item for item in bigcommerce_ctx.likely_navigation)


def test_md_to_rl_keeps_code_spans_out_of_emphasis_matching():
    """A literal * inside a code span must not pair as italic across spans.

    Real MCSL 384 content ("`*.disabled` ... `*.enabled`") produced interleaved
    <font>/<i> tags that ReportLab refused to parse.
    """
    from pipeline.handoff_docs import _md_to_rl

    out = _md_to_rl("Kill-switch (`*.disabled`) suppresses reactivation even when `*.enabled` is true")

    assert "<i>" not in out
    assert out.count('<font name="Courier" fontSize="9">') == 2
    assert out.count("</font>") == 2
    assert ".disabled" in out and ".enabled" in out


def test_md_to_rl_still_renders_bold_italic_and_links():
    from pipeline.handoff_docs import _md_to_rl

    out = _md_to_rl("**bold** and *italic* and `code` and [card](https://trello.com/c/x)")

    assert "<b>bold</b>" in out
    assert "<i>italic</i>" in out
    assert '<font name="Courier" fontSize="9">code</font>' in out
    assert '<a href="https://trello.com/c/x" color="#1155CC">card</a>' in out


def test_detect_toggles_handles_markdown_wrapped_keys():
    """Real MCSL 384 card text: bold splits keys and sits between colon and value."""
    from pipeline.handoff_docs import detect_toggles

    # ZI-657 — bold between the colon and the value
    assert detect_toggles('**"{accountUUID}.products.bulk.edit.grid.enabled":** **true,**') == [
        "{accountUUID}.products.bulk.edit.grid.enabled"
    ]
    # ZI-651 — bare bolded key on its own line
    assert detect_toggles("**{accountUUID}.wc.cancelled.order.reactivation.enabled**") == [
        "{accountUUID}.wc.cancelled.order.reactivation.enabled"
    ]
    # ZI-664 — bold splitting the key, and prose form
    assert detect_toggles("{accountUUID}.**amazon.referred**") == ["{accountUUID}.amazon.referred"]
    assert detect_toggles("Given the toggle `{accountUUID}.amazon.referred` is ON") == [
        "{accountUUID}.amazon.referred"
    ]


def test_detect_toggles_ignores_filenames_and_domains():
    from pipeline.handoff_docs import detect_toggles

    assert detect_toggles("Affected Files: serviceCodes.js, canpar/constants.js, feature toggle config") == []
    assert detect_toggles("See https://trello.com and pluginhive.com for the toggle docs") == []


def test_request_callout_variants_are_normalized_for_the_pdf_highlighter():
    """Models emit the label with backticks or a doubled dash; both must still highlight."""
    from pipeline.handoff_docs import _normalize_request_callouts, is_request_log_callout

    raw = "\n".join([
        "   - `- Request nodes to verify:` dimension fields in the product update payload",
        "- `Request node to verify:` declarationStatement",
        "- Request/log fields to verify: carrier not found",
        "* Request/response nodes to verify: VAT component",
    ])
    out = _normalize_request_callouts(raw).splitlines()

    assert all(is_request_log_callout(line) for line in out), out
    assert out[0] == "- Request nodes to verify: dimension fields in the product update payload"
    assert out[1] == "- Request node to verify: declarationStatement"
    assert "`" not in "\n".join(out)


def test_normalizer_leaves_ordinary_bullets_alone():
    from pipeline.handoff_docs import _normalize_request_callouts

    text = "- Open the request log and compare the result.\n- Confirm the toggle is on."
    assert _normalize_request_callouts(text) == text


def test_callout_normalizer_clears_unbalanced_backticks_it_creates():
    from pipeline.handoff_docs import _normalize_request_callouts, is_request_log_callout

    raw = "- `Request/log fields to verify: _composite_parent`, `_composite_children` meta keys"
    out = _normalize_request_callouts(raw)

    assert is_request_log_callout(out)
    assert "`" not in out
    assert "_composite_parent" in out and "_composite_children" in out


def test_each_card_section_starts_on_a_new_pdf_page():
    """A card must never begin part-way down the previous card's page."""
    from pipeline.handoff_docs import is_card_section_heading, render_pdf_bytes

    assert is_card_section_heading("ZI-651 - WSS order updates not syncing")
    assert is_card_section_heading("941 - Add DAP Incoterm option")
    assert not is_card_section_heading("Included Story Cards")
    assert not is_card_section_heading("Toggles & Prerequisites")

    doc = "\n".join([
        "# MCSL 384 Support Guide",
        "",
        "## Included Story Cards",
        "| Story ID | Story Title | Toggle Name | Trello card link |",
        "|---|---|---|---|",
        "| ZI-001 | First card | None | - |",
        "",
        "## ZI-001 - First card",
        "### Brief Description",
        "Short body.",
        "",
        "## ZI-002 - Second card",
        "### Brief Description",
        "Short body.",
    ])
    pdf = render_pdf_bytes("MCSL 384 Support Guide", doc)

    # Index page + one page per card, even though the bodies are tiny:
    # header/index page, ZI-001 page, ZI-002 page.
    pages = pdf.count(b"/Type /Page") - pdf.count(b"/Type /Pages")
    assert pages == 3, pages
