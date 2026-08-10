# WooCommerce UPS Shipping Plugin with Print Label 6.6.2 — Support Guide

Platform: WooCommerce (WordPress). Carrier: UPS. Version: **6.6.2**. Release date: **31 July 2026**.

All fixes in this guide are available from plugin version **6.6.2**, released **31 July 2026**. If a merchant does not see the behaviour described here, confirm their plugin version first.

## Included Story Cards

| Story ID | Story Title | Trello card link |
|---|---|---|
| 941 | [Improvement] Add DAP (Delivery at Place) Incoterm option to Terms of Sale | https://trello.com/c/UwvMlJXN |
| 943 | [Bug Fix] UPS Simple Rate incorrectly applied to international shipments | https://trello.com/c/lJxBlnJU |
| 942 | [Bug Fix] Duplicate save-confirmation notice on WordPress admin settings pages | https://trello.com/c/U2LzivwN |

## 941 - [Improvement] Add DAP (Delivery at Place) Incoterm option to Terms of Sale

### Brief Description

Reported in Zendesk ticket 399883.

The Terms of Sale (Incoterm) dropdown used for international UPS shipments was missing **DAP – Delivery at Place**. Merchants had to pick a close-but-wrong term instead. DAP has now been added in both places the dropdown appears — the plugin's International Forms settings and the Terms of shipment dropdown on the order screen. All 12 existing terms are unchanged.

### Step-by-Step Support Walkthrough

**Scenario A — Confirm DAP is available and saves**

1. In WordPress Admin, go to **WooCommerce > Settings > Shipping > UPS > International Forms**.
2. Open the **Terms of Sale (Incoterm)** dropdown.
3. Confirm **DAP – Delivery at Place** is listed between **DAF – Delivered at Frontier** and **DDP – Delivery Duty Paid**.
4. Select **DAP – Delivery at Place** and click **Save changes**.
5. Reload the page and confirm DAP is still the selected value.

**Scenario B — Confirm DAP on an individual order (legacy UPS method)**

6. Go to **WooCommerce > Orders** and open an international order.
7. In the UPS shipping label section, open the **Terms of shipment** dropdown.
8. Confirm **DAP – Delivery at Place** is selectable, and select it.
9. Generate the shipping label and commercial invoice.
10. Confirm the label and invoice are created with no UPS error.
   - `Request node to verify: the Terms of Shipment value in the UPS international forms section of the label request — confirm it is sent as DAP, matching what was selected.`

**Scenario C — Confirm nothing else changed**

11. On a store already set to a different Incoterm (for example DDP), open **WooCommerce > Settings > Shipping > UPS > International Forms**.
12. Confirm the previously saved term is still selected and unchanged.

### Expected Behaviour

DAP appears in both dropdowns, saves and persists after reload, and generates an international label successfully. Every other Incoterm behaves exactly as before.

## 943 - [Bug Fix] UPS Simple Rate incorrectly applied to international shipments

### Brief Description

Reported in Zendesk ticket 399683.

With **UPS Simple Rate** enabled, international orders (for example US to Canada) failed with *"The requested accessory option is unavailable between the selected locations."* Simple Rate is a US-domestic-only UPS service, but its details were being sent on international shipments too. Merchants had to disable Simple Rate, make the label, then re-enable it every time. Simple Rate is now applied only to shipments inside the US 50 states. International destinations — **and Puerto Rico** — use the merchant's normal UPS services instead.

### Step-by-Step Support Walkthrough

**Scenario A — International order no longer fails**

1. In WordPress Admin, go to **WooCommerce > Settings > Shipping > UPS** and confirm **Simple Rate** is enabled.
2. Go to **WooCommerce > Orders** and open an order shipping from the US to Canada.
3. Calculate rates, then generate the UPS label.
4. Confirm the rate and label are produced using standard UPS services, with no *"accessory option unavailable"* error.
   - `Request node to verify: the outbound UPS rate and label request for this order must contain no Simple Rate package details.`

**Scenario B — Puerto Rico is treated the same as international**

5. Open an order shipping from the US to a Puerto Rico address.
6. Calculate rates and generate the label.
7. Confirm Simple Rate is not used and the shipment rates and labels successfully with standard UPS services.
   - Note: WooCommerce stores Puerto Rico as country `US` with state `PR`, which is why it was missed originally.

**Scenario C — Domestic US is unchanged**

8. Open an order shipping within the US 50 states, for example New York to California.
9. Calculate rates and generate the label.
10. Confirm Simple Rate pricing and label are used exactly as before.

**Scenario D — Checkout rates unchanged**

11. As a customer, add a product and go to checkout with a US address in one of the 50 states.
12. Confirm Simple Rate shipping options still appear as before.

**Scenario E — No manual toggling needed**

13. Generate an international label without touching the Simple Rate setting.
14. Confirm it succeeds. The merchant no longer needs the disable/re-enable workaround.

### Expected Behaviour

Simple Rate applies to the US 50 states only. Canada, all other countries, and Puerto Rico rate and label normally with no accessory-option error, and the Simple Rate setting never needs to be toggled.

## 942 - [Bug Fix] Duplicate save-confirmation notice on WordPress admin settings pages

### Brief Description

Reported in Zendesk ticket 399160.

While the UPS plugin was active, saving a WordPress settings page showed the confirmation message twice, stacked. It happened on Settings → General, Permalinks, and the UPS License page. The save itself always worked, but the doubled message looked like an error. The message now appears exactly once, matching normal WordPress behaviour. No page lost its message.

### Step-by-Step Support Walkthrough

**Scenario A — General settings**

1. Confirm the UPS Shipping plugin is active under **Plugins > Installed Plugins**.
2. Go to **WordPress Admin > Settings > General**.
3. Change the Site Title and click **Save Changes**.
4. Confirm the green **"Settings saved."** message appears only once, and the change was saved.

**Scenario B — Permalinks**

5. Go to **Settings > Permalinks** and click **Save Changes**.
6. Confirm the confirmation message appears only once.

**Scenario C — UPS License page**

7. Open the UPS **License** activation page.
8. Enter and save a license key, then deactivate it.
9. Confirm each confirmation or status message appears once, and the License Status updates correctly to Activated or Deactivated.

**Scenario D — Other settings pages**

10. Save changes on **Settings > Writing**, **Reading**, **Discussion**, and **Media**.
11. Confirm the message appears once on each page.

**Scenario E — Regression check with the plugin off**

12. Deactivate the UPS plugin and save any settings page.
13. Confirm the message still appears once, as it always did.

### Expected Behaviour

Exactly one confirmation message on every WordPress settings page, whether the UPS plugin is active or not. All settings still save correctly and no page lost its message.
