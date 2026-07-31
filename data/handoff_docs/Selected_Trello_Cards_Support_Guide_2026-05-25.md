PH
PLUGINHIVE
# MCSL 1.0.380 Release
Support Guide - Story Card Package
May 25, 2026

| Document scope | This package covers the selected Trello cards shared for support enablement. It focuses on what support should verify, what merchants will experience, the important toggles or prerequisites, and the main caveats to keep in mind during customer-facing conversations. |
| --- | --- |

# Included Story Cards
| Story | Support topic | Primary area |
| --- | --- | --- |
| ZI-511 | Stripe `invoice.created` subscription matching | WooCommerce WSS billing and subscription webhook handling |
| ZI-510 | TNT Express special-character and long-name label stability | Shopify MCSL TNT Express label generation |
| ZI-508 | Edit Package restored for FedEx REST | WooCommerce ORDERS package editing |
| ZI-506 | Auto-sync WooCommerce order edits after import | WooCommerce order import and WSS order updates |
| ZI-496 | Bundled Products weight ignore handling | WooCommerce bundled-product weight calculation |
| ZI-474 | Estimated delivery shown as date instead of day count | BigCommerce checkout estimated delivery display |
| ZI-515 | Buffer days for FedEx REST estimated delivery | Shopify carrier settings and estimated delivery |
| ZI-516 | Buffer days for TNT Australia estimated delivery | Shopify carrier settings and estimated delivery |
| ZI-099 | Delivro carrier integration | WooCommerce carrier setup, validation, and label flow |
| ZI-517 | Preserve customer-selected PostNord service point | Shopify automation rules and service-point handling |
| ZI-518 | APC REST carrier integration | Shopify carrier setup, rates, and label creation |
| ZI-519 | FedEx REST dangerous goods / hazmat support | Shopify DG configuration and FedEx REST shipment flow |
| ZI-482 | TNT Australia fallback rates | Shopify and WooCommerce checkout-rate continuity |
| FED-QU | Quantity-units configuration option | FedEx customs quantity-units setting in carrier configuration and bulk actions |

# Table of Contents
Selected Trello support-ready story cards
| Card | Description | Section |
| --- | --- | --- |
| ZI-511 | Stripe `invoice.created` webhook fails to match internal subscription | 1 |
| ZI-510 | TNT Express label fail when product name contains `&` or exceeds length | 2 |
| ZI-508 | Edit Package feature for FedEx REST API accounts | 3 |
| ZI-506 | Auto-sync WooCommerce order updates into WSS after import | 4 |
| ZI-496 | Bundled Products honor Assembled Weight Ignore | 5 |
| ZI-474 | Estimated delivery date showing days instead of date format | 6 |
| ZI-515 | Add buffer days to estimated delivery for FedEx REST | 7 |
| ZI-516 | Add buffer days to estimated delivery for TNT Australia | 8 |
| ZI-099 | Delivro carrier integration request | 9 |
| ZI-517 | PostNord automation rule overrides customer-selected service point | 10 |
| ZI-518 | APC REST API integration for Shopify MCSL | 11 |
| ZI-519 | FedEx REST Dangerous Goods / Hazmat integration | 12 |
| ZI-482 | TNT Australia fallback rates | 13 |
| FED-QU | Add Quantity Units Configuration Option in Carrier Settings | 14 |

CARD 1/14
# ZI-511
# ZI-511 — Stripe `invoice.created` webhook fails to match internal subscription
| Ticket | #387108 |
| --- | --- |
| Release | Selected card package |
| Area | WooCommerce WSS billing and subscription webhook handling |
| Trello | https://trello.com/c/X9PvQPjU/4392-from-sl-zi-511-stripe-invoicecreated-webhook-fails-to-match-internal-subscription-387108 |
| Support scope | WooCommerce WSS billing flow only. This is not a carrier, label, or ORDERS-tab issue. |

# Support Guide: ZI-511
## From SL: ZI-511 — Stripe `invoice.created` webhook fails to match internal subscription [#387108]
## Feature Summary
Stripe `invoice.created` events were using the wrong identifier when matching an internal subscription, so valid billing events could fall into the no-match alert path and leave the merchant's billing state stale. The fix ensures the webhook uses the subscription identifier from the invoice payload and updates the correct subscription and payment record.
## Toggles & Prerequisites
| Toggle / config note \| No feature toggle. Confirm the store is in the WooCommerce WSS billing scope and the event being reviewed is `invoice.created`. |
| --- |

- Confirm the issue is in the subscription or billing area of the WSS app, not in label generation or carrier settings.
- Use a store with an active subscription whose Stripe `sub_*` value is known.
- If support is checking a historical failure, gather the Stripe event ID and approximate event time before asking engineering to investigate.

## Step-by-Step Support Walkthrough
1. Open the affected WooCommerce WSS store and navigate to the subscription or billing area.
2. Confirm the merchant symptom: stale payment status, unmatched subscription state, or prior no-match alert on a valid subscription.
3. Reprocess or inspect the relevant `invoice.created` event and verify the subscription in the app moves to the expected active or paid state.
4. Review the webhook log or billing log for the matching event.
- Request/log fields to verify: `event.type=invoice.created`, `invoice.subscription`, the matched internal `paymentSubscriptionID`, and the absence of lookup behavior based on `invoice.lines.data[0].id`.
5. If the subscription ID is genuinely unknown, confirm the alert path still triggers so support is notified only for real mismatches.

## Expected Behaviour
| What support should observe \| How to confirm |
| --- | --- |
| Valid `invoice.created` events update the correct subscription record. | The billing or subscription page shows the expected active or paid state after processing. |
| Payment history reflects the latest invoice rather than leaving an unmatched state. | Check the billing view or payment record for the recent invoice details. |
| Only truly unknown subscriptions trigger the no-match support alert. | Review the webhook log outcome for a known-valid event versus an intentionally unknown `sub_*` event. |

## Merchant-Safe Explanation
You can explain this as a billing reliability fix. When Stripe sends a normal invoice-created event for an active subscription, the app now matches it correctly and keeps the merchant's subscription status in sync.

CARD 2/14
# ZI-510
# ZI-510 — TNT Express label fail when product name contains `&` or exceeds length
| Ticket | #387029 |
| --- | --- |
| Release | MCSL 380 |
| Area | Shopify MCSL TNT Express label generation |
| Trello | https://trello.com/c/UiynoCKm/4393-from-sl-zi-510-tnt-express-label-fail-when-product-name-contains-or-exceeds-length-387029 |
| Support scope | Shopify MCSL, TNT Express label generation, routing-label name-length safety |

# Support Guide: ZI-510
## From SL: ZI-510 — TNT Express label fail when product name contains `&` or exceeds length [#387029]
## Feature Summary
TNT Express label creation could fail when product names included ampersands or when merchant or recipient text exceeded TNT limits. The fix sanitizes the request values and trims overlong text safely so TNT label generation succeeds without throwing an internal error.
## Toggles & Prerequisites
| Toggle / config note \| No toggle. Confirm the order is using TNT Express and contains the long-name or special-character data that previously broke the request. |
| --- |

- Use a Shopify order in the MCSL ORDERS flow with TNT Express selected.
- Include a product name containing `&`, or a very long product or recipient/company name, when reproducing the original problem.
- If routing labels are part of the merchant flow, include an overlong recipient company name in the validation sample.

## Step-by-Step Support Walkthrough
1. Open the TNT Express order in Shopify MCSL and confirm the problematic text is present in the order or product details.
2. Generate the label from the ORDERS tab.
3. If the merchant uses routing labels, inspect the generated output for long company names and confirm the value is trimmed safely instead of breaking the request.
4. Review the TNT request log for the generated label.
- Request nodes to verify: `pieceReference` and `goodsDescription` should contain TNT-safe values after sanitization and length handling.
5. If services are initially blank, refresh rates once and then continue label verification; the final label flow should still complete successfully.

## Expected Behaviour
| What support should observe \| How to confirm |
| --- | --- |
| TNT labels generate even when product names include ampersands. | A valid label is created without the prior internal error. |
| Long merchant or recipient text no longer blocks label generation. | The label request completes and the output shows safely handled text. |
| Multi-product TNT orders continue to work. | Validate a sample order with more than one line item and confirm label success. |

## Merchant-Safe Explanation
You can describe this as a TNT compatibility fix. Special characters and long item names are now handled more safely, so merchants do not have to rename products just to create a label.

CARD 3/14
# ZI-508
# ZI-508 — Edit Package feature for FedEx REST API accounts
| Ticket | #377088 |
| --- | --- |
| Release | MCSL 380 |
| Area | WooCommerce ORDERS package editing |
| Trello | https://trello.com/c/2akpFmzy/4394-from-sl-zi-508-edit-package-feature-for-fedex-rest-api-accounts-regression-after-soap%E2%86%92rest-migration-377088 |
| Support scope | WooCommerce, FedEx REST accounts only, Edit Package action in ORDERS |

# Support Guide: ZI-508
## From SL: ZI-508 — Edit Package feature for FedEx REST API accounts (regression after SOAP→REST migration) [#377088]
## Feature Summary
After the FedEx SOAP-to-REST migration, FedEx REST accounts lost the Edit Package capability even though the older FedEx SOAP path still supported it. This fix restores the Edit Package action for FedEx REST orders and keeps the edited package values available in the normal order flow.
## Toggles & Prerequisites
| Toggle / config note \| `accnt-uuid.declared.value.recalculation.on.manual.package.edit.enabled` should be enabled for the target account when validating declared-value recalculation behavior during manual package edits. Also confirm the order is using a FedEx REST account and that the store is on the release containing the FedEx REST allowlist fix. |
| --- |

- Validate only on FedEx REST orders, not FedEx SOAP.
- Use an order that already has package details loaded so support can confirm the edit modal pre-fills correctly.
- If the Edit Package action is missing entirely, capture the carrier type shown on the order before escalation.

## Step-by-Step Support Walkthrough
1. Open a FedEx REST order in WooCommerce MCSL ORDERS.
2. Use the order action menu to open Edit Package.
3. Confirm the modal opens without error and that existing package dimensions and weight are prefilled.
4. Edit package values, save the change, and re-check the order package summary or subsequent rate/label flow.
5. If available, compare with a FedEx SOAP order only to confirm this fix was specifically for the REST parity gap.

## Expected Behaviour
| What support should observe \| How to confirm |
| --- | --- |
| Edit Package is visible and usable for FedEx REST orders. | The action appears in the order UI and opens the modal successfully. |
| Existing package values are loaded into the modal. | Current dimensions and weight appear before editing. |
| Saved edits persist into the package flow. | Re-open the modal or proceed to the next rate or label step and confirm the new values are used. |

## Merchant-Safe Explanation
You can explain this as a FedEx REST parity fix. Merchants using the newer FedEx REST connection can again update package details in the same workflow they previously used.

CARD 4/14
# ZI-506
# ZI-506 — Auto-sync WooCommerce order updates (address, items) into WSS after import
| Ticket | #375662 |
| --- | --- |
| Release | MCSL 380 |
| Area | WooCommerce order import and WSS order updates |
| Trello | https://trello.com/c/Xd3NhcrA/4395-from-sl-zi-506-auto-sync-woocommerce-order-updates-address-items-into-wss-after-import-375662 |
| Support scope | WooCommerce order updates after import, address and item changes, pre-label update path |

# Support Guide: ZI-506
## From SL: ZI-506 — Auto-sync WooCommerce order updates (address, items) into WSS after import [#375662]
## Feature Summary
Once an order had been imported into WSS, later WooCommerce edits to the shipping address or line items were not always reflected in the existing WSS order. This fix lets supported order updates flow back into the imported order record automatically when the webhook update arrives.
## Toggles & Prerequisites
| Toggle / config note \| `accountUUID.wc.order.sync.enabled` must be enabled for the store/account. |
| --- |

- Validate on a WooCommerce store where the order has already been imported into WSS.
- Use a test order that has not progressed into a downstream shipping state that intentionally blocks updates.
- Cover both address edits and item edits during support validation when possible.

## Step-by-Step Support Walkthrough
1. Confirm the target WooCommerce store has the order auto-sync feature enabled for the account.
2. Import or locate an order already present in WSS.
3. Update the shipping address or line items in WooCommerce.
4. Wait for or trigger the WooCommerce `order.updated` webhook and then reopen the order in WSS.
5. Verify the changed address or items are reflected in the WSS order without needing a manual re-import.
- Request/log fields to verify: the WooCommerce `order.updated` webhook event, the matched imported order, and the updated address or line-item data written back into the WSS order record.

## Expected Behaviour
| What support should observe \| How to confirm |
| --- | --- |
| Shipping-address edits sync into the imported WSS order. | Compare the WooCommerce address with the reopened WSS order summary. |
| Item updates sync into the imported WSS order. | Compare the updated line items in WooCommerce to the order contents in WSS. |
| Manual re-import is no longer required for supported update timing. | The existing WSS order changes after the update webhook is processed. |

## Merchant-Safe Explanation
You can explain this as an order-sync improvement. If a merchant corrects the order after import but before shipping progresses too far, the app is better able to reflect those changes without forcing a duplicate import flow.

CARD 5/14
# ZI-496
# ZI-496 — WooCommerce Bundled Products honor Assembled Weight Ignore
| Ticket | #260001 |
| --- | --- |
| Release | MCSL 380 |
| Area | WooCommerce bundled-product weight calculation |
| Trello | https://trello.com/c/ud3ClOnU/4398-from-sl-zi-496-woocommerce-bundled-products-honor-assembled-weight-ignore-setting-260001 |
| Support scope | WooCommerce bundle import and order-summary weight behavior |

# Support Guide: ZI-496
## From SL: ZI-496 — WooCommerce Bundled Products honor Assembled Weight Ignore [#260001]
## Feature Summary
WooCommerce bundle orders were counting both the bundle parent and all child products even when the bundle was configured to ignore assembled child weight. This fix makes the imported shipping data honor the bundle setting so support and merchants see the expected weight calculation in the order summary.
## Toggles & Prerequisites
| Toggle / config note \| `account.woocommerce.bundle.classification.enabled: true` should be enabled for the target account. Use live account state as the source of truth before testing. |
| --- |

- Validate on WooCommerce with the bundled-products setup that originally reproduced the issue.
- Use a bundle product configured with Assembled Weight = Ignore.
- If the merchant has multiple bundle-related toggles, capture the live state rather than relying on card text alone.

## Step-by-Step Support Walkthrough
1. Confirm the bundle product is configured in WooCommerce with Assembled Weight set to Ignore.
2. Import or open an order containing that bundle inside the MCSL order flow.
3. Review the order summary weight and package calculation shown for the bundle.
4. Compare the result against the expected parent-weight-only behavior from the merchant's WooCommerce configuration.
5. If needed, inspect the import or classification evidence.
- Request/log fields to verify: bundle parent-versus-child line-item classification and the final weight values applied to the imported shipment.

## Expected Behaviour
| What support should observe \| How to confirm |
| --- | --- |
| Bundle child weight is not added on top of the parent when Ignore is configured. | Compare the expected bundle weight from WooCommerce to the order summary in MCSL. |
| The imported order reflects the merchant's configured bundle behavior. | Open the WooCommerce bundle settings and verify they match the order summary outcome. |
| Bundle-related shipment calculations are more predictable for support. | Re-check a bundle order with known values and confirm the output is stable. |

## Merchant-Safe Explanation
You can explain this as a bundled-product weight-fix. If the merchant intentionally set the bundle to ignore the assembled child weight, the shipping workflow now respects that choice more consistently.

CARD 6/14
# ZI-474
# ZI-474 — Estimated delivery date showing days instead of date format
| Ticket | #345572 |
| --- | --- |
| Release | MCSL 380 |
| Area | BigCommerce checkout estimated delivery display |
| Trello | https://trello.com/c/a5XJ85y9/4401-from-sl-zi-474-estimated-delivery-date-showing-days-instead-of-date-format-345572 |
| Support scope | BigCommerce checkout date formatting, estimated-delivery setting enabled |

# Support Guide: ZI-474
## From SL: ZI-474 — Estimated delivery date showing days instead of date format [#345572]
## Feature Summary
BigCommerce checkout was showing a relative day count instead of a formatted delivery date even when the estimated-delivery feature was enabled. This fix keeps the actual delivery date available so checkout can display a merchant-friendly calendar date.
## Toggles & Prerequisites
| Toggle / config note \| `isEstimatedDeliveryAtCheckoutRequired` must be enabled for the BigCommerce store. |
| --- |

- Validate on BigCommerce checkout, not only inside internal admin screens.
- Use a carrier and lane that returns estimated-delivery data.
- If the store is using FedEx for the reported scenario, keep FedEx in the sample path unless the merchant proves another carrier is affected.

## Step-by-Step Support Walkthrough
1. Confirm the BigCommerce store has estimated delivery enabled in the MCSL app.
2. Create or use a checkout scenario that returns live delivery data.
3. Open checkout and inspect how the delivery promise is shown next to the shipping option.
4. Compare the displayed value against the actual delivery date expected from the carrier response.
5. If the merchant reports a regression, inspect the rate or checkout data.
- Request/response nodes to verify: the carrier delivery date value used for checkout display, such as `operationalDetail.deliveryDate`, and the final formatted date shown to the buyer.

## Expected Behaviour
| What support should observe \| How to confirm |
| --- | --- |
| Checkout shows a calendar date rather than only a day count. | Review the displayed estimated-delivery text on BigCommerce checkout. |
| The date matches the carrier-returned estimated delivery. | Compare checkout output with the underlying delivery-date response. |
| The feature remains controlled by the merchant setting. | Toggle the feature state in a test store and confirm the display follows the setting. |

## Merchant-Safe Explanation
You can explain this as a checkout clarity improvement. Instead of showing a vague number of days, the shipping option can now show a clearer expected delivery date when the merchant has that feature enabled.

CARD 7/14
# ZI-515
# ZI-515 — Add buffer days to estimated delivery for FedEx REST
| Ticket | #388085 |
| --- | --- |
| Release | MCSL 380 |
| Area | Shopify carrier settings and estimated delivery |
| Trello | https://trello.com/c/2hODchcf/4402-from-sl-zi-515-add-buffer-days-to-estimated-delivery-fedex-rest-soap-parity-gap-388085 |
| Support scope | Shopify MCSL, FedEx REST carrier settings, estimated delivery buffer control |

# Support Guide: ZI-515
## From SL: ZI-515 — Add buffer days to estimated delivery — FedEx REST (SOAP parity gap) [#388085]
## Feature Summary
FedEx REST accounts were missing the buffer-days control that older FedEx SOAP setups already had. This fix exposes the buffer-days field for FedEx REST and applies the saved value to estimated-delivery calculations.
## Toggles & Prerequisites
| Toggle / config note \| No separate feature toggle mentioned for support use. Confirm the store is using a FedEx REST carrier account and the field is available in carrier Other Details. |
| --- |

- Validate in Shopify MCSL on a FedEx REST account.
- Use an order or rate lookup where estimated delivery is visible so the buffer change can be observed.
- Test at least one value inside the supported 0 to 10 day range.

## Step-by-Step Support Walkthrough
1. Open Shopify MCSL and edit the FedEx REST carrier from hamburger menu > Carriers.
2. Go to Other Details and locate the buffer-days field for estimated delivery.
3. Save a supported value between 0 and 10.
4. Run a rate or checkout verification flow where estimated delivery is displayed.
5. Confirm the displayed estimated delivery reflects the configured extra days.
- Request/log fields to verify: the saved buffer-days value and the estimated-delivery output after the adjustment is applied.

## Expected Behaviour
| What support should observe \| How to confirm |
| --- | --- |
| FedEx REST shows the buffer-days field in carrier settings. | Open Other Details and verify the field is present. |
| Values from 0 to 10 can be saved and validated. | Save a test value and confirm no validation error occurs within range. |
| Estimated delivery reflects the configured buffer. | Compare delivery output before and after changing the field. |

## Merchant-Safe Explanation
You can explain this as a delivery-promise configuration option. Merchants using FedEx REST can add a small cushion to the estimated delivery shown to customers, matching what earlier FedEx setups already supported.

CARD 8/14
# ZI-516
# ZI-516 — Add buffer days to estimated delivery for TNT Australia
| Ticket | #379692 |
| --- | --- |
| Release | MCSL 380 |
| Area | Shopify carrier settings and estimated delivery |
| Trello | https://trello.com/c/OTTLqidH/4403-from-sl-zi-516-add-buffer-days-to-estimated-delivery-tnt-australia-379692 |
| Support scope | Shopify MCSL, TNT Australia carrier settings, estimated delivery buffer control |

# Support Guide: ZI-516
## From SL: ZI-516 — Add buffer days to estimated delivery — TNT Australia [#379692]
## Feature Summary
TNT Australia did not expose the same buffer-days estimated-delivery control available in other carrier paths. This fix adds the setting to TNT Australia so support and merchants can intentionally pad the shown delivery promise.
## Toggles & Prerequisites
| Toggle / config note \| No separate support-side toggle is required in the card notes. Confirm TNT Australia is the configured carrier and validate within the 0 to 10 day range. |
| --- |

- Validate on a TNT Australia account in Shopify MCSL.
- Use a flow where estimated delivery is visible to support or to the buyer.
- If the merchant is discussing rollout timing, confirm there is no additional hidden dependency before promising the field.

## Step-by-Step Support Walkthrough
1. Open the TNT Australia carrier configuration from hamburger menu > Carriers.
2. Go to the Other Details section and locate the Add Buffer Days to Estimated Delivery field.
3. Save a value between 0 and 10.
4. Run the estimated-delivery flow and verify the displayed date or timing reflects the additional days.
5. Re-test with a different in-range value if the merchant needs proof the setting is active.

## Expected Behaviour
| What support should observe \| How to confirm |
| --- | --- |
| TNT Australia displays the buffer-days field. | Open carrier Other Details and verify the field is present. |
| In-range values save correctly. | Save values inside 0 to 10 and confirm they persist. |
| The estimated-delivery output reflects the configured extra days. | Compare the visible delivery estimate before and after the change. |

## Merchant-Safe Explanation
You can explain this as a checkout-expectation setting. The merchant can intentionally add a few extra days to the shown delivery estimate when TNT Australia needs a safer promise window.

CARD 9/14
# ZI-099
# ZI-099 — Delivro carrier integration request
| Ticket | #381046 |
| --- | --- |
| Release | MCSL 380 scope with prior 379 references on the card |
| Area | WooCommerce carrier setup, validation, and label flow |
| Trello | https://trello.com/c/LdCZfIeq/4400-from-sl-zi-099-delivro-carrier-integration-request-381046 |
| Support scope | WooCommerce Delivro integration only. Exclude stale FedEx, UPS, and DHL labels on the card. |

# Support Guide: ZI-099
## From SL: ZI-099 — Delivro carrier integration request [#381046]
## Feature Summary
This card adds Delivro as a WooCommerce carrier integration using the DispatchScience API path. Support should treat the main scope as carrier setup, credential validation, service selection, label generation, and tracking visibility, while also keeping in mind that QA captured a few caveats during testing that may still require escalation if reproduced.
## Toggles & Prerequisites
| Toggle / config note \| The store must have the `request` or `Requests` feature enabled before QA-style request-log verification is available. |
| --- |

- Validate only in WooCommerce MCSL with Delivro selected as the carrier.
- Do not use stale carrier labels from the card to broaden scope to FedEx, UPS, or DHL.
- Use merchant-approved Delivro credentials already configured in the store; do not share or restate credentials in support documentation or customer communication.

## Step-by-Step Support Walkthrough
1. Open WooCommerce MCSL carrier settings and verify Delivro appears in the Add Carrier list alongside other supported carriers.
2. Open the Delivro configuration form and confirm the expected credential fields and validation action are present.
3. Validate the Delivro connection and confirm a readable success or failure message is shown.
4. Open a Delivro-ready order, select a Delivro service, and generate a label.
5. Review the request log and order output.
- Request/log fields to verify: Delivro request success for validation and label creation, selected `service` code, package dimensions, converted weight, generated tracking value, and whether the returned label reflects requested special services when applicable.

## Expected Behaviour
| What support should observe \| How to confirm |
| --- | --- |
| Delivro can be added and validated as a distinct WooCommerce carrier. | The carrier appears in settings and saves successfully after valid credential validation. |
| Supported Delivro services are available during label generation. | Open the service selector and confirm it shows Delivro-only service options. |
| Label generation returns a label and tracking number for supported requests. | Generate a supported label and review the order detail or download output. |

## Merchant-Safe Explanation
You can explain this as a new carrier-connectivity option. Merchants who use Delivro can configure it directly in the WooCommerce MCSL flow and use it in the same order workflow as their other connected carriers.

CARD 10/14
# ZI-517
# ZI-517 — PostNord automation rule overrides customer-selected service point
| Ticket | #387640 |
| --- | --- |
| Release | MCSL 380 |
| Area | Shopify automation rules and service-point handling |
| Trello | https://trello.com/c/M9VT6Yc2/4404-from-sl-zi-517-postnord-automation-rule-overrides-customer-selected-service-point-387640 |
| Support scope | Shopify MCSL, PostNord service-point selection, automation precedence |

# Support Guide: ZI-517
## From SL: ZI-517 — PostNord automation rule overrides customer-selected service point [#387640]
## Feature Summary
A PostNord automation rule that assigned a default service point could overwrite the service point already chosen by the buyer at checkout. The fix preserves the buyer's selected service point and only falls back to the automation rule when the order does not already contain a customer selection.
## Toggles & Prerequisites
| Toggle / config note \| No extra feature toggle called out. Confirm the store uses PostNord service-point checkout and has an automation rule configured for the fallback path. |
| --- |

- Validate on Shopify MCSL with PostNord and service-point checkout support enabled.
- Use one scenario where the customer selected a service point and one where they did not.
- Keep the automation rule active during testing so support can confirm the precedence logic.

## Step-by-Step Support Walkthrough
1. Open a PostNord order where the customer selected a service point at checkout.
2. Confirm the store also has a default PostNord service-point automation rule configured.
3. Generate the shipping flow or inspect the service-point handling in the order.
4. Verify the order continues to use the customer's chosen service point instead of the automation fallback.
5. Run a second control case with no customer-selected service point and confirm the automation fallback is applied there.
- Request/log fields to verify: customer pickup-location data such as `order.localPickupLocation.*` and the final `deliveryParty` or service-point value sent for label creation.

## Expected Behaviour
| What support should observe \| How to confirm |
| --- | --- |
| Customer-selected service points are preserved. | Compare the checkout-selected service point to the value used in the shipment flow. |
| Automation fallback only applies when no customer service point exists. | Test a control order without a customer selection and verify the fallback value is used. |
| Removing the service-point action does not break customer-selected orders. | Recheck the order behavior after adjusting the automation action in a test store. |

## Merchant-Safe Explanation
You can explain this as a checkout-choice protection fix. If the buyer already chose a PostNord pickup point, the app now respects that choice instead of silently replacing it with the merchant's automation fallback.

CARD 11/14
# ZI-518
# ZI-518 — APC REST API integration for Shopify MCSL
| Ticket | #389070 |
| --- | --- |
| Release | MCSL 380 |
| Area | Shopify carrier setup, rates, and label creation |
| Trello | https://trello.com/c/XWNW05G3/4405-from-sl-zi-518-apc-rest-api-integration-for-shopify-mcsl-389070 |
| Support scope | Shopify APC REST setup, rate lookup, and supported international label generation |

# Support Guide: ZI-518
## From SL: ZI-518 — APC REST API integration for Shopify MCSL [#389070]
## Feature Summary
This card completes APC support for carrier validation and label creation through the REST path, aligning those flows with APC areas that were already using REST. Support should treat the main merchant-facing scope as APC setup, service availability, supported international label generation, and readable error handling when APC rejects the request.
## Toggles & Prerequisites
| Toggle / config note \| Use an APC REST-capable store and supported APC credentials. Tracking was noted as disabled in QA notes; do not promise tracking parity from this card alone. |
| --- |

- Validate only on APC international shipments because APC domestic US-to-US shipping is not in scope here.
- Use a service that QA already confirmed as supported for successful label generation when demonstrating the flow.
- Do not promise manifest, pickup, or returns from this card.

## Step-by-Step Support Walkthrough
1. Open APC carrier setup and confirm the store can register APC with the expected credential fields and sender-location options.
2. Validate the APC carrier connection and confirm the result is readable rather than a legacy SOAP-style failure.
3. Run an APC rate or label flow for a supported international shipment.
4. Generate a label for a supported APC service and confirm the order receives the expected label output.
5. Review the APC request log when support needs proof of service mapping.
- Request/log fields to verify: REST validation or shipment success, the APC `service` code used for the request, and the resulting label or error outcome for that code.

## Expected Behaviour
| What support should observe \| How to confirm |
| --- | --- |
| APC carrier validation and label creation run through REST. | Validate the carrier and generate a supported label while reviewing the request path. |
| Supported APC international services can be selected and used. | Confirm the service selector contains APC-specific codes mapped for the store. |
| Unsupported or invalid APC requests fail with readable output. | Submit an invalid scenario and confirm the merchant sees a clear error instead of an opaque transport failure. |

## Merchant-Safe Explanation
You can explain this as a carrier-integration modernization. APC setup and label creation now follow the newer REST path, which improves consistency with the rest of the APC experience inside the app.

CARD 12/14
# ZI-519
# ZI-519 — FedEx REST Dangerous Goods / Hazmat integration
| Ticket | #389072 |
| --- | --- |
| Release | MCSL 380 |
| Area | Shopify DG configuration and FedEx REST shipment flow |
| Trello | https://trello.com/c/uE0fFUGm/4406-from-sl-zi-519-fedex-rest-dangerous-goods-dg-hazmat-integration-389072 |
| Support scope | Shopify MCSL, FedEx REST DG configuration, supported hazmat shipment path |

# Support Guide: ZI-519
## From SL: ZI-519 — FedEx REST Dangerous Goods (DG) / Hazmat integration [#389072]
## Feature Summary
This card introduces supported Dangerous Goods handling for FedEx REST shipments, closing a key parity gap from older FedEx assumptions. Support should treat the current scope carefully: it is not a blanket DG enablement for every lane or account, and the card explicitly documents toggle-controlled behavior plus a limited supported commodity and regulation set.
## Toggles & Prerequisites
| Toggle / config note \| Use live store/account state for `fedex.rest.dg.enabled.after.store.createdAt.greater.than`, `accountUUID.fedex.rest.dg.enabled`, and `accountUUID.fedex.rest.dg.disabled`. |
| --- |

- Current supported scope called out on the card: `LIMITED_QUANTITIES_COMMODITIES` with regulations `DOT`, `IATA`, and `ORMD`.
- Use a supported FedEx REST DG account and shipment lane before promising end-to-end success.
- Battery behavior should remain available even when the DG switch is off, so keep non-DG battery checks separate from full DG verification.

## Step-by-Step Support Walkthrough
1. Confirm the account-level DG toggle state before testing and verify the store is allowed into the FedEx REST DG path.
2. Open the product or shipment DG configuration area and confirm the hazardous-goods details expected for the supported scenario are present.
3. Generate a FedEx REST shipment using a supported DG scenario.
4. Verify that the label and any applicable hazardous-goods documents are returned only when the shipment is within the supported scope.
5. Review the request path for DG-specific evidence.
- Request/response nodes to verify: the FedEx DG shipment path, the dangerous-goods details included in rates or shipment requests when the toggle is ON, the selected regulation, and the absence of DG details when the toggle is OFF for non-supported DG cases.

## Expected Behaviour
| What support should observe \| How to confirm |
| --- | --- |
| Supported DG shipments use the FedEx REST hazardous-goods flow successfully. | Generate a supported DG shipment and verify label plus applicable documentation output. |
| Unsupported lanes or invalid DG setups fail clearly rather than appearing successful. | Submit a non-supported or invalid DG case and review the returned validation outcome. |
| Standard non-DG FedEx REST shipments are not regressed. | Run a normal FedEx REST shipment and confirm it still behaves as expected. |

## Merchant-Safe Explanation
You can explain this as controlled hazmat support for supported FedEx REST scenarios. Merchants in the supported scope can use the app for those DG shipments more directly, while unsupported DG cases still need a clear validation outcome rather than a silent or misleading success.

CARD 13/14
# ZI-482
# ZI-482 — TNT Australia fallback rates
| Ticket | #384139 |
| --- | --- |
| Release | Selected card package |
| Area | Shopify and WooCommerce checkout-rate continuity |
| Trello | https://trello.com/c/Ia9Qpqzx/4411-from-sl-zi-482-store-pickup-orders-blocked-after-store-closing-ti-384139 |
| Support scope | TNT Australia fallback rates for Shopify and WooCommerce. The live card body clearly describes fallback-rates behavior even though the card title is stale. |

# Support Guide: ZI-482
## From SL: ZI-482 — TNT Australia fallback rates [#384139]
## Feature Summary
This card adds fallback shipping rates for TNT Australia so checkout can still show a usable shipping option when the live TNT API is unavailable. The feature is meant to protect checkout conversion during TNT outages or broken response windows, while still making it visible to support that the order used a fallback path.
## Toggles & Prerequisites
| Toggle / config note \| Live toggle state matters. Examples on the card include `carriers.tntAustralia.fallbackRates.enabled`, per-account enable, date-based enable, and per-account disable overrides. |
| --- |

- Trust live toggle state over the stale card title when validating this feature.
- Configure fallback services in the TNT Australia carrier-services area before testing checkout behavior.
- The card notes say fallback rates should not appear for international shipments, so keep the main demo case domestic unless the merchant specifically reports otherwise.

## Step-by-Step Support Walkthrough
1. Open `Shipping Rates > Carrier Services > Tnt Australia > Enable Fallback Services` and confirm the fallback-services setup is visible with the expected fields for Name, Display Name, Rate, and Currency.
2. Enable fallback services and configure one or more static TNT fallback services.
3. Trigger a checkout scenario where TNT live rates fail or are unavailable.
4. Verify checkout still shows the configured fallback service instead of showing no shipping option.
5. After order placement, open the order in MCSL and confirm support can identify the fallback service in the order summary.
- Request/log fields to verify: TNT error evidence such as the reported failure codes, the configured fallback service, and the `FB:`-prefixed shipping code or equivalent stored fallback indicator on the order.

## Expected Behaviour
| What support should observe \| How to confirm |
| --- | --- |
| Checkout still shows a shipping option when TNT live rates fail. | Simulate a TNT failure case and verify fallback service visibility at checkout. |
| The merchant-configured fallback service name and price are used. | Compare checkout output to the saved fallback configuration. |
| Support can tell the order used a fallback path. | Inspect the order summary for the stored fallback service indicator. |

## Merchant-Safe Explanation
You can explain this as a checkout-protection feature. If TNT Australia has a service outage or transient rate failure, the merchant can still present a backup shipping option instead of losing the order entirely.

CARD 14/14
# FED-QU
# FED-QU — Add Quantity Units Configuration Option in Carrier Settings
| Ticket | Trello card `vHFtPEvQ` |
| --- | --- |
| Release | MCSL 380 |
| Area | FedEx customs quantity-units setting in carrier configuration and bulk actions |
| Trello | https://trello.com/c/vHFtPEvQ/4475-add-quantity-units-configuration-option-in-carrier-settings |
| Support scope | FedEx customs/testcase configuration only. Focus on configurable `quantityUnits` behavior instead of the previous hardcoded `EA` value. In the current product flow, this option is available only in Carrier Settings, even if older documentation mentions Bulk Action Settings. |

# Support Guide: FED-QU
## Add Quantity Units Configuration Option in Carrier Settings
## Feature Summary
FedEx customs requests were sending `requestedShipment.customsClearanceDetail.commodities.quantityUnits` as a hardcoded `EA` value even when a different unit was needed for the merchant's testcase or shipment setup. This update adds a configurable quantity-units option in Carrier Settings so support can verify the correct unit is saved and used in the outgoing request while keeping `EA` as the default. If older documentation mentions Bulk Action Settings, treat that as stale for now because the current option is available only in Carrier Settings.
## Toggles & Prerequisites
| Toggle / config note \| No separate feature toggle is described on the card. Confirm the store is on the build containing the FedEx quantity-units configuration option and that the shipment path being tested uses FedEx customs commodity data. |
| --- |

- Validate on a FedEx flow where customs commodity details are part of the request.
- Use a testcase that expects a non-default unit such as `PCS` so support can confirm the change clearly.
- If the merchant has not changed the setting, `EA` can still be the correct default behavior.

## Step-by-Step Support Walkthrough
1. Open the FedEx Carrier Settings area where customs options are maintained.
2. Locate the quantity-units configuration field and confirm the merchant can select or save the required value instead of relying on a hardcoded default.
3. Save a non-default test value such as `PCS` for the supported FedEx scenario.
4. Generate or preview the FedEx shipment flow that includes customs commodity details.
5. Review the request evidence for the outgoing FedEx commodity payload.
- Request node to verify: `requestedShipment.customsClearanceDetail.commodities.quantityUnits` should reflect the saved value such as `PCS`, while stores that do not override the setting may still send `EA`.

## Expected Behaviour
| What support should observe \| How to confirm |
| --- | --- |
| Quantity units can be configured instead of always being fixed to `EA`. | Save a non-default unit in the FedEx configuration area and confirm the value persists. |
| FedEx customs requests use the configured quantity unit for supported scenarios. | Compare the saved setting with the outgoing commodity request node. |
| Default behavior remains safe for stores that do not change the setting. | Leave the setting unchanged in a control case and confirm `EA` is still used where expected. |

## Merchant-Safe Explanation
You can explain this as a customs-configuration improvement. Merchants who need a different quantity unit for FedEx testcase or customs workflows can now set it more directly instead of being locked to a single hardcoded value.
