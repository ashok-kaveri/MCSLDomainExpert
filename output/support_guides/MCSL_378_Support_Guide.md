# MCSL 378 — FedEx REST & PostNord Support Guide Support Guide

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
## Support Guide: MCSL 378 — Remove Rates and Transit API from FedEx REST

*Remove Rates and Transit api from Fedex Rest*

---

### Feature Summary

In MCSL 378, the FedEx REST integration no longer makes a separate call to the `/availability/transittimes` endpoint to retrieve transit time data. Transit times are now sourced directly from the fields already present in the Rates API response (`transitTime`, `operationalDetail.commitDate`, `operationalDetail.commitDay`). This change eliminates a redundant API call that was causing intermittent 503 errors under load and simplifies the request flow. All FedEx REST services — including Ground, 2Day, Priority Overnight, and International Priority — continue to return rates and estimated delivery dates at checkout without any change to the customer-facing experience.

---

### Toggles & Prerequisites

| Toggle / config note | What support should confirm |
|---|---|
| No feature toggles detected | Change is applied globally to all FedEx REST-enabled stores on MCSL 378+ |
| FedEx REST carrier must be active | Confirm the store is using FedEx REST (not FedEx SOAP/legacy) via hamburger menu > Carriers |
| MCSL release version | Confirm store is on MCSL 378 or later before troubleshooting transit time or rate issues |
| FedEx carrier account credentials | Confirm valid FedEx REST API credentials are saved and active in hamburger menu > Carriers |
| Shopify store (test/customer platform) | Validated on Shopify; confirm platform if escalating a non-Shopify report |

---

### Step-by-Step Support Walkthrough

1. **Confirm the store is on MCSL 378 or later.**
   Verify the installed MCSL version before proceeding. If the store is on an earlier release, this change is not present and transit time issues should be escalated as a pre-378 regression.

2. **Confirm FedEx REST is the active carrier configuration.**
   Navigate to **hamburger menu > Carriers** in MCSL. Confirm that FedEx REST is listed and enabled. If the store is using a legacy FedEx SOAP connection, this change does not apply.

3. **Confirm FedEx REST credentials are valid and saving correctly.**
   Still in **hamburger menu > Carriers**, open the FedEx REST carrier settings and confirm API credentials are present and not flagged with an auth error. A credential issue here will prevent any Rates API response from returning, including transit time fields.

4. **Reproduce a rate request from the Shopify checkout or test order.**
   Place a test order or use a Shopify Admin draft order to trigger a live rate request for a FedEx REST-eligible shipment. Confirm that FedEx rates appear at checkout with estimated delivery dates visible.

5. **Verify transit time is displaying correctly for all relevant FedEx REST services.**
   Confirm estimated delivery dates or transit time labels appear for:
   - FedEx Ground
   - FedEx 2Day
   - FedEx Priority Overnight
   - FedEx International Priority

   If any service is missing a transit time, note the specific service name and proceed to log verification in the next step.

6. **Check request logs to confirm only one Rates API call is made — no separate transit time call.**
   Navigate to **hamburger menu > Carriers** or the **ORDERS** tab request log viewer (confirm exact log path from live store context). Review the outbound API calls for the FedEx REST request.

   - **Request nodes to verify:** Confirm the log contains a call to `/rates/quotes` and does **not** contain any call to `/availability/transittimes`. A single Rates API call should be present per rate request.
   - **Request/response nodes to verify:** In the Rates API response, confirm the presence of `transitTime`, `operationalDetail.commitDate`, and `operationalDetail.commitDay` fields with populated values.

7. **Cross-check transit time values shown at checkout against the Rates API response fields.**
   Compare the estimated delivery date or transit time displayed at Shopify checkout against the values returned in `transitTime` and `operationalDetail.commitDate` from the `/rates/quotes` response.

   - **Request/response nodes to verify:** `transitTime`, `operationalDetail.commitDate`, `operationalDetail.commitDay`

8. **Check for 503 errors or instability in request logs (regression check).**
   If a customer reports intermittent rate failures or missing rates on a FedEx REST store running MCSL 378+, review request logs for any 503 responses. The removal of the `/availability/transittimes` call was specifically intended to resolve load-related 503 instability. If 503s are still present, confirm which endpoint is returning them and escalate with log evidence.

9. **Run a regression check on existing FedEx REST stores.**
   For any store that was previously working on FedEx REST before MCSL 378, confirm rates are still returning without error after the update. No configuration change is required on the merchant side.

---

### Expected Behaviour

| What support should observe | How to confirm |
|---|---|
| FedEx REST rates appear at Shopify checkout for all tested services | Place a test order or draft order and confirm rate options are listed |
| Estimated delivery date / transit time is shown for FedEx Ground, 2Day, Priority Overnight, and International Priority | Verify each service displays a delivery estimate at checkout |
| Transit time values match the Rates API response fields | Compare checkout display against `transitTime` and `operationalDetail.commitDate` in the `/rates/quotes` response log |
| Request logs show only one API call per rate request — the `/rates/quotes` call | Open request logs and confirm absence of any `/availability/transittimes` call |
| No `/availability/transittimes` endpoint call appears in logs | Explicitly search log entries for this endpoint path — it must not be present |
| `transitTime`, `operationalDetail.commitDate`, `operationalDetail.commitDay` are populated in the Rates API response | Inspect the raw `/rates/quotes` response in request logs for these fields |
| No 503 errors or intermittent rate failures under normal load | Review request logs for 503 responses; none expected after this change |
| No merchant-side configuration change required | Confirm with merchant that no FedEx REST settings were altered — change is backend only |

---

### Support Escalation Packet

- **Story card:** Remove Rates and Transit API from FedEx REST — MCSL 378 (approved 2026-05-12); Trello URL: not available on card
- **Store URL and account UUID:** Provide the affected store URL and MCSL account UUID from the live ticket
- **Carrier account:** FedEx REST carrier account name/ID as shown in hamburger menu > Carriers
- **Order number:** Include the Shopify order number or draft order used to trigger the rate request
- **Generated label / tracking / report identifier:** Include any label ID or tracking number if a label was generated during testing; include rate request log ID or timestamp if available
- **Screenshots required:**
  - hamburger menu > Carriers showing FedEx REST enabled and credentials saved
  - Shopify checkout showing FedEx rate options and transit time / delivery estimate
  - Request log entry confirming `/rates/quotes` call is present
  - Request log confirming **no** `/availability/transittimes` call is present
  - Raw Rates API response showing `transitTime`, `operationalDetail.commitDate`, and `operationalDetail.commitDay` fields populated
- **Exact toggle / config value:** No feature toggle — change is applied to all FedEx REST stores on MCSL 378+; confirm release version at time of escalation

## ZI-031 - From SL: ZI-031 — PostNord service updates for May 2026 [#373200]
## Support Guide: ZI-031 — PostNord Service Updates for May 2026

*From SL: ZI-031 — PostNord service updates for May 2026 [#373200]*

---

### Feature Summary

MCSL 378 updates the PostNord service-code mapping table to align with PostNord's May 2026 API catalogue. Specific changes include: P19 (MyPack Collect) renamed, P82 updated, and a new Economy delivery code added. Deprecated codes have been removed or remapped so they no longer appear as selectable options. This affects the PostNord service dropdown in the MCSL carrier configuration, checkout rate display, and label generation for both domestic and cross-border Nordic shipments. The change was triggered by SL ticket #373200, where a customer reported outdated services appearing in the PostNord dropdown.

---

### Toggles & Prerequisites

| Toggle / config note | What support should confirm |
|---|---|
| No feature toggles detected | Change is applied globally for all stores using PostNord in MCSL 378+ |
| MCSL release version | Confirm store is on MCSL 378 or later; earlier releases will not have the updated codes |
| PostNord carrier account connected | Confirm a valid PostNord carrier account is linked under hamburger menu > Carriers |
| PostNord API credentials active | Confirm credentials are not expired and the carrier account is in live/production mode |
| Existing PostNord service configurations | Confirm whether the store had deprecated codes previously selected — these may need to be remapped manually after upgrade |
| Customer/test platform | Shopify (SL ticket #373200); validate on Shopify Admin and MCSL app accordingly |

---

### Step-by-Step Support Walkthrough

1. **Confirm MCSL release version**
   Verify the store is running MCSL 378 or later. If the store is on an earlier release, the updated PostNord service codes will not be present. Escalate for release upgrade if needed.

2. **Open PostNord carrier settings**
   In the MCSL app, navigate to **hamburger menu > Carriers**. Locate the PostNord carrier entry and open its configuration.

3. **Verify the service dropdown reflects May 2026 codes**
   Within the PostNord carrier configuration, open the service selection dropdown. Confirm:
   - P19 appears with its updated name (MyPack Collect renamed per May 2026 catalogue)
   - P82 appears with its updated definition
   - The new Economy delivery code is present and selectable
   - No deprecated codes are listed as selectable options
   - `- Request/log fields to verify:` PostNord service code values sent in the carrier API request — confirm updated code identifiers (P19 updated label, P82, new Economy code) appear in the `serviceCode` or equivalent node in the outbound request log.

4. **Check that deprecated codes are no longer selectable**
   In the same service dropdown, scroll through all available PostNord services. Deprecated codes should not appear. If a deprecated code is still visible, this indicates the mapping table update has not applied — confirm release version and escalate if confirmed on MCSL 378.

5. **Test domestic PostNord label generation (TC2)**
   Navigate to the **ORDERS** tab in MCSL. Select or create a test order shipping within the domestic PostNord service area. Assign an updated PostNord service code (e.g., updated P19 or new Economy code) and attempt label generation.
   - `- Request/response nodes to verify:` Outbound request should carry the updated service code; response should return a valid label URL or tracking number with no error code. Check request logs for the `serviceCode` node and confirm the response contains a `labelUrl` or `trackingNumber` field without error.

6. **Test cross-border Nordic shipment (TC4)**
   In the **ORDERS** tab, select or create a test order with a Nordic cross-border destination. Assign a valid PostNord cross-border service code and verify:
   - Rates display correctly at checkout (Shopify Admin > checkout preview or live checkout)
   - Label generation succeeds
   - `- Request/response nodes to verify:` Confirm the outbound request carries the correct cross-border service code and that the PostNord API response returns a valid rate and label without rejection errors.

7. **Regression check for existing PostNord configurations (TC5)**
   Identify any orders or shipment profiles that were using PostNord services prior to the MCSL 378 upgrade. Confirm:
   - Previously working service codes that are still valid continue to generate labels without error
   - Rate display at Shopify checkout is unaffected for retained services
   - If a previously selected code was deprecated, MCSL should either block selection or surface a clear error — confirm from live store behaviour and escalate if silent failures occur.

8. **Verify checkout rate display on Shopify**
   In **Shopify Admin**, navigate to a test order or use a live checkout session. Confirm PostNord rates surface correctly for services using the updated codes. If rates are missing or showing incorrect service names, cross-reference the service code in the MCSL carrier configuration against the May 2026 catalogue.

---

### Expected Behaviour

| What support should observe | How to confirm |
|---|---|
| Updated PostNord service codes (P19 renamed, P82 updated, new Economy code) appear in the MCSL service dropdown | hamburger menu > Carriers > PostNord configuration > service dropdown |
| Deprecated PostNord codes are absent from the service dropdown | Scroll full dropdown list; no legacy/deprecated entries should be present |
| Label generation succeeds for updated domestic PostNord service codes | Generate label from ORDERS tab; confirm label URL or tracking number returned in response log |
| Label generation succeeds for cross-border Nordic PostNord services | Generate label for Nordic destination order; confirm successful response with no API rejection |
| PostNord rates display correctly at Shopify checkout for updated service codes | Live or test Shopify checkout; rates appear with correct service names and prices |
| No regression in existing valid PostNord service configurations | Previously working codes continue to generate labels and display rates without error |
| `serviceCode` node in outbound PostNord API request carries updated May 2026 code values | Request log review — confirm updated code strings, not deprecated values, are transmitted |
| PostNord API response returns no error for updated codes | Response log — confirm absence of service-code rejection errors; label/tracking data present |

---

### Support Escalation Packet

- **Story card:** ZI-031 — PostNord Service Updates for May 2026 | **Trello URL:** Not provided — confirm from internal Trello board
- **SL ticket reference:** #373200 (customer-reported outdated PostNord service dropdown)
- **Store URL:** Confirm from live store/card context
- **Account UUID:** Confirm from live store/card context
- **Carrier account:** PostNord — confirm account ID and whether live/production credentials are active
- **Order number(s) used for testing:** Confirm from QA or live store test session
- **Generated label / tracking identifier:** Capture label URL or tracking number from successful TC2 and TC4 label generation attempts
- **Screenshots required:**
  - PostNord service dropdown showing updated codes (P19 renamed, P82, new Economy code visible; deprecated codes absent)
  - MCSL hamburger menu > Carriers > PostNord configuration page
  - Request log showing updated `serviceCode` node values in outbound PostNord API call
  - Response log confirming successful label/tracking return for updated codes
  - Shopify checkout screenshot showing PostNord rates for updated services
- **Toggle / config value:** No feature toggle — confirm store is on MCSL 378; if deprecated code behaviour is unexpected, capture the exact code value displayed and include in escalation

## ZI-056 - From SL: ZI-056 — PostNord return label product codes [#379784]
## Support Guide: ZI-056 — PostNord Return Label Product Codes

*From SL: ZI-056 — PostNord return label product codes [#379784]*

---

### Feature Summary

Prior to MCSL 378, PostNord return label requests were being sent with the outbound product code, causing PostNord's API to reject the request with a product-code validation error. This release adds a dedicated return product code mapping for all PostNord services that support return labels, so the correct return-specific `productCode` is now submitted in the API request. The fix resolves merchant-reported label generation failures on return shipments while leaving outbound PostNord label generation unchanged. Affected carrier: **PostNord**. Affected platform: **Shopify**.

---

### Toggles & Prerequisites

| Toggle / config note | What support should confirm |
|---|---|
| No feature toggle detected | Change is applied automatically for all PostNord return label requests on MCSL 378+ |
| MCSL release prerequisite | Confirm store is running MCSL 378 or later |
| PostNord carrier account | Confirm a valid PostNord carrier account is connected under hamburger menu > Carriers |
| PostNord service must support returns | Confirm the selected PostNord service has a mapped return product code; not all PostNord services support return labels — confirm from live store/card context which services are in scope |
| Shopify store | Validate on the merchant's Shopify store; this card was reported and tested on Shopify |

---

### Step-by-Step Support Walkthrough

1. **Confirm the MCSL app version on the merchant's Shopify store.**
   Navigate to the PluginHive MCSL app in the merchant's Shopify Admin. Verify the installed version is MCSL 378 or later before proceeding.

2. **Confirm PostNord is connected and configured.**
   In MCSL, go to **hamburger menu > Carriers**. Confirm PostNord is listed, credentials are active, and at least one PostNord service that supports return labels is enabled.

3. **Locate or create a test return shipment.**
   In MCSL, go to the **ORDERS** tab. Identify an order for which a PostNord return label needs to be generated, or use a test order on the merchant's Shopify store. Confirm the order is associated with a PostNord service that supports returns.

4. **Trigger PostNord return label generation.**
   From the **ORDERS** tab, select the relevant order and initiate return label generation using the PostNord service. Do not use the outbound label flow — confirm the return label action is selected explicitly.

5. **Verify the API request payload for the correct return product code.**
   After triggering the return label, pull the request log for that order from MCSL's request/response logs.
   - `- Request node to verify: productCode field in the PostNord return label API request must contain the return-specific product code, not the outbound product code for that service.`

6. **Confirm the return label is generated without a product-code validation error.**
   Check that the PostNord API response returns a success status and that no "invalid product code" or equivalent rejection error appears in the response log.
   - `- Request/response nodes to verify: PostNord API response status and any error/rejection message nodes — confirm absence of product-code validation errors.`

7. **Download and inspect the return label PDF.**
   From the **ORDERS** tab, download the generated return label PDF. Confirm it opens correctly, displays the expected PostNord service reference, and is visually consistent with a return label (not an outbound label).

8. **Verify outbound PostNord label generation is unaffected.**
   On a separate order, generate a standard outbound PostNord label using the same or a different PostNord service. Pull the request log and confirm the outbound `productCode` is unchanged and the label generates successfully.
   - `- Request node to verify: productCode field in the outbound PostNord label API request must still reflect the correct outbound product code — no regression introduced.`

---

### Expected Behaviour

| What support should observe | How to confirm |
|---|---|
| PostNord return label API request contains the return-specific `productCode` | Inspect request log for the return label order; `productCode` must be the return-mapped code, not the outbound code |
| No product-code validation error returned by PostNord API | Check response log for the return label request — no rejection or invalid-product-code error should be present |
| Return label PDF downloads successfully | Download label from ORDERS tab; PDF opens and displays correct PostNord service reference |
| Outbound PostNord label generation is unaffected | Generate an outbound label; confirm `productCode` in request log is the correct outbound code and label generates without error |

---

### Support Escalation Packet

- **Story card:** ZI-056 — PostNord return label product codes | **Trello URL:** Not provided — confirm from internal card tracker
- **Store URL:** Collect from merchant or SL ticket #379784
- **Account UUID:** Collect from MCSL account record
- **Carrier account:** PostNord account credentials/ID connected under hamburger menu > Carriers
- **Order number:** Order used to trigger the failing or test return label
- **Generated label/tracking identifier:** Return label reference or tracking number from the PostNord API response
- **Screenshots required:**
  - PostNord carrier configuration screen (hamburger menu > Carriers)
  - ORDERS tab showing the return label generation action
  - Request log showing the `productCode` field value in the PostNord return label API request
  - Response log confirming success or showing the rejection error (for failure cases)
  - Downloaded return label PDF showing PostNord service reference
- **Exact config value if gated:** No toggle detected — escalate with MCSL version number confirmed from the merchant's Shopify store

## From SL: MCSL 378 Missing Importer of Record in Fedex Rest - From SL: MCSL 378 Missing Importer of Record in Fedex Rest
## Support Guide: MCSL 378 — Missing Importer of Record in FedEx REST

*From SL: MCSL 378 Missing Importer of Record in FedEx REST*

---

### Feature Summary

Prior to this fix, the FedEx REST shipment creation request was missing the `importerOfRecord` block even when Importer of Record (IOR) details were configured in MCSL. This caused incomplete payloads for international FedEx REST shipments and could result in label generation failures or non-compliant customs data. The fix ensures that when IOR is configured, the full `importerOfRecord` party block — including name, address, contact, and account number — is correctly injected into the `/ship/v1/shipments` payload. FedEx REST shipments without IOR configured are unaffected. This applies to FedEx international services (e.g., International Priority, International Economy) on Shopify stores using MCSL.

---

### Toggles & Prerequisites

| Toggle / config note | What support should confirm |
|---|---|
| No feature toggles detected | No gating required; fix is applied at the carrier request-build layer |
| IOR details must be configured in MCSL | Confirm IOR fields are populated in the FedEx REST carrier settings before testing |
| FedEx REST carrier account required | Confirm the store is using FedEx REST (not FedEx SOAP/legacy) — check hamburger menu > Carriers |
| International shipment required | IOR block only applies to international FedEx REST shipments; domestic shipments are unaffected |
| Shopify store (test/live platform) | Validate on Shopify Admin — confirm orders are routed through MCSL for label generation |
| Release: MCSL 378, approved 2026-05-12 | Confirm the store is on MCSL 378 or later before troubleshooting |

---

### Step-by-Step Support Walkthrough

1. **Confirm the store is on MCSL 378 or later.**
   Check the installed MCSL version in the Shopify app or backend. If the store is on an earlier release, escalate for an update before proceeding.

2. **Confirm FedEx REST is the active carrier integration.**
   Navigate to **hamburger menu > Carriers** in MCSL. Verify the FedEx carrier entry is configured as FedEx REST (not a legacy/SOAP connection). If the carrier type is unclear, confirm from the card/live store context.

3. **Confirm IOR details are configured in the FedEx REST carrier settings.**
   In **hamburger menu > Carriers**, open the FedEx REST carrier configuration. Verify that the Importer of Record section is populated with:
   - Name
   - Address (street lines, city, state/province code, postal code, country code)
   - Contact (person name, phone number)
   - Account number

   If any of these fields are blank, the `importerOfRecord` block will not be sent — this is expected behaviour, not a bug.

4. **Create or locate an international FedEx REST order in Shopify Admin.**
   Go to **Shopify Admin > Orders** and identify an order shipping to an international destination. Confirm the order is being processed through MCSL for label generation (not a third-party fulfillment flow).

5. **Generate a FedEx REST international label from the MCSL ORDERS tab.**
   Navigate to the **ORDERS** tab in MCSL, locate the international order, and trigger label generation. Note the order number and any label/tracking identifier returned.

6. **Verify the `importerOfRecord` block in the request log.**
   After label generation, navigate to the request/response logs in MCSL (confirm exact log path from live store context). Locate the `/ship/v1/shipments` request for the order.

   - **Request node to verify:** `requestedShipment.importerOfRecord` — must contain `name`, `contact` (with `personName` and `phoneNumber`), `address` (with `streetLines`, `city`, `stateOrProvinceCode`, `postalCode`, `countryCode`), and `accountNumber`.

7. **Confirm label generation succeeds.**
   Verify that a valid FedEx label and tracking number are returned in the MCSL ORDERS tab and in Shopify Admin > Orders for the fulfilled shipment.

8. **Regression check — FedEx REST shipments without IOR configured.**
   On a store or test order where IOR is **not** configured, generate a FedEx REST international label and review the request log. Confirm that the `requestedShipment.importerOfRecord` block is **absent** from the payload and that label generation completes without error.

9. **Validate across FedEx international service types.**
   Repeat steps 4–6 for both **FedEx International Priority** and **FedEx International Economy** service selections. Both should include the `importerOfRecord` block when IOR is configured.

---

### Expected Behaviour

| What support should observe | How to confirm |
|---|---|
| `importerOfRecord` block present in `/ship/v1/shipments` payload when IOR is configured | Check request log — `requestedShipment.importerOfRecord` node must be present with all required sub-fields |
| `importerOfRecord.name` populated correctly | Verify value matches the IOR name entered in hamburger menu > Carriers > FedEx REST settings |
| `importerOfRecord.address` contains `streetLines`, `city`, `stateOrProvinceCode`, `postalCode`, `countryCode` | Inspect address sub-object in `requestedShipment.importerOfRecord` in the request log |
| `importerOfRecord.contact` contains `personName` and `phoneNumber` | Inspect contact sub-object in `requestedShipment.importerOfRecord` in the request log |
| `importerOfRecord.accountNumber` populated | Verify account number value is present in the request log node |
| FedEx REST international label generates successfully with IOR configured | Valid label and tracking number returned in MCSL ORDERS tab and Shopify Admin > Orders |
| `importerOfRecord` block absent when IOR is not configured | Request log for non-IOR shipments must not contain `requestedShipment.importerOfRecord` |
| FedEx International Priority includes IOR block when configured | Verify via request log for an International Priority shipment |
| FedEx International Economy includes IOR block when configured | Verify via request log for an International Economy shipment |
| Domestic FedEx REST shipments unaffected | Confirm domestic label generation succeeds and no `importerOfRecord` block appears in domestic request logs |

---

### Support Escalation Packet

- **Story card:** MCSL 378 — *From SL: MCSL 378 Missing Importer of Record in FedEx REST*
- **Card URL:** Not provided — confirm from internal Trello/project board
- **Store URL:** Confirm from live store or ticket context
- **Account UUID:** Confirm from live store or ticket context
- **Carrier account:** FedEx REST — confirm carrier account ID from hamburger menu > Carriers
- **Order number:** Provide the Shopify order number used for label generation during verification
- **Generated label / tracking identifier:** Provide the FedEx tracking number returned after label generation
- **Screenshots required:**
  - IOR configuration screen in hamburger menu > Carriers > FedEx REST settings (showing all IOR fields populated)
  - Request log showing the full `requestedShipment.importerOfRecord` block for the international shipment
  - Request log for a non-IOR shipment confirming the block is absent (regression evidence)
  - MCSL ORDERS tab showing successful label generation with tracking number
- **Toggle / config value:** No feature toggle — confirm IOR fields are populated in FedEx REST carrier settings as the sole prerequisite
- **MCSL version:** Confirm store is on MCSL 378 or later before escalating

## Label generation fails for One Rate with custom box - Label generation fails for One Rate with custom box
## Support Guide: MCSL 378 — Label Generation Fails for One Rate with Custom Box

*Label generation fails for One Rate with custom box*

---

### Feature Summary

Prior to MCSL 378, selecting a FedEx One Rate service alongside a custom box in MCSL would silently fail with a `PACKAGING.MISMATCH` error from FedEx — no merchant-facing message was shown, and the label request was sent with `packagingType: CUSTOM`, which FedEx rejects for all One Rate services. This release adds pre-send packaging validation: when a One Rate service is selected, MCSL now checks the packaging type before dispatching the label request and either surfaces a clear error prompting the merchant to select FedEx-branded packaging, or auto-selects a compatible One Rate packaging type. Non-One Rate FedEx services using custom boxes are unaffected. This change is specific to **FedEx** on **Shopify** and applies to all `ONE_RATE_*` service enumerations.

---

### Toggles & Prerequisites

| Toggle / config note | What support should confirm |
|---|---|
| No feature toggles detected | No gating — change is active for all eligible stores on MCSL 378 |
| Release prerequisite | Store must be on MCSL 378 or later; confirm app version in store dashboard |
| FedEx carrier account connected | Confirm FedEx account is active under hamburger menu > Carriers |
| FedEx One Rate service enabled | Confirm at least one `ONE_RATE_*` service is enabled in the FedEx carrier settings |
| Custom box configured in MCSL | Confirm a custom/non-FedEx box exists under hamburger menu > Products (or Packaging settings) |
| Shopify store | Validation confirmed on Shopify; confirm platform if ticket originates from a different platform |
| FedEx REST API in use | `packagingType` node is specific to the FedEx REST request; confirm REST integration is active, not legacy SOAP |

---

### Step-by-Step Support Walkthrough

1. **Confirm the store is on MCSL 378 or later.**
   Check the installed app version in the Shopify Admin app listing or MCSL internal dashboard before proceeding.

2. **Confirm the FedEx carrier account is connected and active.**
   Navigate to **hamburger menu > Carriers** in MCSL. Verify the FedEx account is listed, credentials are valid, and the account is not in an error state.

3. **Confirm a One Rate service is enabled.**
   Still in **hamburger menu > Carriers**, open the FedEx carrier configuration. Verify that at least one service with a `ONE_RATE_*` designation (e.g., FedEx One Rate Express Saver, FedEx One Rate Priority Overnight) is toggled on.

4. **Confirm a custom box is configured.**
   Navigate to **hamburger menu > Products** (or the Packaging/Box configuration area in MCSL). Verify that a custom/merchant-defined box exists and is assigned or selectable for shipments.

5. **Reproduce the mismatch scenario on the Shopify store.**
   Go to the **ORDERS** tab in MCSL. Open or create a test order. Attempt to generate a FedEx label by selecting a One Rate service with the custom box as the packaging source.
   - **Expected (post-378):** A clear merchant-facing error is displayed — *"One Rate requires FedEx-branded packaging. Please select a FedEx One Rate box."* — and the label request is **not** dispatched to FedEx.
   - **Pre-378 symptom to rule out:** Silent failure with no UI message, or a raw `PACKAGING.MISMATCH` error surfaced from FedEx.

6. **Reproduce the success scenario with FedEx-branded packaging.**
   On the same order, switch the packaging to a FedEx One Rate box (e.g., FedEx Small Box, FedEx Envelope). Attempt label generation again.
   - **Expected:** Label generates successfully and a tracking number is returned.

7. **Verify the outbound FedEx REST label request payload.**
   Open **Request Logs** (or the diagnostic log viewer in MCSL) and locate the label request for the successful One Rate attempt.
   - **Request node to verify:** `packagingType` must be one of: `FEDEX_ENVELOPE`, `FEDEX_PAK`, `FEDEX_SMALL_BOX`, `FEDEX_MEDIUM_BOX`, `FEDEX_LARGE_BOX`, `FEDEX_EXTRA_LARGE_BOX`, or `FEDEX_TUBE`. The value `CUSTOM` must **not** appear in any One Rate label request.

8. **Verify non-One Rate FedEx services are unaffected (regression check).**
   On a separate test order, select a standard FedEx service (e.g., FedEx Ground, FedEx 2Day) with the custom box. Attempt label generation.
   - **Expected:** Label generates successfully. No error about packaging type is shown. Custom box is accepted as normal.
   - **Request node to verify:** `packagingType` value is `YOUR_PACKAGING` or the appropriate custom packaging enum — **not** a One Rate packaging enum — confirming no cross-contamination from the new validation logic.

9. **Check for any residual silent failures.**
   In **Request Logs**, search for any recent FedEx label requests returning `PACKAGING.MISMATCH`. If found on a store running MCSL 378, this is an escalation signal — the pre-send validation may not have fired correctly.
   - **Request/log fields to verify:** FedEx error code `PACKAGING.MISMATCH` should be absent from all post-378 One Rate attempts where the merchant was shown the UI error (i.e., the request should not have been sent at all).

---

### Expected Behaviour

| What support should observe | How to confirm |
|---|---|
| Clear UI error shown when custom box + One Rate service is selected | Error message reads: *"One Rate requires FedEx-branded packaging. Please select a FedEx One Rate box."* — visible in the label generation flow on the Shopify ORDERS tab |
| No label request dispatched to FedEx when packaging mismatch is detected | Request Logs show no outbound FedEx REST call for the rejected attempt; no `PACKAGING.MISMATCH` response from FedEx |
| `packagingType` in FedEx REST request is a valid One Rate enum | Request log for successful One Rate label shows `packagingType` as one of: `FEDEX_ENVELOPE`, `FEDEX_PAK`, `FEDEX_SMALL_BOX`, `FEDEX_MEDIUM_BOX`, `FEDEX_LARGE_BOX`, `FEDEX_EXTRA_LARGE_BOX`, or `FEDEX_TUBE` |
| `packagingType` is never `CUSTOM` in a One Rate label request | Confirm in Request Logs — `CUSTOM` value must not appear alongside any `ONE_RATE_*` service selection |
| Label generates successfully when FedEx-branded packaging is selected with One Rate | Tracking number returned, label available for download in the ORDERS tab |
| Non-One Rate FedEx services with custom boxes continue to work without error | Standard FedEx service + custom box produces a successful label; no packaging validation error triggered |
| No regression on non-One Rate FedEx label flows | Request Logs for standard FedEx services show `YOUR_PACKAGING` or equivalent custom packaging enum — no One Rate packaging enum injected |

---

### Support Escalation Packet

- **Story card:** Label generation fails for One Rate with custom box — MCSL 378 (approved 2026-05-12); Trello URL: not available — confirm from card owner or release manager
- **Store URL and account UUID:** Collect from the merchant's Shopify Admin or MCSL account record
- **Carrier account:** FedEx account ID/credentials as shown under hamburger menu > Carriers — confirm account is active and One Rate-eligible
- **Order number:** The specific Shopify order number used during the failed or successful label attempt
- **Generated label / tracking identifier:** Tracking number returned on successful One Rate label generation, or note "no label generated" for the mismatch error scenario
- **Screenshots required:**
  - MCSL label generation screen showing the UI error message (custom box + One Rate selection)
  - MCSL label generation screen showing successful label with FedEx-branded packaging selected
  - hamburger menu > Carriers — FedEx configuration with One Rate service enabled
  - hamburger menu > Products / Packaging — custom box configuration
  - Request Log entry showing `packagingType` value for both the blocked attempt (no request sent) and the successful attempt
- **Exact config values to capture:**
  - One Rate service name/enum selected at time of failure (e.g., `ONE_RATE_PRIORITY_OVERNIGHT`)
  - `packagingType` value in the successful label request payload
  - MCSL app version — must be 378 or later; if earlier, escalate as a version deployment issue