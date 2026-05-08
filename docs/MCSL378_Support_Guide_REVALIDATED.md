PH
PLUGINHIVE
# MCSL 378 Support Guide
Support Guide - Story Card Package
May 05, 2026
| Document scope This package includes only the MCSL 378 cards that are actionable for support. Cards marked Traded Off, waiting for carrier response, lacking development detail, or closed by support per the user's ignore list are excluded. |
| --- |

# Included Story Cards
| Story | Support topic | Primary area |
| --- | --- | --- |
| ZI-058 | ZI-058 — eParcel bulk label generation delay (8+ sec consistently) | Australia Post eParcel and StarTrack label generation performance |
| ZI-065 | ZI-065 — DHL Export Declaration Surcharge incorrectly applied for Japan shipments | DHL Express rates for Japan-origin high-value shipments |
| ZI-063 | ZI-063 — Custom declaration statement on FedEx commercial invoice not available | FedEx REST commercial invoice custom declaration statement |
| ZI-062 | ZI-062 — Shipment type classification per order | Per-order shipment type/classification for international customs |
| ZI-034 | ZI-034 — Discounted price not reflected on commercial invoice | UPS REST commercial invoice discount handling |
| ZI-132 | ZI-132 — Touchless SLGP auto-print regression | Touchless SLGP auto-printing for FedEx, UPS, and USPS |
| ZI-016 | ZI-016 — No product-to-box mapping rules | Product-to-box mapping rules for packaging |
| ZI-005 | ZI-005 — Product name/variant changes create duplicates | Shopify product rename and variant change deduplication |
| ZI-003 | ZI-003 — Variant SKU search not working | Variant SKU search behavior |
| ZI-001 | ZI-001 — Variant SKU search not supported | Products page variant SKU search support |
| ZI-133 | ZI-133 — Product weight updates in Shopify not syncing to MCSL | Shopify product weight update sync |
| ZI-092 | ZI-092 — Shipping class/product category sync failure | Shopify product category/shipping class sync on force import |
| ZI-053 | ZI-053 — Auto-upload documents failing in REST | FedEx REST electronic trade document auto-upload |
| ZI-266 | ZI-266 — Product weight changes sync to shipping label in real-time | Real-time Shopify weight changes reflected in label generation |
| ZI-059 | ZI-059 — Australia Post international tracking not syncing to Shopify | Australia Post international tracking sync to Shopify |
| ZI-014 | ZI-014 — Pickup date/time not available in order report | Pickup date/time fields in order reports |
| ZI-097 | ZI-097 — Canpar Adult Signature (SA) service support | Canpar Adult Signature service support |
| ZI-357 | ZI-357 — FedEx rate display option to exclude VAT for EU tax compliance | FedEx rate display excluding VAT for EU compliance |
| ZI-360 | ZI-360 — Custom BigCommerce theme blocking shipping rate display at checkout | BigCommerce MCSL checkout rates: rate automation carrier/service validation |


# Table of Contents
MCSL 378 - 19 support-ready story cards
| Card | Description | Section |
| --- | --- | --- |
| ZI-058 | ZI-058 — eParcel bulk label generation delay (8+ sec consistently) | 1 |
| ZI-065 | ZI-065 — DHL Export Declaration Surcharge incorrectly applied for Japan shipments | 2 |
| ZI-063 | ZI-063 — Custom declaration statement on FedEx commercial invoice not available | 3 |
| ZI-062 | ZI-062 — Shipment type classification per order | 4 |
| ZI-034 | ZI-034 — Discounted price not reflected on commercial invoice | 5 |
| ZI-132 | ZI-132 — Touchless SLGP auto-print regression | 6 |
| ZI-016 | ZI-016 — No product-to-box mapping rules | 7 |
| ZI-005 | ZI-005 — Product name/variant changes create duplicates | 8 |
| ZI-003 | ZI-003 — Variant SKU search not working | 9 |
| ZI-001 | ZI-001 — Variant SKU search not supported | 10 |
| ZI-133 | ZI-133 — Product weight updates in Shopify not syncing to MCSL | 11 |
| ZI-092 | ZI-092 — Shipping class/product category sync failure | 12 |
| ZI-053 | ZI-053 — Auto-upload documents failing in REST | 13 |
| ZI-266 | ZI-266 — Product weight changes sync to shipping label in real-time | 14 |
| ZI-059 | ZI-059 — Australia Post international tracking not syncing to Shopify | 15 |
| ZI-014 | ZI-014 — Pickup date/time not available in order report | 16 |
| ZI-097 | ZI-097 — Canpar Adult Signature (SA) service support | 17 |
| ZI-357 | ZI-357 — FedEx rate display option to exclude VAT for EU tax compliance | 18 |
| ZI-360 | ZI-360 — Custom BigCommerce theme blocking shipping rate display at checkout | 19 |


CARD 1/19
# ZI-058
# ZI-058 — eParcel bulk label generation delay (8+ sec consistently)
| Ticket | #380339 |
| --- | --- |
| Release | MCSL 378 |
| Area | Australia Post eParcel and StarTrack label generation performance |
| Trello | https://trello.com/c/WADXzgnk/4217-from-sl-zi-058-eparcel-bulk-label-generation-delay-8-sec-consistently-380339 |
| Support scope | Shopify MCSL, MCSL 378, Label & Document Quality, Australia Post eParcel and StarTrack, Pain 10, QA verified. Note: this is eParcel legacy API, not MyPost Business. |


# Support Guide: ZI-058
## From SL: ZI-058 — eParcel bulk label generation delay (8+ sec consistently) [#380339]
## Feature Summary
Bulk label generation was consistently slow because the eParcel legacy API flow made extra shipment-status calls and waited on a hardcoded delay. The fix reduces the number of calls used for eParcel/StarTrack label creation and improves bulk-label throughput. Do not validate this card with MyPost Business-only evidence.
## Toggles & Prerequisites
| Toggle / config note \| australiaPost.skip.get.shipment.enabled: true |
| --- |

- Confirm the store/account is on the MCSL 378 release path before promising the behavior to a merchant.
- Use live MCSL store/account state as the source of truth for the toggle/config value above.
- For carrier-specific cards, verify the exact carrier account and service before testing the behavior.

## Step-by-Step Support Walkthrough
1. Confirm the merchant uses Australia Post eParcel or StarTrack in MCSL.
2. Confirm the account/store has the toggle australiaPost.skip.get.shipment.enabled set to true.
3. Open MCSL > ORDERS and select several eParcel-ready orders.
4. Run bulk Generate Label from the order grid.
5. Watch label status until the orders move to SUCCESS and verify that no order is stuck only because of shipment-status polling.
6. For high-volume support checks, compare the time taken for 10+ labels against the old 8+ second per-label behavior.
## Expected Behaviour
| What support should observe \| Labels should complete faster because MCSL skips the unnecessary get-shipment polling path. The card is for Australia Post eParcel legacy API and StarTrack, not MyPost Business. Verification notes include 36 eParcel labels in 3 min 29 sec and 79 StarTrack labels in 7 min 23 sec. |
| --- |

## Merchant-Safe Explanation
You can explain this as an MCSL release improvement that makes the affected workflow more reliable for the specific carrier or product area. The merchant should not need to understand the internal request-builder, sync, or feature-flag details; support should translate the change into the visible setup or result described above.
## Common Questions & Troubleshooting
- This is an eParcel legacy API / StarTrack performance card, not a MyPost Business card; if the merchant account is MPB-only, gather separate evidence before applying this support script.
- If labels are still slow, first confirm the toggle is enabled for the exact store/account.
- If only one or two labels are slow, check Australia Post response time and request logs before treating it as the fixed bulk-delay issue.
- If labels fail rather than delay, inspect the carrier response and order data because this fix is performance-focused, not a generic label-failure fix.
## Support Escalation Packet
- Story card: ZI-058 - ZI-058 — eParcel bulk label generation delay (8+ sec consistently)
- Trello URL: https://trello.com/c/WADXzgnk/4217-from-sl-zi-058-eparcel-bulk-label-generation-delay-8-sec-consistently-380339
- Store URL, account UUID, carrier account, order number, and generated label/tracking/report identifier.
- Screenshots of the setup page and request/log evidence whenever carrier behavior is involved.
- Exact toggle/config value used for this card.

CARD 2/19
# ZI-065
# ZI-065 — DHL Export Declaration Surcharge incorrectly applied for Japan shipments
| Ticket | #381261 |
| --- | --- |
| Release | MCSL 378 |
| Area | DHL Express rates for Japan-origin high-value shipments |
| Trello | https://trello.com/c/9E8R5MCZ/4185-from-sl-zi-065-dhl-export-declaration-surcharge-incorrectly-applied-for-japan-shipments-381261 |
| Support scope | Shopify MCSL, MCSL 378, DHL Express, International & Customs, Japan-origin high-value shipments, QA verified |


# Support Guide: ZI-065
## From SL: ZI-065 — DHL Export Declaration Surcharge incorrectly applied for Japan shipments [#381261]
## Feature Summary
DHL Export Declaration Surcharge was being applied globally for high-value shipments. Japan-origin DHL shipments should be excluded, so the surcharge service code WO must not be added when the origin country is Japan.
## Toggles & Prerequisites
| Toggle / config note \| No toggle. Validate MCSL 378 deployment and DHL Japan-origin high-value shipment scope; no store/account feature flag is required. |
| --- |

- Confirm the store/account is on the MCSL 378 release path before promising the behavior to a merchant.
- For carrier-specific cards, verify the exact carrier account and service before testing the behavior.

## Step-by-Step Support Walkthrough
1. Open a store with DHL Express configured.
2. Create or select a high-value Japan-origin DHL international shipment.
3. Run rate calculation or label preparation for DHL Express.
4. Open the request log or carrier request payload.
- Request node to verify: `QtdShpExChrg.SpecialServiceType`; Japan-origin high-value shipments must not include `WO`.
5. Verify the WO special service is not present for Japan-origin shipments.
6. Run a non-Japan high-value DHL control shipment and verify surcharge behavior remains unchanged where applicable.
## Expected Behaviour
| What support should observe Japan-origin high-value DHL shipments should not show the Export Declaration Surcharge. Non-excluded countries should continue using the configured DHL surcharge logic. |
| --- |

## Merchant-Safe Explanation
You can explain this as an MCSL release improvement that makes the affected workflow more reliable for the specific carrier or product area. The merchant should not need to understand the internal request-builder, sync, or feature-flag details; support should translate the change into the visible setup or result described above.
## Common Questions & Troubleshooting
- If Japan still shows the surcharge, verify the origin country is JP and not only a Japan destination.
- Check config for exportDeclarationExcludedCountries and confirm JP is present.
- For new countries, support should request a config update rather than a code change if the country only needs exclusion.
## Support Escalation Packet
- Story card: ZI-065 - ZI-065 — DHL Export Declaration Surcharge incorrectly applied for Japan shipments
- Trello URL: https://trello.com/c/9E8R5MCZ/4185-from-sl-zi-065-dhl-export-declaration-surcharge-incorrectly-applied-for-japan-shipments-381261
- Store URL, account UUID, carrier account, order number, and generated label/tracking/report identifier.
- Screenshots of the setup page and request/log evidence whenever carrier behavior is involved.

CARD 3/19
# ZI-063
# ZI-063 — Custom declaration statement on FedEx commercial invoice not available
| Ticket | #380784 |
| --- | --- |
| Release | MCSL 378 |
| Area | FedEx REST commercial invoice custom declaration statement |
| Trello | https://trello.com/c/tHOnnmuh/4186-from-sl-zi-063-custom-declaration-statement-on-fedex-commercial-invoice-not-available-380784 |
| Support scope | SLA Breached, Shopify MCSL, Pain 8-9, 🚚 FedEx, International & Customs, MCSL 378 |


# Support Guide: ZI-063
## From SL: ZI-063 — Custom declaration statement on FedEx commercial invoice not available [#380784]
## Feature Summary
FedEx REST commercial invoice custom declaration behavior is account/origin specific. When shipping is done from the US, MCSL should show the default U.S. Government export-control declaration on the commercial invoice. For all other accounts, the commercial invoice should show the Custom Declaration Statement configured by the user in the FedEx carrier Other Details settings.
## Toggles & Prerequisites
| Toggle / config note \| No toggle. Confirm FedEx REST carrier account, shipment origin country, and the value saved in Carriers > FedEx REST > Other Details > Custom Declaration Statement for non-US accounts. |
| --- |

- Confirm the store/account is on the MCSL 378 release path before promising the behavior to a merchant.
- For carrier-specific cards, verify the exact carrier account and service before testing the behavior.

## Step-by-Step Support Walkthrough
1. Open Shopify Admin > Apps > PH Multi Carrier Shipping Label App.
2. Open the hamburger menu > Carriers and edit the FedEx REST carrier account.
3. Open the carrier Other Details / commercial-invoice area and locate Custom Declaration Statement.
4. Confirm the shipment origin/account type before testing: US-origin shipping follows the default declaration path; all other accounts follow the configured carrier Other Details path.
5. For a US-origin FedEx REST international shipment, generate a label that creates a commercial invoice and verify the default U.S. Government declaration appears on the invoice.
6. For a non-US FedEx REST account, save the merchant-provided Custom Declaration Statement in carrier Other Details, then generate an international commercial-invoice shipment.
7. Open the request log and commercial invoice document. Confirm declarationStatement/request evidence and the invoice output match the rule for that account type.
- Request node to verify: `declarationStatement`
## Expected Behaviour
| What support should observe US-origin FedEx REST commercial invoices should show the default declaration: "These items are controlled by the U.S. Government and authorized for export only to the country of ultimate destination for use by the ultimate consignee or end-user(s) herein identified. They may not be resold, transferred, or otherwise disposed of, to any other country or to any person other than the authorized ultimate consignee or end-user(s), either in their original form or after being incorporated into other items, without first obtaining approval from the U.S. government or as otherwise authorized by U.S. law and regulations." For all other FedEx REST accounts, the commercial invoice should show the Custom Declaration Statement configured by the user in carrier Other Details. Domestic/non-customs flows should not be affected. |
| --- |

## Merchant-Safe Explanation
You can explain this as account-aware commercial invoice declaration handling. US-origin FedEx REST shipments use the required default export-control statement, while non-US FedEx REST accounts can use the merchant-configured declaration from carrier Other Details.
## Common Questions & Troubleshooting
- If the invoice does not show the default statement for a US-origin shipment, confirm the ship-from/origin country is US and the shipment generated a commercial invoice.
- If a non-US account does not show the merchant text, reopen FedEx REST > Other Details and confirm the Custom Declaration Statement was saved for the exact carrier account used on the order.
- If the request still uses the old CustomDeclaration field or ignores declarationStatement, escalate with request-log evidence, carrier account UUID, origin country, and the generated commercial invoice.
## Support Escalation Packet
- Story card: ZI-063 - ZI-063 — Custom declaration statement on FedEx commercial invoice not available
- Trello URL: https://trello.com/c/tHOnnmuh/4186-from-sl-zi-063-custom-declaration-statement-on-fedex-commercial-invoice-not-available-380784
- Store URL, account UUID, carrier account, order number, and generated label/tracking/report identifier.
- Screenshots of the setup page and request/log evidence whenever carrier behavior is involved.

CARD 4/19
# ZI-062
# ZI-062 — Shipment type classification per order
| Ticket | #380339 |
| --- | --- |
| Release | MCSL 378 |
| Area | Per-order shipment type/classification for international customs |
| Trello | https://trello.com/c/CIhn4HuZ/4187-from-sl-zi-062-shipment-type-classification-per-order-380339 |
| Support scope | Shopify MCSL, MCSL 378, International & Customs, Order Summary shipment classification, DHL Express enabled by toggle; Australia Post/eParcel reported customer context |


# Support Guide: ZI-062
## From SL: ZI-062 — Shipment type classification per order [#380339]
## Feature Summary
Shipment type classification was only available through the Touchless Print path. MCSL now exposes the classification at the international Order Summary level so support and merchants can set the reason/content type per order before label generation.
## Toggles & Prerequisites
| Toggle / config note \| shipment.classification.enabled.carriers: ["C1", "C33", "C49"]. Carrier-specific support only for DHL, Australia Post/eParcel, and MyPost; carrier code can differ by store/registry. |
| --- |

- Confirm the store/account is on the MCSL 378 release path before promising the behavior to a merchant.
- Use live MCSL store/account state as the source of truth for the toggle/config value above.
- For carrier-specific cards, verify the exact carrier account and service before testing the behavior.

## Step-by-Step Support Walkthrough
1. Confirm the target carrier is enabled in shipment.classification.enabled.carriers.
2. Open MCSL > ORDERS and select an international order for the enabled carrier.
3. Open Order Summary.
4. Find the Shipment Type or Shipment Classification dropdown.
5. Select the correct classification shown by the app, such as merchandise, gift, documents, sample, return, or the equivalent configured option.
6. Save the order summary change.
7. Refresh the page and confirm the selected value persists.
8. Generate the label and confirm the selected classification and, for OTHER, the Classification Description are used in the carrier request/customs payload.
- Request node to verify: carrier-specific shipment classification field, for example Australia Post/eParcel `classification_type`; the value must come from the Order Summary selection.
## Expected Behaviour
| What support should observe \| The selected shipment classification must be order-specific, visible on the international Order Summary page, and not limited to Touchless Print. When OTHER is selected, Classification Description must be mandatory, visible, saved, and persisted after success/failure/fulfillment. The selected classification and description should be reflected in the carrier request/customs payload. |
| --- |

## Merchant-Safe Explanation
You can explain this as an MCSL release improvement that makes the affected workflow more reliable for the specific carrier or product area. The merchant should not need to understand the internal request-builder, sync, or feature-flag details; support should translate the change into the visible setup or result described above.
## Common Questions & Troubleshooting
- If the dropdown is missing from international Order Summary or appears only under Touchless Print, confirm the carrier toggle and capture the order/store evidence for escalation.
- If DHL AUS-US label generation fails with xml not generated, collect the store/order context, request logs, and carrier response for escalation.
- If OTHER is selected, Classification Description must be mandatory, visible, saved, and persisted after success, failure, refresh, and fulfillment; if the UI goes blank while the old value is still sent in payload, escalate with order and request logs.
- If the value disappears after refresh, capture the order ID and browser/API response because persistence is failing.
- If the request ignores the selected classification, inspect request logs for the carrier adapter mapping.
## Support Escalation Packet
- Story card: ZI-062 - ZI-062 — Shipment type classification per order
- Trello URL: https://trello.com/c/CIhn4HuZ/4187-from-sl-zi-062-shipment-type-classification-per-order-380339
- Store URL, account UUID, carrier account, order number, and generated label/tracking/report identifier.
- Screenshots of the setup page and request/log evidence whenever carrier behavior is involved.
- Exact toggle/config value used for this card.

CARD 5/19
# ZI-034
# ZI-034 — Discounted price not reflected on commercial invoice
| Ticket | #374022 |
| --- | --- |
| Release | MCSL 378 |
| Area | UPS REST commercial invoice discount handling |
| Trello | https://trello.com/c/s1w3iq7e/4188-from-sl-zi-034-discounted-price-not-reflected-on-commercial-invoice-374022 |
| Support scope | Shopify MCSL, MCSL 378, UPS REST, International & Customs, discounted commercial invoice values |


# Support Guide: ZI-034
## From SL: ZI-034 — Discounted price not reflected on commercial invoice [#374022]
## Feature Summary
Discounted order prices were not reflected correctly on UPS REST commercial invoices. The release adds a controlled path to pass order discount information into UPS REST commercial invoice logic when safe to do so. Support should verify both the commercial invoice totals and the request payload: the invoice shows Invoice Line Total, Discount-Rebate, Invoice Sub-Total, and Total Invoice Amount, while the request log passes the discount value in the discount node when the toggle applies.
## Toggles & Prerequisites
| Toggle / config note \| account.ups.rest.commercial.invoice.discount.enabled: true |
| --- |

- Confirm the store/account is on the MCSL 378 release path before promising the behavior to a merchant.
- Use live MCSL store/account state as the source of truth for the toggle/config value above.
- For carrier-specific cards, verify the exact carrier account and service before testing the behavior.

## Step-by-Step Support Walkthrough
1. Confirm UPS REST is configured for the store.
2. Enable account.ups.rest.commercial.invoice.discount.enabled for the target account/store.
3. Create an international order with a real product discount such as BOGO or line-item discount.
4. Do not set a custom insured value or manually edited product price for the first positive test.
5. Generate the UPS label and commercial invoice.
6. Compare the commercial invoice totals: Invoice Line Total should show the pre-discount line value, Discount-Rebate should show the applied discount, and Total Invoice Amount should match the discounted invoice amount.
7. Open the UPS REST request log and confirm the applied discount value is present when the toggle applies.
- Request node to verify: `discount`
8. Run control tests where custom insured value is configured, product preferred customs/insured value is set, or the package was edited from the order grid; in those cases the discount node should not be passed and previous behavior is intentionally preserved.
## Expected Behaviour
| What support should observe \| When enabled and no bypass configuration blocks it, UPS REST commercial invoice values should use discounted order values. The commercial invoice should show Invoice Line Total, Discount-Rebate, Invoice Sub-Total, and Total Invoice Amount, with Total Invoice Amount matching the discounted value. The UPS REST request log should include the discount node carrying the applied discount value. Discounts are not applied when custom insured value is Percentage Of Product Price, Fixed Value, product Preferred Customs/Insured value is set, or the package was edited from the order grid. Free-shipping discounts must not reduce product total, and Amount off products must not fail label generation. |
| --- |

## Merchant-Safe Explanation
You can explain this as an MCSL release improvement that makes the affected workflow more reliable for the specific carrier or product area. The merchant should not need to understand the internal request-builder, sync, or feature-flag details; support should translate the change into the visible setup or result described above.
## Common Questions & Troubleshooting
- If discounts are ignored, confirm the enabled toggle is on, the disabled toggle is not active, and none of the bypass cases apply: Percentage Of Product Price, Fixed Value, product Preferred Customs/Insured value, or package edited from the order grid.
- If the commercial invoice shows Discount-Rebate but the request log does not include the discount node, capture the CI PDF, request payload, order discount details, and toggle value for escalation.
- If free shipping is deducted from product totals, collect invoice, order discount details, and request logs; free shipping should apply to the shipping amount while product total remains unchanged.
- If Amount off products makes label generation fail with The request is well formed but the request is not valid, capture the discount setup, request logs, and order details for escalation.
- If the merchant uses product-level insured value, explain that discount node behavior may be bypassed by design.
## Support Escalation Packet
- Story card: ZI-034 - ZI-034 — Discounted price not reflected on commercial invoice
- Trello URL: https://trello.com/c/s1w3iq7e/4188-from-sl-zi-034-discounted-price-not-reflected-on-commercial-invoice-374022
- Store URL, account UUID, carrier account, order number, and generated label/tracking/report identifier.
- Screenshots of the setup page and request/log evidence whenever carrier behavior is involved.
- Exact toggle/config value used for this card.

CARD 6/19
# ZI-132
# ZI-132 — Touchless SLGP auto-print regression
| Ticket | #384058 |
| --- | --- |
| Release | MCSL 378 |
| Area | Touchless SLGP auto-printing for FedEx, UPS, and USPS |
| Trello | https://trello.com/c/mtuY8s5G/4189-from-sl-zi-132-touchless-slgp-auto-print-regression-384058 |
| Support scope | Shopify MCSL, Label & Document Quality, 🚚 FedEx, 🚚 USPS, 🚚 UPS, Pain 10, MCSL 378, Closed By Support |


# Support Guide: ZI-132
## From SL: ZI-132 — Touchless SLGP auto-print regression [#384058]
## Feature Summary
Touchless SLGP auto-printing must fire automatically after label generation. The issue was tied to touchless printing feature flags or print orchestration, causing labels to generate without a print job.
## Toggles & Prerequisites
| Toggle / config note \| No toggle. Validate release deployment, SLGP/Touchless setup, and the affected auto-print workflow. |
| --- |

- Confirm the store/account is on the MCSL 378 release path before promising the behavior to a merchant.
- For carrier-specific cards, verify the exact carrier account and service before testing the behavior.

## Step-by-Step Support Walkthrough
1. Confirm the account is eligible for touchless printing and is not disabled by account-level flag.
2. Confirm the merchant workstation/certificate service is connected and able to receive print jobs.
3. Run SLGP label generation for FedEx, UPS, and USPS sample orders.
4. Do not click a manual print button after label success.
5. Verify the print job appears on the connected workstation queue automatically.
6. Check logs from PrintingCertificateService if no physical print event is visible.
## Expected Behaviour
| What support should observe After SLGP label success, auto-print should trigger without manual action for the enabled account/workstation. QA notes say sanity passed and SLGP worked as expected. |
| --- |

## Merchant-Safe Explanation
You can explain this as an MCSL release improvement that makes the affected workflow more reliable for the specific carrier or product area. The merchant should not need to understand the internal request-builder, sync, or feature-flag details; support should translate the change into the visible setup or result described above.
## Common Questions & Troubleshooting
- If label generation succeeds but no print job appears, verify the account toggle and workstation certificate service first.
- If only one carrier fails, check carrier-specific label output and print format.
- If auto-print fires while disabled, escalate because the account-level disabled flag is not being respected.
## Support Escalation Packet
- Story card: ZI-132 - ZI-132 — Touchless SLGP auto-print regression
- Trello URL: https://trello.com/c/mtuY8s5G/4189-from-sl-zi-132-touchless-slgp-auto-print-regression-384058
- Store URL, account UUID, carrier account, order number, and generated label/tracking/report identifier.
- Screenshots of the setup page and request/log evidence whenever carrier behavior is involved.

CARD 7/19
# ZI-016
# ZI-016 — No product-to-box mapping rules
| Ticket | #361776 |
| --- | --- |
| Release | MCSL 378 |
| Area | Product-to-box mapping rules for packaging |
| Trello | https://trello.com/c/WOwgVH5u/4192-from-sl-zi-016-no-product-to-box-mapping-rules-361776 |
| Support scope | Shopify MCSL, MCSL 378, Packaging / product-to-box mapping, UPS reported path, QA verified |


# Support Guide: ZI-016
## From SL: ZI-016 — No product-to-box mapping rules [#361776]
## Feature Summary
Merchants can map specific products or SKUs to specific box types so MCSL respects manufacturer packaging requirements before falling back to generic packing logic.
## Toggles & Prerequisites
| Toggle / config note \| accountUUID.product.box.mapping.enabled: true |
| --- |

- Confirm the store/account is on the MCSL 378 release path before promising the behavior to a merchant.
- Use live MCSL store/account state as the source of truth for the toggle/config value above.
- For carrier-specific cards, verify the exact carrier account and service before testing the behavior.

## Step-by-Step Support Walkthrough
1. Enable accountUUID.product.box.mapping.enabled for the merchant account.
2. Open MCSL > menu > Products or Packaging/Product Box Mapping area.
3. Create or select the custom box types required by the merchant.
4. Map each product/SKU to the intended box type and quantity rule.
5. Save the mapping rules.
6. Create an order containing mapped and unmapped products.
7. Open Order Summary and run packaging/label preparation.
8. Verify mapped SKUs use their assigned boxes while unmapped products use existing default packing.
## Expected Behaviour
| What support should observe \| Mapped products should be packed into their designated manufacturer box types. Unmapped products should continue through the normal packaging algorithm. Existing packaging behavior should remain unchanged for products without mapping rules. |
| --- |

## Merchant-Safe Explanation
You can explain this as an MCSL release improvement that makes the affected workflow more reliable for the specific carrier or product area. The merchant should not need to understand the internal request-builder, sync, or feature-flag details; support should translate the change into the visible setup or result described above.
## Common Questions & Troubleshooting
- If the mapping UI is missing, confirm the account toggle is enabled.
- If mapped SKUs still use generic boxes, check SKU/product identity and whether the order product matches the mapped product record.
- If conflicting rules save, capture the rule setup because support should expect validation or a clear warning.
## Support Escalation Packet
- Story card: ZI-016 - ZI-016 — No product-to-box mapping rules
- Trello URL: https://trello.com/c/WOwgVH5u/4192-from-sl-zi-016-no-product-to-box-mapping-rules-361776
- Store URL, account UUID, carrier account, order number, and generated label/tracking/report identifier.
- Screenshots of the setup page and request/log evidence whenever carrier behavior is involved.
- Exact toggle/config value used for this card.

CARD 8/19
# ZI-005
# ZI-005 — Product name/variant changes create duplicates
| Ticket | #277997 |
| --- | --- |
| Release | MCSL 378 |
| Area | Shopify product rename and variant change deduplication |
| Trello | https://trello.com/c/wOd9bAUk/4193-from-sl-zi-005-product-name-variant-changes-create-duplicates-277997 |
| Support scope | Shopify MCSL, SLA Breached, Pain 8-9, 🚚 FedEx, Order & Product Data, MCSL 378 |


# Support Guide: ZI-005
## From SL: ZI-005 — Product name/variant changes create duplicates [#277997]
## Feature Summary
Legacy product import paths could create duplicate MCSL product records after Shopify product or variant names changed. The fix relies on Shopify variant ID based matching so the existing record is updated instead of duplicated.
## Toggles & Prerequisites
| Toggle / config note \| No toggle. Validate release deployment and Shopify product/variant sync state. |
| --- |

- Confirm the store/account is on the MCSL 378 release path before promising the behavior to a merchant.
- For carrier-specific cards, verify the exact carrier account and service before testing the behavior.

## Step-by-Step Support Walkthrough
1. Open Shopify Admin and rename a product already synced into MCSL.
2. Run the normal sync or force import from MCSL Products.
3. Open MCSL > Products and search for the renamed product.
4. Confirm one active product record exists, not old-name and new-name duplicates.
5. Repeat with a variant rename or variant status change.
6. Confirm downstream references remain attached to the surviving product record.
## Expected Behaviour
| What support should observe MCSL should update the existing product/variant record and avoid duplicate rows for normal rename or variant updates. |
| --- |

## Merchant-Safe Explanation
You can explain this as an MCSL release improvement that makes the affected workflow more reliable for the specific carrier or product area. The merchant should not need to understand the internal request-builder, sync, or feature-flag details; support should translate the change into the visible setup or result described above.
## Common Questions & Troubleshooting
- If old duplicate products are already present, cleanup may still be needed; the fix prevents new duplicates.
- If different products merge into one, escalate immediately because dedup is too broad.
- If SKU search is involved, refer to ZI-001 and ZI-003 because that is adjacent but separate search behavior.
## Support Escalation Packet
- Story card: ZI-005 - ZI-005 — Product name/variant changes create duplicates
- Trello URL: https://trello.com/c/wOd9bAUk/4193-from-sl-zi-005-product-name-variant-changes-create-duplicates-277997
- Store URL, account UUID, carrier account, order number, and generated label/tracking/report identifier.
- Screenshots of the setup page and request/log evidence whenever carrier behavior is involved.

CARD 9/19
# ZI-003
# ZI-003 — Variant SKU search not working
| Ticket | #277997 |
| --- | --- |
| Release | MCSL 378 |
| Area | Variant SKU search behavior |
| Trello | https://trello.com/c/vKDjnEyW/4194-from-sl-zi-003-variant-sku-search-not-working-277997 |
| Support scope | Shopify MCSL, SLA Breached, Pain 8-9, 🚚 FedEx, Order & Product Data, MCSL 378 |


# Support Guide: ZI-003
## From SL: ZI-003 — Variant SKU search not working [#277997]
## Feature Summary
Merchants can search products by variant SKU instead of being forced to search only by parent product name. This supports variant-heavy catalogs and updated SKU values after Shopify sync.
## Toggles & Prerequisites
| Toggle / config note \| No toggle. Validate release deployment and Products search behaviour. |
| --- |

- Confirm the store/account is on the MCSL 378 release path before promising the behavior to a merchant.
- For carrier-specific cards, verify the exact carrier account and service before testing the behavior.

## Step-by-Step Support Walkthrough
1. Open Shopify and confirm the product has one or more variants with distinct SKUs.
2. Sync or force import the products into MCSL.
3. Open MCSL > Products.
4. Search by an exact variant SKU.
5. Search by a supported partial SKU if partial search is enabled.
6. Update a variant SKU in Shopify, sync again, and confirm the new SKU searches correctly while the stale SKU no longer returns that product.
## Expected Behaviour
| What support should observe Variant SKU search should return the correct parent product and matching variant context without unrelated products or stale SKU results. |
| --- |

## Merchant-Safe Explanation
You can explain this as an MCSL release improvement that makes the affected workflow more reliable for the specific carrier or product area. The merchant should not need to understand the internal request-builder, sync, or feature-flag details; support should translate the change into the visible setup or result described above.
## Common Questions & Troubleshooting
- If search works by name but not SKU, confirm the latest Shopify sync completed.
- If old SKU still returns the product, force import and recheck variant mapping.
- If unrelated products appear, capture the search term and result list for backend query review.
## Support Escalation Packet
- Story card: ZI-003 - ZI-003 — Variant SKU search not working
- Trello URL: https://trello.com/c/vKDjnEyW/4194-from-sl-zi-003-variant-sku-search-not-working-277997
- Store URL, account UUID, carrier account, order number, and generated label/tracking/report identifier.
- Screenshots of the setup page and request/log evidence whenever carrier behavior is involved.

CARD 10/19
# ZI-001
# ZI-001 — Variant SKU search not supported
| Ticket | #218195 |
| --- | --- |
| Release | MCSL 378 |
| Area | Products page variant SKU search support |
| Trello | https://trello.com/c/x09Qjr61/4195-from-sl-zi-001-variant-sku-search-not-supported-218195 |
| Support scope | Shopify MCSL, SLA Breached, Pain 8-9, Order & Product Data, MCSL 378 |


# Support Guide: ZI-001
## From SL: ZI-001 — Variant SKU search not supported [#218195]
## Feature Summary
Older customer requests for variant SKU search are covered by the same product-search improvement. MCSL should support exact and valid partial SKU lookup in the Products page for variant-rich catalogs.
## Toggles & Prerequisites
| Toggle / config note \| No toggle. Validate release deployment and Products search behaviour. |
| --- |

- Confirm the store/account is on the MCSL 378 release path before promising the behavior to a merchant.
- For carrier-specific cards, verify the exact carrier account and service before testing the behavior.

## Step-by-Step Support Walkthrough
1. Open MCSL > Products.
2. Search by product name and confirm baseline search still works.
3. Search by product-level SKU.
4. Search by variant SKU for a multi-variant product.
5. Try an invalid SKU and confirm no unrelated products are returned.
6. Confirm the search result does not duplicate the same product for one variant.
## Expected Behaviour
| What support should observe Support should be able to tell merchants they can find variant products directly by SKU in MCSL after sync, without exporting the catalog to CSV. |
| --- |

## Merchant-Safe Explanation
You can explain this as an MCSL release improvement that makes the affected workflow more reliable for the specific carrier or product area. The merchant should not need to understand the internal request-builder, sync, or feature-flag details; support should translate the change into the visible setup or result described above.
## Common Questions & Troubleshooting
- If a newly changed SKU is missing, force import products and retry.
- If duplicate products appear in the search results, cross-check ZI-005 duplicate handling.
- If the merchant searches order-time SKU in Orders, clarify whether they are using Products search or Orders filter.
## Support Escalation Packet
- Story card: ZI-001 - ZI-001 — Variant SKU search not supported
- Trello URL: https://trello.com/c/x09Qjr61/4195-from-sl-zi-001-variant-sku-search-not-supported-218195
- Store URL, account UUID, carrier account, order number, and generated label/tracking/report identifier.
- Screenshots of the setup page and request/log evidence whenever carrier behavior is involved.

CARD 11/19
# ZI-133
# ZI-133 — Product weight updates in Shopify not syncing to MCSL
| Ticket | #384061 |
| --- | --- |
| Release | MCSL 378 |
| Area | Shopify product weight update sync |
| Trello | https://trello.com/c/MpDgExFq/4199-from-sl-zi-133-product-weight-updates-in-shopify-not-syncing-to-mcsl-384061 |
| Support scope | Shopify MCSL, Pain 8-9, Order & Product Data, MCSL 378 |


# Support Guide: ZI-133
## From SL: ZI-133 — Product weight updates in Shopify not syncing to MCSL [#384061]
## Feature Summary
Shopify product weight, weight unit, and shipping-required changes were not always detected by MCSL product sync. The fix adds those fields to the change-detection path.
## Toggles & Prerequisites
| Toggle / config note \| No toggle. Validate release deployment and Shopify product weight sync state. |
| --- |

- Confirm the store/account is on the MCSL 378 release path before promising the behavior to a merchant.
- For carrier-specific cards, verify the exact carrier account and service before testing the behavior.

## Step-by-Step Support Walkthrough
1. Open Shopify Admin and edit the weight of a simple product.
2. Wait for sync or trigger force import in MCSL.
3. Open MCSL > Products and verify the new weight is visible.
4. Repeat with a variable product/variant.
5. Generate or prepare a label using the updated product and verify MCSL does not use the stale weight.
## Expected Behaviour
| What support should observe Simple and variable product weights should update from Shopify to MCSL. QA notes verified both simple and variable products. |
| --- |

## Merchant-Safe Explanation
You can explain this as an MCSL release improvement that makes the affected workflow more reliable for the specific carrier or product area. The merchant should not need to understand the internal request-builder, sync, or feature-flag details; support should translate the change into the visible setup or result described above.
## Common Questions & Troubleshooting
- If the product still shows old weight, confirm Shopify product update webhook or force import completed.
- If only variants fail, capture product ID, variant ID, old weight, and new weight.
- If label uses stale weight while Products page is correct, check order/product enrichment at label time.
## Support Escalation Packet
- Story card: ZI-133 - ZI-133 — Product weight updates in Shopify not syncing to MCSL
- Trello URL: https://trello.com/c/MpDgExFq/4199-from-sl-zi-133-product-weight-updates-in-shopify-not-syncing-to-mcsl-384061
- Store URL, account UUID, carrier account, order number, and generated label/tracking/report identifier.
- Screenshots of the setup page and request/log evidence whenever carrier behavior is involved.

CARD 12/19
# ZI-092
# ZI-092 — Shipping class/product category sync failure
| Ticket | #383437 |
| --- | --- |
| Release | MCSL 378 |
| Area | Shopify product category/shipping class sync on force import |
| Trello | https://trello.com/c/qRe1Cz6V/4200-from-sl-zi-092-shipping-class-product-category-sync-failure-383437 |
| Support scope | Shopify MCSL, Pain 8-9, 🚚 FedEx, 🚚 UPS, 🚚 USPS, Order & Product Data, MCSL 378 |


# Support Guide: ZI-092
## From SL: ZI-092 — Shipping class/product category sync failure [#383437]
## Feature Summary
Changing a Shopify product category/product_type did not update MCSL shipping class even after Force Import because an inner timestamp filter still blocked the update. The fix lets Force Import update category-only changes.
## Toggles & Prerequisites
| Toggle / config note \| No toggle. Validate release deployment and Shopify product category/shipping class sync state. |
| --- |

- Confirm the store/account is on the MCSL 378 release path before promising the behavior to a merchant.
- For carrier-specific cards, verify the exact carrier account and service before testing the behavior.

## Step-by-Step Support Walkthrough
1. Open Shopify and change a product category/product type.
2. Open MCSL > Products.
3. Run Force Import.
4. Open the product in MCSL and verify Shipping Class reflects the new Shopify category.
5. Repeat for a variable product.
6. Confirm other product fields remain intact after force import.
## Expected Behaviour
| What support should observe Force Import should update category-only changes for simple and variable products. QA verified both product types. |
| --- |

## Merchant-Safe Explanation
You can explain this as an MCSL release improvement that makes the affected workflow more reliable for the specific carrier or product area. The merchant should not need to understand the internal request-builder, sync, or feature-flag details; support should translate the change into the visible setup or result described above.
## Common Questions & Troubleshooting
- If Shipping Class stays old, confirm Force Import was used and not only passive sync.
- If only one variant updates, capture all variant IDs and timestamps.
- Because the fix affects all Shopify product attribute sync, watch for accidental overwrites of unrelated fields.
## Support Escalation Packet
- Story card: ZI-092 - ZI-092 — Shipping class/product category sync failure
- Trello URL: https://trello.com/c/qRe1Cz6V/4200-from-sl-zi-092-shipping-class-product-category-sync-failure-383437
- Store URL, account UUID, carrier account, order number, and generated label/tracking/report identifier.
- Screenshots of the setup page and request/log evidence whenever carrier behavior is involved.

CARD 13/19
# ZI-053
# ZI-053 — Auto-upload documents failing in REST
| Ticket | #379042 |
| --- | --- |
| Release | MCSL 378 |
| Area | FedEx REST electronic trade document auto-upload |
| Trello | https://trello.com/c/glNHyl10/4201-from-sl-zi-053-auto-upload-documents-failing-in-rest-379042 |
| Support scope | Shopify MCSL, SLA Breached, 🚚 FedEx, MCSL 378 |


# Support Guide: ZI-053
## From SL: ZI-053 — Auto-upload documents failing in REST [#379042]
## Feature Summary
FedEx REST international shipments need the correct ETD/product document upload request data so commercial documents are uploaded automatically instead of failing after REST migration.
## Toggles & Prerequisites
| Toggle / config note \| account-uuid.fedex.product.document.auto.upload.enabled: true |
| --- |

- Confirm the store/account is on the MCSL 378 release path before promising the behavior to a merchant.
- Use live MCSL store/account state as the source of truth for the toggle/config value above.
- For carrier-specific cards, verify the exact carrier account and service before testing the behavior.

## Step-by-Step Support Walkthrough
1. Enable account-uuid.fedex.product.document.auto.upload.enabled for the FedEx REST account.
2. Open MCSL > Carriers and confirm FedEx REST is configured for international shipping.
3. Prepare an international order requiring product/commercial documents.
4. Generate the label.
5. Open request logs and verify Electronic Trade Documents indicators and document specification are present.
- Request nodes to verify: FedEx REST ETD special-service/documentSpecification details and `enablePostUpload` for the document upload path.
6. Confirm the shipment completes without document auto-upload failure.
## Expected Behaviour
| What support should observe FedEx REST should include the required ETD/document data and successfully process auto-upload documents for eligible international shipments. |
| --- |

## Merchant-Safe Explanation
You can explain this as an MCSL release improvement that makes the affected workflow more reliable for the specific carrier or product area. The merchant should not need to understand the internal request-builder, sync, or feature-flag details; support should translate the change into the visible setup or result described above.
## Common Questions & Troubleshooting
- If auto-upload does not run, confirm the exact account UUID toggle is enabled.
- If SOAP-era metadata appears in the REST request, escalate because REST mapping is still wrong.
- If the shipment is domestic, explain that ETD document upload is an international/customs flow.
## Support Escalation Packet
- Story card: ZI-053 - ZI-053 — Auto-upload documents failing in REST
- Trello URL: https://trello.com/c/glNHyl10/4201-from-sl-zi-053-auto-upload-documents-failing-in-rest-379042
- Store URL, account UUID, carrier account, order number, and generated label/tracking/report identifier.
- Screenshots of the setup page and request/log evidence whenever carrier behavior is involved.
- Exact toggle/config value used for this card.

CARD 14/19
# ZI-266
# ZI-266 — Product weight changes sync to shipping label in real-time
| Ticket | #384731 |
| --- | --- |
| Release | MCSL 378 |
| Area | Real-time Shopify weight changes reflected in label generation |
| Trello | https://trello.com/c/1o49nwpU/4203-from-sl-zi-266-product-weight-changes-sync-to-shipping-label-in-real-time-384731 |
| Support scope | Shopify MCSL, Order & Product Data, MCSL 378 |


# Support Guide: ZI-266
## From SL: ZI-266 — Product weight changes sync to shipping label in real-time [#384731]
## Feature Summary
When a merchant updates product weight in Shopify, new label generation should use the updated weight rather than the stale value captured during an earlier sync.
## Toggles & Prerequisites
| Toggle / config note \| No toggle. Validate release deployment and real-time Shopify product weight sync before label generation. |
| --- |

- Confirm the store/account is on the MCSL 378 release path before promising the behavior to a merchant.
- For carrier-specific cards, verify the exact carrier account and service before testing the behavior.

## Step-by-Step Support Walkthrough
1. In Shopify, change a product or variant weight, for example from 2 lb to 2.5 lb.
2. Sync or force import products into MCSL.
3. Create a new order using the updated product or open an order that should refresh product data.
4. Generate or preview the shipping label.
5. Open package/request details and verify the updated weight is used.
6. Repeat for a variant-specific weight change and confirm only that variant is affected.
## Expected Behaviour
| What support should observe New label generation should use the latest Shopify weight after sync. QA notes verified simple and variable product weight updates. |
| --- |

## Merchant-Safe Explanation
You can explain this as an MCSL release improvement that makes the affected workflow more reliable for the specific carrier or product area. The merchant should not need to understand the internal request-builder, sync, or feature-flag details; support should translate the change into the visible setup or result described above.
## Common Questions & Troubleshooting
- If Products page is correct but the label uses old weight, check the order enrichment path.
- If only existing orders are stale, create a fresh order to distinguish order snapshot behavior from product-sync behavior.
- If weight unit changes are involved, verify both numeric weight and unit.
## Support Escalation Packet
- Story card: ZI-266 - ZI-266 — Product weight changes sync to shipping label in real-time
- Trello URL: https://trello.com/c/1o49nwpU/4203-from-sl-zi-266-product-weight-changes-sync-to-shipping-label-in-real-time-384731
- Store URL, account UUID, carrier account, order number, and generated label/tracking/report identifier.
- Screenshots of the setup page and request/log evidence whenever carrier behavior is involved.

CARD 15/19
# ZI-059
# ZI-059 — Australia Post international tracking not syncing to Shopify
| Ticket | #380339 |
| --- | --- |
| Release | MCSL 378 |
| Area | Australia Post international tracking sync to Shopify |
| Trello | https://trello.com/c/hMK8aQ3F/4204-from-sl-zi-059-australia-post-international-tracking-not-syncing-to-shopify-380339 |
| Support scope | Shopify MCSL, MCSL 378, Australia Post international tracking sync, QA verified |


# Support Guide: ZI-059
## From SL: ZI-059 — Australia Post international tracking not syncing to Shopify [#380339]
## Feature Summary
International Australia Post/eParcel tracking milestones should sync back to Shopify instead of leaving the order at only Tracking Added.
## Toggles & Prerequisites
| Toggle / config note \| No toggle. Validate release deployment and Australia Post international tracking event sync. |
| --- |

- Confirm the store/account is on the MCSL 378 release path before promising the behavior to a merchant.
- For carrier-specific cards, verify the exact carrier account and service before testing the behavior.

## Step-by-Step Support Walkthrough
1. Generate an Australia Post international label in MCSL.
2. Confirm tracking number is added to the Shopify order.
3. Wait for or simulate a supported international tracking milestone.
4. Check MCSL order grid Tracking Status.
5. Open Shopify order timeline and customer order status page.
6. Verify the latest milestone appears in Shopify and MCSL rather than remaining at Tracking Added.
## Expected Behaviour
| What support should observe Supported international tracking events should update MCSL tracking status and Shopify timeline/order status page. |
| --- |

## Merchant-Safe Explanation
You can explain this as an MCSL release improvement that makes the affected workflow more reliable for the specific carrier or product area. The merchant should not need to understand the internal request-builder, sync, or feature-flag details; support should translate the change into the visible setup or result described above.
## Common Questions & Troubleshooting
- If only Tracking Added appears, check whether the carrier has returned a later supported international milestone and whether the tracking event is eligible for Shopify sync.
- If MCSL updates but Shopify does not, inspect Shopify fulfillment/tracking sync logs.
- If domestic tracking works but international does not, capture the eParcel tracking payload for carrier-specific review.
## Support Escalation Packet
- Story card: ZI-059 - ZI-059 — Australia Post international tracking not syncing to Shopify
- Trello URL: https://trello.com/c/hMK8aQ3F/4204-from-sl-zi-059-australia-post-international-tracking-not-syncing-to-shopify-380339
- Store URL, account UUID, carrier account, order number, and generated label/tracking/report identifier.
- Screenshots of the setup page and request/log evidence whenever carrier behavior is involved.

CARD 16/19
# ZI-014
# ZI-014 — Pickup date/time not available in order report
| Ticket | #360396 |
| --- | --- |
| Release | MCSL 378 |
| Area | Pickup date/time fields in order reports |
| Trello | https://trello.com/c/QLBwlKPc/4205-from-sl-zi-014-pickup-date-time-not-available-in-order-report-360396 |
| Support scope | Shopify MCSL, SLA Breached, 🚚 BlueDart, Rates & Intelligence, MCSL 378 |


# Support Guide: ZI-014
## From SL: ZI-014 — Pickup date/time not available in order report [#360396]
## Feature Summary
Order reports should include pickup date and time when carrier pickup events are available, especially for BlueDart/customer reporting workflows.
## Toggles & Prerequisites
| Toggle / config note \| No toggle. Validate release deployment and report/export data source. |
| --- |

- Confirm the store/account is on the MCSL 378 release path before promising the behavior to a merchant.
- For carrier-specific cards, verify the exact carrier account and service before testing the behavior.

## Step-by-Step Support Walkthrough
1. Use a store/order where carrier pickup tracking has an actual pickup event.
2. Confirm tracking or pickup data is visible in MCSL for the order.
3. Open the reporting/order export flow.
4. Generate the order report.
5. Open the exported report and locate Pickup Date and Pickup Time columns.
6. Verify orders with pickup events show the correct values and orders without pickup events remain blank or show the expected empty state.
## Expected Behaviour
| What support should observe \| Reports should expose pickup timing when recorded. Card comments note BlueDart tracking was tested with customer credentials and worked as expected. Existing non-pickup report columns should not regress, and pickup date/time should reflect the expected report timezone/source scan. |
| --- |

## Merchant-Safe Explanation
You can explain this as an MCSL release improvement that makes the affected workflow more reliable for the specific carrier or product area. The merchant should not need to understand the internal request-builder, sync, or feature-flag details; support should translate the change into the visible setup or result described above.
## Common Questions & Troubleshooting
- Do not confuse scheduled pickup time with actual carrier pickup scan time; use the report/export timezone and source tracking scan when validating Pickup Date and Pickup Time.
- If pickup exists in tracking but not in report, check the internal API/reporting projection path.
- If only BlueDart is failing, collect carrier tracking response, order ID, and generated report row.
## Support Escalation Packet
- Story card: ZI-014 - ZI-014 — Pickup date/time not available in order report
- Trello URL: https://trello.com/c/QLBwlKPc/4205-from-sl-zi-014-pickup-date-time-not-available-in-order-report-360396
- Store URL, account UUID, carrier account, order number, and generated label/tracking/report identifier.
- Screenshots of the setup page and request/log evidence whenever carrier behavior is involved.

CARD 17/19
# ZI-097
# ZI-097 — Canpar Adult Signature (SA) service support
| Ticket | #379378 |
| --- | --- |
| Release | MCSL 378 |
| Area | Canpar Adult Signature service support |
| Trello | https://trello.com/c/sy0CwkjW/4196-from-sl-zi-097-canpar-adult-signature-sa-service-support-379378 |
| Support scope | SLA Breached, Pain 8-9, WooCommerce, 🚚 Canpar, MCSL 378 |


# Support Guide: ZI-097
## From SL: ZI-097 — Canpar Adult Signature (SA) service support [#379378]
## Feature Summary
Canpar shipments need support for Adult Signature (SA) rather than only the older NSR boolean behavior. The request should pass the correct Canpar signature service when selected.
## Toggles & Prerequisites
| Toggle / config note \| <storeAccountUUID>.canpar.use.2026.wsdls.enabled: true |
| --- |

- Confirm the store/account is on the MCSL 378 release path before promising the behavior to a merchant.
- Use live MCSL store/account state as the source of truth for the toggle/config value above.
- For carrier-specific cards, verify the exact carrier account and service before testing the behavior.

## Step-by-Step Support Walkthrough
1. Confirm the merchant uses Canpar and that Canpar services are configured.
2. Open the order or carrier service options where Canpar signature service is selected.
3. Select Adult Signature where available.
4. Generate or rate the shipment.
5. Open the request payload.
- Request nodes to verify: `signature` should carry `SA` or `SR`; legacy `nsr` should be omitted when not required.
6. Verify the request includes SA for Adult Signature or SR for Signature Required, and does not send an inappropriate nsr field when it should be omitted.
## Expected Behaviour
| What support should observe \| Canpar Adult Signature should be selectable/sent as SA. Signature Required should send SR and Adult Signature should send SA through Order Summary, bulk, and automation-rule flows. The legacy nsr field should not be included in shipment/rate requests when it is not required. |
| --- |

## Merchant-Safe Explanation
You can explain this as an MCSL release improvement that makes the affected workflow more reliable for the specific carrier or product area. The merchant should not need to understand the internal request-builder, sync, or feature-flag details; support should translate the change into the visible setup or result described above.
## Common Questions & Troubleshooting
- If Adult Signature is missing, confirm the release containing PR 2952 is deployed and verify both Order Summary and automation-rule paths.
- If nsr:false still appears unexpectedly, or automation rules do not pass SR/SA, capture the rate and shipment request payloads for escalation.
- This card is marked WooCommerce in Trello; confirm the exact app/store context before merchant-facing guidance.
## Support Escalation Packet
- Story card: ZI-097 - ZI-097 — Canpar Adult Signature (SA) service support
- Trello URL: https://trello.com/c/sy0CwkjW/4196-from-sl-zi-097-canpar-adult-signature-sa-service-support-379378
- Store URL, account UUID, carrier account, order number, and generated label/tracking/report identifier.
- Screenshots of the setup page and request/log evidence whenever carrier behavior is involved.
- Exact toggle/config value used for this card.

CARD 18/19
# ZI-357
# ZI-357 — FedEx rate display option to exclude VAT for EU tax compliance
| Ticket | #385094 |
| --- | --- |
| Release | MCSL 378 |
| Area | FedEx rate display excluding VAT for EU compliance |
| Trello | https://trello.com/c/PIEqO2BZ/4266-from-sl-zi-357-fedex-rate-display-option-to-exclude-vat-for-eu-tax-compliance-385094 |
| Support scope | MCSL 378, FedEx REST rates, EU VAT display, WooCommerce, rate shopping, QA in progress |


# Support Guide: ZI-357
## From SL: ZI-357 — FedEx rate display option to exclude VAT for EU tax compliance [#385094]
## Feature Summary
Merchants need an option to display FedEx rates excluding VAT for EU tax-compliance workflows, while preserving raw carrier response data and normal rate behavior when the option is off.
## Toggles & Prerequisites
| Toggle / config note \| account.uuid.fedex.rest.rates.changes.enabled: true |
| --- |

- Confirm the store/account is on the MCSL 378 release path before promising the behavior to a merchant.
- Use live MCSL store/account state as the source of truth for the toggle/config value above.
- For carrier-specific cards, verify the exact carrier account and service before testing the behavior.

## Step-by-Step Support Walkthrough
1. Enable account.uuid.fedex.rest.rates.changes.enabled for the target FedEx REST account.
2. Open the relevant FedEx REST rate/display setting and enable Exclude VAT from rate display if present.
3. Create an EU-destination checkout/rate-shopping scenario.
4. Request rates in MCSL or checkout.
5. Verify the displayed rate excludes VAT while the request/response log retains the full VAT-inclusive carrier amount and the VAT/tax component returned by FedEx.
- Request/response nodes to verify: gross rate amount and VAT/tax surcharge or component line in the raw FedEx REST rate response.
6. Turn the option off and confirm the normal VAT-inclusive display behavior returns where applicable.
## Expected Behaviour
| What support should observe \| When enabled, the rate shopping panel should display FedEx rates excluding VAT for the relevant EU scenario. Raw FedEx REST request/response logs must retain the full VAT-inclusive carrier amount and VAT/tax component or surcharge line; disabling the option should restore normal gross display behavior without changing label cost or carrier payload. |
| --- |

## Merchant-Safe Explanation
You can explain this as an MCSL release improvement that makes the affected workflow more reliable for the specific carrier or product area. The merchant should not need to understand the internal request-builder, sync, or feature-flag details; support should translate the change into the visible setup or result described above.
## Common Questions & Troubleshooting
- If the option is missing, confirm the account-level toggle is enabled.
- If displayed rate does not match logs, compare carrier returned charge, VAT/tax fields, UI display calculation, and whether the option is enabled only for display rather than mutating carrier payloads or label cost.
- This card is labeled WooCommerce as well as MCSL; confirm the target app/store before giving setup instructions.
## Support Escalation Packet
- Story card: ZI-357 - ZI-357 — FedEx rate display option to exclude VAT for EU tax compliance
- Trello URL: https://trello.com/c/PIEqO2BZ/4266-from-sl-zi-357-fedex-rate-display-option-to-exclude-vat-for-eu-tax-compliance-385094
- Store URL, account UUID, carrier account, order number, and generated label/tracking/report identifier.
- Screenshots of the setup page and request/log evidence whenever carrier behavior is involved.
- Exact toggle/config value used for this card.

CARD 19/19
# ZI-360
# ZI-360 — Custom BigCommerce theme blocking shipping rate display at checkout
| Ticket | #381243 |
| --- | --- |
| Release | MCSL 378 |
| Area | BigCommerce MCSL checkout rates: rate automation carrier/service validation |
| Trello | https://trello.com/c/6ojjAb0Z/4272-from-sl-zi-360-custom-bigcommerce-theme-blocking-shipping-rate-display-at-checkout-381243 |
| Support scope | BigCommerce MCSL, MCSL 378, rate automation rule validation, FedEx checkout rates, QA verified |


# Support Guide: ZI-360
## From SL: ZI-360 — Custom BigCommerce theme blocking shipping rate display at checkout [#381243]
## Feature Summary
The checkout rate issue is handled as a rate-automation configuration/validation problem: flat-rate rules without carrier attachment can produce carrier-not-found, and service restrictions can hide rates when FedEx returns a different service such as FEDEX_GROUND.
## Toggles & Prerequisites
| Toggle / config note \| No toggle. Validate BigCommerce MCSL rate automation carrier/service rule configuration. |
| --- |

- Confirm the store/account is on the MCSL 378 release path before promising the behavior to a merchant.
- For carrier-specific cards, verify the exact carrier account and service before testing the behavior.

## Step-by-Step Support Walkthrough
1. Confirm the merchant uses the BigCommerce MCSL checkout rate flow; do not assume the custom theme is the root cause until rate automation configuration is checked.
2. Open MCSL rate automation rules.
3. Inspect affected flat-rate automation rules for missing carrier attachment.
4. Compare the services required by the rule with the actual carrier response; for example, allow FEDEX_GROUND if FedEx is returning only FEDEX_GROUND for the shipment.
- Request/log fields to verify: rate automation rule carrier attachment, returned service such as `FEDEX_GROUND`, and rate errors such as `carrier not found` or `RateUnavailableForCarrierService`.
5. Save the corrected carrier/service rule configuration.
6. Open BigCommerce checkout and request shipping rates after the corrected automation rule is active.
7. Verify rates appear instead of an empty rate list or pickup-only checkout option.
## Expected Behaviour
| What support should observe \| Checkout should display available shipping rates after the automation rule is correctly attached to carrier/service data. Do not treat the custom theme as the root cause until carrier attachment and service restrictions are checked; examples include carrier-not-found and FedEx returning FEDEX_GROUND while the rule allows only express services. |
| --- |

## Merchant-Safe Explanation
You can explain this as a rate automation configuration validation fix. The merchant does not need to diagnose custom theme code first; support should verify whether the flat-rate rule has a carrier attached and whether its allowed service list matches what FedEx actually returns.
## Common Questions & Troubleshooting
- If logs say carrier not found, inspect the rate automation rule carrier attachment first.
- If FedEx returns FEDEX_GROUND but the automation rule expects FEDEX_2_DAY or FEDEX_EXPRESS_SAVER, include FEDEX_GROUND or remove the service restriction so returned carrier rates can pass through.
- If rates still do not appear after carrier attachment and service restrictions are corrected, collect checkout request/response logs and rule UUIDs before escalating.
- If only one checkout scenario fails, collect checkout URL, rate request logs, and the rate automation rule details.
## Support Escalation Packet
- Story card: ZI-360 - ZI-360 — Custom BigCommerce theme blocking shipping rate display at checkout
- Trello URL: https://trello.com/c/6ojjAb0Z/4272-from-sl-zi-360-custom-bigcommerce-theme-blocking-shipping-rate-display-at-checkout-381243
- Store URL, account UUID, carrier account, order number, and generated label/tracking/report identifier.
- Screenshots of the setup page and request/log evidence whenever carrier behavior is involved.
