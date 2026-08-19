# Estimated Delivery 2.3.1 — Support Guide

Platform: WooCommerce (WordPress). Product: Estimated Delivery. Version **2.3.1**, released **13 August 2026**. If a merchant does not see the behaviour described here, confirm their plugin version first.

This release is a single fix to the estimated delivery date shown on the **Blocks** checkout page, where the date could lag one shipping-method selection behind. A loading placeholder now covers the moment while a new date is being worked out.

## Included Story Cards

| Story ID | Story Title | Trello card link |
|---|---|---|
| 961 | [Bug Fix] Stale estimated delivery date in Blocks checkout | [961](https://trello.com/c/LJ8nvxfM) |

## 961 - [Bug Fix] Stale estimated delivery date in Blocks checkout

### Brief Description

On the WooCommerce **Blocks** checkout page, the estimated delivery date shown next to the shipping options could go stale. When a customer switched from one shipping method to another, the date sometimes still showed the date belonging to the method they had just moved away from — one selection behind. The page was deciding when to refresh the date from information that changes before the real delivery date is actually known, so it could redraw the date too early, using whatever value it still had.

The date now refreshes only once the confirmed date for the newly chosen method is actually available, so a leftover value from the previous selection can no longer be displayed. While the change is still being worked out, a brief loading placeholder appears where the date sits — the same loading style the checkout page already uses elsewhere, for example on the Subtotal row — and is replaced by the correct date as soon as it is ready.

This matters commercially: a customer choosing an express method and still seeing the standard method's slower date has every reason to abandon the order or to raise a complaint later about a promise the store never actually made.

### Prerequisites

- Plugin version 2.3.1 or later.
- The store must be using the **Blocks** checkout page. The classic shortcode-based cart and checkout use a different display path and were never affected by this problem.
- At least two shipping methods available at checkout, each producing a **different** estimated delivery date — otherwise there is nothing visible to tell a correct date from a stale one.
- Estimated delivery display must already be switched on and configured for the methods being tested, exactly as the merchant normally runs it. No new or changed setting is introduced by this release.

### Step-by-Step Support Walkthrough

**Scenario A — the date follows the selected method**

1. On the front end, add a product to the cart and open the **Blocks** checkout page.
2. Select shipping method A and confirm the estimated delivery date shown matches the date method A's own rule should produce.
3. Select shipping method B and confirm the date updates to method B's correct date — not the date left over from method A.
4. Switch back and forth between A and B several times in quick succession. Confirm the date on screen always belongs to the method currently selected, never to the previous one. Rapid switching was the most reliable way to reproduce the original problem, so this is the step worth repeating.
5. Re-select the shipping method that is already active, so nothing actually changes. Confirm the date does not flicker or change incorrectly.

**Scenario B — the loading placeholder**

6. Switch shipping methods again and watch the place where the delivery date sits.
7. Confirm a loading placeholder appears there while the new rate is being applied, rather than the old date staying on screen.
8. Confirm that placeholder looks like the loading style already used elsewhere on the checkout page, for example on the **Subtotal** row — it should not look like a new or foreign element.
9. Confirm the placeholder is replaced by the correct estimated delivery date once the shipping change finishes.
10. Load the Blocks checkout page fresh, without changing any shipping method. Confirm **no** loading placeholder appears — it belongs only to the moment a change is being processed.

**Scenario C — nothing else has moved**

11. Confirm the estimated delivery date still displays correctly on the classic shortcode-based **cart** and **checkout** pages, not only on Blocks checkout.
12. On the Blocks checkout, apply a coupon and then remove it. Confirm the delivery date neither disappears nor falls back to a stale value.
13. Confirm the estimated delivery date still appears correctly in the other places it is shown: the **product page**, the **shop listing**, the **order email**, and the **order screens in admin**.

### Expected Behaviour

On the Blocks checkout page the estimated delivery date always belongs to the shipping method currently selected. During the moment a change is being applied, the customer sees a familiar loading placeholder instead of a date that may be wrong, and the correct date replaces it once confirmed. First page load shows the date directly with no placeholder. Everywhere else the delivery date appears — classic cart and checkout, product page, shop listing, order emails, admin order screens — behaves exactly as before.

If a merchant reports a wrong date on Blocks checkout after updating, check the two things that decide what a correct date even looks like: whether the methods being compared genuinely produce different dates under their own rules, and whether they are looking at the Blocks checkout rather than the classic one. A date that is genuinely wrong for the selected method under its own rule is a different matter from the staleness fixed here, and is worth raising separately.
