# Canada Post Shipping Plugin for WooCommerce with Print Label 3.3.10 — Support Guide

Platform: WooCommerce (WordPress). Carrier: Canada Post. Version: **3.3.10**. Release date: **August 7, 2026**.

Everything in this guide is available from version **3.3.10**, released **August 7, 2026**. If a merchant does not see the behaviour described here, confirm their plugin version first.

## Included Story Cards

| Story ID | Story Title | Trello card link |
|---|---|---|
| 964 | [Bug Fix] Shipment tracking box fields collapse on WooCommerce 11, and two warnings appear after Canada Post account setup | https://trello.com/c/BDZcPo9Z |

## 964 - [Bug Fix] Shipment tracking box fields collapse on WooCommerce 11, and two warnings appear after Canada Post account setup

### Brief Description

This card fixes two separate admin-side problems.

**1. The tracking box became unusable after a WooCommerce update.** On stores running WooCommerce 11.0 or newer, the **CanadaPost Shipment Tracking** box on the order edit screen was broken. The service dropdown, **Enter Tracking IDs** box, and **Shipment Date** field were crammed side by side on one line, each squeezed to roughly two characters wide — too narrow to read or type into. The same box looked fine on older WooCommerce versions, so it only appeared after a WooCommerce update. The fields now stack vertically and each spans the full width of the box.

**2. Two PHP warnings on every admin page.** Once a Canada Post account had been registered from the plugin, warnings about undefined array keys `availability` and `countries` appeared on every admin page load. They are visible on any store that displays PHP warnings — typically staging or development stores. The plugin now falls back to sensible defaults when those settings have not been saved yet: **All Countries** for Method Availability, and an empty Specific Countries list.

No settings were added, removed, or renamed. Rates, labels, tracking, and manifests are unchanged.

### Prerequisites

- Plugin version 3.3.10 or later.
- Nothing to switch on — the fix applies automatically.
- **WooCommerce 11.0 or newer** is required to reproduce the layout problem. On older versions the bug never appeared.
- **PHP warning display must be on** to check the warnings — that means a staging or development store, not a normal live store where warnings are hidden.
- **The warnings scenario needs a store where Canada Post settings were never saved through the settings form** — a fresh install, or reset Canada Post settings first. Once settings have been saved normally, the warnings will not reproduce even without the fix. This is the single easiest thing to get wrong when testing.
- An existing order is needed to see the tracking box.

### Step-by-Step Support Walkthrough

**Scenario A — Tracking box layout on WooCommerce 11+**

1. Confirm the store is on WooCommerce 11.0 or newer with the Canada Post plugin active.
2. Go to **WooCommerce > Orders** and open any existing order.
3. In the **CanadaPost Shipment Tracking** box, confirm the service dropdown, **Enter Tracking IDs**, and **Shipment Date** are stacked one below another, each spanning the full width of the box.
4. Confirm **Save/Show Tracking Info** sits on its own row below them.

**Scenario B — WooCommerce's own box unchanged**

5. On the same screen, look at WooCommerce's **Order actions** box.
6. Confirm its dropdown and button still sit side by side on one row, exactly as WooCommerce intends.

**Scenario C — Tracking still works**

7. Choose **Canada Post**, type a tracking number into **Enter Tracking IDs**, optionally pick a Shipment Date, and click **Save/Show Tracking Info**.
8. Confirm the tracking information saves and the tracking result displays as before.

**Scenario D — Older WooCommerce unaffected**

9. On a store running a WooCommerce version older than 11.0, open an order and check the tracking box.
10. Confirm the fields are stacked and full width, with no visual regression.

**Scenario E — No warnings after fresh account registration**

11. On a store with PHP warning display switched on and Canada Post settings never saved through the form, register a Canada Post account from the plugin settings.
12. Load the Canada Post settings page and any other admin page.
13. Confirm no *"Undefined array key"* warning for `availability` or `countries` appears anywhere.
    - `Request/log fields to verify: the admin page output and the site debug log — confirm no undefined-array-key warning is raised for the availability or countries settings.`

**Scenario F — Method Availability default**

14. On a store where Canada Post settings were never saved through the form, open **Canada Post settings > Rates** tab.
15. Confirm **Method Availability** shows **All Countries**, and rates are offered to all countries rather than being blocked.

**Scenario G — A saved Specific Countries choice is respected**

16. Set **Method Availability** to **Specific Countries**, select Canada and United States, and save.
17. Reload the settings page.
18. Confirm it still shows **Specific Countries** with Canada and United States selected, and rates are offered only for those countries. The fallback must never overwrite a saved choice.

**Scenario H — Both order screen types**

19. With **High-Performance Order Storage** enabled (**WooCommerce > Settings > Advanced > Features**), open an order and confirm the tracking box layout is correct.
20. Repeat with HPOS turned off, on the older order screen.

### Expected Behaviour

The tracking box fields stack vertically and fill the box width on WooCommerce 11.0+ and on older versions, WooCommerce's own Order actions box is untouched, and saving and displaying tracking works exactly as before. No undefined-array-key warnings appear on any admin page, before or after account registration. Method Availability defaults to All Countries when nothing has been saved, and a saved Specific Countries selection is preserved and honoured.
