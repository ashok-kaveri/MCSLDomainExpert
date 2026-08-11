# WooCommerce UPS Shipping Plugin with Print Label 6.6.3 — Support Guide

Platform: WooCommerce (WordPress). Carrier: UPS. Version: **6.6.3**. Release date: **7 August 2026**.

Everything in this guide is available from version **6.6.3**, released **7 August 2026**. If a merchant does not see the behaviour described here, confirm their plugin version first.

## Included Story Cards

| Story ID | Story Title | Trello card link |
|---|---|---|
| 947 | [Improvement] Add additional shipment document links to auto-generated label email | https://trello.com/c/AKZzEkMG |

## 947 - [Improvement] Add additional shipment document links to auto-generated label email

### Brief Description

The shipping label email used to carry only the shipping label. Any extra documents created with the shipment — Commercial Invoice, Return Commercial Invoice, Dangerous Goods Manifest, Dangerous Goods Signatory Info, Control Log Receipt — were never sent.

A new email tag, `[ADDITIONAL LABELS]`, now inserts a download button for each of those documents that actually exists for the shipment, and attaches the files to the same email. Only the documents present are shown; the rest are skipped silently.

This is opt-in: the merchant must add `[ADDITIONAL LABELS]` to their label email content. It does not appear on its own in the default template.

### Prerequisites

- Plugin version 6.6.3 or later.
- **Send Shipping Label via Email** must be set to **Shipper**, **Receiver**, or both, under **UPS Settings → Shipping Labels**. This applies to the shipping label email generally — it is not limited to automatic label generation.
- **Required setup:** go to **UPS Settings → Shipping Labels → Send Shipping Label via Email → Content of Email With Label** and add the `[ADDITIONAL LABELS]` tag.
  - The **Content of Email With Label** field is only displayed once **Send Shipping Label via Email** has a selection, so set that first.
  - The tag is also available from the tag picker next to the field.
- To see each document type, the shipment must actually produce it (for example an international shipment for the Commercial Invoice, a Dangerous Goods shipment for the DG documents).

### Step-by-Step Support Walkthrough

**Setup — add the tag to the label email content**

1. In WordPress Admin, go to **UPS Settings → Shipping Labels**.
2. Set **Send Shipping Label via Email** to **Shipper**, **Receiver**, or both. The **Content of Email With Label** field appears only once a selection is made.
3. In **Content of Email With Label**, add `[ADDITIONAL LABELS]` where the document buttons should appear in the email body, then save.
4. Confirm the tag is listed among the available tags shown next to the field.

**Scenario A — Commercial Invoice**

5. Generate a forward shipment label for an international order that produces a Commercial Invoice.
6. Open the shipping label email and confirm a **Commercial Invoice** download button appears and the PDF is attached to the email.
7. Click the button and confirm the correct invoice opens.

**Scenario B — Return Commercial Invoice**

8. Generate a Return Label with a Return Commercial Invoice for an international order.
9. Confirm the email shows a **Return Commercial Invoice** button, the file is attached, and the download opens correctly.

**Scenario C — Dangerous Goods documents**

10. Generate a label for a shipment flagged as Dangerous Goods.
11. Confirm buttons appear for the **DG Manifest** and **DG Signatory Info**, the files are attached, and both downloads open and match the shipment.

**Scenario D — Control Log Receipt**

12. Generate a label for a shipment that produces a Control Log Receipt.
13. Confirm the **Control Log Receipt** button appears, the file is attached, and the download opens correctly.

**Scenario E — Multiple documents in one shipment**

14. Generate a shipment that produces more than one extra document (for example Commercial Invoice + DG Manifest).
15. Confirm all relevant buttons appear and all files are attached in the same email.

**Scenario F — Shipment with no extra documents**

16. Generate a label for a plain domestic shipment with none of these documents.
17. Confirm the email sends normally, with no leftover `[ADDITIONAL LABELS]` text and no empty or broken buttons.

**Scenario G — No regression on the existing email**

18. On any of the emails above, confirm the shipping label attachment, tracking number, customer name, and the rest of the content are unchanged.

### Expected Behaviour

When `[ADDITIONAL LABELS]` is present in **Content of Email With Label**, the shipping label email shows a download button for every extra document that exists for that shipment and attaches those files. Shipments without extra documents send exactly as before, with no tag text left in the email.

If a merchant reports the buttons are missing, check two things first, in this order: that **Send Shipping Label via Email** is set to **Shipper**, **Receiver**, or both, and that the `[ADDITIONAL LABELS]` tag is present in **Content of Email With Label**. A missing tag is the most common cause, not a failed document.
