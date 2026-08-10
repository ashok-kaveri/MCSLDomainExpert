# WooCommerce FedEx Shipping Plugin with Print Label 8.7.1 — Support Guide

Platform: WooCommerce (WordPress). Carrier: FedEx. Version: **8.7.1**.

Everything in this guide is available from version **8.7.1**. If a merchant does not see the behaviour described here, confirm their plugin version first.

## Included Story Cards

| Story ID | Story Title | Trello card link |
|---|---|---|
| 948 | [Compatibility] PHP v8.4 – Full Regression Pass | https://trello.com/c/oYTnXDar |
| 959 | [Bug Fix] SHIPMENTVALIDATION.EEIEDIT.ERROR for PR/VI-origin international shipments | https://trello.com/c/g2tOgfKu |
| 955 | [New Feature] Add FedEx Extra Small Box (opt-in) to Box Packing + One Rate | https://trello.com/c/QvGU268C |
| 954 | [Bug Fix] FedEx Shipment Tracking box layout broken after WooCommerce update | https://trello.com/c/A0vxMo05 |
| 953 | [Bug Fix] PHP warnings + broken redirects when Hold at Location enabled without completed FedEx registration | https://trello.com/c/OyRl75yc |

## 948 - [Compatibility] PHP v8.4 – Full Regression Pass

### Brief Description

The plugin is now verified end-to-end on **PHP 8.4**. A full regression round was run across every core service area, so merchants on PHP 8.4 can be told the version is supported. No code change is tied to this card — it is a compatibility confirmation.

### Prerequisites

- Site running PHP 8.4.
- A working FedEx account connected in plugin settings.
- No setting to enable — this is confirmation of existing behaviour on a newer PHP version.

### Step-by-Step Support Walkthrough

Use this list when a merchant asks whether PHP 8.4 is safe, or when reproducing an issue reported on PHP 8.4. Each area was covered in the release pass:

1. **Rate** — rates calculate and display at cart and checkout.
2. **Label** — domestic and international label generation.
3. **Tracking** — live tracking and the tracking metabox on the order page.
4. **Pickup** — pickup request scheduling.
5. **Void** — voiding a shipment or label.
6. **Return** — return label generation.
7. **Freight** — LTL freight shipments.
8. **Packaging** — box packing, per-item, pre-packed, and weight-based all cost correctly.
9. **End of day** — package handover / manifest for FedEx Ground.
10. **Documents** — uploading extra documents such as invoices, plus custom label images and signatures.
11. **Account** — new FedEx sign-up and login.
12. **Bulk actions** — creating and cancelling labels for multiple orders at once.
13. **Third-party compatibility** — new checkout page (block checkout), currency switchers, product bundles, mixed & match products, multiple shipping addresses, and PayPal.

If a merchant reports a problem on PHP 8.4, confirm the plugin version is 8.7.1 or later before treating it as a PHP-version issue.

### Expected Behaviour

On PHP 8.4 every service area behaves exactly as on earlier supported PHP versions — no fatal errors, no deprecation notices, and no behavioural change.

## 959 - [Bug Fix] SHIPMENTVALIDATION.EEIEDIT.ERROR for PR/VI-origin international shipments

### Brief Description

Stores shipping from **Puerto Rico** or the **US Virgin Islands** could not create international labels to Hong Kong, China, Belgium, Saudi Arabia, France, Ireland, or Australia. FedEx rejected the shipment with an export-compliance error about the FTR Exemption / AES Citation, and the plugin gave the merchant no field to enter that information.

PR and VI origins are now handled the same way as US origins for this export-compliance requirement, matching FedEx's own rules. The required compliance information is sent automatically. Nothing changes for any other origin country.

### Prerequisites

- No setting to enable — the fix applies automatically on 8.7.1.
- To reproduce: store FedEx origin address set to Puerto Rico or the US Virgin Islands, and an international order to one of the affected destinations.

### Step-by-Step Support Walkthrough

**Scenario A — Puerto Rico origin now works**

1. Confirm the store's FedEx origin address is set to Puerto Rico.
2. Open an international order to Hong Kong (or China, Belgium, Saudi Arabia, France, Ireland, Australia).
3. Generate the FedEx label.
4. Confirm the label is created with no *"FTR Exemption or AES Citation… not valid for EEI"* error and no other export-compliance error.
   - `Request node to verify: the export/customs-clearance detail in the FedEx label request — confirm the FTR exemption / AES citation value is present for the PR-origin shipment, exactly as it is for a US-origin shipment.`

**Scenario B — US Virgin Islands origin**

5. Repeat step 2-4 with the origin set to the US Virgin Islands. Confirm the same successful result.

**Scenario C — US origin unchanged**

6. With a US origin, generate the same international label.
7. Confirm behaviour is identical to before the fix.

**Scenario D — Other origins unchanged**

8. With an origin such as Germany, UK, or Canada, generate an international label.
9. Confirm nothing changed for that store.

**Scenario E — Domestic PR/VI shipments unchanged**

10. From a PR or VI origin, ship domestically (for example Puerto Rico to the US mainland) or to a destination outside the affected list.
11. Confirm nothing changed.

### Expected Behaviour

PR-origin and VI-origin stores create international labels to the affected destinations successfully, with no export-compliance error and no extra field for the merchant to fill in. Every other origin behaves exactly as before.

## 955 - [New Feature] Add FedEx Extra Small Box (opt-in) to Box Packing + One Rate

### Brief Description

FedEx added a new box to its official lineup and to the One Rate flat-rate programme: the **FedEx Extra Small Box**. It is now available in the plugin's Box Packing settings with FedEx's published size — **7 1/4" x 2 1/2" x 4 11/16"** — and a content capacity of **5 lbs / 2.27 kg**. It also qualifies for FedEx One Rate flat pricing, like the other standard boxes.

Because it is a brand-new box that merchants have never approved, it ships **turned OFF**. Existing merchants and their existing box setups are untouched until someone enables it.

### Prerequisites

- Parcel Packing Method must be set to **Box Packing**.
- **FedEx Extra Small Box > Enable** checkbox in the **Packaging** tab — unchecked by default.
- For One Rate testing: FedEx One Rate enabled, a single domestic US package, and items that fit the box size and weight.

### Step-by-Step Support Walkthrough

**Scenario A — Box is visible but off by default**

1. In WordPress Admin, go to **FedEx Shipping settings > Packaging**, with Parcel Packing Method set to **Box Packing**.
2. Find **FedEx Extra Small Box** in the Box Sizes table.
3. Confirm its dimensions read 7 1/4" x 2 1/2" x 4 11/16" and its weight capacity 5 lbs (2.27 kg).
4. Confirm the **Enable** checkbox is **unchecked**, for both new and existing merchants.

**Scenario B — Merchant opts in**

5. Tick the **Enable** checkbox and click **Save**.
6. Place an order with a small, light item that fits the box.
7. Check rates at cart/checkout and confirm the item can be packed into the Extra Small Box.
8. Generate the label and confirm the shipment is created using that box.

**Scenario C — FedEx One Rate**

9. Enable FedEx One Rate along with the Extra Small Box.
10. Place a single-package domestic US order whose items fit the box.
11. Confirm the order qualifies for One Rate flat pricing using the Extra Small Box, the same as Small/Medium/Large/Extra Large/Pak/Envelope.

**Scenario D — Existing merchants unaffected**

12. On a store that never enables the new box, check rates at checkout and create a label as usual.
13. Confirm existing enabled boxes behave exactly as before and the Extra Small Box is never used.

### Expected Behaviour

The Extra Small Box appears in Box Packing settings with the correct size and weight, stays off until a merchant explicitly enables and saves it, and then participates normally in packing, rating, labels, and One Rate pricing. No other box changes behaviour.

## 954 - [Bug Fix] FedEx Shipment Tracking box layout broken after WooCommerce update

### Brief Description

After a recent WooCommerce update, the **FedEx Shipment Tracking** box on the order edit screen looked broken — the service dropdown, tracking-IDs field, and shipment-date field were squeezed into a narrow sliver with labels wrapping beside them.

The FedEx box was sharing an internal identifier with WooCommerce's own **Order actions** box, so WooCommerce's restyling was being applied to it too. The FedEx box now has its own identifier and displays normally again. Only the layout changed — saving tracking information works exactly as before.

### Prerequisites

- No setting to enable.
- Reproduce on the order edit screen in wp-admin, on either the classic Orders screen or the HPOS Orders screen.

### Step-by-Step Support Walkthrough

**Scenario A — Layout is correct**

1. Open any order's edit page in wp-admin.
2. Scroll to the **FedEx Shipment Tracking** box in the sidebar.
3. Confirm the service dropdown, **Enter Tracking IDs** field, and **Shipment Date** field each sit on their own full-width row, with a readable label above each — nothing squeezed, wrapped, or overlapping.

**Scenario B — Saving still works**

4. Select **FedEx** from the dropdown.
5. Enter a tracking number (for example 794843953245) in **Enter Tracking IDs**, and optionally pick a Shipment Date.
6. Click **Save/Show Tracking Info**.
7. Confirm the tracking number saves to the order and the tracking information displays as before.

**Scenario C — WooCommerce's own box unaffected**

8. On the same page, look at WooCommerce's **Order actions** box.
9. Confirm its status dropdown and **Update** button still sit side by side, exactly as WooCommerce intends.

**Scenario D — Classic and HPOS screens**

10. Repeat Scenario A on both the classic Orders screen and the HPOS Orders screen.
11. Confirm the box displays and works identically on both.

### Expected Behaviour

The FedEx Shipment Tracking box renders with one field per row on both order screens, tracking saves as it always did, and WooCommerce's Order actions box is untouched.

## 953 - [Bug Fix] PHP warnings + broken redirects when Hold at Location enabled without completed FedEx registration

### Brief Description

If a merchant turned **Hold at Location** on before finishing FedEx registration — or after registration details were lost, for example during a site clone or migration — every page load produced a batch of PHP warnings. On hosts that print warnings on the page, this escalated into a *"headers already sent"* error that broke redirects after login, after checkout, and after saving admin settings or orders.

The Hold at Location feature was reading an incomplete copy of the store's FedEx account details. It now uses the complete, defaulted version already used elsewhere, so nothing is missing and no warnings are raised — whether or not registration is finished.

### Prerequisites

- **Hold at Location** setting in FedEx shipping settings (OFF by default for every store).
- To reproduce the original issue: Hold at Location ON with FedEx registration incomplete or reset.
- Helpful for verification: WordPress debug logging enabled so warnings are written to the debug log.

### Step-by-Step Support Walkthrough

**Scenario A — Incomplete registration, Hold at Location ON**

1. On a store with FedEx registration incomplete or reset, turn **Hold at Location** ON.
2. Load the shop page, the checkout page, and wp-admin, and save an order.
3. Confirm every page loads and redirects normally — no blank page, no *"headers already sent"*, no broken redirect after login, checkout, or save.
   - `Request/log fields to verify: the site debug log (wp-content/debug.log) during these page loads — confirm no PHP warnings referencing missing FedEx account details are written.`

**Scenario B — Default setup**

4. On a store with Hold at Location OFF, load the same pages.
5. Confirm behaviour is unchanged and the log stays clean.

**Scenario C — Fully registered store (current REST connection)**

6. On a store with FedEx registration completed, turn Hold at Location ON.
7. Go to checkout and open the Hold at Location picker.
8. Confirm the same locations are shown and selection behaves exactly as before.

**Scenario D — Legacy SOAP-registered store**

9. Repeat Scenario C on a store using the older SOAP connection method with its account details intact.
10. Confirm no regression — same locations, same behaviour, no warnings.

### Expected Behaviour

No PHP warnings and no broken redirects when Hold at Location is on with incomplete registration. Stores with Hold at Location off, fully registered REST stores, and legacy SOAP stores all behave exactly as before.
