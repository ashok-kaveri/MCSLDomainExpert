# PH Royal Mail Shipping with Tracking for WooCommerce 2.2.2 — Support Guide

Platform: WooCommerce (WordPress). Carrier: Royal Mail. Version **2.2.2**, released **10 August 2026**. If a merchant does not see the behaviour described here, confirm their plugin version first.

This release is a single compatibility fix. WooCommerce 11.0.0 changed some of its own admin styling, which broke the layout of the **Shipment Tracking** box on the order edit page. The box now displays correctly again, and this version is declared as tested up to WooCommerce 11.0.0.

## Included Story Cards

| Story ID | Story Title | Trello card link |
|---|---|---|
| 965 | [Compatibility] Fix broken Shipment Tracking box layout on order edit page (WC 11.0.0) | [965](https://trello.com/c/cq48ZTgJ) |

## 965 - [Compatibility] Fix broken Shipment Tracking box layout on order edit page (WC 11.0.0)

### Brief Description

After a merchant updated to the latest WooCommerce version, the **Shipment Tracking** box on the order edit page looked broken. Its fields were squeezed together and misaligned, and the **Shipping Service** dropdown had no visible label above it, so it was not obvious what the dropdown was for. WooCommerce 11.0.0 introduced new layout styling for one of its own admin boxes, and that styling caught this box as well.

The box now displays correctly again. Each of the three fields — **Shipping Service**, **Enter Tracking IDs** and **Shipment Date** — has a clear label above it, the inputs run the full width of the box, and the spacing between fields is even. The information icon beside each label now sits close to the label text instead of drifting away from it.

This is a display fix only. Nothing about how tracking information is entered, saved, or shown to the customer has changed.

### Prerequisites

- Plugin version 2.2.2 or later. This version is declared as tested up to WooCommerce 11.0.0.
- Best confirmed on a store running **WooCommerce 11.0.0 or later**, since that is where the broken layout appears. On earlier WooCommerce versions the box looked correct before this release and still does.
- Access to the **order edit page** in WordPress admin for an order the Royal Mail Shipment Tracking box appears on.
- A hard refresh of the order edit page may be needed the first time after updating, so the merchant's browser picks up the corrected styling rather than a cached copy.

### Step-by-Step Support Walkthrough

**Scenario A — the box looks right again**

1. In WordPress Admin, open **WooCommerce → Orders** and open any order that shows the Royal Mail **Shipment Tracking** box.
2. Confirm the box renders fully aligned and matches the width of the other boxes in the same sidebar column.
3. Confirm each of the three fields has a visible label above it: **Shipping Service**, **Enter Tracking IDs**, and **Shipment Date**. The missing Shipping Service label was the most obvious symptom of this problem, so check that one specifically.
4. Confirm the inputs run the full width of the box rather than being squeezed narrow.
5. Confirm the spacing between the three fields looks even, with no extra gap above the first field and none between the box header and that first field.
6. Confirm the information **(i)** icon next to each label sits close to its label text rather than floating away from it.
7. If the box still looks wrong, have the merchant hard-refresh the page once before investigating further — a cached copy of the old styling is the most likely explanation immediately after an update.

**Scenario B — saving tracking information still works**

8. In the box, choose a **Shipping Service**, enter one or more tracking IDs separated by commas, and set a **Shipment Date**.
9. Click **Save / Show Tracking Info** and confirm the values save and display correctly in the box.
10. Reload the order edit page and confirm the values entered are still shown correctly.
11. Open the same order as the customer sees it, on the order details page in **My Account**, and confirm the saved tracking information still appears there exactly as before.

### Expected Behaviour

On WooCommerce 11.0.0 and later, the Shipment Tracking box on the order edit page is properly laid out: three clearly labelled fields, full-width inputs, even spacing, and information icons sitting tight against their labels. Entering, saving and reloading tracking information works exactly as it did before, and the customer-facing order details page is unchanged. Stores on earlier WooCommerce versions see no difference from this release.

**Known pre-existing item, deliberately left out of scope:** the date picker on the **Shipment Date** field has a separate long-standing issue of its own, unrelated to this layout fix and not addressed in this release. If a merchant reports trouble opening or using that date picker rather than trouble with how the box looks, treat it as a separate item and pass it back to the team rather than as a fault in this fix.
