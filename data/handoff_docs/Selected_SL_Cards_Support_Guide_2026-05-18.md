# Release 1.0.379 Support Guide

Support Guide - Story Card Package

Generated on May 18, 2026

## Included Story Cards
| Story / card | Card title |
| --- | --- |
| ZI-491 | FedEx REST API rate timeouts during token refresh |
| ZI-487 | CSV signature update feature broken post-REST migration |
| ZI-007 | Order notes not synced after import |
| ZI-058 | eParcel bulk label generation delay (8+ sec consistently) |
| ZI-043 | Packing slip sort helper |
| ZI-029 | Bundle product support missing |
| ZI-018 | DPD services not appearing via EasyPost |
| ZI-098 | PostNL service code 6942 (Boxable Track & Trace) not available |
| ZI-038 | DHL Express "reason for return" field not supported |
| ZI-484 | Yearly plan billing not yet supported in MCSL app |
| ZI-472 | USPS Media Mail service not available in app |
| ZI-006 | USPS Ground Advantage Cubic service not implemented |
| ZI-010 | Subscription plans page error on Safari |
| ZI-475 | USPS Flat Rate Box dimensions incorrect and packing logic no |
| ZI-478 | Shipment notification email missing carrier name |
| ZI-480 | PostNord international label and CN22 must print o |
| ZI-483 | Plugin fails to load due to isActive:false flag ca |
| ZI-490 | USPS transit time buffer feature in development |
| SL item - USPS Stamps transit days | Estimated Transit days not showing up at checkout in USPS Stamps |
| ZI-477 | PostNord customs invoice duty calculated on subtotal not grand total |
| ZI-494 | Customer concern about DHL SOAP API v2 deprecation resolved through REST migration |
| ZI-495 | DHL Paket label generation complete failure requiring emergency REST API migration |

## How Support Should Use This Package

- Use this guide to explain the intended change, verify it in the relevant MCSL area, and gather the right evidence before escalating.
- Default platform is Shopify unless the card or store context explicitly says otherwise.
- For any card below, do not promise behavior until the store is confirmed on the release or rollout path that contains the change.
- If a card requires request-log or payload verification and the exact field is not named here, inspect the relevant request/response log and escalate with screenshots rather than guessing.

CARD 1/22
## ZI-491 - FedEx REST API rate timeouts during token refresh

### Feature Summary
This card covers intermittent FedEx REST rate failures when the access token refresh path overlaps with rate fetching. Support should treat the intended fix as a stability improvement: rate requests should complete without customer-visible timeout errors even when MCSL needs to refresh FedEx REST authentication in the background.

### Toggles & Prerequisites
| Check | What to confirm |
| --- | --- |
| Release | Confirm the store is on the build containing the ZI-491 fix |
| Carrier account | FedEx REST account is active in hamburger menu > Carriers |
| Platform | Default to Shopify unless the card/store says otherwise |
| Toggle | No toggle detected locally; confirm from card/store context |

### Step-by-Step Support Walkthrough
1. Open Shopify Admin > Apps > PH Multi Carrier Shipping Label App and confirm the affected store is using FedEx REST, not an older SOAP path.
2. Go to an order or checkout-rate scenario that reproduces FedEx REST rate fetching.
3. Trigger rates more than once, especially after enough idle time that token refresh is likely.
4. Confirm rates return without a timeout banner, endless loader, or forced retry loop.
5. If the issue still appears, capture the FedEx REST request/response log and the exact timestamp of the failure.

### Expected Behaviour
| What support should observe | How to confirm |
| --- | --- |
| FedEx REST rates still load when auth refresh happens | Run repeated rate checks after an idle period |
| No customer-facing timeout loop during token refresh | Confirm the UI does not stall or require manual retries |
| Escalation evidence is clean if it fails | Collect request log, store URL, carrier account, and affected order |


### Support Escalation Packet
- Story card: ZI-491
- Ticket: #379340
- Store URL, carrier account, order/cart scenario, timezone-correct timestamp
- Screenshot of the UI failure and the matching FedEx REST request/response log

CARD 2/22
## ZI-487 - CSV signature update feature broken post-REST migration

### Feature Summary
This card concerns a regression where a CSV-driven signature-related update stopped applying correctly after a REST migration. Support should validate that CSV import/update still saves the intended signature setting and that the updated value is honored in the downstream shipment flow.

### Toggles & Prerequisites
| Check | What to confirm |
| --- | --- |
| Release | Confirm the build includes the post-migration CSV fix |
| Field scope | Confirm from card/store context whether the CSV updates product-level signature settings, service options, or document signature data |
| Platform | Shopify by default |
| Toggle | No toggle detected locally |

### Step-by-Step Support Walkthrough
1. Open the same area and CSV template type referenced by the card or merchant workflow.
2. Import or update a sample row that changes the signature-related field.
3. Reopen the affected product, order, or config record inside MCSL and confirm the value persisted.
4. Run the downstream shipment or document flow that uses that signature setting.
5. Confirm the updated value is reflected in the UI or output instead of being ignored after save/import.

### Expected Behaviour
| What support should observe | How to confirm |
| --- | --- |
| CSV update succeeds without silently dropping the signature field | Reopen the updated record in MCSL |
| Updated signature setting is used downstream | Check the shipment/document behavior that depends on the field |
| No manual re-entry is needed after import | Compare saved value before and after refresh |


### Support Escalation Packet
- Story card: ZI-487
- Ticket: #379098
- CSV sample used, affected field name, store URL, product/order identifiers
- Before/after screenshots showing the saved value did not persist or apply

CARD 3/22
## ZI-007 - Order notes not synced after import

### Feature Summary
This card addresses missing order notes after order import into MCSL. Support should verify that notes present on the source order now appear in the imported order view and remain available for shipping operations that rely on those notes.

### Toggles & Prerequisites
| Check | What to confirm |
| --- | --- |
| Release | Confirm the store is on the fix build |
| Source platform | Shopify by default; verify if the merchant uses another supported platform |
| Order import path | Confirm the merchant is using the same import flow covered by the card |
| Toggle | No toggle detected locally |

### Step-by-Step Support Walkthrough
1. Open the source order in Shopify Admin and confirm it contains order notes or additional order instructions.
2. Import or refresh the same order into the PH Multi Carrier Shipping Label App.
3. Open the order inside the ORDERS tab and inspect the order details/summary.
4. Confirm the notes are visible after import and match the source order content.
5. Refresh the order once more to make sure the notes do not disappear on re-sync.

### Expected Behaviour
| What support should observe | How to confirm |
| --- | --- |
| Source order notes sync into MCSL | Compare Shopify order notes to the ORDERS view |
| Notes remain visible after refresh | Re-sync the order and recheck |
| Shipping workflow can proceed with the synced notes in place | Confirm support can still prepare the shipment normally |


### Support Escalation Packet
- Story card: ZI-007
- Ticket: #304193
- Store URL, source order number, screenshot from source platform, screenshot from MCSL ORDERS view

CARD 4/22
## ZI-058 - eParcel bulk label generation delay (8+ sec consistently)

### Feature Summary
Bulk label generation was consistently slow because the eParcel legacy flow made unnecessary shipment-status polling calls. The intended fix improves bulk label throughput for Australia Post eParcel and StarTrack and should not be validated with MyPost Business-only evidence.

### Toggles & Prerequisites
| Check | What to confirm |
| --- | --- |
| Release | Store is on the release path containing the performance fix |
| Carrier scope | Australia Post eParcel legacy API or StarTrack |
| Toggle | `australiaPost.skip.get.shipment.enabled` is enabled for the store/account |
| Platform | Shopify by default |

### Step-by-Step Support Walkthrough
1. Confirm the merchant uses Australia Post eParcel or StarTrack in MCSL.
2. Confirm the store/account has `australiaPost.skip.get.shipment.enabled` enabled.
3. Open the ORDERS tab and select multiple eParcel-ready orders.
4. Run bulk label generation and watch the orders move to success.
5. Compare the observed runtime against the prior 8+ second per-label behavior if historical evidence is available.

### Expected Behaviour
| What support should observe | How to confirm |
| --- | --- |
| Bulk label generation completes faster | Compare runtime for a multi-order batch |
| Orders are not stuck behind extra shipment polling | Watch status progression in the order grid |
| Scope remains limited to eParcel/StarTrack legacy flow | Do not use MyPost Business-only evidence for sign-off |


### Support Escalation Packet
- Story card: ZI-058
- Ticket: #380339
- Store URL, carrier account, batch size, elapsed time, request-log screenshots, toggle state

CARD 5/22
## ZI-043 - Packing slip sort helper

### Feature Summary
The Custom A4 SKU Sort and Custom A6 SKU Sort packing slip templates now sort line items by SKU in ascending order. The intended rule is numeric SKUs first in ascending order, followed by alphabetical SKUs in A-Z order.

### Toggles & Prerequisites
| Check | What to confirm |
| --- | --- |
| Release | Confirm the packing-slip helper change is live |
| Document flow | Confirm the merchant uses the Custom A4 SKU Sort or Custom A6 SKU Sort packing slip template |
| Sort expectation | SKU sort must be ascending: numbers first, then A-Z |
| Toggle | No toggle detected locally |

### Step-by-Step Support Walkthrough
1. Open an order with multiple line items whose SKUs include both numeric values and alphabetic values so the sort order is easy to verify.
2. Generate or re-download the packing slip using the Custom A4 SKU Sort or Custom A6 SKU Sort template.
3. Confirm the line items are sorted by SKU in ascending order, with numeric SKUs listed first.
4. Confirm the remaining alphabetic SKUs appear after the numeric entries in A-Z order.
5. If the order is incorrect, capture the source order data and the generated packing slip PDF.

### Expected Behaviour
| What support should observe | How to confirm |
| --- | --- |
| Packing slip line order is consistent | Generate the same slip twice and compare |
| Numeric SKUs appear first in ascending order | Review the first group of line items on the packing slip |
| Alphabetic SKUs appear after the numeric entries in A-Z order | Review the remaining line items on the packing slip |
| No unrelated packing-slip content is broken | Check item names, quantities, and addresses still render normally |


### Support Escalation Packet
- Story card: ZI-043
- Ticket: #377526
- Source order, generated packing slip PDF, visible SKU list in expected order, store URL

CARD 6/22
## ZI-029 - Bundle product support missing

### Feature Summary
This card concerns missing support for bundle products in the MCSL workflow. Support should validate that bundle-based orders can now be imported, prepared, and processed without dropping item data or blocking shipment setup.

### Toggles & Prerequisites
| Check | What to confirm |
| --- | --- |
| Release | Confirm the bundle support change is deployed |
| Product type | Confirm the affected items are true bundle/composite products in the source store |
| Platform | Shopify by default |
| Toggle | No toggle detected locally; confirm from card/store context |

### Step-by-Step Support Walkthrough
1. Open a source order containing a bundle product.
2. Sync or import that order into MCSL.
3. Open the order in the ORDERS tab and confirm the bundle product data appears correctly for shipment preparation.
4. Attempt rate calculation or label preparation for the order.
5. Confirm the order is not blocked because the bundle item is missing, duplicated incorrectly, or flattened in an unusable way.

### Expected Behaviour
| What support should observe | How to confirm |
| --- | --- |
| Bundle-product orders import into MCSL without breaking | Compare source order to imported order |
| Shipment preparation remains possible | Open Prepare Shipment / Generate Label |
| Item data stays usable for support and fulfillment | Confirm names, quantities, and package selection still make sense |


### Support Escalation Packet
- Story card: ZI-029
- Ticket: #372492
- Source platform, order number, bundle product example, imported-order screenshot, store URL

CARD 7/22
## ZI-018 - DPD services not appearing via EasyPost

### Feature Summary
This card concerns missing DPD services when the merchant uses EasyPost as the carrier connection layer. Support should validate that the expected DPD services now appear in the EasyPost-backed flow and can be selected for shipment processing.

### Toggles & Prerequisites
| Check | What to confirm |
| --- | --- |
| Carrier path | EasyPost account is active and configured for the affected store |
| Service scope | Confirm the merchant expects DPD services specifically through EasyPost |
| Platform | Shopify by default |
| Toggle | No toggle detected locally |

### Step-by-Step Support Walkthrough
1. Open hamburger menu > Carriers and confirm the store uses EasyPost for the affected carrier flow.
2. Open an order that should qualify for the DPD services mentioned by the merchant.
3. Run rate calculation or label preparation using the EasyPost-backed carrier flow.
4. Check whether the expected DPD services now appear in the rate/service selection area.
5. If still missing, capture the request log and the exact ship-from/ship-to scenario used.

### Expected Behaviour
| What support should observe | How to confirm |
| --- | --- |
| Expected DPD services appear through EasyPost | Review available service list on the affected order |
| Support can proceed to shipment selection | Service can be chosen, not just displayed |
| Missing-service escalations contain enough context | Include addresses, parcel details, and EasyPost account path |


### Support Escalation Packet
- Story card: ZI-018
- Ticket: #366630
- EasyPost account path, order scenario, expected DPD services, store URL, request-log screenshot

CARD 8/22
## ZI-098 - PostNL service code 6942 (Boxable Track & Trace) not available

### Feature Summary
This card addresses a missing PostNL service option, specifically service code 6942 for Boxable Track & Trace. Support should verify that the service is now available where merchants select eligible PostNL services and that the order can proceed with that option.

### Toggles & Prerequisites
| Check | What to confirm |
| --- | --- |
| Carrier account | PostNL account is connected in hamburger menu > Carriers |
| Service scope | Merchant expects PostNL service code 6942 for the tested shipment type |
| Platform | Shopify by default |
| Toggle | No toggle detected locally |

### Step-by-Step Support Walkthrough
1. Open the PostNL carrier configuration and confirm the account is active.
2. Prepare a shipment/order that matches the merchant's Boxable Track & Trace scenario.
3. Run the service or rate selection flow.
4. Confirm service code 6942 is available for selection when the shipment qualifies.
5. If available, complete label preparation to make sure the service is usable and not only visible.

### Expected Behaviour
| What support should observe | How to confirm |
| --- | --- |
| PostNL service code 6942 appears for eligible shipments | Review the service selection result |
| The service can be used for shipment processing | Continue into label creation |
| No manual workaround is required for that service | Compare against the merchant's previous limitation |


### Support Escalation Packet
- Story card: ZI-098
- Ticket: #379796
- Store URL, PostNL account, shipment details, screenshot of service list, request-log screenshot if available

CARD 9/22
## ZI-038 - DHL Express "reason for return" field not supported

### Feature Summary
This card covers missing support for a DHL Express return-related field, `reason for return`. Support should verify that the return flow now provides the required field where applicable and that return shipments/documents reflect the chosen value.

### Toggles & Prerequisites
| Check | What to confirm |
| --- | --- |
| Carrier account | DHL Express is active in hamburger menu > Carriers |
| Flow type | Confirm this is a DHL return shipment flow, not a standard outbound-only shipment |
| Platform | Shopify by default |
| Toggle | Confirm from card/store context if the field is rollout-gated |

### Step-by-Step Support Walkthrough
1. Open a DHL Express return-shipment scenario in the app.
2. Go to the order or return flow where return-specific customs/document inputs are configured.
3. Confirm a `reason for return` field is available when the shipment requires it.
4. Generate the return shipment or its documents using a known test value.
5. Confirm the chosen value is reflected in the output or the DHL-facing flow instead of being ignored.

### Expected Behaviour
| What support should observe | How to confirm |
| --- | --- |
| The DHL return flow exposes a reason-for-return input where required | Check the return shipment setup UI |
| The chosen value is carried through the process | Compare selected value to final output/log evidence |
| Outbound non-return flows remain unaffected | Run a normal DHL shipment as a control if needed |


### Support Escalation Packet
- Story card: ZI-038
- Ticket: #377217
- Store URL, DHL account, order/return scenario, selected return reason, output screenshot

CARD 10/22
## ZI-484 - Yearly plan billing not yet supported in MCSL app

### Feature Summary
This card is about yearly billing-plan support. Because the title indicates a support gap, support should first confirm whether the release in question adds yearly-plan availability or whether the card is still documenting a known limitation for some stores.

### Toggles & Prerequisites
| Check | What to confirm |
| --- | --- |
| Rollout status | Confirm from card/store context whether yearly billing is enabled, partially rolled out, or still unavailable |
| Account scope | Confirm which subscription plan and billing screen the merchant is using |
| Platform | Shopify app billing flow by default |
| Toggle | Confirm from card/store context |

### Step-by-Step Support Walkthrough
1. Open the merchant's subscription or plan-management page in the app.
2. Confirm whether a yearly plan option should be visible for that store under the current rollout.
3. If yearly billing is expected to be supported, verify the plan option displays correctly and can be selected without error.
4. If yearly billing is not yet available for that store, avoid promising it and position the current state as rollout-limited.
5. Capture the billing screen and the exact merchant expectation if the observed behavior differs from the card status.

### Expected Behaviour
| What support should observe | How to confirm |
| --- | --- |
| Support knows whether yearly billing is available or still gated | Check card/store rollout context first |
| Eligible stores can see or use the yearly plan if released | Verify on the subscription page |
| Ineligible stores are not incorrectly promised the feature | Use the confirmed rollout status in merchant communication |


### Support Escalation Packet
- Story card: ZI-484
- Ticket: #381931
- Store URL, current plan page screenshot, expected billing option, rollout confirmation source

CARD 11/22
## ZI-472 - USPS Media Mail service not available in app

### Feature Summary
This card addresses missing USPS Media Mail availability inside MCSL. Support should verify that Media Mail now appears for eligible USPS shipments and that merchants can use it without manual workaround.

### Toggles & Prerequisites
| Check | What to confirm |
| --- | --- |
| Carrier path | Confirm whether the store uses USPS directly or USPS through a supported integration path |
| Eligibility | Media Mail shipment contents and origin/destination meet USPS eligibility |
| Platform | Shopify by default |
| Toggle | `account-uuid.usps.rest.media.mail.enabled: true` must be enabled for the target USPS account |
| Store rollout date | `usps.rest.media.mail.enabled.for.store.createdAt.greater.than: date` must allow the store based on its created-at date |

### Step-by-Step Support Walkthrough
1. Open an order that qualifies for USPS Media Mail based on the merchant's use case.
2. Confirm the target USPS account has `account-uuid.usps.rest.media.mail.enabled: true`.
3. Confirm the store also satisfies the rollout gate `usps.rest.media.mail.enabled.for.store.createdAt.greater.than: date`.
4. Run the USPS service/rate selection flow in MCSL and confirm Media Mail appears for the eligible order.
5. Continue through label generation to verify the service is usable, not just visible.

### Expected Behaviour
| What support should observe | How to confirm |
| --- | --- |
| Media Mail appears for eligible USPS scenarios | Review the service list on the order |
| Media Mail is visible only when both toggle conditions are satisfied | Check the account UUID toggle and the store created-at rollout gate |
| The service can be used end to end | Continue to label generation |
| Ineligible scenarios still hide the service appropriately | Compare with a non-qualifying control order if needed |


### Support Escalation Packet
- Story card: ZI-472
- Ticket: #302656
- Store URL, USPS account path, order details, service-list screenshot, label attempt result, toggle state for `account-uuid.usps.rest.media.mail.enabled`, and the store created-at value checked against `usps.rest.media.mail.enabled.for.store.createdAt.greater.than`

CARD 12/22
## ZI-006 - USPS Ground Advantage Cubic service not implemented

### Feature Summary
This card concerns support for USPS Ground Advantage Cubic. Support should verify whether the release adds the service to eligible USPS flows and whether cubic-eligible shipments can surface and use the service correctly.

### Toggles & Prerequisites
| Check | What to confirm |
| --- | --- |
| Carrier path | Confirm the USPS integration path used by the merchant |
| Eligibility | Shipment qualifies for Ground Advantage Cubic based on the account and package scenario |
| Platform | Shopify by default |
| Toggle | No toggle detected locally |

### Step-by-Step Support Walkthrough
1. Prepare a USPS shipment that should qualify for Ground Advantage Cubic.
2. Run the service/rate lookup in MCSL.
3. Confirm Ground Advantage Cubic appears in the service list if the release adds it.
4. Select the service and attempt label generation.
5. If unavailable, capture the shipment details and whether other USPS services appear normally.

### Expected Behaviour
| What support should observe | How to confirm |
| --- | --- |
| Ground Advantage Cubic appears for eligible scenarios | Review USPS service list |
| The service can be selected for label generation | Continue through shipment creation |
| Non-eligible shipments do not falsely expose the service | Compare with a control order if needed |


### Support Escalation Packet
- Story card: ZI-006
- Ticket: #299137
- Store URL, USPS account path, package details, service-list screenshot, label attempt result

CARD 13/22
## ZI-010 - Subscription plans page error on Safari

### Feature Summary
This card addresses a browser-specific problem on Safari affecting the subscription plans page. Support should verify that the page now loads and functions correctly on Safari without blocking the merchant from reviewing or choosing plans.

### Toggles & Prerequisites
| Check | What to confirm |
| --- | --- |
| Browser | Reproduce on Safari using the merchant's reported version when possible |
| Scope | Confirm the issue is on the subscription plans page |
| Platform | Shopify app billing/subscription page |
| Toggle | No toggle detected locally |

### Step-by-Step Support Walkthrough
1. Open the subscription plans page in Safari.
2. Confirm the page loads without a blank screen, script error, or blocked interaction.
3. Verify the plan cards, buttons, and billing details render correctly.
4. If the page previously failed during selection, attempt the same click path again.
5. If the issue persists, compare briefly in Chrome to confirm it is Safari-specific.

### Expected Behaviour
| What support should observe | How to confirm |
| --- | --- |
| Subscription page opens correctly in Safari | Load the page fresh in Safari |
| Plan details and actions are usable | Interact with the visible plan controls |
| Safari no longer blocks the merchant from progressing | Compare against the earlier failing step |


### Support Escalation Packet
- Story card: ZI-010
- Ticket: #338603
- Safari version, macOS version if known, store URL, screenshot/video of the failing page

CARD 14/22
## ZI-475 - USPS Flat Rate Box dimensions incorrect and packing logic no

### Feature Summary
This card appears to cover incorrect USPS Flat Rate Box dimensions and the downstream packing logic that depends on them. Support should validate that the right USPS flat-rate package dimensions are used and that shipment packing behavior no longer chooses or rejects boxes incorrectly because of bad size data.

### Toggles & Prerequisites
| Check | What to confirm |
| --- | --- |
| Carrier scope | USPS flat-rate packaging flow |
| Scenario | Use an order where flat-rate package selection is easy to observe |
| Platform | Shopify by default |
| Toggle | No toggle detected locally |

### Step-by-Step Support Walkthrough
1. Open or create an order that should be packed into the affected USPS Flat Rate Box.
2. Review the package or packing-method selection in MCSL.
3. Confirm the expected flat-rate box appears with the correct dimensions or is chosen correctly by the packing logic.
4. Continue through rate calculation or label preparation.
5. If the wrong box is chosen, capture the order items, package list, and visible box dimensions.

### Expected Behaviour
| What support should observe | How to confirm |
| --- | --- |
| Correct USPS flat-rate box dimensions are used | Inspect the package details shown in the app |
| Packing logic does not mis-handle the shipment because of bad dimensions | Continue through rate/label flow |
| USPS shipment can proceed without manual box workaround | Compare against prior merchant workaround if known |


### Support Escalation Packet
- Story card: ZI-475
- Ticket: #364411
- Store URL, order number, affected USPS package name, screenshot of visible dimensions, label/rate result

CARD 15/22
## ZI-478 - Shipment notification email missing carrier name

### Feature Summary
This card concerns shipment notification emails that do not show the carrier name. Support should verify that the carrier name now appears in the relevant notification email template/output and matches the actual shipment carrier used.

### Toggles & Prerequisites
| Check | What to confirm |
| --- | --- |
| Notification flow | Confirm the email is generated by the affected MCSL shipment flow |
| Shipment carrier | Use a shipment where the carrier is obvious and verifiable |
| Platform | Shopify by default |
| Toggle | No toggle detected locally |

### Step-by-Step Support Walkthrough
1. Generate or trigger a shipment notification email from the affected store.
2. Open the email received by the test recipient.
3. Confirm the carrier name is present in the email content where merchants or customers expect it.
4. Compare the displayed carrier name with the actual carrier used on the shipment.
5. If missing, capture the email content and the corresponding order/shipment details in MCSL.

### Expected Behaviour
| What support should observe | How to confirm |
| --- | --- |
| Shipment email includes the carrier name | Review the delivered email body |
| Displayed carrier matches the actual shipment carrier | Compare email content to order/shipment details |
| Other notification content remains intact | Check tracking and order references still render correctly |


### Support Escalation Packet
- Story card: ZI-478
- Ticket: #376463
- Store URL, shipment/order number, email screenshot, actual carrier used

CARD 16/22
## ZI-480 - PostNord international label and CN22 must print o

### Feature Summary
This card appears to address PostNord international shipments where both the label and CN22 customs document must print correctly together. Support should validate that the required shipping document set is produced for the qualifying PostNord international flow.

### Toggles & Prerequisites
| Check | What to confirm |
| --- | --- |
| Carrier account | PostNord account is active |
| Shipment scope | International PostNord order that requires CN22 |
| Platform | Shopify by default |
| Toggle | Confirm from card/store context if document printing is rollout-gated |

### Step-by-Step Support Walkthrough
1. Open an international PostNord order that requires customs documentation.
2. Generate the shipment and download/print the available documents.
3. Confirm the shipping label is present and valid.
4. Confirm the CN22 document also prints or is included in the generated document set.
5. If either item is missing, capture the generated files and the order's international destination details.

### Expected Behaviour
| What support should observe | How to confirm |
| --- | --- |
| PostNord international shipment produces the label successfully | Review the generated label output |
| CN22 is also available when required | Review the printed/downloaded document set |
| Support can send both outputs to the merchant if needed | Confirm both files open cleanly |


### Support Escalation Packet
- Story card: ZI-480
- Ticket: #379784
- Store URL, destination country, PostNord account, generated label/CN22 files or screenshots

CARD 17/22
## ZI-483 - Plugin fails to load due to isActive:false flag ca

### Feature Summary
This card addresses a plugin/app load failure tied to an `isActive:false` state or flag. Support should validate that the affected plugin now loads correctly when the store/integration should be active and that the inactive-state handling no longer blocks startup incorrectly.

### Toggles & Prerequisites
| Check | What to confirm |
| --- | --- |
| Affected build | Confirm the store is on the build containing the load fix |
| Scope | Confirm which plugin/module was failing to load |
| Activation state | Confirm whether the store or plugin should be active in this scenario |
| Toggle | No toggle detected locally; activation logic itself is the focus |

### Step-by-Step Support Walkthrough
1. Open the affected plugin/module in the same environment where the merchant saw the load failure.
2. Confirm the store or integration should be active for that scenario.
3. Reload the page or app entry path.
4. Confirm the plugin/module loads instead of failing because of an incorrect inactive-state check.
5. If it still fails, capture the visible error and any state indicator showing active versus inactive.

### Expected Behaviour
| What support should observe | How to confirm |
| --- | --- |
| Plugin/module loads for stores that should be active | Reopen the affected entry path |
| Inactive-state handling no longer blocks valid cases | Compare with the previous failing scenario |
| Escalation includes the activation context if it still fails | Capture state and environment details |


### Support Escalation Packet
- Story card: ZI-483
- Ticket: #386476
- Store URL, module/page URL, visible error, active/inactive state evidence

CARD 18/22
## ZI-490 - USPS transit time buffer feature in development

### Feature Summary
This card is explicitly described as in development, so support should treat it as rollout-gated until the store context confirms it is live. The feature appears to involve buffering or adjusting USPS transit-time display logic.

### Toggles & Prerequisites
| Check | What to confirm |
| --- | --- |
| Status | Confirm whether the store is on an early rollout or whether the card is still not GA |
| Carrier path | USPS or USPS/Stamps flow in question |
| Platform | Shopify by default |
| Toggle | Confirm from card/store context before promising availability |

### Step-by-Step Support Walkthrough
1. Check the card/store rollout status before testing anything with the merchant.
2. If the feature is live for the store, run the USPS rate scenario where transit time buffering should apply.
3. Compare the shown transit-time behavior against the expected buffered result from the card context.
4. If the feature is not yet live, position it as not generally available instead of treating absence as a bug.
5. Capture screenshots and the exact USPS scenario if the observed result conflicts with rollout status.

### Expected Behaviour
| What support should observe | How to confirm |
| --- | --- |
| Support knows whether the feature is live before promising it | Confirm rollout status first |
| Rolled-out stores show the intended transit-time behavior | Test the USPS rate scenario |
| Non-rolled-out stores are not treated as bugs by default | Use rollout status in merchant communication |


### Support Escalation Packet
- Story card: ZI-490
- Ticket: #377113
- Store URL, rollout confirmation source, USPS scenario, screenshots of shown transit time

CARD 19/22
## SL item - Estimated Transit days not showing up at checkout in USPS Stamps

### Feature Summary
This support item covers missing estimated transit days at checkout for USPS Stamps. Support should validate that checkout rates now show transit-day information when the carrier/service and store configuration support it.

### Toggles & Prerequisites
| Check | What to confirm |
| --- | --- |
| Carrier path | USPS via Stamps integration |
| Checkout setup | Live checkout-rate display is configured for the store |
| Service scope | Use a USPS Stamps service that should expose transit days |
| Toggle | No toggle detected locally |

### Step-by-Step Support Walkthrough
1. Confirm the store uses USPS Stamps for checkout rates.
2. Run a checkout scenario that returns USPS Stamps rates.
3. Review the visible rate lines and confirm whether estimated transit days appear.
4. If not visible, compare one other carrier or service if available to check whether the issue is USPS-specific.
5. Capture both the checkout screen and the matching rate configuration in the app if transit days are still absent.

### Expected Behaviour
| What support should observe | How to confirm |
| --- | --- |
| USPS Stamps checkout rates show estimated transit days where supported | Review the live checkout rate lines |
| Missing transit days are no longer a USPS-specific display gap | Compare across eligible services if needed |
| Support can explain whether transit-day display is service-dependent | Use the observed eligible/ineligible examples |


### Support Escalation Packet
- Story item: Estimated Transit days not showing up at checkout in USPS Stamps
- Store URL, checkout screenshot, USPS Stamps configuration screenshot, service names shown

CARD 20/22
## ZI-477 - PostNord customs invoice duty calculated on subtotal not grand total

### Feature Summary
This card concerns duty/customs invoice calculation logic for PostNord, where duty was being based on subtotal rather than grand total. Support should validate that the customs invoice now uses the intended total basis for the affected scenario.

### Toggles & Prerequisites
| Check | What to confirm |
| --- | --- |
| Carrier account | PostNord is active |
| Shipment scope | International/customs flow that generates the affected invoice |
| Pricing example | Use an order where subtotal versus grand total difference is visible |
| Toggle | No toggle detected locally |

### Step-by-Step Support Walkthrough
1. Open a PostNord international order where duty/tax calculation can be inspected.
2. Generate the shipment and its customs invoice/document.
3. Compare the invoice duty basis against the order's subtotal and grand total.
4. Confirm the behavior matches the fixed grand-total expectation for the card.
5. If incorrect, capture the order totals and the generated invoice side by side.

### Expected Behaviour
| What support should observe | How to confirm |
| --- | --- |
| Duty/customs invoice calculation no longer uses subtotal incorrectly | Compare invoice values to order totals |
| PostNord customs documents reflect the intended basis | Review the generated customs invoice |
| Support can explain the correction clearly to the merchant | Use the before/after total comparison |


### Support Escalation Packet
- Story card: ZI-477
- Ticket: #376223
- Store URL, order totals breakdown, generated customs invoice, PostNord account details

CARD 21/22
## ZI-494 - Customer concern about DHL SOAP API v2 deprecation resolved through REST migration

### Feature Summary
This card is primarily about support positioning and verification after migrating away from a deprecated DHL SOAP v2 path to REST. Support should validate that the merchant is using the REST-backed flow and explain that the deprecation concern is resolved through that migration.

### Toggles & Prerequisites
| Check | What to confirm |
| --- | --- |
| Migration status | DHL REST migration is active for the affected store/account |
| Carrier path | Merchant is no longer relying on the deprecated SOAP v2 path |
| Platform | Shopify by default |
| Toggle | No toggle detected locally; migration state is the key prerequisite |

### Step-by-Step Support Walkthrough
1. Open the DHL carrier configuration for the affected store.
2. Confirm the account/path now uses the intended REST migration flow rather than SOAP v2.
3. Run a basic DHL rate or label scenario.
4. Confirm the workflow succeeds normally under the REST path.
5. Use the migration confirmation when explaining to the merchant why the prior deprecation concern is no longer blocking them.

### Expected Behaviour
| What support should observe | How to confirm |
| --- | --- |
| Store is on the REST-backed DHL path | Review the carrier configuration or release context |
| Core DHL workflow still works after migration | Run a basic rate or label test |
| Support can close the deprecation concern confidently | Tie the merchant explanation to the live REST path |


### Support Escalation Packet
- Story card: ZI-494
- Ticket: #330209
- Store URL, DHL account path, screenshot confirming REST usage, rate/label test result

CARD 22/22
## ZI-495 - DHL Paket label generation complete failure requiring emergency REST API migration

### Feature Summary
This card concerns a severe DHL Paket label-generation failure that required an emergency move to a REST API path. Support should verify that the migrated path is active and that DHL Paket label creation now works for the previously blocked scenario.

### Toggles & Prerequisites
| Check | What to confirm |
| --- | --- |
| Migration status | Emergency REST migration is active for the affected DHL Paket flow |
| Carrier account | Confirm the exact DHL Paket account used |
| Platform | Shopify by default |
| Toggle | No toggle detected locally; migration state is the key prerequisite |

### Step-by-Step Support Walkthrough
1. Confirm the affected store is on the migrated DHL Paket REST path.
2. Open an order that previously reproduced the complete label-generation failure.
3. Generate the DHL Paket label again.
4. Confirm the label now generates successfully instead of failing outright.
5. If it still fails, capture the order, carrier account, and the full visible error/result from the current REST path.

### Expected Behaviour
| What support should observe | How to confirm |
| --- | --- |
| DHL Paket labels generate successfully on the migrated path | Run the known-failing scenario again |
| The prior complete failure is no longer reproducible | Compare against the merchant's earlier error description |
| Support can differentiate migration success from unrelated carrier issues | Gather fresh evidence from the current path |


### Support Escalation Packet
- Story card: ZI-495
- Ticket: #332163
- Store URL, DHL Paket account, order number, fresh error screenshot, proof of migrated path

