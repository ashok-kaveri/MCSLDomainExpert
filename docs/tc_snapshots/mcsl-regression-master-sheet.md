# MCSL Regression - Master Sheet Snapshot

**Source:** https://docs.google.com/spreadsheets/d/1oVtOaM2PesVR_TkuVaBKpbp_qQdmq4FQnN43Xew0FuY
**Captured:** 2026-04-15
**Purpose:** RAG ingestion source for MCSLDomainExpert Domain Expert Chat and AI QA Agent

---

## Sheet Structure (Tabs)

| Tab | Description |
|-----|-------------|
| Draft Plan | Feature/team assignment matrix |
| Sections | Coverage tracker across all test sections |
| Defects | Known defects/bugs |
| Manual Must Cover | Critical manual test areas |
| Pluginhive app Setup | App setup, carrier config, product management TCs |
| Batch Flow | Label batch creation and management TCs |
| Single Label Generation | Single label flow TCs (32+) |
| Orders Grid | Order grid + Actions menu TCs (200+) |
| Order_Update | Order sync/update TCs (24+) |
| Rate_Domestic_Packaging Type | Packaging type + rate TCs (24) |

---

## Section Coverage Tracker

The **Sections** tab tracks which test sections have been covered:

1. Pluginhive app setup
2. Single Label Generation
3. Orders Grid
4. Rate_Domestic_Packaging Type
5. Rate_International_Packaging Type
6. Label_Domestic_Packaging Type
7. Label_International_Packaging Type
8. Reports
9. General Settings
10. Views
11. SLGP Flow & Quick Ship
12. Label Automation *(yet to add test cases)*
13. Rate Automation *(yet to add test cases)*
14. Special Services *(yet to add test cases)*
15. Product/Tracking/Account page settings
16. Orders Update

> Note: "Automated test cases not included in the sheet"

---

## Draft Plan — Feature Matrix

The main regression feature areas and sub-items:

### Single Label
- Simple Product
- Digital Product
- Custom Product
- High Value products (Insurance etc.)
- Dangerous goods
- Prepackaged & Self Packing
- Multi Product
- Variable

### Order Grid
- Filters
- Saved views
- Imports
- Action menu items
- Initial / Processing / Partial FF / Order update Ring

### Auto Import

### Packaging
- 5 Types
- General Setting
- Packing Slip, Tax Invoice

### Quick Ship

### Reports | Views

### Rate Automation >>> Rules
### Label Automation >>> Rules

### Carrier Registration

### Platform Products
- Single Product edit, Bulk Upload (CSV)
- Retrieve / Date filter / Status filter

### Tracking page

---

## Manual Must Cover (Critical Manual Test Areas)

These require manual or AI QA verification — NOT automated:

| # | Test Area |
|---|-----------|
| 1 | Batch Creation |
| 2 | Create batch with Failed + Success Orders (E2E: label, packing slips, etc.) |
| 3 | Volumetric weights |
| 4 | Box Packing |
| 5 | Stacking Packing |
| 6 | Weight based packing |
| 7 | Rates |
| 8 | Automation rules sanity |
| 9 | Discounts |
| 10 | Label with long shipping address (label fits in one page) |
| 11 | Auto order update script run |
| 12 | BoGo Fix |
| 13 | Edit packages sanity |
| 14 | Touchless one print |
| 15 | Reports |
| 16 | COD cases |

---

## Single Label Generation Test Cases (32+)

**Key scenarios:**

| ID | Scenario | Status |
|----|----------|--------|
| 1 | Simple product — Initial status label generation | PASS |
| 2 | Order processing status update | PASS |
| 3 | Label creation and failure handling | PASS |
| 4 | Order fulfillment with manifest details | PASS |
| 5 | Document printing (labels, packing slips, invoices) | PASS |
| 6 | Physical + digital product handling | PASS (Pending) |
| 9 | Multiple products — single package | PASS |
| 10 | Multiple products — multiple packages | PASS |
| 16 | Label summary display post-generation | PASS |
| 19 | Rate summary details and sorting | PASS |
| 26-28 | Pre-packaged and self-packaged items | PASS |
| 30-31 | Edit package functionality | PASS |
| 32 | Cancel shipment operation | PASS |

**Features tested:**
- Order status transitions: Initial → Processing → Label Created → Fulfilled
- Multi-product packaging scenarios
- Document generation and printing (labels, packing slips, invoices)
- Rate selection and carrier switching
- Package weight/dimension editing
- Fulfillment tracking across Shopify + WooCommerce

---

## Orders Grid Test Cases (200+)

### Single Label Generation from Grid (Cases 1-29)
- Cases 1-6: Order viewing, selection, label generation workflow
- Cases 7-15: Document download and printing
- Cases 16-17: Pickup request and fulfillment marking
- Case 29: Order tracking features

### Bulk Label Generation (Cases 30-46)
- Cases 30-34: Bulk order preparation and label generation
- Cases 35-46: Bulk document handling and fulfillment

### Grid Management (Cases 47-56)
- Cases 47-49: OPEN, LABELED, FULFILLED tab viewing
- Cases 50-53: Column config, sorting, pagination, filtering
- Cases 55-56: Custom view creation, duplication, deletion

### Actions Menu (Cases 57+) — 55+ action items
- Carrier and service changes
- Address validation and modifications
- Special services: insurance, signatures, Saturday delivery
- Carrier-specific features: FedEx, DHL, Canada Post, etc.
- Document regeneration and transmission
- Payment type modifications

**Test data structure per case:**
- Story/Scenario: User action context
- Given-When-Then: BDD-style acceptance criteria
- Platform Coverage: Shopify + WooCommerce columns
- Automation Status: automated or manual
- Notes/Remarks: constraints and dependencies

---

## Batch Flow Test Cases (10 scenarios)

| # | Scenario |
|---|----------|
| 1 | SKU Sorting — print labels alphabetically by SKU, multi-SKU orders at end |
| 2 | Single Batch, Multiple Orders — create batch → generate label → print → fulfill → manifest |
| 3 | Multiple Batches, Multiple Orders — bulk batch operations |
| 4a | Batch Filter by Name — partial/full batch name search |
| 4b | Batch Filter by Date Range — date range filter |
| 5 | Batch Rename — edit icon → rename → search by new name |
| 6 | Pagination — navigate across pages, actions work across pages |
| 7 | Parallel Batch Processing — concurrency, queue progression |
| 8 | Retry Batch — retry failed orders only |
| 9 | Partially Fulfilled Orders — On Hold/Release workflow, 2 batches for same order |
| 10 | Bulk Picklist Printing (400+ orders) — opens in new tab, order/product-based |

---

## Order Update Test Cases (24+ scenarios)

### Address Updates
- Initial/Processing: Shopify address change → MCSL reflects in 30-60 seconds
- Label Created/Failed/Fulfilled: Yellow update icon → modal warning about in-progress shipment
- Expected: Generated label includes updated address

### Product Additions
- Existing physical products added in Shopify → appears in MCSL within 30-60 seconds
- Digital products: verified via "edit package" product list window
- Custom physical products: note "Test with Touchless print provider"
- Custom non-physical products: reflected in both Initial and Processing statuses

### Quantity Modifications
- Increase: reflected in MCSL; label includes updated quantity
- **Known Issue — Quantity Reduction:** "Not working as of now, existing issue"

### Tag Management
- Tested across: Fulfilled, Initial/Processing, Label Created, Label Failed, Externally Fulfilled, Partially Externally Fulfilled, Return Created
- Multiple tags from Shopify sync to MCSL grid
- Tag filter supports search (e.g., "CR_BC/1.2,ab")
- Custom views/tabs for tagged orders

### Order Cancellation
- Cancelled in Shopify → MCSL updates in 30-60 seconds to "CANCELLED"
- Visual: strikethrough text, red color

### Hold & Release Fulfillment
1. Hold product in Shopify → removed from MCSL within 30 seconds
2. Generate label/fulfill → "Label Created" then "Fulfilled"
3. Release in Shopify → update icon appears
4. Confirm → status "Partially Externally Fulfilled"
5. Generate label for released product → only new product fulfilled

### External Fulfillment
- Mark as Fulfilled in Shopify → MCSL: "Externally Fulfilled"
- Partial: "Externally Partially Fulfilled" — only unfulfilled products in MCSL

### COD ↔ Prepaid Payment Changes
- COD → Prepaid: collectible amount ₹0, prepaid label
- Prepaid → Partial COD: outstanding amount from Shopify
- **Provider limitation:** Only XpressBees, Delhivery, BlueDart, Amazon support payment mode changes

### Known Issues
1. Quantity Reduction Bug — not functioning, existing issue
2. Retry Batch Loop — infinite loop after Shopify address update for label-failed orders
3. Cancel Fulfillment — not properly functioning for partial-fulfilled orders

---

## Rate & Packaging Type Test Cases (24 scenarios)

### 5 Packaging Methods × ~5 configurations each:

#### 1. Weight-Based Packaging (Cases 1-5)
- Pounds/Inches with Volumetric ON
- Variable products, Prepacked, Kg/Cm, Grams/Cm multi-package

#### 2. Stack-Based Packaging (Cases 6-10)
- Items stacked in configured boxes with height buffering
- Carrier Box + Custom Box variants
- Multi-package stacking

#### 3. Box-Based Packaging (Cases 11-15)
- Items fit into predefined boxes
- Volumetric + Stacking combinations
- Grams/Cm and Kg/Cm carrier boxes

#### 4. Weight & Volume-Based Packaging (Cases 16-20)
- Greater of actual or volumetric weight
- Max weight splits, sophisticated dynamic packaging
- Multi-package configurations

#### 5. Quantity-Based Packaging (Cases 21-24)
- Items per box based on quantity parameter
- Variable multi-package, Prepacked, Carrier box variants

**Validation pattern:**
1. Settings → Shipping → Packaging → configure method
2. Customer checkout → verify rates appear
3. Request Log → packing method, package count, weights
4. XML validation → product weight/units, box parameters, dimensions

---

## Pluginhive App Setup Test Cases (47+)

### Store Creation (TC 1)
- Admin → Stores → Add Store → Create dev store (US country)

### Product Management (TC 2-22)
- Simple, Variable, Multi-variant, Digital products
- Weight, price, HS code, country of manufacture
- Variant creation via "+" button
- App sync after product creation

**Editable in MCSL App:** Shipping, Customs, Special Service, Dry Ice, Dangerous Goods, Alcohol

### Carrier Setup (TC 23-25)
- Path: Hamburger → Settings → Carriers → "+" Icon
- Supported: FedEx, STAMPS USPS
- "How to get" button shows animated GIF for FedEx registration
- Expected: "Registration successful message should be displayed"

### Address Management (TC 26-28)
- View/Add/Delete store addresses
- Sync matches Shopify exactly

### Product Imports (TC 29-31)
- Force Import vs Standard Import
- Syncs: Title, SKU, weight, dimensions, HS codes, country of manufacture

### App Installation (TC 32-35)
- Install → analytics + Zendesk updates triggered
- Uninstall/Reinstall workflows
- WSS (WooCommerce) Plugin Registration

### Subscription (TC 36)
- Account → Manage Subscription → Change plan
- Active plan indicator; changes reflect immediately

### Product Search & Filter (TC 37-38)
- Search by name or SKU
- Filter by: Alcohol, Dry Ice, Dangerous Goods, Shipping Required, Signature Required

### Order Import (TC 40-42)
- Auto import on install (orders > 5 days or custom date range)
- New orders auto-appear in grid
- Manual import via Import button

---

## SLGP Flow & Quick Ship Test Cases

### Quick Ship
1. **Successful label generation** — multi-order selection, modal pre-fills address/carrier/service, generates batch, marks Fulfilled
2. **Failed label** — failed orders stay unchanged, system continues processing others, Label Batch shows SUCCESS/FAILED
3. **Quick Ship with Package & Signature** — Supports: Parcel Force, DHL Sweden, Aramex, Canada Post, PostNord, TNT Express, Sendle, Australia Post
4. **Quick Ship with Presets** — presets from SLGP auto-populate modal fields

### Touchless Print
1. Barcode scan → auto-fills order search → opens order
2. Print label from Initial status — "Generate Label & Fulfill" → auto-prints → Fulfilled
3. Print from Processing status — same flow
4. Print after reviewing/editing — updated values in XML log

### Order Summary Presets/Favorites
1. Create/prioritize/delete up to 20 presets (Initial or Processing only)
2. Preset icon auto-highlights when order matches preset
3. Deselect preset via right-click
4. Preset icon resets on carrier/service change
5. Edit recipient address → rates auto-refresh → prints on label
6. Edit payment mode (COD ↔ Prepaid) → order reprocesses
7. Change carrier service → rate summary updates

---

## Key MCSL-Specific Flows (vs FedEx)

### Status Transitions
```
Initial → Processing → Label Created → Fulfilled
                    ↘ Label Failed
```

Special statuses:
- Partially Externally Fulfilled
- Externally Fulfilled
- CANCELLED (strikethrough, red)
- Return Created

### Document Types
- **Label** — main shipping label
- **Packing Slip** — order contents list
- **Tax Invoice** — billing document
- **Commercial Invoice** — international customs
- **Manifest** — end-of-day carrier manifest
- **Pick List** — warehouse pick list

### Print Options
- Print Documents → opens new tab (NOT zip download)
- Download Documents → ZIP (label PDF + packing slip + CI)
- How To → ZIP with createShipment JSON request log

### Carrier-Specific Notes
- **FedEx:** signature, dry ice, alcohol, battery, HAL, insurance
- **UPS:** signature, insurance, COD
- **USPS (STAMPS):** signature, registered mail
- **DHL:** insurance, signature, international
- **Canada Post:** package + signature required
- **Australia Post, Aramex, TNT, Sendle, PostNord, DHL Sweden, Parcel Force**

### Known Limitations / Bugs
1. Quantity Reduction in Order Update — not working (existing bug)
2. Retry Batch loop — infinite loop after address update for label-failed
3. Cancel Fulfillment — broken for partially fulfilled orders
4. Payment mode changes — only XpressBees, Delhivery, BlueDart, Amazon supported

---

*Snapshot captured: 2026-04-15*
*Source: MCSL Regression - Master Sheet (Google Sheets)*
