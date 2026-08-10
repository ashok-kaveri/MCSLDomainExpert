# USPS WooCommerce Shipping Plugin 1.0.5 — Support Guide

Platform: WooCommerce (WordPress). Carrier: USPS. Version: **1.0.5**.

Everything in this guide is available from version **1.0.5**. If a merchant does not see the behaviour described here, confirm their plugin version first.

## Included Story Cards

| Story ID | Story Title | Trello card link |
|---|---|---|
| 917 | Shipping connection/token lapses after periods of low activity | https://trello.com/c/ZAffJDkM |
| 922 | Skip zero-quantity products when auto-generating manual packaging | https://trello.com/c/4YTBLcgD |

## 917 - Shipping connection/token lapses after periods of low activity

### Brief Description

On low-order-volume stores, the USPS connection could lapse after several days with no rate requests or orders. Merchants saw *"Invalid Refresh Token: Not Found"* and *"Client credentials unavailable"*, and had to manually re-register the account and reactivate the plugin licence to get live rates back.

A new developer-only setting, **Keep USPS Account Active**, has been added to the **Debug** tab. When enabled, it pings the USPS connection on a daily schedule so the token does not go stale during quiet periods.

Three things support should know:

- It is **off by default** — nothing changes for stores that do not need it.
- The ping tracks the account's real connection status **immediately**: it starts the moment the account connects and stops the moment it disconnects, with no settings resave needed.
- With Debug Mode on, the ping writes to its **own separate log file**, not the normal request log, and each entry states plainly that the request and response are an automatic keep-active check rather than a real customer order.

### Prerequisites

- Plugin version 1.0.5 or later.
- A connected USPS account.
- **Keep USPS Account Active** checkbox under USPS settings > **Debug** tab — unchecked by default. Enable it only for stores that actually see connection lapses.
- Debug Mode enabled if you want to inspect the ping's log entries.
- WP Crontrol (**Tools > Cron Events**) is the easiest way to confirm the schedule.

### Step-by-Step Support Walkthrough

**Scenario A — Off by default**

1. On a fresh plugin activation, leave **Keep USPS Account Active** unchecked.
2. Go to **Tools > Cron Events** and confirm no `ph_usps_keep_account_active_cron` event is listed.

**Scenario B — Enabling and disabling the setting**

3. Go to USPS settings > **Debug** tab, tick **Keep USPS Account Active**, and save.
4. In **Tools > Cron Events**, confirm `ph_usps_keep_account_active_cron` is now listed with a **24-hour** recurrence.
5. Untick the checkbox and save again.
6. Confirm the event is no longer listed — with no plugin deactivate/reactivate needed.

**Scenario C — What the ping actually does**

7. With the setting on, a USPS account connected, and Debug Mode enabled, find `ph_usps_keep_account_active_cron` in **Tools > Cron Events** and click **Run Now**.
8. Confirm a successful dummy rate request and response is recorded.
   - `Request/log fields to verify: the entry must be written to the ph-usps-keep-account-active-cron-log file, not the general debug log, and must state that the request/response is an automatic check to keep the account active rather than a real customer order.`

**Scenario D — Connection status sync**

9. With the setting enabled and the account connected, disconnect the USPS account.
10. In **Tools > Cron Events**, confirm `ph_usps_keep_account_active_cron` is unscheduled immediately, without saving settings again.
11. Reconnect the USPS account while the setting is still enabled.
12. Confirm the event is scheduled again immediately, again with no settings resave.

**Scenario E — Plugin deactivation**

13. Deactivate the plugin.
14. Confirm the `ph_usps_keep_account_active_cron` event is cleared, whether the setting was on or off.

### Expected Behaviour

Stores that never enable the setting behave exactly as before. Once a merchant enables it, the connection is pinged every 24 hours so the token stays valid through quiet periods, the schedule follows the account's connect/disconnect state instantly, and the ping's log entries are kept in their own file and clearly marked as automatic checks.

If a merchant reports refresh-token errors after idle days, update them to 1.0.5 and enable **Keep USPS Account Active** on the Debug tab. If they report odd requests in their debug log, check whether this setting is on — those entries are the keep-active ping, not real orders.

## 922 - Skip zero-quantity products when auto-generating manual packaging

### Brief Description

When a manual package contained a line item with **zero quantity**, that item was still counted while building the package contents. This could produce an invalid shipment request and block rate and label generation. On international orders the same zero-quantity item also flowed into the customs declaration with zero value, quantity, and weight — an inaccurate entry that could get the customs form rejected.

Zero-quantity products are now skipped when manual packaging is built, so shipment requests and customs declarations only contain items that are actually shipping. The manual packaging dialog is also slightly wider, so the package fields are no longer cramped.

### Prerequisites

- Plugin version 1.0.5 or later.
- No setting to enable — the fix applies automatically.
- To reproduce: an order with a manual package that includes a zero-quantity line item.

### Step-by-Step Support Walkthrough

**Scenario A — Package with only a zero-quantity item**

1. Create a manual package containing only a zero-quantity product line item.
2. Confirm it no longer triggers a rate/label request error and a valid shipment request is generated.

**Scenario B — Mixed quantities**

3. Create a manual package with a mix of zero-quantity and normal-quantity products.
4. Confirm only the non-zero items appear in the generated package contents.
5. Confirm rate calculation and label generation complete successfully.

**Scenario C — International order and customs form**

6. Create a manual package for an international order with a mix of zero-quantity and normal-quantity products, then generate the shipment.
7. Confirm the customs declaration lists only the non-zero-quantity products.
   - `Request/log fields to verify: the customs form contents in the shipment request — confirm no content line is generated with zero value, quantity, or weight.`
8. Confirm the international shipment request completes and the customs form is accepted.

**Scenario D — Normal orders unaffected**

9. Create a manual package with normal quantities only.
10. Confirm packaging and rate/label generation work exactly as before.

**Scenario E — Dialog width**

11. Open the manual packaging dialog and confirm it is visibly wider, with no cramped fields.

### Expected Behaviour

Zero-quantity line items are excluded from manual packaging, so rate and label generation succeed and international customs declarations list only the goods actually being shipped. Orders without zero-quantity items behave exactly as before.
