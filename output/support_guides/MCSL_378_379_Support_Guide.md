# MCSL 378/379 — FedEx REST & PostNord Support Guide Support Guide

## Included Story Cards
| Story / card | Platform | Carrier scope | Toggle / prerequisite signal |
|---|---|---|---|
| Remove Rates and Transit api from Fedex Rest | Shopify | FedEx | None detected |
| ZI-031 | Shopify | PostNord | None detected |
| ZI-056 | Shopify | PostNord | None detected |
| From SL: MCSL 378 Missing Importer of Record in Fedex Rest | Shopify | FedEx | None detected |
| Label generation fails for One Rate with custom box | Shopify | FedEx | None detected |

## How Support Should Use This Package
- Use each card section as the support/demo guide for that feature.
- Confirm customer/test platform, live store, carrier account, order/product, and toggle state before promising behavior.
- Capture the escalation packet listed in the relevant card section if behavior does not match.

## Remove Rates and Transit api from Fedex Rest - Remove Rates and Transit api from Fedex Rest
## Support Guide: MCSL 379 — Remove Rates and Transit API from FedEx REST

*Remove Rates and Transit api from Fedex Rest*

---

### Feature Summary

In MCSL 379, the separate FedEx REST Transit/Time-in-Transit API call (`/availability/transittimes`) has been removed from the FedEx REST rate-fetching flow. Transit time data — including delivery date, transit days, and commit time — is now sourced directly from the fields already present in the FedEx REST Rates API response (`transitTime`, `operationalDetail.commitDate`, `operationalDetail.commitDay`). This change eliminates a redundant API call that was causing intermittent 503 errors under load, and simplifies the request flow without any loss of transit time visibility at checkout. All FedEx REST-enabled stores on Shopify are affected; no merchant-facing configuration change is required.

---

### Toggles & Prerequisites

| Toggle / config note | What support should confirm |
|---|---|
| No feature toggle detected | Change is applied globally to all FedEx REST-enabled stores on MCSL 379+ |
| FedEx REST must be the active carrier integration (not FedEx SOAP/legacy) | Confirm the store is using FedEx REST in hamburger menu > Carriers |
| MCSL release version must be 379 or later | Confirm release version from store/account context |
| FedEx carrier account must be connected and active | Confirm carrier credentials are valid in hamburger menu > Carriers > FedEx |
| Customer/test platform: Shopify | Walkthrough below is validated on Shopify; confirm platform from store context |

---

### Step-by-Step Support Walkthrough

1. **Confirm the store is on MCSL 379 or later.**
   Verify the release version from the store's account context or internal dashboard before proceeding.

2. **Confirm FedEx REST is the active carrier integration.**
   Navigate to **hamburger menu > Carriers** in MCSL. Confirm FedEx is listed and that the REST integration is active (not a legacy/SOAP connection). If the store is on FedEx SOAP, this change does not apply.

3. **Trigger a test rate request from the Shopify checkout.**
   Place a test order or use a draft order in **Shopify Admin > Orders** (or the Shopify storefront checkout) with a domestic shipment destination. Confirm that FedEx REST rates are returned and that estimated delivery dates/transit times are displayed at checkout.

   - **Request nodes to verify:** `transitTime`, `operationalDetail.commitDate`, `operationalDetail.commitDay` in the FedEx REST `/rates/quotes` response.

4. **Inspect the request logs to confirm only one API call is made.**
   Navigate to **ORDERS** in MCSL and open the relevant order. Review the request/response logs for the rate fetch event. Confirm that only the FedEx REST `/rates/quotes` endpoint is called — there should be **no** call to `/availability/transittimes` in the log.

   - **Request/log fields to verify:** Absence of any log entry for `/availability/transittimes`; presence of a single `/rates/quotes` call with transit time fields populated in the response.

5. **Verify transit time accuracy for domestic FedEx REST services.**
   Check that FedEx Ground and FedEx 2Day both return rates and transit times correctly. Confirm the estimated delivery date shown at checkout matches the values in the `operationalDetail.commitDate` field of the Rates API response.

   - **Request nodes to verify:** `operationalDetail.commitDate`, `operationalDetail.commitDay`, `transitTime` for each service in the `/rates/quotes` response.

6. **Verify transit time accuracy for international FedEx REST services.**
   Repeat the rate request using an international destination (e.g., FedEx International Priority). Confirm that transit time and delivery estimate display correctly at checkout and are sourced from the same Rates API response fields.

   - **Request nodes to verify:** `operationalDetail.commitDate`, `operationalDetail.commitDay`, `transitTime` in the `/rates/quotes` response for the international service.

7. **Regression check — confirm no errors at checkout for existing FedEx REST stores.**
   Confirm that rates are returned without error for existing FedEx REST-enabled stores. There should be no 503 errors or missing rate responses in the logs. If a store was previously experiencing intermittent 503 errors during rate fetch, confirm those are no longer present after MCSL 379.

---

### Expected Behaviour

| What support should observe | How to confirm |
|---|---|
| FedEx REST rates and transit times display correctly at Shopify checkout | Trigger a test rate request; confirm rates and estimated delivery dates appear for all tested FedEx REST services |
| Only one API call (`/rates/quotes`) appears in request logs per rate fetch | Review MCSL ORDERS request logs; confirm no `/availability/transittimes` call is logged |
| `transitTime` field is populated in the `/rates/quotes` response | Inspect the raw response in request logs for the `transitTime` node |
| `operationalDetail.commitDate` and `operationalDetail.commitDay` are populated in the response | Inspect the raw response in request logs for these nodes under `operationalDetail` |
| FedEx Ground, FedEx 2Day, FedEx Priority Overnight, and FedEx International Priority all return rates normally | Test each service; confirm no missing or errored rate responses |
| No intermittent 503 errors in rate fetch logs | Review request logs; confirm absence of 503 error responses on the rate call |
| No regression in rate display or service availability for existing FedEx REST stores | Confirm existing stores continue to receive rates without configuration changes |

---

### Merchant-Safe Explanation

We've made an internal improvement to how FedEx shipping rates and estimated delivery times are retrieved at checkout. Previously, two separate requests were made to FedEx — one for rates and one for transit times. We've streamlined this so that both rates and delivery estimates are retrieved in a single request, which is fully supported by FedEx. This means checkout rates and estimated delivery dates will continue to display exactly as before, and you may also notice improved reliability during high-traffic periods.

---

### Common Questions & Troubleshooting

- **Transit time or delivery date is missing at checkout after MCSL 379:**
  - First, check the request logs in MCSL ORDERS for the `/rates/quotes` response. Confirm that `transitTime` and `operationalDetail.commitDate` are present and populated in the response.
  - If these fields are absent, confirm the FedEx carrier account is active and that the correct FedEx REST services are enabled in hamburger menu > Carriers.
  - Confirm the store is on MCSL 379 or later.

- **Rates are not returning at checkout:**
  - Check request logs for any error responses on the `/rates/quotes` call. Note the HTTP status code and any error message returned by FedEx.
  - Confirm FedEx carrier credentials are valid in hamburger menu > Carriers.
  - Confirm no `/availability/transittimes` call is being made — if it is, the store may not be on MCSL 379 yet.

- **503 errors still appearing in logs:**
  - Confirm the store is on MCSL 379. If the release has been applied and 503 errors persist, they are originating from the `/rates/quotes` endpoint itself (a FedEx-side issue), not the removed transit endpoint. Escalate with log evidence.

- **When to inspect logs:**
  - Any time transit time is missing, incorrect, or rates are not displaying — pull the full request/response log from MCSL ORDERS for the affected order or rate fetch event.

- **When to escalate:**
  - Transit time fields (`transitTime`, `operationalDetail.commitDate`) are absent from the `/rates/quotes` response and FedEx credentials are confirmed valid.
  - A `/availability/transittimes` call is still appearing in logs on a store confirmed to be on MCSL 379 (possible release deployment issue).
  - Persistent 503 errors on `/rates/quotes` after MCSL 379 is confirmed.
  - Any regression in rate display or service availability not explained by carrier account or configuration issues.

---

### Support Escalation Packet

- **Story card:** Remove Rates and Transit api from Fedex Rest — MCSL 379 | Card URL: Not available
- **Store URL:** Confirm from live store/card context
- **Account UUID:** Confirm from live store/card context
- **Carrier account:** FedEx REST — confirm account ID and connection status from hamburger menu > Carriers
- **Order number:** Provide the order number used for the test rate request or the affected order
- **Generated label/tracking/report identifier:** Provide if a label was generated during testing; otherwise provide the rate request log ID from MCSL ORDERS
- **Screenshots required:**
  - hamburger menu > Carriers showing FedEx REST connection status
  - MCSL ORDERS request log showing the `/rates/quotes` call and response (with `transitTime` and `operationalDetail` nodes visible)
  - Confirmation that no `/availability/transittimes` call appears in the log
  - Checkout screenshot showing rates and estimated delivery dates (or absence thereof, if reporting a bug)
- **Exact toggle/config value:** No toggle detected — change is release-gated to MCSL 379+; confirm release version from store context

## ZI-031 - From SL: ZI-031 — PostNord service updates for May 2026 [#373200]
## Support Guide: ZI-031 — PostNord Service Updates for May 2026

*PostNord service list updated to May 2026 API catalogue; deprecated codes removed or remapped.*

---

### Feature Summary

MCSL's PostNord carrier integration has been updated to reflect PostNord's May 2026 API service catalogue changes, effective from June 2026. Several product codes have been deprecated or renamed by PostNord — including P19 (MyPack Collect) and P82 (PostNord Parcel) — and a new Economy delivery code has been introduced. MCSL's internal service-code mapping table has been updated to match the new catalogue, ensuring that merchants see current service names in the carrier dropdown and at checkout, and that label generation continues to work without requiring manual reconfiguration. This update affects all MCSL stores using PostNord for domestic and Nordic cross-border shipments.

---

### Toggles & Prerequisites

| Toggle / config note | What support should confirm |
|---|---|
| No feature toggles detected | This update ships automatically with MCSL 379; no toggle activation is required |
| MCSL release prerequisite | Store must be on MCSL 379 or later; confirm the installed plugin version before troubleshooting |
| PostNord carrier account configured | Confirm PostNord is active under hamburger menu > Carriers and that API credentials are saved |
| Existing PostNord service selections | Confirm whether the merchant had P19, P82, or other affected codes selected before the update |
| Customer/test platform | Shopify (SL ticket #373200); validate on Shopify Admin and MCSL app accordingly |
| Deprecated code handling | Deprecated codes should be removed from the selectable list or silently remapped — confirm which behaviour applies from live store/card context |

---

### Step-by-Step Support Walkthrough

1. **Confirm the MCSL plugin version on the merchant's Shopify store.**
   Navigate to the MCSL app on the merchant's Shopify Admin. Check the version displayed in the app footer or settings area. Confirm the store is running MCSL 379 or later before proceeding.

2. **Open the PostNord carrier configuration in MCSL.**
   Go to **hamburger menu > Carriers** in the MCSL app. Locate the PostNord carrier entry and open its settings. Confirm PostNord is enabled and that API credentials are present and saved.

3. **Verify the updated service codes appear in the carrier services dropdown.**
   Within the PostNord carrier settings, open the service/product code selection dropdown. Confirm that:
   - Updated service names for P19 (MyPack Collect, renamed) and P82 (PostNord Parcel, updated) are present with their new labels.
   - The new Economy delivery code is visible and selectable.
   - No deprecated codes remain as selectable options (or confirm graceful mapping behaviour — confirm exact handling from live store/card context).

4. **Check the checkout rate display on the Shopify storefront.**
   Place a test order on the merchant's Shopify store using a domestic PostNord-eligible address. Proceed to checkout and confirm that:
   - PostNord rates are returned and displayed correctly.
   - Service names shown at checkout match the updated May 2026 catalogue names.
   - No stale or deprecated service names appear.

5. **Generate a test label for a domestic PostNord shipment using an updated product code.**
   In the MCSL **ORDERS** tab, locate a test or recent PostNord domestic order. Attempt label generation and confirm the label is created successfully without errors.
   - **Request/response nodes to verify:** Confirm the outbound carrier API request carries the updated product code (e.g., the new P19 or P82 equivalent) and that the PostNord API response returns a valid label or tracking reference with no service-code rejection error.

6. **Generate a test label for a Nordic cross-border PostNord shipment.**
   In the MCSL **ORDERS** tab, locate or create a test order with a Nordic cross-border destination (e.g., Sweden to Denmark or Norway). Attempt label generation and confirm rates and label generation succeed.
   - **Request/response nodes to verify:** Confirm the product code in the outbound request matches the expected cross-border code from the May 2026 catalogue and that no deprecated-code error is returned by PostNord.

7. **Run a regression check on existing PostNord store configurations.**
   For merchants who had PostNord services configured before the MCSL 379 update, confirm that:
   - Previously saved service selections have been preserved or gracefully remapped.
   - Label generation for existing PostNord orders (pre-update) continues to succeed.
   - No errors appear in the MCSL request logs related to unrecognised or invalid PostNord product codes.
   - **Request/log fields to verify:** Check request logs in the MCSL app for any `invalid_service_code`, `product_not_found`, or equivalent PostNord API error nodes on orders placed before and after the update.

8. **Confirm no re-configuration is required from the merchant.**
   The update should be transparent — merchants on MCSL 379 should see the new service names automatically. If a merchant reports that their PostNord dropdown still shows old service names, confirm the plugin version first (Step 1), then check whether a carrier settings save/refresh resolves the display.

---

### Expected Behaviour

| What support should observe | How to confirm |
|---|---|
| Updated PostNord service names (P19, P82, new Economy code) visible in carrier services dropdown | hamburger menu > Carriers > PostNord service selection dropdown |
| Deprecated PostNord service codes absent from the selectable list, or silently remapped | Inspect dropdown; confirm no deprecated codes are selectable — exact mapping behaviour to confirm from live store/card context |
| New Economy delivery code appears and is selectable | hamburger menu > Carriers > PostNord dropdown |
| PostNord rates returned correctly at Shopify checkout for domestic and Nordic cross-border shipments | Test checkout with eligible address; rates display with updated service names |
| Label generation succeeds for domestic PostNord shipments using updated product codes | ORDERS tab > generate label; no API rejection error; label/tracking reference returned |
| Label generation succeeds for Nordic cross-border PostNord shipments | ORDERS tab > generate label for cross-border order; confirm success |
| Outbound API request carries updated PostNord product code | Request log: product code node matches May 2026 catalogue code, not a deprecated value |
| PostNord API response contains no service-code rejection or deprecated-code error | Response log: no `invalid_service_code` or equivalent error node |
| Existing PostNord configurations continue to function without merchant re-configuration | Regression test on pre-update orders; label generation succeeds; no errors in request logs |
| Merchants on MCSL 379 see new service names without manual changes | Confirm on live store after plugin update; no reconfiguration prompt required |

---

### Merchant-Safe Explanation

PostNord updated their shipping service catalogue in May 2026, renaming and retiring several product codes effective June 2026. We've updated our PostNord integration to match their new catalogue, so your shipping services, rates, and label generation will continue to work correctly. You don't need to change any settings — the new service names will appear automatically once your store is on the latest plugin version. If you notice any PostNord services missing or see unexpected errors after updating, please contact support with your store details and a screenshot of your PostNord carrier settings.

---

### Common Questions & Troubleshooting

- **Merchant reports PostNord dropdown still shows old service names:**
  Check the installed MCSL plugin version first. If the store is not yet on MCSL 379, the update has not been applied. Advise the merchant to update the plugin.

- **Merchant reports a PostNord service they previously used is no longer available:**
  Confirm whether the service code was deprecated by PostNord in the May 2026 catalogue. If it was deprecated, advise the merchant to select the replacement service. Confirm the exact deprecated-to-replacement mapping from live store/card context.

- **Label generation fails after the update with a PostNord API error:**
  Inspect the request log in the MCSL app for the failing order. Check the outbound product code node — if a deprecated code is still being sent, this may indicate a mapping gap. Escalate with the full request/response log.

- **Rates not appearing at checkout after the update:**
  Confirm PostNord API credentials are still valid under hamburger menu > Carriers. Check request logs for rate-fetch errors. If credentials are valid and logs show a service-code error, escalate.

- **Existing orders placed before the update are failing label generation:**
  Check whether the order has a deprecated product code stored against it. Inspect request logs for the specific error node. Escalate if remapping did not apply to saved orders.

- **When to inspect logs:**
  Any time label generation or rate fetch fails for a PostNord order after MCSL 379 is installed. Focus on the product code node in the outbound request and any error codes in the PostNord response.

- **When to escalate:**
  Escalate if a deprecated code is still being sent in the outbound request after the update, if label generation fails for a service that should be supported in the new catalogue, or if a merchant's existing configuration was not preserved after the plugin update.

---

### Support Escalation Packet

- **Story card:** ZI-031 — PostNord Service Updates for May 2026 | **Trello URL:** Not provided — confirm from card context
- **Release:** MCSL 379 | **Approved:** 2026-05-12
- **SL ticket reference:** #373200
- **Store URL:** Confirm from merchant/ticket context
- **Account UUID:** Confirm from merchant/ticket context
- **Carrier account:** PostNord — confirm API credentials and account region from hamburger menu > Carriers
- **Order number(s):** Provide the failing order number(s) from the MCSL ORDERS tab
- **Generated label / tracking reference:** Include any label ID or tracking number returned (or the error returned in place of one)
- **Screenshots required:**
  - PostNord carrier settings page showing

## ZI-056 - From SL: ZI-056 — PostNord return label product codes [#379784]
## Support Guide: ZI-056 — PostNord Return Label Product Codes

*From SL: ZI-056 — PostNord return label product codes [#379784]*

---

### Feature Summary

Prior to MCSL 379, generating a PostNord return label sent the outbound product code in the API request, causing PostNord to reject the request with an invalid product code error. This fix introduces a dedicated return product code mapping for all PostNord services that support returns (e.g. return variants of P19, P82), so that return label requests now carry the correct return-specific `productCode` value. This change affects PostNord label generation on Shopify and resolves merchant-reported failures when attempting to create return labels through the app.

---

### Toggles & Prerequisites

| Toggle / config note | What support should confirm |
|---|---|
| No feature toggle detected | Fix is applied at the code level; no merchant-side toggle required |
| PostNord carrier account must be connected | Confirm PostNord is active under hamburger menu > Carriers in MCSL |
| PostNord service must support returns | Confirm the selected service has a return variant (e.g. return variant of P19 or P82); not all PostNord services support returns |
| Return label generation must be enabled | Confirm the merchant is using the return label workflow, not standard outbound label generation |
| MCSL 379 or later must be installed | Confirm the store is on release 379 or above before troubleshooting product code errors |
| Customer/test platform: Shopify | Validate on Shopify Admin and MCSL app; confirm store is Shopify-based |

---

### Step-by-Step Support Walkthrough

1. **Confirm the store is on MCSL 379 or later.**
   Check the installed app version in the merchant's Shopify Admin or via the MCSL dashboard before proceeding.

2. **Confirm PostNord is connected and configured.**
   In MCSL, go to **hamburger menu > Carriers**, locate PostNord, and confirm the carrier account is active and credentials are valid.

3. **Confirm the PostNord service selected supports return labels.**
   In MCSL, go to **hamburger menu > Carriers > PostNord settings** and verify the service being used has a return variant available (e.g. return variant of P19 or P82). If the selected service does not support returns, the merchant will need to select a compatible service.

4. **Navigate to the order and attempt return label generation.**
   In the MCSL **ORDERS** tab, locate the relevant order. Initiate a return label from the order actions. Confirm the return label workflow is being used (not the standard outbound label action).

5. **Verify the API request sends the correct return product code.**
   Open the request logs for the PostNord return label request.
   - `- Request node to verify:` `productCode` field in the PostNord return label API request must contain the return-specific product code (e.g. return variant of P19 or P82), **not** the outbound product code.

6. **Confirm the return label is generated successfully.**
   After submission, confirm:
   - No `invalid product code` error is returned by the PostNord API.
   - The return label PDF is available for download from the ORDERS tab.
   - The PDF displays correct PostNord return service branding and reference information.

7. **Verify outbound PostNord label generation is unaffected.**
   From the MCSL **ORDERS** tab, generate a standard outbound PostNord label on a separate test order. Confirm the outbound label generates without error and the `productCode` in the outbound request remains the correct outbound code.
   - `- Request node to verify:` `productCode` field in the outbound PostNord label API request must still contain the outbound product code, unchanged from pre-fix behaviour.

---

### Expected Behaviour

| What support should observe | How to confirm |
|---|---|
| PostNord return label generates without API error | No `invalid product code` or validation error in the PostNord API response |
| `productCode` in return label request contains the return-specific code | Inspect the `productCode` node in the PostNord return label API request log |
| `productCode` in outbound label request is unchanged | Inspect the `productCode` node in a standard outbound PostNord label request log |
| Return label PDF downloads successfully | PDF is accessible from the ORDERS tab after label generation |
| Return label PDF shows correct PostNord return service branding/reference | Open the downloaded PDF and confirm PostNord return service details are present |
| No regression in outbound PostNord label generation | Generate an outbound label and confirm it succeeds with the correct outbound product code |

---

### Merchant-Safe Explanation

PostNord requires a different service code when generating return labels compared to standard outbound labels. Previously, the app was sending the outbound code for both label types, which caused PostNord to reject return label requests. This has been corrected — the app now automatically sends the right code for return labels, so merchants can generate PostNord return labels without errors. No changes to your settings are needed; the fix applies automatically on MCSL 379.

---

### Common Questions & Troubleshooting

- **Check first:** Confirm the store is on MCSL 379 or later. The fix is not available on earlier releases.
- **Check first:** Confirm the PostNord service selected by the merchant supports return labels. Not all PostNord services have a return variant — if the service does not support returns, the merchant must switch to a compatible service.
- **Check first:** Confirm the merchant is using the return label workflow in the ORDERS tab, not the standard outbound label action.
- **If the error persists after upgrading to 379:** Pull the PostNord return label API request log and inspect the `productCode` field. If it still shows an outbound code, escalate with the log attached — this may indicate the return product code mapping is missing for that specific service.
- **If the outbound label is now failing:** Pull the outbound PostNord label request log and inspect the `productCode` field. Confirm it has not been overwritten with a return code. Escalate if regression is confirmed.
- **If the PDF does not download:** Confirm the API response shows a successful label creation (no errors). If the API succeeded but the PDF is unavailable, escalate as a label retrieval issue separate from the product code fix.
- **Do not escalate** solely because the merchant's PostNord service does not support returns — this is a PostNord service limitation, not an app defect.
- **Escalate** if the `productCode` in the return label request is still incorrect on MCSL 379, or if a previously working outbound PostNord service is now failing after the upgrade.

---

### Support Escalation Packet

- **Story card:** ZI-056 — PostNord return label product codes | **Trello URL:** Not available — reference SL ticket #379784
- **Store URL:** Confirm from live store/card context
- **Account UUID:** Confirm from live store/card context
- **Carrier account:** PostNord — confirm account ID and connected credentials
- **Order number:** Order used to reproduce the return label failure
- **Generated label / tracking identifier:** Return label ID or tracking number from the failed or successful attempt
- **Screenshots required:** MCSL ORDERS tab showing the return label action; PostNord carrier settings page (hamburger menu > Carriers); request log showing the `productCode` field in the return label API request and response
- **Toggle/config value:** No toggle gating this fix — confirm MCSL release version is 379 or later and include it in the escalation packet

## From SL: MCSL 378 Missing Importer of Record in Fedex Rest - From SL: MCSL 378 Missing Importer of Record in Fedex Rest
## Support Guide: MCSL 378 — Missing Importer of Record in FedEx REST

*From SL: MCSL 378 Missing Importer of Record in FedEx Rest*

---

### Feature Summary

Prior to this fix, the Importer of Record (IOR) details configured in MCSL's FedEx REST carrier settings were not being included in the FedEx REST shipment creation request payload. This meant international shipments that legally require an IOR party block were being submitted to FedEx without it, potentially causing label generation failures or compliance issues. MCSL 378 corrects this by ensuring the `importerOfRecord` block is correctly populated and sent under `requestedShipment` in the FedEx REST `/ship/v1/shipments` payload whenever IOR details are configured. This fix is specific to the FedEx REST integration and affects international shipment services such as FedEx International Priority and FedEx International Economy.

---

### Toggles & Prerequisites

| Toggle / config note | What support should confirm |
|---|---|
| No feature toggle detected | Fix is applied at the code level; no toggle needs to be enabled |
| IOR details must be configured in MCSL FedEx REST carrier settings | Confirm the merchant has entered IOR name, address, contact, and account number in the FedEx REST carrier settings page |
| FedEx REST integration (not FedEx SOAP/legacy) | Confirm the store is using the FedEx REST carrier, not the legacy FedEx SOAP integration |
| International shipment service required | IOR block is relevant only for international shipments (e.g., FedEx International Priority, FedEx International Economy) |
| Release MCSL 378 must be deployed | Confirm the store/plugin version is on or after the MCSL 378 release (approved 2026-05-12) |
| Customer/test platform: Shopify | Validate on the merchant's Shopify store; confirm MCSL app is active and connected |

---

### Step-by-Step Support Walkthrough

1. **Confirm the merchant is on MCSL 378 or later.**
   Verify the installed MCSL plugin/app version on the merchant's Shopify store is at or above the MCSL 378 release date (2026-05-12). If the version is older, the fix is not present — advise upgrade before further troubleshooting.

2. **Confirm FedEx REST is the active carrier integration.**
   In MCSL, navigate to **hamburger menu > Carriers**, locate the FedEx carrier entry, and confirm it is configured as **FedEx REST** (not FedEx SOAP or a legacy FedEx connection). The carrier settings page should reference REST API credentials (API Key / Secret), not a FedEx meter number.

3. **Confirm IOR details are configured in FedEx REST carrier settings.**
   Still in **hamburger menu > Carriers**, open the FedEx REST carrier settings. Scroll to the Importer of Record section and confirm all required fields are populated:
   - **Name**
   - **Address** (street lines, city, state/province code, postal code, country code)
   - **Contact** (person name, phone number)
   - **Account Number**

   If any field is blank, the `importerOfRecord` block will not be sent. Ask the merchant to complete all fields and save.

4. **Generate a test international shipment label from the Shopify Admin / MCSL ORDERS tab.**
   Navigate to the **ORDERS** tab in MCSL. Locate or create an order with an international destination. Attempt to generate a FedEx REST label using an international service (FedEx International Priority or FedEx International Economy). Confirm label generation completes successfully without error.

5. **Inspect the FedEx REST request log to verify the `importerOfRecord` block.**
   In MCSL, navigate to the request/response logs for the shipment created in Step 4. Locate the outbound FedEx REST `/ship/v1/shipments` request payload.

   - **Request node to verify:** `requestedShipment.importerOfRecord` — confirm the block is present and contains the following child fields:
     - `name`
     - `accountNumber`
     - `contact.personName`
     - `contact.phoneNumber`
     - `address.streetLines`
     - `address.city`
     - `address.stateOrProvinceCode`
     - `address.postalCode`
     - `address.countryCode`

6. **Verify regression: FedEx REST shipments without IOR configured are unaffected.**
   If the merchant has a second FedEx REST carrier configuration without IOR details, or if IOR fields are cleared and saved, generate a domestic or non-IOR international shipment and confirm:
   - The `importerOfRecord` block is **absent** from the request payload.
   - Label generation still succeeds normally.
   - No unintended data is injected into the request.

---

### Expected Behaviour

| What support should observe | How to confirm |
|---|---|
| `importerOfRecord` block appears in FedEx REST `/ship/v1/shipments` request when IOR is configured | Inspect request log; locate `requestedShipment.importerOfRecord` and confirm all child fields are populated |
| `importerOfRecord.name` matches the name entered in MCSL FedEx REST carrier settings | Compare request log value against the IOR Name field in hamburger menu > Carriers > FedEx REST settings |
| `importerOfRecord.accountNumber` matches the account number entered in MCSL settings | Compare request log value against the IOR Account Number field in carrier settings |
| `importerOfRecord.contact` contains `personName` and `phoneNumber` | Verify both sub-fields are present and non-empty in the request log |
| `importerOfRecord.address` contains `streetLines`, `city`, `stateOrProvinceCode`, `postalCode`, `countryCode` | Verify all five address sub-fields are present and correctly mapped in the request log |
| International label generation succeeds (FedEx International Priority, FedEx International Economy) when IOR is configured | Label is generated without error; tracking number is returned in the ORDERS tab on the Shopify store |
| FedEx REST shipments without IOR configured are unaffected — no `importerOfRecord` block in request | Inspect request log for a non-IOR shipment; confirm the block is absent and label generation succeeds |

---

### Merchant-Safe Explanation

When you configure Importer of Record details in your FedEx REST carrier settings within the PluginHive app, those details are now correctly included in every international shipment request sent to FedEx. This ensures your international labels generate successfully and that FedEx receives the required IOR information for customs and compliance purposes. If you have not configured IOR details, your domestic and non-IOR international shipments continue to work exactly as before — nothing changes for those shipments.

---

### Common Questions & Troubleshooting

- **Check first:** Confirm the merchant is on MCSL 378 or later. If the plugin version predates 2026-05-12, the fix is not active — upgrade is required.
- **Check first:** Confirm the carrier in use is FedEx REST, not FedEx SOAP/legacy. The IOR fix applies only to the REST integration.
- **Check first:** Confirm all IOR fields (name, address, contact, account number) are fully populated and saved in hamburger menu > Carriers > FedEx REST settings. A partially filled IOR section may result in the block being omitted or causing a FedEx API validation error.
- **If the `importerOfRecord` block is missing from the request log despite IOR being configured:** Confirm the plugin version, re-save the carrier settings, and attempt label generation again. If the block is still absent, escalate with the full request log.
- **If label generation fails with IOR configured:** Capture the FedEx REST response/error from the request log. FedEx may return a validation error if any IOR field value is invalid (e.g., incorrect country code format, missing phone number). Share the exact error node from the response log with the merchant or escalation team.
- **If the merchant reports IOR appearing on shipments where it should not:** Verify whether IOR fields were inadvertently saved in the carrier settings. Clear the IOR fields, save, and retest.
- **When to inspect logs:** Any time label generation fails or the merchant questions whether IOR data is being sent — always pull the FedEx REST request log and check `requestedShipment.importerOfRecord`.
- **When to escalate:** If the `importerOfRecord` block is absent after confirming MCSL 378 is deployed and IOR is fully configured, or if FedEx returns an unexpected error related to the IOR block, escalate with the full support packet below.

---

### Support Escalation Packet

- **Story card:** MCSL 378 — Missing Importer of Record in FedEx REST | Card URL: not available (confirm from internal tracker)
- **Store URL:** *(collect from merchant)*
- **Account UUID:** *(collect from MCSL account record)*
- **Carrier account:** FedEx REST — collect the FedEx account number associated with the carrier configuration in MCSL
- **Order number:** *(collect the Shopify order number used for the test label)*
- **Generated label / tracking identifier:** *(collect the FedEx tracking number returned for the test shipment)*
- **Screenshots required:**
  - MCSL hamburger menu > Carriers > FedEx REST settings page showing the IOR fields populated
  - Full FedEx REST `/ship/v1/shipments` request log showing the `requestedShipment.importerOfRecord` block (or its absence if the issue is that it is missing)
  - FedEx REST response log if label generation failed, showing the exact error message and error code
- **Exact toggle/config value:** No feature toggle — confirm MCSL plugin version is 378 or later and IOR fields are saved in carrier settings

## Label generation fails for One Rate with custom box - Label generation fails for One Rate with custom box
## Support Guide: MCSL 379 — FedEx One Rate Label Failure with Custom Box

*Label generation fails for One Rate with custom box*

---

### Feature Summary

Prior to MCSL 379, attempting to generate a FedEx One Rate label with a custom box configured as the packaging would result in a silent failure driven by a `PACKAGING.MISMATCH` error returned from the FedEx REST API. The merchant received no actionable feedback. This release adds pre-request packaging validation for FedEx One Rate services on Shopify: MCSL now either surfaces a clear, merchant-safe error explaining that One Rate requires FedEx-branded packaging, or automatically selects the appropriate FedEx One Rate packaging type before the label request is sent. Non-One-Rate FedEx services with custom boxes are unaffected.

---

### Toggles & Prerequisites

| Toggle / config note | What support should confirm |
|---|---|
| No feature toggles detected | Fix is applied at the platform level for all eligible stores on MCSL 379 |
| Release prerequisite: MCSL 379 | Confirm the store is running MCSL 379 or later before troubleshooting |
| FedEx carrier account connected | Confirm a valid FedEx account is connected under hamburger menu > Carriers |
| FedEx One Rate service enabled | Confirm a One Rate service (e.g., FedEx One Rate Express Saver) is selected in the shipping configuration |
| Packaging configured in MCSL | Confirm packaging type is set — either a custom box or a FedEx-branded One Rate box — under hamburger menu > Products or packaging settings |
| Customer/test platform: Shopify | Validate all steps in the Shopify Admin and MCSL on the merchant's Shopify store |

---

### Step-by-Step Support Walkthrough

1. **Confirm the MCSL release version.** Verify the store is on MCSL 379. If the store is on an earlier release, this fix is not available — note the version and escalate if needed.

2. **Confirm the FedEx carrier connection.**
   Navigate to **hamburger menu > Carriers** in MCSL. Confirm the FedEx account is connected and active. Note the carrier account identifier for the escalation packet.

3. **Confirm the packaging configuration.**
   Navigate to **hamburger menu > Products** (or the packaging/box settings area in MCSL). Identify whether the merchant has a custom box set as the default packaging or a FedEx-branded One Rate packaging type (e.g., FEDEX_SMALL_BOX, FEDEX_MEDIUM_BOX, FEDEX_ENVELOPE, FEDEX_PAK, FEDEX_LARGE_BOX, FEDEX_EXTRA_LARGE_BOX, FEDEX_TUBE).

4. **Reproduce the custom box + One Rate scenario (TC1).**
   With a custom box configured as packaging, attempt to generate a FedEx One Rate label from the **ORDERS** tab in MCSL (or from **Shopify Admin > Orders**, selecting the relevant order and triggering label generation through MCSL).
   - Confirm that MCSL **does not silently fail**. A clear, merchant-safe error message should appear — for example: *"One Rate requires FedEx-branded packaging. Please select a FedEx One Rate box from the packaging settings."*
   - Confirm the `PACKAGING.MISMATCH` error is **not** surfaced raw to the merchant.

5. **Reproduce the FedEx-branded packaging + One Rate scenario (TC2 / TC5).**
   Switch the packaging to a FedEx One Rate packaging type (e.g., FedEx Small Box or FedEx Envelope) and attempt label generation again from the **ORDERS** tab.
   - Confirm the label generates successfully and a tracking number is returned.

6. **Inspect the FedEx REST label request payload.**
   Open the request/response logs in MCSL (request logs or diagnostic log area). Locate the FedEx REST label request for the One Rate shipment.
   - Request nodes to verify: `requestedShipment.requestedPackageLineItems[0].dimensions` and `packagingType` — when a One Rate service is selected, `packagingType` must be a valid One Rate packaging enum (`FEDEX_ENVELOPE`, `FEDEX_PAK`, `FEDEX_SMALL_BOX`, `FEDEX_MEDIUM_BOX`, `FEDEX_LARGE_BOX`, `FEDEX_EXTRA_LARGE_BOX`, or `FEDEX_TUBE`). The value `YOUR_PACKAGING` or `CUSTOM` must **not** appear in this field for One Rate requests.

7. **Confirm non-One-Rate regression is absent (TC4).**
   With a custom box configured, attempt label generation using a standard (non-One-Rate) FedEx service from the **ORDERS** tab. Confirm the label generates successfully and no new errors are introduced.

---

### Expected Behaviour

| What support should observe | How to confirm |
|---|---|
| Custom box + One Rate service → clear merchant-facing error displayed | Error message visible in MCSL ORDERS tab or Shopify Admin label generation UI; no silent failure |
| Error message is merchant-safe and actionable | Message reads approximately: *"One Rate requires FedEx-branded packaging. Please select a FedEx One Rate box from the packaging settings."* |
| `PACKAGING.MISMATCH` API error is no longer exposed raw to the merchant | Check UI — raw FedEx error code should not be visible to the merchant |
| FedEx-branded One Rate packaging + One Rate service → label generated successfully | Label and tracking number returned; visible in ORDERS tab and Shopify Admin order |
| `packagingType` in FedEx REST label request is a valid One Rate enum | In request logs: `packagingType` = `FEDEX_SMALL_BOX`, `FEDEX_MEDIUM_BOX`, `FEDEX_ENVELOPE`, `FEDEX_PAK`, `FEDEX_LARGE_BOX`, `FEDEX_EXTRA_LARGE_BOX`, or `FEDEX_TUBE` — never `CUSTOM` or `YOUR_PACKAGING` when One Rate service is selected |
| `requestedShipment.requestedPackageLineItems[0].dimensions` reflects the selected FedEx box | Verify dimensions in the request log correspond to the FedEx One Rate box type selected, not a custom box dimension |
| Non-One-Rate FedEx services with custom boxes are unaffected | Label generation succeeds as before; no new errors in request logs |

---

### Merchant-Safe Explanation

FedEx One Rate is a flat-rate shipping program that requires shipments to be sent in FedEx-branded packaging — custom or merchant-supplied boxes are not accepted by FedEx for this service. Previously, if a custom box was configured in the app, attempting to generate a One Rate label would fail without a clear explanation. With this update, the app now catches this mismatch before sending the request to FedEx and shows a clear message asking you to select a FedEx One Rate box (such as FedEx Small Box, Medium Box, Envelope, or Pak) in your packaging settings. Once the correct FedEx packaging is selected, One Rate labels will generate as expected.

---

### Common Questions & Troubleshooting

- **Merchant reports label still failing silently after MCSL 379:** Confirm the store is actually running MCSL 379 — check the release version first. If on an older release, escalate for upgrade.
- **Merchant sees the error message but doesn't know how to fix it:** Direct them to **hamburger menu > Products** (or the packaging settings area in MCSL) and instruct them to select a FedEx One Rate packaging type instead of a custom box.
- **Merchant asks which packaging types are valid for One Rate:** Valid options are FedEx Envelope, FedEx Pak, FedEx Small Box, FedEx Medium Box, FedEx Large Box, FedEx Extra Large Box, and FedEx Tube. These must be available as selectable options in MCSL packaging settings.
- **Merchant reports One Rate label failing even after selecting a FedEx-branded box:** Inspect the FedEx REST label request log. Check that `packagingType` is set to the correct One Rate enum and not `CUSTOM`. If `packagingType` is still `CUSTOM` in the request, this is a bug — collect logs and escalate.
- **Merchant reports non-One-Rate FedEx labels broken after this release:** This is a potential regression. Collect the request/response log, order number, and packaging configuration, and escalate immediately.
- **When to inspect logs:** Any time label generation fails for a FedEx One Rate service, pull the FedEx REST label request log and verify `packagingType` and `requestedShipment.requestedPackageLineItems[0].dimensions`.
- **When to escalate:** If the clear error message is not shown for custom box + One Rate, if `packagingType` is still `CUSTOM` in the outbound request on MCSL 379, or if non-One-Rate services are regressing.

---

### Support Escalation Packet

- **Story:** MCSL 379 — Label generation fails for One Rate with custom box | Card URL: None provided
- **Store URL:** *(collect from merchant)*
- **Account UUID:** *(collect from MCSL account record)*
- **Carrier account:** FedEx account identifier as shown under hamburger menu > Carriers
- **Order number:** *(collect the specific Shopify order number where label generation failed)*
- **Generated label / tracking identifier:** *(collect if a label was partially created, or note "label not generated" if failure occurred pre-request)*
- **Screenshots required:**
  - MCSL packaging settings showing the configured box type (custom or FedEx-branded)
  - MCSL ORDERS tab or Shopify Admin showing the error message displayed (or absence of one)
  - Full FedEx REST label request log showing `packagingType` and `requestedShipment.requestedPackageLineItems[0].dimensions` values
  - F