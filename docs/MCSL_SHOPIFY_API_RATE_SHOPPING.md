# MCSL Shopify API Recipes — Store Setup, Markets, Rate-Shopping

Working recipes verified end-to-end on the `test1121-3x1v0ncz` dev store on 2026-06-08. Each pattern shows exactly which Admin API calls succeed, which are blocked, and which require admin UI follow-up. Use this as the canonical reference for setting up a Shopify dev store for MCSL QA and triggering MCSL's carrier-service callback via API.

---

## Big-picture answer: how to trigger MCSL's rate callback via API

For QA testing of MCSL's rate response, there are three orthogonal API surfaces. Pick by the constraints you care about:

| Approach | Hits MCSL callback? | Creates real order? | Needs Online Store channel? | Notes |
|---|---|---|---|---|
| **Admin API `draftOrderCalculate`** (recommended for rate QA) | ✅ | No | No | Works on freshly installed dev stores. Returns `availableShippingRates` from every carrier service attached to the destination zone. |
| **Admin API `orderCreate` + `BYPASS_STOCK`** | ❌ | Yes | No | Order is created in admin but Shopify skips rate-shopping entirely. Good for label-generation QA when you already have a known shipping method, bad for rate verification. |
| **Storefront API `cart.deliveryGroups(withCarrierRates: true) @defer`** | ✅ | No (just rates) | Yes | Mirrors the buyer-side flow exactly. Requires the Online Store sales channel activated (which is admin-UI-only on dev stores). |

**For most QA work, `draftOrderCalculate` is the fastest path** — it bypasses Online Store activation and gives you actual carrier rates in one round-trip.

---

## Store prerequisites for India shipping (and other localised QA)

These are the API-doable setup steps to get a dev store ready for India→India rate-shopping. Order doesn't matter, but later steps depend on earlier ones being correct.

### 1. Change the primary location to the target country

REST `PUT /admin/api/.../locations/{id}.json` returns **HTTP 406** on API version 2026-04 — the endpoint is deprecated. Use GraphQL `locationEdit` instead.

```python
import requests

STORE   = "<slug>"
V       = "2026-04"
TOKEN   = "shpat_..."
GQL     = f"https://{STORE}.myshopify.com/admin/api/{V}/graphql.json"
HDR     = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

# Find the primary location id first via { locations(first:10) { nodes { id name } } }
LOC_ID = "gid://shopify/Location/116113211757"

r = requests.post(GQL, headers=HDR, json={
    "query": """
mutation locEdit($id: ID!, $input: LocationEditInput!) {
  locationEdit(id: $id, input: $input) {
    location { id name address { address1 city zip countryCode } }
    userErrors { field message }
  }
}
""",
    "variables": {
        "id": LOC_ID,
        "input": {
            "name": "Bengaluru Warehouse",
            "address": {
                "address1": "MG Road",
                "city": "Bengaluru",
                "countryCode": "IN",
                "zip": "560001",
                "phone": "+919876543210",
            },
        },
    },
})
```

**Critical schema note**: `LocationEditAddressInput` does NOT have a `province` field. Including it returns `INVALID_VARIABLE` — `"Field is not defined on LocationEditAddressInput"`. Pass `address1`, `city`, `countryCode`, `zip`, `phone` only.

### 2. Update the Domestic shipping zone to contain the target country

REST `PUT /admin/api/.../shipping_zones/{id}.json` also returns **HTTP 406** on 2026-04. Use GraphQL `deliveryProfileUpdate` instead.

First query the structure to grab the IDs you need:

```python
r = requests.post(GQL, headers=HDR, json={"query": """
{
  deliveryProfiles(first: 5) {
    nodes {
      id name default
      profileLocationGroups {
        locationGroup { id }
        locationGroupZones(first: 10) {
          nodes { zone { id name countries { code { countryCode } } } }
        }
      }
    }
  }
}
"""})
```

Then update:

```python
r = requests.post(GQL, headers=HDR, json={
    "query": """
mutation profUpdate($id: ID!, $profile: DeliveryProfileInput!) {
  deliveryProfileUpdate(id: $id, profile: $profile) {
    profile { id name }
    userErrors { field message }   # NOTE: 'code' is NOT a field of UserError here
  }
}
""",
    "variables": {
        "id": "gid://shopify/DeliveryProfile/<PROFILE_ID>",
        "profile": {
            "locationGroupsToUpdate": [{
                "id": "gid://shopify/DeliveryLocationGroup/<LOCATION_GROUP_ID>",
                "zonesToUpdate": [{
                    "id": "gid://shopify/DeliveryZone/<ZONE_ID>",
                    "name": "Domestic",
                    "countries": [{"code": "IN", "includeAllProvinces": True}],
                }],
            }],
        },
    },
})
```

**Schema notes:**
- `code` is NOT a field of `UserError` returned by `deliveryProfileUpdate` (only on more specific subtypes). Including it returns `undefinedField`.
- The carrier-rate provider attached to the zone is preserved automatically — you don't need to re-attach MCSL after a country change.

### 3. Add a Market for the destination country

`marketCreate` mutation. This is what controls **presentment currency** for a buyer in that region.

```python
r = requests.post(GQL, headers=HDR, json={
    "query": """
mutation marketCreate($input: MarketCreateInput!) {
  marketCreate(input: $input) {
    market { id name handle enabled primary regions(first: 5) { nodes { ... on MarketRegionCountry { code name } } } }
    userErrors { field message }
  }
}
""",
    "variables": {
        "input": {
            "name": "India",
            "regions": [{"countryCode": "IN"}],
            "enabled": True,
        },
    },
})
```

**Important emergent behaviour**: once an India market exists, draft orders/carts with India shipping addresses **automatically use INR as presentment currency** even though `Shop.currency` is still USD. You do NOT need to change `Shop.currency` to get INR-priced rate quotes — the market handles it.

### 4. What CAN'T be done via API

Confirmed against the live Shopify Admin API on 2026-04:

| Setting | API-mutable? | Where to do it |
|---|---|---|
| `Shop.currency` (store-level default) | ❌ | Admin UI: Settings → Store details → Standards & formats |
| `Shop.weight_unit` (store-level default) | ❌ | Same |
| `Shop.country` (store-level) | ❌ | Same |
| Online Store sales channel activation | ❌ | Settings → Apps and sales channels → Add channel |
| Staff member creation | ❌ | Settings → Users → Add staff (Shopify owns the invitation email flow) |
| Partner collaborator request | ❌ via store API | Partner dashboard → Stores → Manage collaborators |

Note that for India-destined carts/orders, the Markets fallback (step 3) gives you INR pricing without needing to change `Shop.currency`.

---

## Triggering MCSL rate-shopping via `draftOrderCalculate`

This is the primary recipe — works on any dev store with MCSL installed and at least one shipping zone covering the destination.

```python
import json, requests

STORE = "<slug>"
V     = "2026-04"
TOKEN = "shpat_..."          # Admin API token with read_orders + write_draft_orders
GQL   = f"https://{STORE}.myshopify.com/admin/api/{V}/graphql.json"
HDR   = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

VARIANT = "gid://shopify/ProductVariant/<ID>"

ADDR = {
    "firstName": "QA", "lastName": "Tester",
    "address1": "Bandra West, Hill Road", "city": "Mumbai",
    "province": "Maharashtra", "provinceCode": "MH",
    "country": "India", "countryCode": "IN",
    "zip": "400050", "phone": "+919876543210",
}

r = requests.post(GQL, headers=HDR, json={
    "query": """
mutation calc($input: DraftOrderInput!) {
  draftOrderCalculate(input: $input) {
    calculatedDraftOrder {
      subtotalPriceSet { presentmentMoney { amount currencyCode } }
      totalShippingPriceSet { presentmentMoney { amount currencyCode } }
      totalPriceSet { presentmentMoney { amount currencyCode } }
      availableShippingRates {
        handle
        title
        price { amount currencyCode }
      }
    }
    userErrors { field message }
  }
}
""",
    "variables": {
        "input": {
            "lineItems": [{"variantId": VARIANT, "quantity": 1}],
            "shippingAddress": ADDR,
            "billingAddress":  ADDR,
            "email": "qa.test@pluginhive.com",
            "tags":  ["qa-test", "rate-check"],
        }
    }
})
```

**Verified result for IN→IN, 500g, ₹500 product** (test1121, 2026-06-08):

```
subtotal       : 500.0 INR
total shipping : 0.0 INR    (rates available, none auto-selected)
total          : 590.0 INR  (includes tax estimate)

availableShippingRates:
  - Business Parcel    41.0 INR     handle=eyJhbGciOiJ...
  - Speed Post         96.0 INR     handle=eyJhbGciOiJ...
```

**Schema notes:**
- `Money` is a scalar (string) — do NOT select `{ amount currencyCode }` on `shippingLine.price`. Use `MoneyV2` or `MoneyBag.presentmentMoney` for the nested form.
- Each `availableShippingRates.handle` is a JWT. Decoding the base64 payload reveals MCSL's full response per rate (title, code, source carrier, price, currency, ETA range, group_id):
  ```json
  {"title":"Business Parcel","code":"BUSINESS_PARCEL","source":"Multi Carrier Shipping Label","price":"41.0","currency":"INR","price_presentment":"41.0","currency_presentment":"INR","estimated_delivery_time_range":null,"group_id":null}
  ```
- Pass the handle as `shippingLine.handle` on `draftOrderUpdate` to lock in that rate before completing the draft into a real order.

### Verifying MCSL is attached to the destination zone

If `availableShippingRates` is empty or only contains static rates (no MCSL entries), MCSL isn't wired into the destination zone. Inspect with:

```graphql
{
  deliveryProfiles(first: 3) {
    nodes {
      name
      profileLocationGroups {
        locationGroupZones(first: 10) {
          nodes {
            zone { name countries { code { countryCode } } }
            methodDefinitions(first: 20) {
              nodes {
                name active
                rateProvider {
                  __typename
                  ... on DeliveryParticipant { carrierService { name } }
                  ... on DeliveryRateDefinition { price { amount currencyCode } }
                }
              }
            }
          }
        }
      }
    }
  }
}
```

Expected output for a healthy MCSL-attached zone:

```
zone 'Domestic' → ['IN']
  • carrier-rate provider: 'Multi Carrier Shipping Label' (active=True)
```

MCSL automatically registers its carrier service on install, so usually no follow-up is needed.

---

## Convert a rate quote into a real Order — `draftOrder*` chain

`draftOrderCalculate` is **preview-only** — it doesn't persist anything. To turn a rate quote into a real order that hits the admin Orders list (and gets picked up by MCSL for label generation), chain three mutations:

```
draftOrderCalculate  → get availableShippingRates with their JWT handles
                       (this is the call that fires MCSL)
        ↓
draftOrderCreate     → persists the draft, with shippingLine.shippingRateHandle
                       set to the handle of the rate you want
        ↓
draftOrderComplete   → converts the draft into a real Order with that exact
                       shipping line preserved
```

### Working code — verified IN→IN, Speed Post locked in (2026-06-08)

```python
import requests
STORE, V, TOKEN = "test1121-3x1v0ncz", "2026-04", "shpat_..."
GQL = f"https://{STORE}.myshopify.com/admin/api/{V}/graphql.json"
HDR = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

VARIANT = "gid://shopify/ProductVariant/53421255524717"
ADDR = {
    "firstName":"QA","lastName":"Tester","address1":"Bandra West, Hill Road",
    "city":"Mumbai","province":"Maharashtra","provinceCode":"MH",
    "country":"India","countryCode":"IN","zip":"400050","phone":"+919876543210",
}
DRAFT_INPUT = {
    "lineItems":       [{"variantId": VARIANT, "quantity": 1}],
    "shippingAddress": ADDR,
    "billingAddress":  ADDR,
    "email":           "qa.test@pluginhive.com",
    "tags":            ["qa-test", "speed-post"],
}

def gql(q, v=None):
    return requests.post(GQL, headers=HDR, json={"query": q, "variables": v or {}}).json()

# 1) Get rates from MCSL (no persistence yet)
calc = gql("""
mutation calc($input: DraftOrderInput!) {
  draftOrderCalculate(input: $input) {
    calculatedDraftOrder {
      availableShippingRates { handle title price { amount currencyCode } }
    }
    userErrors { field message }
  }
}
""", {"input": DRAFT_INPUT})
rates = calc["data"]["draftOrderCalculate"]["calculatedDraftOrder"]["availableShippingRates"]
# Pick the one you want — by title, by price, by code (decode the JWT handle), etc.
chosen = next(r for r in rates if r["title"] == "Speed Post")

# 2) Persist the draft with the chosen rate locked in
created = gql("""
mutation create($input: DraftOrderInput!) {
  draftOrderCreate(input: $input) {
    draftOrder {
      id name
      shippingLine { title originalPriceSet { presentmentMoney { amount currencyCode } } }
      totalPriceSet { presentmentMoney { amount currencyCode } }
    }
    userErrors { field message }
  }
}
""", {"input": {**DRAFT_INPUT, "shippingLine": {"shippingRateHandle": chosen["handle"]}}})
draft_id = created["data"]["draftOrderCreate"]["draftOrder"]["id"]

# 3) Complete the draft → real Order in admin
completed = gql("""
mutation complete($id: ID!, $paymentPending: Boolean) {
  draftOrderComplete(id: $id, paymentPending: $paymentPending) {
    draftOrder {
      order {
        id name
        displayFinancialStatus displayFulfillmentStatus
        shippingLine { title originalPriceSet { presentmentMoney { amount currencyCode } } }
        totalPriceSet { presentmentMoney { amount currencyCode } }
      }
    }
    userErrors { field message }
  }
}
""", {"id": draft_id, "paymentPending": True})
order = completed["data"]["draftOrderComplete"]["draftOrder"]["order"]
print(f"Order {order['name']} — {order['shippingLine']['title']} "
      f"@ {order['shippingLine']['originalPriceSet']['presentmentMoney']}")
```

### Verified output (test1121, IN→IN, 500g, ₹500 product)

```
rates from MCSL (step 1):
  • Business Parcel    41.0 INR
  • Speed Post         96.0 INR

draft created (step 2):
  #D1 status=OPEN
  shippingLine : Speed Post @ ₹96.00 INR
  total        : ₹686.00 INR  (500 + 96 + 90 tax)

order created (step 3):
  #1001  id=12218336837997
  financial_status  : PENDING
  fulfillment_status: UNFULFILLED
  shipping line     : Speed Post @ ₹96.00 INR    ← MCSL rate preserved
  total             : ₹686.00 INR
```

### Schema gotchas

| Mistake | Symptom | Fix |
|---|---|---|
| `availableShippingRates` on persisted `DraftOrder` | `undefinedField: Field 'availableShippingRates' doesn't exist on type 'DraftOrder'` | It lives on `CalculatedDraftOrder` only — call `draftOrderCalculate` for rates, not `draftOrderCreate`'s response. |
| `shippingLine: { handle: "..." }` on `DraftOrderInput` | `INVALID_VARIABLE: Field is not defined on ShippingLineInput` | The field is `shippingRateHandle`, not `handle`. |
| `paymentPending: false` on test stores | May fail without a configured payment gateway | Pass `paymentPending: true` to create the order in PENDING state for QA. |

### When to use this vs other order-creation paths

| | `orderCreate` + `BYPASS_STOCK` (skill G1) | `draftOrder*` chain (this section) |
|---|---|---|
| Triggers MCSL rate callback | ❌ skipped | ✅ on step 1 |
| Shipping line on the order | You supply it manually | Carries MCSL's actual rate response (incl. carrier code, ETA) |
| Inventory behavior | Bypassed by request option | Decrements unless you set `inventoryBehaviour: BYPASS` separately |
| Number of API calls | 1 | 3 |
| Use when | Quick order for label QA with a known shipping method | Full pipeline: rate-shop → pick → order → label |

---

## Build a carrier-env with products in UPS-canonical order

### Why ordering matters (more than you'd think)

The automation's packaging tests in [`tests/packagingTypes/*.spec.ts`]($MCSL_AUTOMATION_REPO_PATH/tests/packagingTypes) reference products **by index** into the env arrays, not by title. From [`createOrderAPI.ts:454-464`]($MCSL_AUTOMATION_REPO_PATH/support/pages/shopifyAPI/createOrderAPI.ts:454):

```typescript
// CASE 1 — quantities length == 1 → pick only N-th product
else if (req.quantities && req.quantities.length === 1) {
  const index = count - 1;
  if (productList[index]) {
    products = [{ ...productList[index], quantity: req.quantities[0] }];
  }
}
// CASE 2/3 — slice 0..count-1
```

So `{ productType: 'simple', productCount: 6, quantities: [2] }` resolves to `SIMPLE_PRODUCTS[5]` × qty 2. For tests like `weightAndVolume.spec.ts:123` (Test 2) to run identically against any new store, **`SIMPLE_PRODUCTS[5]` must point to the same logical product across every carrier-env**.

The canonical sequence lives in `carrier-envs/packaging-ups.env`. Building a new env in any other order (alphabetical, by-creation-time, by-product-id) silently breaks index-based tests.

### The reusable script

[scripts/build_carrier_env_ups_ordered.py](scripts/build_carrier_env_ups_ordered.py:1):

```bash
python3 scripts/build_carrier_env_ups_ordered.py \
    --target-store dhl-express-automation \
    --target-token shpat_xxxxxxxxxxxxxxxx \
    --carrier dhl-express-rest \
    --output $MCSL_AUTOMATION_REPO_PATH/carrier-envs/dhl-express-automation-rest.env
```

Algorithm:
1. Parse `packaging-ups.env` (or whatever `--source-env` points at) to extract the canonical `SIMPLE_PRODUCTS_JSON` / `VARIABLE_PRODUCTS_JSON` / `DIGITAL_PRODUCTS_JSON` arrays in order.
2. For each `(product_id, variant_id)` entry, hit the **source store** (`packaging-mcsl-automation`) to resolve it to `(product_title, (option1, option2, option3))`. This is the canonical sequence.
3. Fetch all products on the **target store**, index by title.
4. For each canonical entry: find the same title on target, pick the variant whose option triplet matches. Emit target's `{product_id, variant_id}`.
5. Write env with metadata inherited from the source env (`SLACK_WEBHOOK_URL`, `USER_PASSWORD`, etc.) unless `--user-email`, `--user-password`, etc. override.

Exit codes: `0` if every canonical entry matched. `3` if the env was written but some entries had no match on the target store — the failing rows print at the end with title and signature so you can investigate.

### Schema and source-data gotchas (each cost real debug time)

| Issue | Symptom | Fix |
|---|---|---|
| Source variant deleted, product still exists | Source lookup returns `sig=None`; can't match on target | Fallback: if source product is currently single-variant, treat as `("__default__",)`; otherwise emit unresolved. We hit this on UPS for `20 lb Prepacked Product`. |
| Single-variant Shopify products | `option1 == "Default Title"`, option2/3 = `None` | Treat as sentinel `("__default__",)` so it matches any single-variant product on target regardless of options |
| Typo in canonical env: `(product_id, variant_id)` pair where IDs don't belong together | Resolver reports the wrong product title for that slot; index-based tests pick the wrong product | One-line fix in the canonical env file. Verified live with UPS env where a copy-paste had `product_id: 9038078771426, variant_id: 47151713976546` — the variant actually belonged to product `9043250249954`. |
| Cross-classification (product is SIMPLE in spec, DIGITAL in canonical) | The script puts it in canonical's category, which may surprise | Faithful by design — index tests are written against canonical's classification, not the spec's |
| Multi-element `quantities` array | Test resolver hits CASE 2 (slice 0..count-1), NOT CASE 1 (only index N-1) | When reading test code, check `quantities.length`. Long `quantities` arrays mean the test exercises a *range* of indexes, not just one. |

### How to find which test uses which array index

```bash
cd $MCSL_AUTOMATION_REPO_PATH
# Tests that pick SIMPLE_PRODUCTS[5] specifically (CASE 1, single-element quantities):
grep -rn "productType:\s*['\"]simple['\"].*productCount:\s*6.*quantities:\s*\[[^,]*\]" \
  tests/packagingTypes/
```

Live example: for `SIMPLE_PRODUCTS[5]` we found exactly 3 callers — `weightAndVolume.spec.ts:123` (Test 2), `:292` (Test 5), `:511` (Test 8) — all using `{ productType: 'simple', productCount: 6, quantities: [2] }`.

### Verification after writing the env

```python
import json, re
env = open("carrier-envs/<new-store>.env").read()
simple = json.loads(re.search(r"SIMPLE_PRODUCTS_JSON='(\[.*?\])'", env).group(1))
print(f"SIMPLE_PRODUCTS[5] (used by Test 2/5/8 in weightAndVolume.spec.ts):")
print(f"  product_id  = {simple[5]['product_id']}")
print(f"  variant_id  = {simple[5]['variant_id']}")
```

Hit `GET /products/{product_id}.json` on the target store, confirm the title matches what UPS env's position-5 title resolves to (`WV _ Simple-1 _ 1 lb _23\`25\`20` as of the most recent UPS-env correction). If it doesn't, something drifted — re-run the script.

---

## The complete "create XXX carrier store" pipeline (with manual handoff)

When the request is *"create <X> carrier store and give me full env"* (or paraphrases like "set up YYY", "give me env for ZZZ"), run the AUTO phases end-to-end, then STOP for the carrier-registration handoff. **Do NOT auto-add product dimensions before the carrier is registered** — MCSL's dimension UI may not be reachable until a carrier is configured, and product seeding before carrier registration produces unusable env files.

### Phase map

```
AUTO phases (run end-to-end, no mid-way confirmation):
  1. create_store_and_install_app(store_name)     — store + QA app via Partner OAuth
  2. plan QA-Plan-3 + Approve charges             — inside step 1
  3. capture realized slug from post-install URL  — Shopify appends suffix
  4. create_dev_app_and_reveal_token(slug)        — admin scopes + storefront scopes + install + shpat_*
  4.5 marketCreate "International" (234 non-US)   — default; only deviate on explicit domestic override
       Write minimal env to carrier-envs/<slug>.env (empty product arrays)

HANDOFF (USER does this manually, in this order):
  a. Open <app_url> → fill onboarding form (Email/Phone/agree/Submit/Start)
  b. Register the carrier inside the MCSL app UI (no API for this)
  c. Tell me "done" / "carrier added"

POST-HANDOFF phases (run on confirmation):
  5. seed-packaging-store.ts                      — 22 products + L×W×H dimensions
  6. build_carrier_env_ups_ordered.py --country <ISO>
                                                   — rebuild env in UPS-canonical order
                                                     + country-aware SHIPPING_ADDRESS_JSON
                                                     + AI_ENABLED=false
  7. notify_qa_store_toggles_to_ashok.py          — place test order + capture accountUUID +
                                                    DM Ashok with substituted 41-toggle JSON

→ USER tells me when Ashok replies "done" in Slack (toggles enabled)

  8. run_smoke_sanity_for_carrier.sh              — auto-run @smoke then @sanity, restore .env
```

### Phase 6: the two extra env fields

Beyond the product arrays and token, every carrier-env includes two fields:

- **`SHIPPING_ADDRESS_JSON`** — country-aware default ship-to. From `pipeline.new_carrier_validation.default_shipping_address(country_code)`. Presets for `US`, `IN`, `AU`, `CA`, `GB`, `NZ`; unknown codes fall back to US. Pass `--country <ISO>` to `build_carrier_env_ups_ordered.py` (defaults to `US`). Single-key-dict array shape matching existing carrier-envs.
- **`AI_ENABLED=false`** — always emitted; every observed carrier-env uses `false`.

Defaults to `--country US` unless the user explicitly localised the store (see [[mcsl-store-defaults-no-auto-localisation]]). For India: `--country IN` → ship-to becomes Mumbai/Maharashtra. Add new country presets by editing `_DEFAULT_SHIPPING_ADDRESS` in `pipeline/new_carrier_validation.py`.

Example output (with `--country IN`):

```ini
SHIPPING_ADDRESS_JSON='[{"street":"221B Baker Street"},{"city":"Mumbai"},{"state":"Maharashtra"},{"countryCode":"IN"},{"zip":"400001"}]'
AI_ENABLED=false
```

### Phase 7: toggle enablement request (the final auto step)

The MCSL app has ~41 feature toggles that must be enabled per-store before QA can run the full suite. They're keyed by the store's `accountUUID`, which is only present in the MCSL `/orders` API response — so an order must exist before capture works.

```bash
PYTHONPATH=. .venv/bin/python scripts/notify_qa_store_toggles_to_ashok.py \
    --store-slug <realized-slug> \
    --carrier-env-path $MCSL_AUTOMATION_REPO_PATH/carrier-envs/<slug>.env
```

What it does internally:
1. **`pipeline.order_creator.create_order(carrier_env_path=...)`** — places one test order using the first product from `SIMPLE_PRODUCTS_JSON`.
2. **`pipeline.toggle_state.capture_store_and_toggle_state(app_url)`** — opens the MCSL app via Playwright, intercepts the `/orders` response, extracts `accountUUID` and `storeUUID`.
3. **Substitutes** `__ACCOUNT_UUID__` placeholders in [`templates/qa_store_toggles.json`](templates/qa_store_toggles.json:1) with the captured UUID. Produces a copy-pasteable JSON block keyed like `"<accountUUID>.tag.search.enabled": true,` for all 41 toggle entries.
4. **`pipeline.slack_client.search_slack_users("Ashok Kumar")` + `chat.postMessage`** — DMs Ashok with the substituted block inside a code fence and the message *"Hi Ashok, please enable these toggles for my new QA store <slug>. Account UUID: ..."*.

Toggle template structure (41 entries, mix of `true`, integers, strings, arrays):

```json
{
  "__ACCOUNT_UUID__.tag.search.enabled": true,
  "__ACCOUNT_UUID__.storepep.orders.pagesize": 100,
  "__ACCOUNT_UUID__.auto.order.update.status": ["INITIAL"],
  "__ACCOUNT_UUID__.order.maxQuantityInLineItem.enabled": 350,
  "__ACCOUNT_UUID__.shipping.method.search.enabled.after.store.createdAt.greater.than": "2025-09-30",
  ...
}
```

After substitution: `__ACCOUNT_UUID__` → e.g. `9362966b-a81b-418f-8c0a-0bd243d438bc` (the captured UUID).

Exit codes:
- `0` — DM sent
- `2` — accountUUID not captured (no orders exist, stale `auth-chrome.json`, or onboarding form not completed)
- `4` — Ashok not found in Slack search
- `6-7` — Slack API errors

Use `--dry-run` to print the substituted block without sending Slack, `--skip-order-create` if the store already has ≥1 order.

### Phase 8: auto-run @smoke + @sanity on Ashok's "done"

When the user signals that Ashok confirmed the toggle request (replies "done" / "Ashok confirmed" / "toggles enabled"), the pipeline kicks the final phase automatically:

```bash
bash scripts/run_smoke_sanity_for_carrier.sh \
    $MCSL_AUTOMATION_REPO_PATH/carrier-envs/<slug>.env
```

Internals:
1. Backs up `mcsl-test-automation/.env` to `.env.smoke-sanity-backup.$$`.
2. Copies the carrier-env file to `mcsl-test-automation/.env` so the dotenv-config in `playwright.config.ts` picks it up. The automation reads `process.env.*` set from this `.env`.
3. Runs `npx playwright test --grep @smoke --reporter=list`. Log: `/tmp/smoke_<carrier>.log`.
4. Runs `npx playwright test --grep @sanity --reporter=list`. Log: `/tmp/sanity_<carrier>.log`.
5. Restores the original `.env` via bash `trap EXIT INT TERM` — happens regardless of pass/fail.
6. Prints PASS/FAIL summary with exit codes.

Time budget: smoke ~5-10 min, sanity ~10-15 min, total ~20-30 min. Run in background. Tags are defined in the `test.describe(...)` blocks of `tests/**/*.spec.ts` (e.g. `{ tag: '@smoke' }`, `{ tag: '@sanity' }`).

### Why the handoff exists

- The QA app shows a **post-install onboarding form** (email/phone/agree/Submit) that blocks every other screen including the carrier-registration page. Until it's submitted, the app is unusable.
- **Carrier registration** (entering DHL/UPS/FedEx/India Post account credentials, license keys, etc.) is **admin-UI-only** in the MCSL app. Shopify exposes no API surface, and MCSL doesn't either.
- Setting product dimensions BEFORE a carrier is registered can navigate to a "configure a carrier first" wizard instead of the product list, breaking the dimension UI loop.

By the time the user says "carrier added", they've already completed the onboarding form (it was in their way) AND registered the carrier. The post-handoff phases can skip `maybeFillOnboarding` entirely — the seed script goes straight to the Menu navigation.

### Default Markets setup (phase 4.5)

Every new store gets two Markets unless explicitly overridden:

- `United States` (PRIMARY, regions=[US]) — Shopify auto-creates this with the store
- `International` (regions=[all 234 non-US ISO country codes]) — added via `marketCreate`

The deny-list of country codes Shopify doesn't accept for Markets: `US` (kept as primary), `ZZ` (rest-of-world placeholder), `AN` (Netherlands Antilles, dissolved), `BV` / `HM` (uninhabited islands), `AC` / `TA` (Saint Helena dependencies), and the four sanctioned: `CU`, `IR`, `KP`, `SY`. That leaves 234 valid non-US codes.

**Override**: if the user says *"create X carrier, domestic = India"* (or any non-US country), modify phase 4.5:
- Create that country as a market (or as the only Market, deleting US)
- `locationEdit` the primary location to that country (no `province` field on `LocationEditAddressInput`)
- `deliveryProfileUpdate` to set Domestic shipping zone to that country
- `Shop.currency` / `weight_unit` / `country` stay default — Markets handles presentment currency for buyer-facing pricing

### Onboarding form selectors (when the helper handles it before handoff)

Shopify shows the form right after Approve-charges in phase 1-2 too. The helper's `maybeFillOnboarding` attempts to clear it — works most runs but if it loses the race, the form persists for the user to clear during handoff.

Correct selectors (DOM uses `<input type="text">` NOT `type="email"`/`type="tel"`):

```
Email   : input[name="email"]         (or input[placeholder="john@gmail.com"])
Phone   : input[name="phoneNumber"]   (or input[placeholder="7567812342"])
Agree   : input[type="checkbox"]      (inside Material-UI label.jss3)
Submit  : starts disabled — poll submit.isDisabled() until false, then click
```

Submit values used by the helper: email `qa.test@pluginhive.com`, phone `1234567890`.

After Submit, wait for `Start` button → click → wait for `Menu` button as the readiness signal that onboarding is fully complete.

---

## Storefront API rate-shopping (when Online Store is active)

Mirrors the buyer-side flow exactly — the same path the storefront uses at checkout. Requires:

1. Online Store sales channel **activated** (admin UI only — without it, both `storefront_access_tokens.json` POST and any cart mutation return `Online Store channel is locked`).
2. A Storefront API public token — mint via `POST /admin/api/.../storefront_access_tokens.json` once the channel is active.

```python
# Step 1: cartCreate with line + India buyer identity
cart_create = """
mutation cartCreate($input: CartInput!) {
  cartCreate(input: $input) {
    cart { id checkoutUrl cost { totalAmount { amount currencyCode } } }
    userErrors { field message }
  }
}
"""
variables = {
    "input": {
        "lines": [{"merchandiseId": "gid://shopify/ProductVariant/<ID>", "quantity": 1}],
        "buyerIdentity": {
            "email": "qa.test@pluginhive.com",
            "countryCode": "IN",
            "deliveryAddressPreferences": [{
                "deliveryAddress": {
                    "firstName": "QA", "lastName": "Test",
                    "address1": "MG Road", "city": "Bengaluru",
                    "province": "Karnataka", "country": "India",
                    "zip": "560001", "phone": "+919876543210"
                }
            }]
        }
    }
}

# Step 2: deliveryGroups WITH carrier rates — this is what triggers MCSL
rates_query = """
query RatesWithCarriers($id: ID!) {
  cart(id: $id) {
    ... @defer(label: "carrier_rates") {
      deliveryGroups(first: 10, withCarrierRates: true) {
        nodes {
          deliveryOptions {
            handle
            title
            estimatedCost { amount currencyCode }
          }
        }
      }
    }
  }
}
"""
# Must accept multipart response for @defer
resp = requests.post(
    f"https://{STORE}.myshopify.com/api/{V}/graphql.json",
    headers={"X-Shopify-Storefront-Access-Token": SF_TOKEN,
             "Content-Type": "application/json",
             "Accept": "multipart/mixed; deferSpec=20220824"},
    json={"query": rates_query, "variables": {"id": cart_id}},
    stream=True,
)
```

**Trigger requirements:**
- `withCarrierRates: true` argument on `deliveryGroups` — without it, only static rates are returned.
- `@defer` directive is **mandatory** on this argument (Shopify hard-rejects it otherwise).
- A `buyerIdentity` with a `shippingAddress` (or `deliveryAddressPreferences`) must be set first — otherwise Shopify has no destination and returns static rates only.

**Required Storefront API scopes:**
- `unauthenticated_read_checkouts` — cart reads + `deliveryGroups`
- `unauthenticated_write_checkouts` — `cartCreate`, `cartBuyerIdentityUpdate`, line adds
- `unauthenticated_read_product_listings` — fetch the variant in the first place

---

## Cross-reference: which API does what

| Goal | API surface | Key call |
|---|---|---|
| Add product | Admin REST | `POST /products.json` |
| Add product (>100 variants) | Admin GraphQL | `productCreate` + `productVariantsBulkCreate` |
| Mint Storefront token | Admin REST | `POST /storefront_access_tokens.json` (needs Online Store channel) |
| Change ship-from origin | Admin GraphQL | `locationEdit` (REST is 406) |
| Change shipping zones | Admin GraphQL | `deliveryProfileUpdate` (REST is 406) |
| Add a Market | Admin GraphQL | `marketCreate` |
| Trigger rate-shopping (rates only) | Admin GraphQL | `draftOrderCalculate` ← recommended for QA |
| Trigger rate-shopping (mirroring buyer flow) | Storefront GraphQL | `cart.deliveryGroups(withCarrierRates: true) @defer` |
| Create order with known shipping | Admin GraphQL | `orderCreate(BYPASS_STOCK)` — but skips rate-shopping |
| Add staff member | ❌ NOT API-doable | Admin UI only |

---

## Known dev-store gotchas (verified on test1121-3x1v0ncz, 2026-06-08)

1. **REST shipping/location endpoints are 406** — use GraphQL.
2. **`Online Store channel is locked`** on freshly created dev stores — blocks Storefront API. Activate manually in admin.
3. **Default dev store country is the Partner's country** (US for PluginHive Internal). The location, the Domestic zone, and `Shop.country` all start as US — fix the first two via API, fix the third in admin UI.
4. **`carrier_services.json` `callback_url`** returns `None` for some dev apps — visibility depends on the scope set granted to your admin token. The carrier service is still active, the callback just isn't readable.
5. **Multiple shipping zones don't need re-attaching carrier providers** after a country change — the `carrier_shipping_rate_providers` list is preserved across `deliveryProfileUpdate`.
6. **Adding a Market makes presentment currency follow the market**, so even with `Shop.currency=USD`, an India market means India-destined draft orders calculate in INR. This is the cleanest way to get correct-currency rate quotes without touching `Shop.currency`.

---

## Related skill sections

See [skills/mcsl-shopify-store-actions/SKILL.md](skills/mcsl-shopify-store-actions/SKILL.md):

- **17b** — Create dev store + install QA app (Playwright)
- **17b.1** — Custom dev app + Admin API token reveal (Playwright)
- **17c** — Admin/Storefront scope catalogue + minimum-viable scope set
- **17d** — End-to-end onboarding pipeline
- **17e** — Configure store for QA (location, zones, markets) — _this doc's code in skill form_
- **17f** — Triggering MCSL rate-shopping via `draftOrderCalculate`
- **17g** — Storefront API rate path
