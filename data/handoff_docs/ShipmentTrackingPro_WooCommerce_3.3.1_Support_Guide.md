# Shipment Tracking Pro for WooCommerce 3.3.1 — Support Guide

Platform: WooCommerce (WordPress). Version: **3.3.1**. Release date: **August 7, 2026**.

Everything in this guide is available from version **3.3.1**, released **August 7, 2026**. If a merchant does not see the behaviour described here, confirm their plugin version first.

## Included Story Cards

| Story ID | Story Title | Trello card link |
|---|---|---|
| 962 | [Bug Fix] Fix Shipment Tracking metabox layout broken by WooCommerce 11.0 | https://trello.com/c/lNUjqyRB |

## 962 - [Bug Fix] Fix Shipment Tracking metabox layout broken by WooCommerce 11.0

### Brief Description

After updating to **WooCommerce 11.0**, the **Shipment Tracking** box in the order edit sidebar rendered badly. The carrier dropdown, **Enter Tracking IDs** box, **Descriptions** box, and **Shipment Date** field were squeezed into narrow columns side by side instead of stacking down the box, so labels and fields overlapped and were hard to read or type into.

The cause was a naming clash: the tracking box's internal container used the same ID as WooCommerce's own **Order actions** box. WooCommerce 11.0 added new styling for that ID, and our box picked it up by accident. The box now uses its own ID, and all four fields are set to take the full width of the box.

This is a layout fix only. Saving and displaying tracking information is unchanged.

### Prerequisites

- Plugin version 3.3.1 or later.
- No setting to enable — the fix applies automatically.
- **WooCommerce 11.0 or newer is required to see the difference.** On older WooCommerce versions the box looked fine either way, so testing there proves nothing. Confirm the store's WooCommerce version before treating this as a valid check.
- An existing order is needed to see the tracking box.

### Step-by-Step Support Walkthrough

**Scenario A — Layout is correct on WooCommerce 11.0+**

1. Confirm the store is on WooCommerce 11.0 or newer.
2. Go to **WooCommerce > Orders** and open any order.
3. Find the **Shipment Tracking** box in the sidebar.
4. Confirm the carrier dropdown, **Enter Tracking IDs** box, **Descriptions** box, and **Shipment Date** field are stacked one below the other, each spanning the full width of the box — matching the width of the **Save/Show Tracking Info** button below them.

**Scenario B — Saving tracking still works**

5. Select a carrier from the dropdown, for example FedEx or UPS.
6. Enter a tracking ID such as `1Z999AA10123456784` in **Enter Tracking IDs**, optionally add text in **Descriptions**, and pick a **Shipment Date**.
7. Click **Save/Show Tracking Info**.
8. Confirm the tracking information saves and appears on the order exactly as before — this change affects appearance only.

**Scenario C — HPOS on**

9. With **High-performance order storage** enabled (**WooCommerce > Settings > Advanced > Features**), open an order from the new Orders screen.
10. Confirm the full-width stacked layout from Scenario A.

**Scenario D — HPOS off**

11. With HPOS turned off, open an order from the classic Edit Order screen.
12. Confirm the same correct layout.

**Scenario E — Orders with tracking saved before the fix**

13. Open an order that already had a carrier, tracking ID, description, and date saved before this update.
14. Confirm all previously saved values still display correctly in the properly sized fields, with nothing cut off or overlapping.

**Scenario F — Nothing else on the page changed**

15. On the same order edit page, check WooCommerce's own **Order actions** box and any other carrier tracking boxes present.
16. Confirm none of them changed in appearance or behaviour.

### Expected Behaviour

On WooCommerce 11.0 and later, the Shipment Tracking box shows its four fields stacked and full width on both the classic and HPOS order screens. Tracking saves and displays exactly as it always did, previously saved values render correctly, and no other box on the page is affected.

If a merchant still reports the squeezed layout, confirm they are on plugin version 3.3.1 or later, then clear any page or browser cache before investigating further.
