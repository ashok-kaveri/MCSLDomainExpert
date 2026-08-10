# MCSL 384 Support Guide (Sample)

## Included Story Cards
| Story ID | Story Title | Toggle Name | Trello card link |
|---|---|---|---|
| ZI-629 | WooCommerce Composite Products import [#350796] | {accountUUID}.woocommerce.composite.classification.enabled, {accountUUID}.woocommerce.bundle.classification.enabled | [ZI-629](https://trello.com/c/JktOfk88/4678-from-sl-zi-629-woocommerce-composite-products-import-350796) |
| ZI-646 | Delivro carrierCode missing — service fallback [#381046] | None | [ZI-646](https://trello.com/c/dJc4YbM8/4687-from-sl-zi-646-delivro-carriercode-missing-service-fallback-381046) |
| ZI-651 | WSS order updates not syncing after edit [#375662] | {accountUUID}.wc.cancelled.order.reactivation.enabled | [ZI-651](https://trello.com/c/UQPDRAGJ/4692-from-sl-zi-651-wss-order-updates-not-syncing-after-edit-375662) |
| ZI-653 | UPS third party billing in bulk actions [#396557] | None | [ZI-653](https://trello.com/c/PgQDfo9v/4694-from-sl-zi-653-ups-third-party-billing-in-bulk-actions-396557) |
| ZI-655 | Display customer-selected rate amount [#396457] | None | [ZI-655](https://trello.com/c/tInlmtsj/4696-from-sl-zi-655-display-customer-selected-rate-amount-396457) |
| ZI-661 | PostNord currency conversion on zero-value [#394908] | None | [ZI-661](https://trello.com/c/qDLxIVtv/4702-from-sl-zi-661-postnord-currency-conversion-on-zero-value-394908) |

## ZI-629 - WooCommerce Composite Products import [#350796]

### Brief Description

Some WooCommerce merchants sell a product the shopper builds from several parts, using the WooCommerce Composite Products plugin. Until now the app did not recognise that product type, so those products were skipped when products were imported, or they were packed wrongly. From MCSL 384 they import correctly and show up in the Products list, and an order that contains one is split the way the merchant set it up: one line per part when the parts ship separately, or a single line for the whole box when they do not. Checked with USPS and USPS Stamps labels.

### Toggles & Prerequisites

| Toggle / config note | What support should confirm |
|---|---|
| `{accountUUID}.woocommerce.composite.classification.enabled` | Must be ON for build-your-own products and their orders to be recognised |
| `{accountUUID}.woocommerce.bundle.classification.enabled` | Must be ON; also confirm the merchant's existing product bundles still behave as before |
| WooCommerce Composite Products plugin | Confirm the merchant has this plugin installed and active on their store |
| Carrier setup | USPS or USPS Stamps must be set up under hamburger menu > Carriers before a label can be made |

### Step-by-Step Support Walkthrough

**Scenario A — the product imports and looks right**

1. In WooCommerce admin, open the MCSL app, go to hamburger menu > Products and start a product import.
2. Confirm the build-your-own product appears in the Products list with the right name and item code, for example "Create Your Own Gift Box".
3. Open the imported product and check the name, item code, weight and dimensions match what the merchant has in WooCommerce.

**Scenario B — the order imports and a label can be made**

4. In WooCommerce admin, open the MCSL app, go to the ORDERS tab and open an order that contains one of these products.
5. If the merchant set the parts to ship separately, confirm each part shows as its own line with its own weight and dimensions.
6. If the parts are not set to ship separately, confirm the order shows one line for the whole product, using the parent product's dimensions.
7. Open Prepare Shipment and confirm the item count loads with no error.
8. Generate the label with USPS Stamps and confirm it is created with no packaging or validation error.

### Expected Behaviour

| What support should observe | How to confirm |
|---|---|
| Build-your-own products appear in the Products list after import | Products list in the MCSL app, matched against the merchant's WooCommerce catalogue |
| Order lines match how the merchant set the parts up | ORDERS tab — separate lines when parts ship individually, one line when they do not |
| Label is created without an error | Generate a USPS or USPS Stamps label from the order |
| Existing product bundles are unchanged | Import an order with an older bundle product and confirm it behaves as before |

## ZI-651 - WSS order updates not syncing after edit [#375662]

### Brief Description

When a WooCommerce order was cancelled and then put back to Processing, the app did not pick it up again. The order stayed as it was before the cancellation and no new label could be made for it. From MCSL 384, a cancelled order that comes back is brought in fresh instead of being patched, so it is ready for a label again. This applies to WooCommerce only and is controlled by a toggle.

### Toggles & Prerequisites

| Toggle / config note | What support should confirm |
|---|---|
| `{accountUUID}.wc.cancelled.order.reactivation.enabled` | Must be ON for the order to come back automatically; confirm it is set for this merchant's account |
| A disable switch overrides the ON setting | If both the enable and disable settings are present, the old behaviour applies — confirm only the enable one is active |
| Toggle OFF | The order will not come back on its own and someone must import it again by hand |
| WooCommerce only | Does not apply to other store platforms |

### Step-by-Step Support Walkthrough

**Scenario A — toggle ON**

1. Import a WooCommerce order into the MCSL app and confirm it appears in the orders list.
2. Generate a shipping label for that order.
3. In WooCommerce admin, cancel the same order.
4. Change the order status back to Processing in WooCommerce.
5. Wait about 60 seconds for the next sync.
6. Open the MCSL app and confirm the order is back in the list, active, with the current delivery address.
7. Generate a new label and confirm it succeeds.
- Request/log fields to verify: in the sync log for this order, confirm the fall-through entry for the cancelled sub-order is present.

Tell the merchant one thing here: the app does not cancel the earlier label. They must cancel the old label themselves in the carrier's own dashboard before using the new one. This is existing behaviour and a separate card has been raised for it.

**Scenario B — toggle OFF**

8. Repeat steps 1 to 5 with the toggle OFF.
9. Open the MCSL app and check the order.

Expect the order to stay as it was before the cancellation. It will not update on its own and must be imported again by hand.

### Expected Behaviour

| What support should observe | How to confirm |
|---|---|
| The reactivated order is back in the ORDERS list with the current address and items | Check the ORDERS tab about 60 to 75 seconds after the status change; no manual import needed |
| A new label can be created for it | Generate a label from the order |
| With the toggle OFF, nothing updates on its own | The order still shows the details from before the cancellation |

## ZI-653 - UPS third party billing in bulk actions [#396557]

### Brief Description

MCSL 384 adds a **Set UPS Third Party Billing** option to the bulk actions on the ORDERS list. A merchant can now apply one third-party billing account — account number, postal code and country — to several UPS orders at once, instead of setting it one order at a time or through an automation rule. Only orders that have not shipped yet are included; orders that already have a label or have shipped are left out of the batch.

### Toggles & Prerequisites

| Toggle / config note | What support should confirm |
|---|---|
| No toggle | Available in MCSL 384 and later on Shopify |
| UPS must be set up | Confirm UPS is active under hamburger menu > Carriers |
| Orders must be selected first | The option only appears in Bulk Actions after at least one order is ticked |
| Only orders not yet shipped are eligible | Orders that already have a label or have shipped are skipped without a message — check the status column |

### Step-by-Step Support Walkthrough

**Scenario A — applying third-party billing to several orders**

1. In Shopify Admin > Apps > PH Multi Carrier Shipping Label App, open the ORDERS tab.
2. Tick one or more UPS orders that have not shipped yet.
3. Open Bulk Actions and confirm **Set UPS Third Party Billing** is listed.
4. Click it and confirm the box opens with Account Number, Billing Postal Code and Billing Country.
5. Enter valid details, for example account `V45V34`, postal code `98055`, country United States or Canada, and submit.
- Request node to verify: POST /bulkaction/upsthirdpartybilling body → { data: { accountNumber, billingPostalCode, billingCountry }, orders: [...] }; UPS payload → ShipmentCharge.BillThirdParty
6. Confirm the message reads "Updated N of N orders" and the list refreshes.

**Scenario B — nothing selected, or orders that cannot be changed**

7. Tick only orders that have already shipped and try the action. Confirm the message says third-party billing can only be set for orders that have not shipped, and the box does not open.
8. With no orders ticked, confirm the message asks the merchant to select one or more orders, and nothing opens.

### Expected Behaviour

| What support should observe | How to confirm |
|---|---|
| "Updated N of N orders" message and a refreshed list | ORDERS tab, straight after submitting |
| The printed label shows third-party billing | Print the label for one of the updated orders |
| The billing details sent to UPS match what was entered | hamburger menu > Settings > Request Log for that order |
| Already-shipped orders are untouched | Their billing details are unchanged after the bulk action |

## ZI-655 - Display customer-selected rate amount [#396457]

### Brief Description

MCSL 384 adds a **Customer selected rate** line to the order page in the app. It shows the delivery option the shopper picked at checkout, with the carrier name and the amount they paid, so support and merchants no longer have to go back to the store admin to look it up. It is for reading only and changes nothing about how rates are worked out or labels are made. Available on Shopify and WooCommerce, for FedEx, UPS, DHL and USPS.

### Toggles & Prerequisites

| Toggle / config note | What support should confirm |
|---|---|
| No toggle | Always on from MCSL 384 on Shopify and WooCommerce |
| Store must be on MCSL 384 | Check the app version before investigating a missing line |
| The checkout choice must have been captured | Orders placed before this release, draft orders, and orders where no delivery option was captured will show blank — this is expected |
| Reading only | Make sure the merchant understands this value does not pre-select anything when a label is made |

### Step-by-Step Support Walkthrough

**Scenario A — the line shows the right thing**

1. In Shopify admin or WooCommerce admin, open the MCSL app and go to the ORDERS tab.
2. Open an order placed after MCSL 384 where the shopper chose a delivery option at checkout.
3. Find **Customer selected rate** on the order page and confirm it shows the carrier name and amount, for example "UPS Ground — $12.45", in the currency used at checkout.
4. Open a second order for a different carrier and confirm it shows that carrier's option and amount.

**Scenario B — it does not affect labels**

5. On an order where the line is filled in, open Prepare Shipment.
6. Confirm the rate list is worked out fresh and nothing is pre-selected to match the amount on the line.
7. Pick a different option, generate the label, and confirm the label follows what was picked, not the amount on the line.
8. Open an older order or a draft order and confirm the line is blank, with no errors and nothing else missing from the page.

### Expected Behaviour

| What support should observe | How to confirm |
|---|---|
| **Customer selected rate** shows carrier and amount on the order page | Orders placed after MCSL 384 where a checkout choice was captured |
| Blank for older or draft orders | Open a pre-release order; the rest of the page still loads normally |
| Labels are unaffected | Generate a label with a different option and confirm the label follows the choice made at label time |

## Technical Cards

### ZI-646 - Delivro carrierCode missing — service fallback [#381046]

Delivro rates could fail to appear at checkout when the stored carrier record was missing its internal carrier code (`carrierCode`), because the app then built an incomplete service reference. The app now works the code out from the carrier's name when the field is missing, so rates keep working instead of failing. No toggle and nothing for the merchant to change. Other carriers are unaffected. If a merchant still reports missing Delivro rates on MCSL 384, check the request log for that rate request and confirm the service reference is complete.

### ZI-661 - PostNord currency conversion on zero-value [#394908]

On BigCommerce stores, a PostNord shipment for a zero-value order was sent with a placeholder value of 1 in the store's own currency instead of Swedish krona, so the declared value could be wrong or the conversion could fail. Zero-value orders now send 1 Swedish krona and convert correctly, which is what shows in the rate summary and on the label. Orders with a real value are unchanged, and WooCommerce PostNord is unchanged. No toggle and nothing for the merchant to change.
