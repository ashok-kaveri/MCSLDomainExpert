# India Post (WooCommerce) — QA Test Scenarios

## 🔧 Plugin Setup

### TC-1: Settings page loads successfully
**Type:** Positive
**Priority:** High
**Preconditions:**
- WooCommerce plugin is installed and active
- PluginHive India Post WooCommerce shipping plugin is installed and active
- Admin is logged into the WordPress dashboard

Given the admin is on the WordPress dashboard
When the admin navigates to WooCommerce > Settings > Shipping > India Post
Then the India Post settings page loads without errors and displays all configuration fields including API credentials, barcode range, service selection, and fallback rate

---

### TC-2: Settings page is inaccessible when plugin is deactivated
**Type:** Negative
**Priority:** Medium
**Preconditions:**
- PluginHive India Post WooCommerce shipping plugin is installed but deactivated

Given the admin is on the WordPress dashboard
When the admin navigates to WooCommerce > Settings > Shipping
Then the India Post tab is not present in the Shipping settings and the India Post settings page is not accessible

---

### TC-3: Save valid sandbox API credentials
**Type:** Positive
**Priority:** High
**Preconditions:**
- Admin is on WooCommerce > Settings > Shipping > India Post

Given the admin is on the India Post settings page
When the admin enters Username: 9999999999, Password: Dop@1234, and Customer ID: 3000064781 in the respective API credential fields
And clicks Save changes
Then a success notice is displayed and the saved values are reflected in the Username, Password, and Customer ID fields on page reload

---

### TC-4: Save fails when API username is left blank
**Type:** Negative
**Priority:** High
**Preconditions:**
- Admin is on WooCommerce > Settings > Shipping > India Post

Given the admin is on the India Post settings page
When the admin leaves the Username field empty, enters a valid Password and Customer ID
And clicks Save changes
Then an error or validation message is displayed indicating the Username field is required and the settings are not saved

---

### TC-5: Save fails when API password is left blank
**Type:** Negative
**Priority:** High
**Preconditions:**
- Admin is on WooCommerce > Settings > Shipping > India Post

Given the admin is on the India Post settings page
When the admin enters a valid Username and Customer ID but leaves the Password field empty
And clicks Save changes
Then an error or validation message is displayed indicating the Password field is required and the settings are not saved

---

### TC-6: Save fails when Customer ID is left blank
**Type:** Negative
**Priority:** High
**Preconditions:**
- Admin is on WooCommerce > Settings > Shipping > India Post

Given the admin is on the India Post settings page
When the admin enters a valid Username and Password but leaves the Customer ID field empty
And clicks Save changes
Then an error or validation message is displayed indicating the Customer ID field is required and the settings are not saved

---

### TC-7: Save fails when all API credential fields are blank
**Type:** Negative
**Priority:** High
**Preconditions:**
- Admin is on WooCommerce > Settings > Shipping > India Post

Given the admin is on the India Post settings page
When the admin leaves the Username, Password, and Customer ID fields all empty
And clicks Save changes
Then an error or validation message is displayed and the settings are not saved

---

### TC-8: Invalid API credentials are accepted at save but fail at rate retrieval
**Type:** Negative
**Priority:** High
**Preconditions:**
- Admin is on WooCommerce > Settings > Shipping > India Post

Given the admin is on the India Post settings page
When the admin enters an incorrect Username: 0000000000, Password: WrongPass, and Customer ID: 0000000000
And clicks Save changes
Then the settings are saved without a credential-validation error at save time
And when a shipping rate request is triggered, the plugin returns an authentication error or no rates are displayed

---

### TC-9: Save valid barcode prefix, range start, and range end
**Type:** Positive
**Priority:** High
**Preconditions:**
- Admin is on WooCommerce > Settings > Shipping > India Post with valid API credentials already saved

Given the admin is on the India Post settings page
When the admin enters Barcode Prefix: EB, Range Start: 468827001, and Range End: 468827999
And clicks Save changes
Then a success notice is displayed and the Barcode Prefix, Range Start, and Range End fields retain the entered values on page reload

---

### TC-10: Save fails when barcode prefix is left blank
**Type:** Negative
**Priority:** High
**Preconditions:**
- Admin is on WooCommerce > Settings > Shipping > India Post

Given the admin is on the India Post settings page
When the admin leaves the Barcode Prefix field empty and enters valid Range Start: 468827001 and Range End: 468827999
And clicks Save changes
Then an error or validation message is displayed indicating the Barcode Prefix is required and the settings are not saved

---

### TC-11: Save fails when range start is left blank
**Type:** Negative
**Priority:** High
**Preconditions:**
- Admin is on WooCommerce > Settings > Shipping > India Post

Given the admin is on the India Post settings page
When the admin enters Barcode Prefix: EB and Range End: 468827999 but leaves Range Start empty
And clicks Save changes
Then an error or validation message is displayed indicating Range Start is required and the settings are not saved

---

### TC-12: Save fails when range end is left blank
**Type:** Negative
**Priority:** High
**Preconditions:**
- Admin is on WooCommerce > Settings > Shipping > India Post

Given the admin is on the India Post settings page
When the admin enters Barcode Prefix: EB and Range Start: 468827001 but leaves Range End empty
And clicks Save changes
Then an error or validation message is displayed indicating Range End is required and the settings are not saved

---

### TC-13: Range end less than range start is rejected
**Type:** Negative
**Priority:** High
**Preconditions:**
- Admin is on WooCommerce > Settings > Shipping > India Post

Given the admin is on the India Post settings page
When the admin enters Barcode Prefix: EB, Range Start: 468827999, and Range End: 468827001
And clicks Save changes
Then an error or validation message is displayed indicating Range End must be greater than or equal to Range Start and the settings are not saved

---

### TC-14: Range start equal to range end is accepted as a single-barcode range
**Type:** Edge Case
**Priority:** Medium
**Preconditions:**
- Admin is on WooCommerce > Settings > Shipping > India Post

Given the admin is on the India Post settings page
When the admin enters Barcode Prefix: EB, Range Start: 468827001, and Range End: 468827001
And clicks Save changes
Then a success notice is displayed and the single-value range is saved correctly, representing exactly one available barcode

---

### TC-15: Non-numeric characters in range start or range end are rejected
**Type:** Negative
**Priority:** Medium
**Preconditions:**
- Admin is on WooCommerce > Settings > Shipping > India Post

Given the admin is on the India Post settings page
When the admin enters Barcode Prefix: EB, Range Start: ABC123, and Range End: 468827999
And clicks Save changes
Then an error or validation message is displayed indicating Range Start must be numeric and the settings are not saved

---

### TC-16: Barcode prefix with special characters is rejected
**Type:** Edge Case
**Priority:** Medium
**Preconditions:**
- Admin is on WooCommerce > Settings > Shipping > India Post

Given the admin is on the India Post settings page
When the admin enters Barcode Prefix: E@, Range Start: 468827001, and Range End: 468827999
And clicks Save changes
Then an error or validation message is displayed indicating the Barcode Prefix format is invalid and the settings are not saved

---

### TC-17: Enable Speed Post service and save
**Type:** Positive
**Priority:** High
**Preconditions:**
- Admin is on WooCommerce > Settings > Shipping > India Post with valid API credentials and barcode range already saved

Given the admin is on the India Post settings page
When the admin enables the Speed Post service option
And clicks Save changes
Then a success notice is displayed and the Speed Post service remains enabled on page reload

---

### TC-18: Enable Business Parcel service and save
**Type:** Positive
**Priority:** High
**Preconditions:**
- Admin is on WooCommerce > Settings > Shipping > India Post with valid API credentials and barcode range already saved

Given the admin is on the India Post settings page
When the admin enables the Business Parcel service option
And clicks Save changes
Then a success notice is displayed and the Business Parcel service remains enabled on page reload

---

### TC-19: Enable both Speed Post and Business Parcel simultaneously
**Type:** Positive
**Priority:** High
**Preconditions:**
- Admin is on WooCommerce > Settings > Shipping > India Post with valid API credentials and barcode range already saved

Given the admin is on the India Post settings page
When the admin enables both the Speed Post and Business Parcel service options
And clicks Save changes
Then a success notice is displayed and both services remain enabled on page reload

---

### TC-20: Disable all services and save
**Type:** Edge Case
**Priority:** Medium
**Preconditions:**
- Admin is on WooCommerce > Settings > Shipping > India Post with both services previously enabled

Given the admin is on the India Post settings page with both Speed Post and Business Parcel enabled
When the admin disables both Speed Post and Business Parcel service options
And clicks Save changes
Then a success notice is displayed, both services remain disabled on page reload, and no India Post shipping rates are presented at checkout

---

### TC-21: Set a valid fallback shipping rate and confirm it saves
**Type:** Positive
**Priority:** High
**Preconditions:**
- Admin is on WooCommerce > Settings > Shipping > India Post

Given the admin is on the India Post settings page
When the admin enters a numeric value of 150 in the Fallback Shipping Rate field
And clicks Save changes
Then a success notice is displayed and the Fallback Shipping Rate field shows 150 on page reload

---

### TC-22: Fallback rate of zero is accepted
**Type:** Edge Case
**Priority:** Medium
**Preconditions:**
- Admin is on WooCommerce > Settings > Shipping > India Post

Given the admin is on the India Post settings page
When the admin enters 0 in the Fallback Shipping Rate field
And clicks Save changes
Then a success notice is displayed and the Fallback Shipping Rate field shows 0 on page reload, indicating free fallback shipping

---

### TC-23: Negative value in fallback rate field is rejected
**Type:** Negative
**Priority:** Medium
**Preconditions:**
- Admin is on WooCommerce > Settings > Shipping > India Post

Given the admin is on the India Post settings page
When the admin enters -50 in the Fallback Shipping Rate field

## 📦 Rate Calculation

### TC-24: Rates displayed for both Speed Post and Business Parcel with valid product weight and dimensions
**Type:** Positive
**Priority:** High
**Preconditions:**
- India Post plugin is installed and activated
- API credentials (Username: 9999999999, Password: Dop@1234, Customer ID: 3000064781) are saved in plugin settings
- Speed Post contract_id 41585456 and Business Parcel contract_id 41367422 are configured
- A product exists with weight (e.g., 0.5 kg) and dimensions (e.g., 10×10×10 cm) set
- A valid India Post shipping zone covering domestic PIN codes is configured in WooCommerce

**Steps:**
Given the store is configured with valid India Post sandbox credentials and both service contract IDs
When a customer adds the weighted and dimensioned product to the cart and proceeds to WooCommerce checkout
And enters a valid domestic destination PIN code (e.g., 110001 – New Delhi)
Then the checkout shipping section displays a rate for Speed Post and a separate rate for Business Parcel, both with non-zero amounts

---

### TC-25: Speed Post rate value is non-zero and distinct from Business Parcel rate
**Type:** Positive
**Priority:** High
**Preconditions:**
- Same as above; both services are active
- Product weight: 1 kg, dimensions: 15×15×15 cm

**Steps:**
Given the cart contains a product with weight 1 kg and dimensions 15×15×15 cm
When the customer proceeds to checkout with destination PIN code 400001 (Mumbai)
And the India Post API returns rates for both services
Then the Speed Post rate and the Business Parcel rate are each greater than zero and the two rate values are not identical to each other

---

### TC-26: Rates update when destination PIN code is changed to a different city
**Type:** Positive
**Priority:** High
**Preconditions:**
- Cart contains a product with weight 0.5 kg and dimensions set
- Checkout is open with initial destination PIN code 110001 (New Delhi)
- India Post rates are already displayed for both services

**Steps:**
Given the checkout page shows Speed Post and Business Parcel rates for PIN code 110001
When the customer changes the destination PIN code to 560001 (Bengaluru) and triggers a rate refresh (tab out or update cart)
Then the displayed rates for Speed Post and Business Parcel update to values that reflect the new destination, and the previously shown rates are replaced

---

### TC-27: Rates update when destination PIN code is changed to a remote/far zone
**Type:** Edge Case
**Priority:** Medium
**Preconditions:**
- Cart contains a product with weight 0.5 kg and dimensions set
- Checkout is open with initial destination PIN code 110001 (New Delhi)

**Steps:**
Given Speed Post and Business Parcel rates are displayed for PIN code 110001
When the customer changes the destination PIN code to 793001 (Shillong, North-East India)
And the rate section refreshes
Then new rates are displayed for both services and the rates are higher than or different from the rates shown for PIN code 110001, confirming zone-based recalculation

---

### TC-28: Fallback or minimum-weight behaviour when product has no weight set
**Type:** Negative
**Priority:** High
**Preconditions:**
- A product exists with weight field left blank and no dimensions set
- India Post plugin is configured with valid credentials and both contract IDs
- Plugin settings define a fallback/minimum weight value (e.g., 0.5 kg) or the expected behaviour is documented

**Steps:**
Given a product with no weight or dimensions configured is added to the cart
When the customer proceeds to checkout and enters a valid domestic PIN code (e.g., 110001)
Then either (a) rates are displayed using the configured fallback/minimum weight, or (b) a descriptive notice is shown indicating weight is required — and the checkout does not throw a fatal error or display a blank shipping section

---

### TC-29: Fallback behaviour when product has weight but no dimensions set
**Type:** Edge Case
**Priority:** Medium
**Preconditions:**
- A product exists with weight set to 1 kg but length, width, and height fields left blank
- India Post plugin is configured with valid credentials

**Steps:**
Given a product with weight 1 kg and no dimensions is added to the cart
When the customer proceeds to checkout with destination PIN code 110001
Then rates are returned using the weight alone (volumetric weight is not applied), and both Speed Post and Business Parcel rates are displayed without error

---

### TC-30: Rates are not displayed for an international destination
**Type:** Negative
**Priority:** High
**Preconditions:**
- Cart contains a product with weight 0.5 kg and dimensions set
- WooCommerce is configured to allow shipping to international countries
- India Post shipping zone is scoped to India only

**Steps:**
Given the cart contains a valid product with weight and dimensions
When the customer proceeds to checkout and selects a shipping country other than India (e.g., United States) with a corresponding postal code
Then no India Post shipping methods (Speed Post or Business Parcel) appear in the checkout shipping options, and no India Post API call error is surfaced to the customer

---

### TC-31: Rates are not displayed when destination country is set to a neighbouring country
**Type:** Negative
**Priority:** Medium
**Preconditions:**
- Cart contains a product with weight 0.5 kg and dimensions set
- WooCommerce allows shipping to multiple countries

**Steps:**
Given the cart contains a weighted and dimensioned product
When the customer selects Nepal (or any non-India country) as the shipping destination at checkout
Then India Post Speed Post and Business Parcel rates do not appear in the shipping methods list, confirming the plugin restricts itself to domestic India destinations only

---

### TC-32: No rates displayed when API credentials are invalid
**Type:** Negative
**Priority:** High
**Preconditions:**
- India Post plugin is installed
- Incorrect API credentials are saved (e.g., wrong password or invalid Customer ID)
- Cart contains a product with weight and dimensions

**Steps:**
Given the plugin is configured with invalid API credentials
When the customer adds a product to the cart and proceeds to checkout with a valid domestic PIN code (e.g., 110001)
Then India Post shipping rates do not appear in the checkout shipping section, and no unhandled PHP error or raw API error message is exposed to the customer

---

### TC-33: No rates displayed when destination PIN code is invalid or malformed
**Type:** Negative
**Priority:** Medium
**Preconditions:**
- Valid API credentials are configured
- Cart contains a product with weight 0.5 kg and dimensions set

**Steps:**
Given the checkout page is open with valid India Post credentials active
When the customer enters a malformed PIN code (e.g., "ABCDEF" or "00000") as the destination
Then India Post rates are not displayed, the shipping section either shows no available methods or an appropriate message, and no fatal error occurs

---

### TC-34: Rates recalculate correctly when cart quantity is increased
**Type:** Edge Case
**Priority:** Medium
**Preconditions:**
- Valid API credentials and both contract IDs are configured
- A product with weight 0.5 kg and dimensions 10×10×10 cm is in the cart at quantity 1
- Rates are already displayed for PIN code 110001

**Steps:**
Given Speed Post and Business Parcel rates are shown for a single unit of the product
When the customer increases the cart quantity to 3 and updates the cart
Then the rates for both services recalculate and reflect the higher total weight (1.5 kg), with the new rate values being greater than or equal to the original single-unit rates

---

### TC-35: Rates displayed for a product at the maximum supported weight boundary
**Type:** Edge Case
**Priority:** Medium
**Preconditions:**
- Valid API credentials and both contract IDs are configured
- A product is configured at the maximum weight accepted by India Post (e.g., 35 kg for Business Parcel)

**Steps:**
Given a product set to the maximum allowable weight for India Post services is added to the cart
When the customer proceeds to checkout with destination PIN code 110001
Then rates are returned and displayed for the applicable service(s) without API errors, and any service that does not support that weight is either hidden or shows an appropriate unavailability message

## 🏷️ Label Generation

### TC-36: Speed Post label generation — successful PDF download
**Type:** Positive
**Priority:** High
**Preconditions:**
- Plugin installed and activated with valid sandbox API credentials (Username: 9999999999, Password: Dop@1234, Customer ID: 3000064781)
- Speed Post contract_id 41585456 configured in plugin settings
- Barcode range configured: Prefix EB, Start 468827001, End 468827999
- A WooCommerce test order exists with India Post Speed Post selected as the shipping method
- Order status is Processing

**Steps:**
Given the admin is on the WooCommerce order detail page for the Speed Post test order
When the admin locates the India Post shipment panel and clicks "Create Shipment"
Then a PDF file is downloaded or displayed in the browser
And the PDF label contains the correct sender name and address matching the store origin address configured in plugin settings
And the PDF label contains the correct recipient name, address, and pincode from the order's shipping address
And the PDF label contains a barcode beginning with prefix "EB" followed by a numeric value within the range 468827001–468827999 and ending with "IN"

---

### TC-37: Speed Post label — barcode value saved against the order
**Type:** Positive
**Priority:** High
**Preconditions:**
- Plugin configured with sandbox credentials and barcode range as above
- A Speed Post test order has had a shipment created successfully
- No prior shipments exist that have consumed the barcode range

**Steps:**
Given a Speed Post shipment has just been created for the test order
When the admin views the India Post shipment panel on the order detail page
Then the barcode number assigned to this shipment (e.g., EB468827001IN) is saved and displayed against the order in the shipment panel

---

### TC-38: Barcode increments correctly on the next Speed Post order
**Type:** Positive
**Priority:** High
**Preconditions:**
- Plugin configured with sandbox credentials and barcode range starting at 468827001
- A first Speed Post order has already had a shipment created and was assigned barcode EB468827001IN
- A second distinct WooCommerce test order exists with India Post Speed Post selected

**Steps:**
Given the first order was assigned barcode EB468827001IN
When the admin opens the second Speed Post order's detail page and clicks "Create Shipment" in the India Post shipment panel
Then the PDF label generated for the second order contains barcode EB468827002IN
And the barcode EB468827002IN is saved against the second order in the shipment panel

---

### TC-39: Business Parcel label generation — successful PDF download
**Type:** Positive
**Priority:** High
**Preconditions:**
- Plugin configured with sandbox credentials and Business Parcel contract_id 41367422
- Barcode range configured: Prefix EB, Start 468827001, End 468827999
- A WooCommerce test order exists with India Post Business Parcel selected as the shipping method
- Order status is Processing

**Steps:**
Given the admin is on the WooCommerce order detail page for the Business Parcel test order
When the admin locates the India Post shipment panel and clicks "Create Shipment"
Then a PDF file is downloaded or displayed in the browser
And the PDF label contains the correct sender name and address matching the store origin address
And the PDF label contains the correct recipient name, address, and pincode from the order's shipping address
And the PDF label contains a valid barcode within the configured range

---

### TC-40: Business Parcel label — transmission_mode is Surface (S) in the API payload
**Type:** Positive
**Priority:** High
**Preconditions:**
- Plugin configured with sandbox credentials and Business Parcel contract_id 41367422
- A WooCommerce test order exists with India Post Business Parcel selected
- Network request logging is available (e.g., browser DevTools, WooCommerce system log, or API request log)

**Steps:**
Given the admin is on the WooCommerce order detail page for the Business Parcel test order
When the admin clicks "Create Shipment" in the India Post shipment panel
And the outgoing API request payload is captured via the network log or plugin debug log
Then the payload sent to the India Post API contains the field transmission_mode with value "S"

---

### TC-41: Duplicate label creation for the same order — blocked or new barcode allocated
**Type:** Negative
**Priority:** High
**Preconditions:**
- Plugin configured with sandbox credentials and barcode range as above
- A Speed Post test order already has a shipment created with barcode EB468827001IN saved against it

**Steps:**
Given the admin is on the WooCommerce order detail page for an order that already has a generated shipment and barcode
When the admin attempts to click "Create Shipment" again in the India Post shipment panel
Then either the plugin blocks the action and displays an informative message indicating a shipment already exists for this order
Or the plugin creates a new shipment and allocates the next available barcode (e.g., EB468827002IN) and saves it against the order
And the previously assigned barcode EB468827001IN is not overwritten without a clear indication to the admin

---

### TC-42: Label generation with invalid API credentials
**Type:** Negative
**Priority:** High
**Preconditions:**
- Plugin installed with an incorrect API password configured (e.g., Password: WrongPass)
- A WooCommerce test order exists with India Post Speed Post selected

**Steps:**
Given the admin is on the WooCommerce order detail page for the Speed Post test order
When the admin clicks "Create Shipment" in the India Post shipment panel
Then no PDF label is generated
And the India Post shipment panel displays an error message indicating authentication failure or invalid credentials
And no barcode is saved against the order

---

### TC-43: Label generation when barcode range is exhausted
**Type:** Edge Case
**Priority:** High
**Preconditions:**
- Plugin configured with a barcode range where the next available barcode number exceeds the configured End value (468827999)
- All barcodes in the range have been consumed by prior shipments
- A WooCommerce test order exists with India Post Speed Post selected

**Steps:**
Given the configured barcode range has been fully consumed and no barcodes remain
When the admin clicks "Create Shipment" in the India Post shipment panel for a new order
Then no PDF label is generated
And the India Post shipment panel displays an error message indicating the barcode range is exhausted or no barcodes are available
And no barcode is saved against the order

---

### TC-44: Label generation when barcode range start equals barcode range end (single barcode range)
**Type:** Edge Case
**Priority:** Medium
**Preconditions:**
- Plugin configured with barcode range Prefix EB, Start 468827001, End 468827001 (a range of exactly one barcode)
- No prior shipments have consumed this barcode
- A WooCommerce test order exists with India Post Speed Post selected

**Steps:**
Given the barcode range contains exactly one available barcode (EB468827001IN)
When the admin clicks "Create Shipment" in the India Post shipment panel
Then a PDF label is generated successfully containing barcode EB468827001IN
And the barcode EB468827001IN is saved against the order
And when a second shipment creation is attempted for any order, the plugin displays an error indicating the barcode range is exhausted

---

### TC-45: Label PDF content — barcode format validation
**Type:** Edge Case
**Priority:** Medium
**Preconditions:**
- Plugin configured with sandbox credentials and barcode range: Prefix EB, Start 468827001, End 468827999
- A Speed Post test order has had a shipment created successfully

**Steps:**
Given a PDF label has been generated for a Speed Post order
When the admin opens or downloads the PDF label
Then the barcode printed on the label follows the format: two-letter prefix "EB" + nine-digit numeric sequence + suffix "IN" (e.g., EB468827001IN)
And the barcode is scannable or visually rendered as a barcode graphic on the PDF (not plain text only)

---

### TC-46: Label generation with missing recipient pincode
**Type:** Negative
**Priority:** Medium
**Preconditions:**
- Plugin configured with valid sandbox credentials and barcode range
- A WooCommerce test order exists with India Post Speed Post selected but the shipping address has no pincode (postcode field is empty or invalid)

**Steps:**
Given the admin is on the WooCommerce order detail page for the order with a missing recipient pincode
When the admin clicks "Create Shipment" in the India Post shipment panel
Then no PDF label is generated
And the India Post shipment panel displays a validation error indicating the recipient pincode is missing or invalid
And no barcode is consumed from the configured range

---

### TC-47: Business Parcel barcode increments independently after Speed Post barcode consumption
**Type:** Edge Case
**Priority:** Medium
**Preconditions:**
- Plugin configured with sandbox credentials, Business Parcel contract_id 41367422, and barcode range Prefix EB, Start 468827001, End 468827999
- One Speed Post shipment has already been created and consumed barcode EB468827001IN
- A WooCommerce test order exists with India Post Business Parcel selected

**Steps:**
Given barcode EB468827001IN has been consumed by a Speed Post shipment
When the admin opens the Business Parcel order detail page and clicks "Create Shipment" in the India Post shipment panel
Then the PDF label generated for the Business Parcel order contains the next available barcode (EB468827002IN)
And the barcode EB468827002IN is saved against the Business Parcel order
And the API payload for this shipment contains transmission_mode with value "S"

## ↩️ Return Labels

### TC-48: Create Return Label for Order with Existing Forward Label
**Type:** Positive
**Priority:** High
**Preconditions:**
- Plugin is installed and activated with valid sandbox credentials (Username: 9999999999, Password: Dop@1234, Customer ID: 3000064781)
- Barcode range configured: Prefix EB, Start 468827001, End 468827999
- A domestic WooCommerce order exists with a forward label already generated (e.g., barcode EB468827001IN)
- Order status allows label actions

**Steps:**
Given a WooCommerce order is open in the admin order detail screen with a forward label already generated
When the admin clicks the "Create Return Label" button on the order screen
Then the system initiates a return label creation request to the India Post sandbox API and a success confirmation is displayed without errors

---

### TC-49: Return Label PDF Downloads Correctly
**Type:** Positive
**Priority:** High
**Preconditions:**
- Plugin configured with valid sandbox credentials and barcode range
- A domestic order exists with a forward label generated
- Return label has been created successfully

**Steps:**
Given a WooCommerce order with a successfully created return label
When the admin clicks the download or view button for the return label
Then a valid PDF file downloads to the browser
And the PDF opens without corruption and contains a readable barcode and address block

---

### TC-50: Return Label Has Sender and Recipient Addresses Swapped from Forward Label
**Type:** Positive
**Priority:** High
**Preconditions:**
- Plugin configured with valid sandbox credentials and barcode range
- A domestic order exists with a forward label generated where the store address is the sender and the customer address is the recipient

**Steps:**
Given a WooCommerce order with both a forward label and a return label generated
When the admin opens the return label PDF
Then the sender address on the return label matches the customer (recipient) address from the forward label
And the recipient address on the return label matches the store (sender) address from the forward label

---

### TC-51: Return Label Barcode Differs from Forward Label Barcode
**Type:** Positive
**Priority:** High
**Preconditions:**
- Plugin configured with barcode range: Prefix EB, Start 468827001, End 468827999
- A domestic order exists with a forward label generated using barcode EB468827001IN

**Steps:**
Given a WooCommerce order with a forward label bearing barcode EB468827001IN
When the admin creates a return label for the same order
Then the return label PDF contains a barcode that is different from EB468827001IN
And the return label barcode follows the configured prefix and range format (e.g., EB468827002IN)

---

### TC-52: Barcode Counter Increments Correctly After Return Label Creation
**Type:** Positive
**Priority:** High
**Preconditions:**
- Plugin configured with barcode range: Prefix EB, Start 468827001, End 468827999
- Forward label generated on Order A consuming barcode EB468827001IN
- Return label generated on Order A consuming barcode EB468827002IN
- A second domestic order (Order B) exists with no labels yet

**Steps:**
Given the barcode counter is at EB468827003IN after forward and return labels were generated for Order A
When the admin generates a forward label for Order B
Then the forward label for Order B uses barcode EB468827003IN
And the internal barcode counter advances to EB468827004IN for the next label

---

### TC-53: Attempt to Create Return Label Without an Existing Forward Label
**Type:** Negative
**Priority:** High
**Preconditions:**
- Plugin configured with valid sandbox credentials and barcode range
- A domestic WooCommerce order exists with no forward label generated

**Steps:**
Given a WooCommerce order that has no forward label generated
When the admin attempts to click "Create Return Label" on the order screen
Then the system displays an appropriate error or the "Create Return Label" button is absent or disabled
And no barcode is consumed from the configured range

---

### TC-54: Return Label Creation Fails Due to Invalid API Credentials
**Type:** Negative
**Priority:** High
**Preconditions:**
- Plugin settings contain incorrect API credentials (e.g., wrong password)
- A domestic order exists with a forward label generated

**Steps:**
Given a WooCommerce order with a forward label and plugin credentials set to an invalid password
When the admin clicks "Create Return Label"
Then the system returns an authentication error message in the order admin screen
And no return label PDF is generated
And no barcode is consumed from the configured range

---

### TC-55: Return Label Creation Attempted When Barcode Range Is Exhausted
**Type:** Edge Case
**Priority:** High
**Preconditions:**
- Plugin configured with barcode range: Prefix EB, Start 468827001, End 468827999
- All 999 barcodes in the range have been consumed by prior forward and return labels
- A domestic order exists with a forward label generated using the last available barcode

**Steps:**
Given the barcode counter has reached the end of the configured range (EB468827999IN already used)
When the admin attempts to create a return label for an order
Then the system displays an error indicating the barcode range is exhausted
And no return label PDF is generated
And the admin is prompted to update the barcode range in plugin settings

---

### TC-56: Return Label PDF Contains Correct Barcode Format
**Type:** Positive
**Priority:** Medium
**Preconditions:**
- Plugin configured with barcode range: Prefix EB, Start 468827001, End 468827999
- A domestic order exists with a forward label generated

**Steps:**
Given a WooCommerce order with a forward label generated
When the admin creates and downloads the return label PDF
Then the barcode printed on the return label PDF matches the format EB{numeric_sequence}IN
And the barcode is scannable and corresponds to the next value in the configured range

---

### TC-57: Return Label Barcode Counter Does Not Increment on Failed Return Label Creation
**Type:** Negative
**Priority:** Medium
**Preconditions:**
- Plugin configured with valid sandbox credentials and barcode range
- A domestic order exists with a forward label generated
- The India Post sandbox API is temporarily unavailable or returns an error

**Steps:**
Given the India Post sandbox API returns an error response during return label creation
When the admin clicks "Create Return Label" on the order screen
Then the system displays an error message indicating the label could not be created
And the barcode counter remains unchanged at its value prior to the failed attempt
And the next successful label generation uses the same barcode number that would have been assigned

---

### TC-58: Multiple Return Labels Cannot Be Created for the Same Order
**Type:** Edge Case
**Priority:** Medium
**Preconditions:**
- Plugin configured with valid sandbox credentials and barcode range
- A domestic order exists with both a forward label and a return label already generated

**Steps:**
Given a WooCommerce order that already has a return label generated
When the admin attempts to click "Create Return Label" again on the same order
Then the system either hides or disables the "Create Return Label" button
Or displays an informational message indicating a return label already exists for this order
And no additional barcode is consumed from the configured range

---

### TC-59: Return Label Reflects Correct Service Type for Business Parcel Order
**Type:** Positive
**Priority:** Medium
**Preconditions:**
- Plugin configured with Business Parcel contract_id 41367422 and transmission_mode Surface (S)
- A domestic order exists with a Business Parcel forward label generated

**Steps:**
Given a WooCommerce order fulfilled via Business Parcel service with an existing forward label
When the admin creates and downloads the return label PDF
Then the return label PDF indicates the Business Parcel service
And the transmission mode on the return label is Surface (S) consistent with the forward label service configuration

## 🛡️ Insurance

### TC-60: Set insurance value on a product and verify rate includes insurance
**Type:** Positive
**Priority:** High
**Preconditions:**
- India Post plugin is installed and activated
- Sandbox API credentials are configured (Username: 9999999999, Password: Dop@1234, Customer ID: 3000064781)
- Insurance setting is enabled in India Post plugin settings
- At least one published product exists

**Steps:**
Given the admin is logged in to WooCommerce admin
When the admin navigates to the product edit page and opens the India Post settings tab
And enters a numeric insurance value (e.g., 500) in the insurance value field and saves the product
And a test customer adds that product to the cart and proceeds to checkout
And the customer enters a valid Indian shipping address
Then the India Post shipping rate displayed at checkout reflects a cost calculated with the insurance value of 500 included

---

### TC-61: Two products with individual insurance values — total insurance is the sum
**Type:** Positive
**Priority:** High
**Preconditions:**
- India Post plugin is installed and activated with sandbox credentials
- Insurance setting is enabled in India Post plugin settings
- Product A has an insurance value of 300 set in its India Post settings tab
- Product B has an insurance value of 700 set in its India Post settings tab

**Steps:**
Given the admin has saved insurance values of 300 on Product A and 700 on Product B
When a test customer adds both Product A and Product B to the cart and proceeds to checkout
And the customer enters a valid Indian shipping address
Then the India Post shipping rate at checkout is calculated using a combined insurance amount of 1000 (300 + 700)

---

### TC-62: Blank insurance value falls back to product sale price
**Type:** Positive
**Priority:** High
**Preconditions:**
- India Post plugin is installed and activated with sandbox credentials
- Insurance setting is enabled in India Post plugin settings
- A product has a sale price of 450 set in WooCommerce
- The insurance value field in the product's India Post settings tab is left blank

**Steps:**
Given the product's India Post insurance value field is empty and the product sale price is 450
When a test customer adds the product to the cart and proceeds to checkout
And the customer enters a valid Indian shipping address
Then the India Post shipping rate at checkout is calculated using an insurance amount equal to the product sale price of 450

---

### TC-63: Insurance disabled in plugin settings — insurance amount is 0 regardless of product values
**Type:** Positive
**Priority:** High
**Preconditions:**
- India Post plugin is installed and activated with sandbox credentials
- Product A has an insurance value of 800 set in its India Post settings tab
- Insurance setting is explicitly disabled in India Post plugin settings

**Steps:**
Given the Insurance setting is toggled off in the India Post plugin settings and saved
When a test customer adds Product A to the cart and proceeds to checkout
And the customer enters a valid Indian shipping address
Then the India Post shipping rate at checkout is calculated with an insurance amount of 0, ignoring the product-level insurance value of 800

---

### TC-64: Insurance disabled — two products with insurance values both contribute 0
**Type:** Negative
**Priority:** Medium
**Preconditions:**
- India Post plugin is installed and activated with sandbox credentials
- Product A has an insurance value of 300 and Product B has an insurance value of 600 in their respective India Post settings tabs
- Insurance setting is disabled in India Post plugin settings

**Steps:**
Given the Insurance setting is toggled off in the India Post plugin settings and saved
When a test customer adds both Product A and Product B to the cart and proceeds to checkout
And the customer enters a valid Indian shipping address
Then the India Post shipping rate at checkout is calculated with a total insurance amount of 0, and neither product's insurance value is applied

---

### TC-65: Insurance value set to zero explicitly on a product
**Type:** Edge Case
**Priority:** Medium
**Preconditions:**
- India Post plugin is installed and activated with sandbox credentials
- Insurance setting is enabled in India Post plugin settings
- A product has a sale price of 350

**Steps:**
Given the admin navigates to the product edit page and opens the India Post settings tab
When the admin enters 0 as the insurance value and saves the product
And a test customer adds the product to the cart and proceeds to checkout
And the customer enters a valid Indian shipping address
Then the India Post shipping rate at checkout is calculated using an insurance amount of 0, and the product sale price of 350 is NOT used as a fallback

---

### TC-66: Blank insurance value with no sale price set — fallback behaviour
**Type:** Edge Case
**Priority:** Medium
**Preconditions:**
- India Post plugin is installed and activated with sandbox credentials
- Insurance setting is enabled in India Post plugin settings
- A product has a regular price set but no sale price configured
- The insurance value field in the product's India Post settings tab is left blank

**Steps:**
Given the product has no sale price and the India Post insurance value field is empty
When a test customer adds the product to the cart and proceeds to checkout
And the customer enters a valid Indian shipping address
Then the checkout does not produce a fatal error, and the India Post shipping rate is calculated using a defined fallback value (e.g., regular price or 0) without breaking rate retrieval

---

### TC-67: Non-numeric insurance value entered on a product
**Type:** Negative
**Priority:** Medium
**Preconditions:**
- India Post plugin is installed and activated with sandbox credentials
- Insurance setting is enabled in India Post plugin settings

**Steps:**
Given the admin navigates to the product edit page and opens the India Post settings tab
When the admin enters a non-numeric value (e.g., "abc") in the insurance value field and saves the product
Then the plugin either displays a validation error preventing the save, or sanitises the value to 0 or blank, and does not pass invalid data to the India Post API during rate calculation

---

### TC-68: Insurance value on one product, blank on the other — mixed cart insurance total
**Type:** Edge Case
**Priority:** Medium
**Preconditions:**
- India Post plugin is installed and activated with sandbox credentials
- Insurance setting is enabled in India Post plugin settings
- Product A has an insurance value of 400 set in its India Post settings tab
- Product B has the insurance value field left blank and a sale price of 250

**Steps:**
Given Product A has an explicit insurance value of 400 and Product B has no insurance value but a sale price of 250
When a test customer adds both products to the cart and proceeds to checkout
And the customer enters a valid Indian shipping address
Then the India Post shipping rate at checkout is calculated using a total insurance amount of 650 (400 from Product A + 250 fallback sale price from Product B)

## 🖥️ Admin UI

### TC-69: Service row radio button selection and highlight
**Type:** Positive
**Priority:** High
**Preconditions:**
- India Post WooCommerce plugin is installed and activated
- Admin is logged in to WooCommerce admin
- India Post settings page is open (WooCommerce → Settings → Shipping → India Post)
- At least two service rows (Speed Post and Business Parcel) are visible in the services table

**Steps:**
Given the India Post settings page is loaded with Speed Post and Business Parcel service rows displayed
When the admin clicks on the Business Parcel service row
Then the radio button within that row becomes selected
And the Business Parcel row is visually highlighted (distinct background colour indicating selection)
And the Speed Post row is no longer highlighted

---

### TC-70: Previously selected service row persists after page reload
**Type:** Positive
**Priority:** High
**Preconditions:**
- India Post WooCommerce plugin is installed and activated
- Admin is logged in to WooCommerce admin
- India Post settings page is open
- Speed Post and Business Parcel service rows are visible

**Steps:**
Given the admin has clicked the Business Parcel service row so its radio button is selected and the row is highlighted
When the admin saves the settings and then reloads the India Post settings page
Then the Business Parcel service row is still highlighted on load
And the radio button for Business Parcel remains in the selected state without requiring any additional interaction

---

### TC-71: No service row is highlighted on first load before any selection
**Type:** Edge Case
**Priority:** Medium
**Preconditions:**
- India Post WooCommerce plugin is freshly installed with no prior settings saved
- Admin is logged in to WooCommerce admin
- India Post settings page is opened for the first time

**Steps:**
Given the plugin has never had a service row selected or saved
When the admin navigates to the India Post settings page
Then no service row is highlighted
And no radio button is in the selected state

---

### TC-72: Selecting a different service row updates highlight and deselects previous row
**Type:** Positive
**Priority:** Medium
**Preconditions:**
- India Post settings page is open
- Business Parcel row is currently selected and highlighted

**Steps:**
Given the Business Parcel service row is currently selected and highlighted
When the admin clicks on the Speed Post service row
Then the Speed Post row becomes highlighted and its radio button becomes selected
And the Business Parcel row loses its highlight
And the Business Parcel radio button is no longer selected

---

### TC-73: Reload persists Speed Post selection after switching from Business Parcel
**Type:** Positive
**Priority:** Medium
**Preconditions:**
- India Post settings page is open
- Business Parcel was previously the saved selection

**Steps:**
Given the admin clicks the Speed Post service row and saves the settings
When the admin reloads the India Post settings page
Then the Speed Post service row is highlighted
And the Speed Post radio button is in the selected state
And the Business Parcel row is not highlighted

---

### TC-74: Row background changes to light grey on hover
**Type:** Positive
**Priority:** Low
**Preconditions:**
- India Post settings page is open
- Speed Post and Business Parcel service rows are visible
- Neither row is currently being hovered

**Steps:**
Given the India Post settings page is loaded with service rows in their default background state
When the admin hovers the mouse cursor over the Speed Post service row
Then the Speed Post row background changes to light grey
And the Business Parcel row background remains unchanged

---

### TC-75: Hover background reverts when cursor leaves the row
**Type:** Edge Case
**Priority:** Low
**Preconditions:**
- India Post settings page is open
- Admin has hovered over the Business Parcel row so it shows a light grey background

**Steps:**
Given the Business Parcel row is displaying a light grey background due to hover
When the admin moves the mouse cursor away from the Business Parcel row
Then the Business Parcel row background reverts to its default (non-hover) state

---

### TC-76: Hover style does not override the selected row highlight
**Type:** Edge Case
**Priority:** Low
**Preconditions:**
- India Post settings page is open
- Speed Post row is currently selected and highlighted

**Steps:**
Given the Speed Post row is selected and displaying the selection highlight colour
When the admin hovers the mouse cursor over the Speed Post row
Then the row continues to display a visually distinct selected state
And the hover style does not replace or obscure the selection highlight in a way that makes the selection ambiguous

---

### TC-77: Cancel Package button shows error message and makes no API call
**Type:** Negative
**Priority:** High
**Preconditions:**
- India Post WooCommerce plugin is installed and activated with valid sandbox credentials saved
- A WooCommerce order exists with an India Post shipment that has a generated label
- Admin is on the WooCommerce order detail page for that shipment
- Browser developer tools Network tab is open and recording

**Steps:**
Given the admin is viewing the order detail page with the India Post shipment meta box visible
When the admin clicks the Cancel Package button for the shipment
Then an error message is displayed on the page (e.g. "Cancellation is not supported" or equivalent plugin-defined error text)
And no network request to any India Post API endpoint is initiated as confirmed by the browser Network tab showing zero new outbound requests after the button click

---

### TC-78: No /label/void API call is made when Cancel Package is clicked
**Type:** Negative
**Priority:** High
**Preconditions:**
- India Post WooCommerce plugin is installed and activated
- A WooCommerce order exists with a generated India Post shipment label
- Admin is on the order detail page
- Browser developer tools Network tab is open, filtered to XHR/Fetch requests, and cleared before the test action

**Steps:**
Given the Network tab is cleared and recording with an XHR/Fetch filter applied
When the admin clicks the Cancel Package button on the India Post shipment
Then no request containing the path /label/void (or any void-related endpoint) appears in the Network tab
And the error message is displayed in the UI confirming the action was blocked client-side without reaching the API

---

### TC-79: Cancel Package error message is displayed without page reload
**Type:** Negative
**Priority:** Medium
**Preconditions:**
- Admin is on the WooCommerce order detail page for an order with a generated India Post label
- The Cancel Package button is visible in the India Post shipment meta box

**Steps:**
Given the order detail page is fully loaded and the Cancel Package button is visible
When the admin clicks the Cancel Package button
Then an error message appears inline on the page without a full page reload
And the shipment details and label information remain visible and unchanged after the error message is shown

---

### TC-80: Cancel Package button does not alter shipment status or label data
**Type:** Edge Case
**Priority:** Medium
**Preconditions:**
- Admin is on the WooCommerce order detail page for an order with a generated India Post label
- The barcode and label PDF link are visible in the shipment meta box

**Steps:**
Given the shipment meta box displays a valid barcode and a PDF label link before the cancel action
When the admin clicks the Cancel Package button and the error message is displayed
Then the barcode value displayed in the meta box remains unchanged
And the PDF label link remains accessible and unchanged
And the WooCommerce order status remains the same as it was before the button was clicked
