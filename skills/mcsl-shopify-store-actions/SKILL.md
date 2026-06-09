---
name: mcsl-shopify-store-actions
description: Use when the user wants to perform any Shopify Admin API action (REST or GraphQL) on any MCSL automation store — create/update/archive/delete products (simple, variable, up to 2048 variants via GraphQL), create/cancel/delete/update orders (preset, custom, draft, with BYPASS_STOCK so test orders never deduct inventory), create order+fulfillment+tracking in one call, bulk inventory update across variants, bulk cleanup by tag, update shipping address, manage customers, list fulfillments/carrier services/webhooks/metafields/collections/locations, create refunds, or set up a fresh dev store + install the MCSL QA-MultiCarrier Shipping Label app via Shopify Partner OAuth (Playwright) — all via natural language. Token comes from the MCSL automation .env (or carrier-envs/<carrier>.env) automatically; if store not found there, asks for a token.
---

# Shopify Store Actions (MCSL)

Use this skill when the user asks to do anything with any Shopify store via the Admin API for the MCSL Multi-Carrier Shipping Label app:

**Products**
- "create 3 products" / "create a variable product with 5 sizes × 5 colors × 5 fabrics"
- "create a product with 500 variants" (GraphQL — up to 2048)
- "list all products and give me the IDs"
- "delete the product called Red Shirt"
- "archive that product" / "set product status to draft"
- "update variant weight to 2.5kg" / "change the price of size M to ₹250"
- "change SKU of all variants to NEW-xxx" / "set barcode on Red Shirt to 012345"
- "allow backorders on this product" / "stop selling when out of stock"
- "mark this variant as digital / no shipping required"
- "update compare at price to ₹300" / "remove the strikethrough price"
- "bulk update all variants: set price to ₹199 and inventory policy to continue"
- "update product title / vendor / description / tags / SEO title"

**Orders**
- "create a test order" / "create order without touching inventory" (BYPASS_STOCK)
- "create an order for Ravi Kumar at MG Road Bengaluru"
- "create a draft order and complete it"
- "create an order already fulfilled with tracking number 12345678"
- "cancel order #1801" / "delete all qa-test tagged orders"
- "update the shipping address on order #1802"
- "list all unfulfilled orders" / "how many open orders are there?"
- "create an order on the India Post carrier-env" / "use the FedEx carrier env"

**Inventory**
- "set inventory of Red Shirt to 9999" / "add 50 stock to Red Shirt"
- "set all variants of this product to 500 qty in one call" (GraphQL bulk)

**Store & App Setup**
- "create a new dev store and install the MCSL QA app"
- "install our QA app on store X" / "install MCSL on this store"
- "set up a fresh store for new-carrier validation"
- "configure Admin API scopes for the custom app" / "what scopes does MCSL need?"
- "set up Storefront API scopes for rate-at-checkout testing"
- "verify the app token has the scopes we need" / "audit granted scopes"
- "onboard a new carrier end-to-end" / "install + token + seed + carrier-env in one go"
- "write a carrier-env file from this store and token"
- "trigger an MCSL rate request via API" / "verify MCSL responds with the right rates"
- "set up this dev store for India shipping" / "change ship-from to India"
- "add an India Market" / "add a new market to this store"
- "what's the difference between draftOrderCalculate and Storefront cart rates"
- "create an order with Speed Post rate from MCSL" / "lock in a specific MCSL rate on an order"
- "rate-shop then create an order via API" / "full draftOrder chain"
- "build a carrier-env in UPS-canonical order" / "prepare env with products in correct sequence"
- "which test uses SIMPLE_PRODUCTS[N]" / "where does the packaging test pick this variant"
- "create XXX carrier store and give me full env" / "set up YYY store" / "give me env for ZZZ" — triggers the complete 7-phase pipeline with handoff (section 17j)
- "check if MCSL app is registered as a carrier"
- "show fulfillments for order #1800"
- "list webhooks" / "get metafields on this product"
- "create a customer called Priya Sharma" / "find customer by email"
- "list all locations" / "list collections"
- "create a refund on order #1799"
- any action on a specific store: "do this on indiapoststore2"

---

## Store & Auth Resolution

### Logic (simple — 4 checks in order)

```
1. No store mentioned by user
   → use SHOPIFY_STORE_NAME + SHOPIFY_ACCESS_TOKEN from automation repo .env
   → no questions asked

2. User mentions a carrier by name (e.g. "india post", "blue dart", "fedex", "dhl")
   → use carrier-envs/<carrier>.env from the automation repo
   → that file may have its own SHOPIFY_STORE_NAME / SHOPIFY_ACCESS_TOKEN +
     seeded product JSONs (SIMPLE_PRODUCTS_JSON, VARIABLE_PRODUCTS_JSON,
     DIGITAL_PRODUCTS_JSON, DANGEROUS_PRODUCTS_JSON)

3. User mentions a store name
   → normalize it (strip .myshopify.com, lowercase, trim spaces)
   → check if it matches SHOPIFY_STORE_NAME in any carrier-env or the root .env
       match  → use the token from that file
       no match → STOP and say: "I need an access token for store X"

4. User provides an explicit token along with the store name
   → use exactly what they gave, skip env lookup
```

---

### Implementation

```python
import config, requests
from pathlib import Path

def _read_env_file(path: Path) -> dict:
    env = {}
    if path and path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip().strip("'\"")
    return env

# MCSL has ONE primary store (.env at the automation repo root)
# Plus optional per-carrier overrides under carrier-envs/<carrier>.env
_automation_root = Path((config.MCSL_AUTOMATION_REPO_PATH or "").strip())
_root_env        = _read_env_file(_automation_root / ".env")
_carrier_env_dir = _automation_root / "carrier-envs"

# Known carrier slugs we expect under carrier-envs/
_CARRIER_KEYWORDS = {
    "india post":   "indiapost",
    "indiapost":    "indiapost",
    "blue dart":    "blue-dart",
    "bluedart":     "blue-dart",
    "fedex":        "fedex-Rest",
    "dhl":          "dhl",
    "aramex":       "aramex",
    "australia post": "australia-post",
    "canada post":  "canada-post",
    "amazon":       "amazon",
    "apc":          "apc-postal-logistics",
    "easypost":     "easypost-usps",
    "usps":         "easypost-usps",
    "landmark":     "landmark-global",
}

def _normalize(name: str) -> str:
    return name.lower().strip().replace(".myshopify.com", "")

def _carrier_env_for(user_text: str) -> dict:
    """Return the carrier-env dict if the user mentioned a known carrier, else {}."""
    s = (user_text or "").lower()
    for kw, slug in _CARRIER_KEYWORDS.items():
        if kw in s:
            path = _carrier_env_dir / f"{slug}.env"
            if path.exists():
                return _read_env_file(path) | {"_source": str(path)}
    return {}

def resolve_store(user_store: str = "", user_token: str = "",
                  carrier_hint: str = "") -> tuple[str, str, str]:
    """
    Returns (STORE, ACCESS_TOKEN, API_VERSION) or raises with a clear message.

    user_store   : store name from the user's message (empty = not mentioned)
    user_token   : token explicitly provided by the user (empty = not provided)
    carrier_hint : carrier name from the user message ("india post", "fedex", ...)
                   pass "" if no carrier mentioned
    """
    api_version = _root_env.get("SHOPIFY_API_VERSION", "2023-01")

    # Case 1 — user gave explicit token
    if user_token:
        store = _normalize(user_store or _root_env.get("SHOPIFY_STORE_NAME", ""))
        return store, user_token, api_version

    # Case 2 — user mentioned a carrier → use its carrier-env
    carrier_env = _carrier_env_for(carrier_hint or user_store)
    if carrier_env:
        store = carrier_env.get("SHOPIFY_STORE_NAME", "").strip()
        token = carrier_env.get("SHOPIFY_ACCESS_TOKEN", "").strip()
        version = carrier_env.get("SHOPIFY_API_VERSION", api_version)
        if store and token:
            print(f"Using carrier env {carrier_env['_source']} → store: {store}")
            return _normalize(store), token, version

    # Case 3 — no specific store → root .env
    if not user_store:
        store = _root_env.get("SHOPIFY_STORE_NAME", "").strip()
        token = _root_env.get("SHOPIFY_ACCESS_TOKEN", "").strip()
        if not store or not token:
            raise ValueError(
                "SHOPIFY_STORE_NAME or SHOPIFY_ACCESS_TOKEN missing in "
                f"{_automation_root / '.env'}"
            )
        print(f"Using automation .env → store: {store}")
        return _normalize(store), token, api_version

    # Case 4 — user named a real store slug → search all carrier envs + root
    user_store_norm = _normalize(user_store)
    candidates = [(_root_env, str(_automation_root / ".env"))]
    if _carrier_env_dir.exists():
        for f in sorted(_carrier_env_dir.glob("*.env")):
            candidates.append((_read_env_file(f), str(f)))

    for env_dict, source in candidates:
        env_store = _normalize(env_dict.get("SHOPIFY_STORE_NAME", ""))
        env_token = env_dict.get("SHOPIFY_ACCESS_TOKEN", "").strip()
        if env_store and env_token and user_store_norm == env_store:
            version = env_dict.get("SHOPIFY_API_VERSION", api_version)
            print(f"Store '{user_store}' found in {source} — using its token.")
            return env_store, env_token, version

    raise ValueError(
        f"Store '{user_store}' is not in the automation .env or any carrier-env.\n"
        f"I need an access token for this store.\n"
        f"Please provide it: \"use store {user_store} with token shpat_xxx\""
    )
```

**Usage in every action:**
```python
try:
    STORE, ACCESS_TOKEN, API_VERSION = resolve_store(
        user_store="",     # from user message, or "" if not mentioned
        user_token="",     # from user message, or "" if not provided
        carrier_hint="",   # e.g. "india post" / "fedex" / "" if not mentioned
    )
except ValueError as e:
    print(e)
    # STOP — do not proceed without a valid token

BASE_URL = f"https://{STORE}.myshopify.com/admin/api/{API_VERSION}"
HEADERS  = {"X-Shopify-Access-Token": ACCESS_TOKEN, "Content-Type": "application/json"}
```

---

### Connection check — always run before the first API call

```python
resp = requests.get(f"{BASE_URL}/shop.json", headers=HEADERS)

if resp.status_code == 200:
    shop = resp.json()["shop"]
    print(f"Connected: {shop['name']} ({shop['myshopify_domain']})")

elif resp.status_code == 401:
    print(f"Token rejected on '{STORE}'.")
    print(f"The MCSL app may not be installed on this store, or the token may have been revoked.")
    print(f"Provide a valid token: \"use store {STORE} with token shpat_xxx\"")
    # STOP

elif resp.status_code == 404:
    print(f"Store '{STORE}' not found — check the store name.")
    # STOP
```

---

### What to say to the user in each case

| Situation | Message |
|---|---|
| No store mentioned | `Using automation .env → store: indiapoststore2` |
| User mentioned a carrier | `Using carrier env carrier-envs/blue-dart.env → store: <slug>` |
| Store slug named, found in root env | `Store 'indiapoststore2' found in automation .env — using its token.` |
| Store slug named, found in carrier env | `Store '<slug>' found in carrier-envs/<carrier>.env — using its token.` |
| Store named, NOT in any env | `Store 'xyz-store' is not in the automation .env or any carrier-env. I need an access token. Please provide it: "use store xyz-store with token shpat_xxx"` |
| Token provided explicitly | `Using store: xyz-store (token provided explicitly)` |
| Token rejected (401) | `Token rejected on 'xyz-store'. The MCSL app may not be installed on this store. Provide a valid token.` |

---

## GraphQL vs REST — When to Use Which

| Use REST when | Use GraphQL when |
|---|---|
| Simple list / get / delete | Creating test orders without touching inventory |
| Single product/order CRUD | Creating order + fulfillment + tracking in one call |
| Inventory set on one variant | Bulk inventory update across many variants/locations at once |
| Small variant counts | Creating products with 100–2048 variants |
| Quick scripts | You need structured per-field error reporting |

**GraphQL endpoint** — same auth header, different URL:
```python
GQL_URL = f"https://{STORE}.myshopify.com/admin/api/{API_VERSION}/graphql.json"

def gql(query: str, variables: dict = None) -> dict:
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    resp = requests.post(GQL_URL, headers=HEADERS, json=payload)
    resp.raise_for_status()
    data = resp.json()
    errors = data.get("errors") or []
    if errors:
        raise ValueError(f"GraphQL errors: {errors}")
    return data.get("data", {})
```

---

## GraphQL Actions

### G1. Create Order — BYPASS_STOCK (test orders, no inventory deducted)

**Most important for QA testing.** Creates real orders without decrementing product inventory — perfect for test runs that would otherwise drain your test store's stock.

```python
query = """
mutation orderCreate($order: OrderCreateOrderInput!, $options: OrderCreateOptionsInput) {
  orderCreate(order: $order, options: $options) {
    userErrors { field message }
    order {
      id
      name
      displayFinancialStatus
      lineItems(first: 10) {
        nodes { title quantity }
      }
    }
  }
}
"""

variables = {
    "order": {
        "lineItems": [
            {
                "variantId": "gid://shopify/ProductVariant/53565711483194",
                "quantity": 1
            }
        ],
        "customer": {
            "toUpsert": {
                "email": "qa.test@pluginhive.com",
                "firstName": "QA",
                "lastName": "Tester"
            }
        },
        "shippingAddress": {
            "firstName": "QA", "lastName": "Tester",
            "address1": "MG Road", "city": "Bengaluru",
            "provinceCode": "KA", "countryCode": "IN", "zip": "560001"
        },
        "financialStatus": "PAID",
        "tags": ["qa-test"],
    },
    "options": {
        "inventoryBehaviour": "BYPASS_STOCK",   # ← does NOT deduct inventory
        "sendReceipt": False,
        "sendFulfillmentReceipt": False,
    }
}

result      = gql(query, variables)
order       = result["orderCreate"]["order"]
user_errors = result["orderCreate"]["userErrors"]

if user_errors:
    print(f"Errors: {user_errors}")
else:
    print(f"Created {order['name']} (ID: {order['id']})")
```

**`inventoryBehaviour` options:**
| Value | Effect |
|---|---|
| `BYPASS_STOCK` | Order created, inventory NOT touched — best for QA test orders |
| `DECREMENT_STOCK` | Reduces available inventory (normal behaviour) |

**`customer.toUpsert`** — no need to pre-create the customer. If the email already exists it updates them; if not it creates them. One step.

---

### G2. Create Order with Fulfillment + Tracking (one mutation)

Creates the order AND marks it as fulfilled with a tracking number in a single call — useful when you need a "label generated" state without going through the browser:

```python
variables = {
    "order": {
        "lineItems": [{"variantId": "gid://shopify/ProductVariant/53565711483194", "quantity": 1}],
        "shippingAddress": {
            "firstName": "QA", "lastName": "Tester",
            "address1": "MG Road", "city": "Bengaluru",
            "provinceCode": "KA", "countryCode": "IN", "zip": "560001"
        },
        "financialStatus": "PAID",
        "fulfillment": {
            "locationId": "gid://shopify/Location/LOCATION_ID",
            "trackingCompany": "India Post",
            "trackingNumber": "EE123456789IN",
            "shipmentStatus": "DELIVERED",
            "notifyCustomer": False,
        },
        "tags": ["qa-test", "qa-fulfilled"],
    },
    "options": {
        "inventoryBehaviour": "BYPASS_STOCK",
        "sendReceipt": False,
        "sendFulfillmentReceipt": False,
    }
}
```

Get `locationId` first if you don't have it:
```python
# REST — quick way to get location IDs
resp = requests.get(f"{BASE_URL}/locations.json", headers=HEADERS)
loc_id     = resp.json()["locations"][0]["id"]
gql_loc_id = f"gid://shopify/Location/{loc_id}"
```

---

### G3. Create Product with Variants up to 2048

**GraphQL supports up to 2048 variants per product** — far beyond the REST limit. Use `productCreate` + `productVariantsBulkCreate` in two steps:

```python
import itertools

# Step 1 — create the product with options (no variants yet)
create_query = """
mutation productCreate($product: ProductCreateInput!) {
  productCreate(product: $product) {
    userErrors { field message }
    product {
      id
      title
      options { id name values }
    }
  }
}
"""

# Example: 8 sizes × 8 colors × 4 fabrics = 256 variants
sizes   = ["XS", "S", "M", "L", "XL", "XXL", "3XL", "4XL"]
colors  = ["Red", "Blue", "Green", "Black", "White", "Yellow", "Purple", "Orange"]
fabrics = ["Cotton", "Polyester", "Wool", "Linen"]

create_vars = {
    "product": {
        "title": "MCSL QA Multi-Variant Product",
        "status": "ACTIVE",
        "productOptions": [
            {"name": "Size",   "values": [{"name": v} for v in sizes]},
            {"name": "Color",  "values": [{"name": v} for v in colors]},
            {"name": "Fabric", "values": [{"name": v} for v in fabrics]},
        ]
    }
}

result     = gql(create_query, create_vars)
product    = result["productCreate"]["product"]
product_id = product["id"]

# Map option name → option ID (needed for bulk variant create)
option_map = {opt["name"]: opt["id"] for opt in product["options"]}

# Step 2 — bulk create all variant combinations
bulk_query = """
mutation productVariantsBulkCreate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
  productVariantsBulkCreate(productId: $productId, variants: $variants) {
    userErrors { field message }
    productVariants { id title price }
  }
}
"""

variants = [
    {
        "price": "150.00",
        "optionValues": [
            {"optionId": option_map["Size"],   "name": size},
            {"optionId": option_map["Color"],  "name": color},
            {"optionId": option_map["Fabric"], "name": fabric},
        ]
    }
    for size, color, fabric in itertools.product(sizes, colors, fabrics)
]

total = len(variants)
print(f"Creating {total} variants...")  # 256 in this example

# Shopify recommends batching in chunks of 100 for large counts
CHUNK   = 100
created = []
for i in range(0, total, CHUNK):
    chunk = variants[i:i+CHUNK]
    r     = gql(bulk_query, {"productId": product_id, "variants": chunk})
    created.extend(r["productVariantsBulkCreate"]["productVariants"])
    print(f"  Batch {i//CHUNK + 1}: {len(chunk)} variants created")

print(f"Done — product '{product['title']}' with {len(created)} variants")
```

**Variant limit comparison:**
| API | Confirmed limit |
|---|---|
| REST | 100 variants (hard limit in REST API 2024-04+) |
| GraphQL `productVariantsBulkCreate` | **2048 per product** (official Shopify limit) |

---

### G4. Bulk Inventory Update (multiple items + locations in one call)

Update inventory for many variants across many locations in a **single GraphQL mutation** — much faster than REST's one-at-a-time approach.

#### What quantity types can be updated

Shopify inventory has 8 quantity types. Not all are writable:

| Name | What it is | Writable? |
|---|---|---|
| `available` | Available for sale on storefront | ✅ Set directly |
| `on_hand` | Physical stock count | ✅ Set directly (also adjusts `available`) |
| `incoming` | Expected from purchase orders / transfers | ✅ Set directly |
| `safety_stock` | Minimum buffer stock level | ✅ Set directly |
| `damaged` | Damaged items set aside | ✅ Set directly |
| `quality_control` | Items in QC hold | ✅ Set directly |
| `committed` | Reserved for open (unfulfilled) orders | ❌ Read-only — calculated from open orders |
| `reserved` | Reserved for draft orders | ❌ Read-only — calculated from draft orders |

**Relationship:**
```
on_hand   = available + committed + reserved + damaged + quality_control
available = on_hand - committed - reserved - damaged - quality_control
```
→ Setting `available` directly is the safest for QA — it's exactly "how many can be sold right now."
→ Setting `on_hand` is for physical stock counts — it recalculates `available` automatically.

**Two mutations — set vs adjust:**

| Mutation | Effect | Use when |
|---|---|---|
| `inventorySetQuantities` | Sets **absolute** value | "set stock to 9999" |
| `inventoryAdjustQuantities` | Applies **relative delta** | "add 50 stock" / "remove 10" |

---

#### inventorySetQuantities — set absolute values (bulk)

```python
SET_QUERY = """
mutation inventorySetQuantities($input: InventorySetQuantitiesInput!) {
  inventorySetQuantities(input: $input) {
    userErrors { field message code }
    inventoryAdjustmentGroup {
      reason
      changes {
        name
        delta
        quantityAfterChange
        item { id }
        location { id name }
      }
    }
  }
}
"""

location_gid = "gid://shopify/Location/LOCATION_ID"

# name can be: "available" | "on_hand" | "incoming" | "safety_stock" | "damaged" | "quality_control"
variables = {
    "input": {
        "name": "available",              # ← which quantity type to set
        "reason": "correction",
        "referenceDocumentUri": "logistics://mcsl-qa-test-run",
        "ignoreCompareQuantity": True,    # skip compare-and-swap — just force-set
        "quantities": [
            {"inventoryItemId": "gid://shopify/InventoryItem/111", "locationId": location_gid, "quantity": 9999},
            {"inventoryItemId": "gid://shopify/InventoryItem/222", "locationId": location_gid, "quantity": 9999},
            # as many items as needed — all updated in ONE API call
        ]
    }
}

result  = gql(SET_QUERY, variables)
changes = result["inventorySetQuantities"]["inventoryAdjustmentGroup"]["changes"]
for c in changes:
    print(f"  {c['item']['id']} @ {c['location']['name']}: delta={c['delta']:+d} → {c['quantityAfterChange']}")
```

---

#### inventoryAdjustQuantities — apply relative delta (bulk)

```python
ADJUST_QUERY = """
mutation inventoryAdjustQuantities($input: InventoryAdjustQuantitiesInput!) {
  inventoryAdjustQuantities(input: $input) {
    userErrors { field message }
    inventoryAdjustmentGroup {
      reason
      changes { name delta quantityAfterChange item { id } location { name } }
    }
  }
}
"""

variables = {
    "input": {
        "name": "available",           # which quantity type to adjust
        "reason": "correction",
        "referenceDocumentUri": "logistics://mcsl-qa-delta-run",
        "changes": [
            {"inventoryItemId": "gid://shopify/InventoryItem/111", "locationId": location_gid, "delta": +50},
            {"inventoryItemId": "gid://shopify/InventoryItem/222", "locationId": location_gid, "delta": -10},
            # positive = add stock, negative = remove stock
        ]
    }
}

result = gql(ADJUST_QUERY, variables)
```

---

#### Helper — update ALL variants of a product in one call

```python
def bulk_set_product_inventory(product_id_rest: int, qty: int, name: str = "available"):
    """Set a specific inventory quantity type for ALL variants of a product at once."""

    # Get inventory_item_ids from REST
    resp     = requests.get(f"{BASE_URL}/products/{product_id_rest}/variants.json", headers=HEADERS)
    variants = [v for v in resp.json()["variants"] if v.get("inventory_management") == "shopify"]

    # Get default location
    loc_id  = requests.get(f"{BASE_URL}/locations.json", headers=HEADERS).json()["locations"][0]["id"]
    loc_gid = f"gid://shopify/Location/{loc_id}"

    quantities = [
        {
            "inventoryItemId": f"gid://shopify/InventoryItem/{v['inventory_item_id']}",
            "locationId": loc_gid,
            "quantity": qty,
        }
        for v in variants
    ]

    result = gql(SET_QUERY, {
        "input": {
            "name": name,
            "reason": "correction",
            "referenceDocumentUri": "logistics://mcsl-qa-bulk-set",
            "ignoreCompareQuantity": True,
            "quantities": quantities,
        }
    })
    user_errors = result["inventorySetQuantities"]["userErrors"]
    if user_errors:
        print(f"Errors: {user_errors}")
    else:
        print(f"Set '{name}' to {qty} for {len(quantities)} variants")

# Usage examples:
bulk_set_product_inventory(10322136203578, qty=9999)               # set available to 9999
bulk_set_product_inventory(10322136203578, qty=0, name="damaged")  # clear damaged stock
bulk_set_product_inventory(10322136203578, qty=50, name="incoming")# set expected incoming
```

---

#### User intent → name mapping

| User says | `name` to use |
|---|---|
| "set stock to X" / "set qty to X" / "make it X" | `available` |
| "set physical count to X" / "stock take" | `on_hand` |
| "expecting X units" / "incoming stock" | `incoming` |
| "X units are damaged" / "mark as damaged" | `damaged` |
| "put X in quality control" | `quality_control` |
| "set safety stock to X" / "minimum buffer" | `safety_stock` |
| "committed" / "reserved" (user asks to set these) | Tell user: these are read-only, calculated from orders |

---

## REST Actions

### 1. List Products

```python
import requests

resp     = requests.get(f"{BASE_URL}/products.json", headers=HEADERS, params={"limit": 250})
products = resp.json().get("products", [])
# Return: id, title, status, variants[].id, variants[].price for each
```

To filter by IDs:
```python
params = {"ids": "123,456,789", "limit": 250}
```

### 2. Create Product

```python
payload = {
    "product": {
        "title": "Test Product",
        "body_html": "<p>Test product for MCSL QA</p>",
        "vendor": STORE,
        "product_type": "Test",
        "status": "active",
        "published_scope": "global",
        "variants": [{
            "price": "100.00",
            "sku": "TEST-001",
            "weight": 1.5,
            "weight_unit": "kg",
            "grams": 1500,
            "requires_shipping": True,
            "inventory_management": None,
        }]
    }
}
resp    = requests.post(f"{BASE_URL}/products.json", headers=HEADERS, json=payload)
product = resp.json().get("product", {})
# Return: product id, variant id, title
```

For **dangerous goods** products (carriers that support DG: FedEx, DHL, India Post Speed Post DG, etc.) set appropriate title/type so the MCSL app can detect them.

### 3. List Orders

```python
params = {"limit": 50, "status": "any"}  # status: open | closed | cancelled | any
resp   = requests.get(f"{BASE_URL}/orders.json", headers=HEADERS, params=params)
orders = resp.json().get("orders", [])
# Return: id, name (#1234), fulfillment_status, financial_status, created_at, line_items[].title
```

Filter by fulfillment status:
```python
params = {"fulfillment_status": "unfulfilled", "limit": 50, "status": "open"}
```

Filter by IDs:
```python
params = {"ids": "111,222,333", "status": "any"}
```

### 4. Create Order (project helper)

Use `pipeline.order_creator.create_order` from the MCSL repo — it reads the per-carrier env and builds line items from `SIMPLE_PRODUCTS_JSON` / `DANGEROUS_PRODUCTS_JSON`:

```python
import sys
# self-locate: works from any clone
sys.path.insert(0, str(Path.home() / "Documents" / "MCSLDomainExpert"))  # or: $MCSL_REPO env var
from pipeline.order_creator import create_order, create_order_multi_package, get_carrier_env_for_code

# Single order via a specific carrier env
env_path  = get_carrier_env_for_code("blue-dart")   # or "indiapost", "fedex-Rest", etc.
order_name = create_order(carrier_env_path=env_path)
# Returns Shopify order name like "#3768"

# Use dangerous-goods products
order_name = create_order(carrier_env_path=env_path, use_dangerous_products=True)

# Multi-package order (so MCSL splits it)
order_name = create_order_multi_package(carrier_env_path=env_path, num_packages=3)
```

User keyword → carrier-env mapping:

| User says | Carrier env file |
|-----------|------------------|
| india post / indiapost / speed post | `carrier-envs/indiapost.env` (if present, else root .env) |
| blue dart / bluedart | `carrier-envs/blue-dart.env` |
| fedex | `carrier-envs/fedex-Rest.env` |
| dhl | `carrier-envs/dhl.env` |
| aramex | `carrier-envs/aramex.env` |
| australia post / aus post | `carrier-envs/australia-post.env` |
| canada post | `carrier-envs/canada-post.env` |
| amazon | `carrier-envs/amazon.env` |
| apc / apc postal | `carrier-envs/apc-postal-logistics.env` |
| easypost / usps | `carrier-envs/easypost-usps.env` |
| landmark | `carrier-envs/landmark-global.env` |

**Note:** Not every carrier-env file populates its own STORE/TOKEN — many carriers share the root automation store. Always fall back to the root `.env` if the carrier env lacks `SHOPIFY_STORE_NAME` / `SHOPIFY_ACCESS_TOKEN`.

### 5. Get a Single Product or Order

```python
# Product by ID
resp = requests.get(f"{BASE_URL}/products/{product_id}.json", headers=HEADERS)

# Order by ID
resp = requests.get(f"{BASE_URL}/orders/{order_id}.json", headers=HEADERS)
```

### 6. Delete Product by Name

Never require the user to provide an ID. If they give a name, search first:

```python
resp    = requests.get(f"{BASE_URL}/products.json", headers=HEADERS, params={"title": product_name, "limit": 10})
matches = resp.json().get("products", [])

if len(matches) == 0:
    print(f"No product found with name '{product_name}'")
elif len(matches) > 1:
    print(f"Found {len(matches)} products matching '{product_name}':")
    for p in matches:
        print(f"  - ID {p['id']} | {p['title']} | {p['status']}")
    print("Please confirm which one to delete (by ID).")
else:
    product = matches[0]
    resp    = requests.delete(f"{BASE_URL}/products/{product['id']}.json", headers=HEADERS)
    if resp.status_code == 200:
        print(f"Deleted: '{product['title']}' (ID {product['id']})")
    else:
        print(f"Delete failed: {resp.status_code} {resp.text}")
```

To delete by ID directly:
```python
resp = requests.delete(f"{BASE_URL}/products/{product_id}.json", headers=HEADERS)
```

---

### 7. Create Variable Product

A variable product has multiple **variants** defined by **options** (e.g. Size + Color). Each variant combination gets its own price, SKU, weight, and inventory.

#### Variant interpretation rule — READ THIS FIRST

| User says | What it means | How to handle |
|---|---|---|
| "variable product with 200 variants" | combination-style (axes × values) | Pick axes whose product ≈ 200 (e.g. Size×Color×Age = 5×5×8) |
| "variable product with 50 variants" | combination-style | Pick axes whose product ≈ 50 (e.g. Size×Color = 5×10) |
| "100 **unique/different/separate** variants" | 100 truly independent SKUs | Use single axis "Variant" with values 1…100 |

**Default = combo.** Any number the user gives is a target for a combination product.
Only use single-axis numbered variants when the user explicitly says "unique", "different", "separate", or "individual" variants.

**Shopify limits:**
- Max **3 option axes** per product
- REST API: max **100 variants** total → use GraphQL `productSet` for >100
- GraphQL supports up to 2048 variants

#### Choosing axes for a target count N

```
N ≤ 100  → use REST (2–3 axes)
N > 100  → use GraphQL productSet

Example targets:
  25  → Size(5) × Color(5)            = 25
  50  → Size(5) × Color(10)           = 50
  100 → Size(5) × Color(5) × Age(4)  = 100
  125 → Size(5) × Color(5) × Age(5)  = 125
  200 → Size(5) × Color(5) × Age(8)  = 200
```

When the user asks for many variants, generate them programmatically with `itertools.product` — never write them by hand.

**Strategy A — REST, ≤100 variants (2–3 axes)**

```python
import itertools, requests

sizes  = ["XS", "S", "M", "L", "XL"]
colors = ["Red", "Blue", "Green", "Black", "White"]
# total = 5 × 5 = 25 variants

combos   = list(itertools.product(sizes, colors))
variants = [
    {
        "option1": size, "option2": color,
        "price": "150.00",
        "sku": f"TV-{size}-{color[:3].upper()}",
        "grams": 500, "weight": 0.5, "weight_unit": "kg",
        "requires_shipping": True,
    }
    for size, color in combos
]

payload = {
    "product": {
        "title": "Test Variable",
        "vendor": STORE,
        "status": "active",
        "options": [
            {"name": "Size",  "values": sizes},
            {"name": "Color", "values": colors},
        ],
        "variants": variants,
        "tags": "qa-test",
    }
}
resp    = requests.post(f"{BASE_URL}/products.json", headers=HEADERS, json=payload)
product = resp.json().get("product", {})
print(f"Created '{product['title']}' with {len(product['variants'])} variants")
```

**Strategy B — GraphQL productSet, >100 variants (required for 101–2000)**

```python
import itertools, requests

SIZES  = ["XS", "S", "M", "L", "XL"]
COLORS = ["Red", "Blue", "Green", "Black", "White"]
AGES   = ["Kids", "Teen", "Adult", "Senior", "Youth"]
# 5 × 5 × 5 = 125 variants

GQL_URL = f"https://{STORE}.myshopify.com/admin/api/{API_VERSION}/graphql.json"

variants_input = [
    {
        "optionValues": [
            {"optionName": "Size",      "name": size},
            {"optionName": "Color",     "name": color},
            {"optionName": "Age Group", "name": age},
        ],
        "price": "150.00",
        "sku": f"TV-{size}-{color[:3].upper()}-{age[:3].upper()}",
        "inventoryItem": {
            "measurement": {"weight": {"value": 0.5, "unit": "KILOGRAMS"}},
            "requiresShipping": True,
        },
    }
    for size, color, age in itertools.product(SIZES, COLORS, AGES)
]

mutation = """
mutation CreateProduct($synchronous: Boolean!, $productSet: ProductSetInput!) {
  productSet(synchronous: $synchronous, input: $productSet) {
    product {
      id
      title
      variantsCount { count }
      options { name optionValues { name } }
      variants(first: 5) { nodes { id title sku price } }
    }
    userErrors { field message code }
  }
}
"""

variables = {
    "synchronous": True,
    "productSet": {
        "title": "Test Variable",
        "vendor": STORE,
        "productType": "Test",
        "status": "ACTIVE",
        "tags": ["qa-test"],
        # NOTE: field is "productOptions" in GraphQL ProductSetInput (NOT "options")
        "productOptions": [
            {"name": "Size",      "values": [{"name": v} for v in SIZES]},
            {"name": "Color",     "values": [{"name": v} for v in COLORS]},
            {"name": "Age Group", "values": [{"name": v} for v in AGES]},
        ],
        "variants": variants_input,
    }
}

resp   = requests.post(GQL_URL, headers=HEADERS, json={"query": mutation, "variables": variables})
result = resp.json()["data"]["productSet"]
if result["userErrors"]:
    print(result["userErrors"])
else:
    p             = result["product"]
    product_id    = int(p["id"].split("/")[-1])
    variant_count = p["variantsCount"]["count"]
    print(f"Created '{p['title']}' — ID {product_id} — {variant_count} variants")
    # Extract numeric variant ID for REST order creation:
    first_variant_id = int(p["variants"]["nodes"][0]["id"].split("/")[-1])
```

**Key GraphQL notes:**
- Use `productOptions` (not `options`) in `ProductSetInput` — Shopify 2024-04+
- `synchronous: true` waits for all variants before returning
- GID format → numeric: `int(gid.split("/")[-1])` — needed for REST order creation

**Strategy C — single axis (only when user explicitly asks for unique/separate variants)**

```python
count         = 100  # user explicitly said "100 unique variants"
option_values = [str(i) for i in range(1, count + 1)]
variants      = [
    {"option1": v, "price": "100.00", "sku": f"VAR-{v.zfill(3)}",
     "grams": 500, "weight": 0.5, "weight_unit": "kg", "requires_shipping": True}
    for v in option_values
]
payload = {
    "product": {
        "title": "Test Product",
        "vendor": STORE, "status": "active",
        "options": [{"name": "Variant", "values": option_values}],
        "variants": variants,
    }
}
# REST for ≤100, GraphQL productSet for >100
```

**Note:** Shopify only supports **up to 3 option axes**. If the user asks for 4 dimensions, combine two into one (e.g. "Color-Fabric" as a single combined option).

---

### 8. Create Custom Order

When the user specifies their own customer name, address, email, or product — build the order payload from what they provide. Fill in any missing fields with sensible defaults.

```python
address = {
    "first_name": "QA",    "last_name": "Tester",
    "address1":   "MG Road", "city": "Bengaluru",
    "province":   "Karnataka", "province_code": "KA",
    "zip":        "560001", "country": "India", "country_code": "IN",
    "phone":      "+919876543210"
}

payload = {
    "order": {
        "email":            "qa.tester@pluginhive.com",
        "financial_status": "paid",
        "customer":         {"first_name": "QA", "last_name": "Tester", "email": "qa.tester@pluginhive.com"},
        "billing_address":  address,
        "shipping_address": address,
        "line_items":       [{"variant_id": variant_id, "quantity": 1}],
        "send_receipt":     False,
        "send_fulfillment_receipt": False,
    }
}
resp  = requests.post(f"{BASE_URL}/orders.json", headers=HEADERS, json=payload)
order = resp.json().get("order", {})
```

Default domestic address: **Bengaluru, KA 560001, India**.
For international tests: pick the carrier's supported destination (UK / US / CA / AU — see [docs/MCSL_CARRIER_CAPABILITY_MATRIX.md](docs/MCSL_CARRIER_CAPABILITY_MATRIX.md:1)).

**Handling user input for custom orders:**
- If user names a product → search by title first, get variant_id, then create order
- If user doesn't specify quantity → default to 1
- If user doesn't specify email → generate: `qa.test+{timestamp}@pluginhive.com`

---

### 9. Update Inventory Quantity

When user says "set stock to 9999" or "update inventory of [product/variant]":

**Step 1 — find the variant's `inventory_item_id`:**
```python
resp              = requests.get(f"{BASE_URL}/products.json", headers=HEADERS, params={"title": product_name, "limit": 5})
product           = resp.json()["products"][0]
variant           = product["variants"][0]
inventory_item_id = variant["inventory_item_id"]
```

**Step 2 — find the location ID:**
```python
resp        = requests.get(f"{BASE_URL}/inventory_levels.json", headers=HEADERS,
                           params={"inventory_item_ids": inventory_item_id})
levels      = resp.json().get("inventory_levels", [])
location_id = levels[0]["location_id"] if levels else None

if not location_id:
    resp        = requests.get(f"{BASE_URL}/locations.json", headers=HEADERS)
    location_id = resp.json()["locations"][0]["id"]
```

**Step 3 — set the inventory quantity:**
```python
payload = {"location_id": location_id, "inventory_item_id": inventory_item_id, "available": 9999}
resp    = requests.post(f"{BASE_URL}/inventory_levels/set.json", headers=HEADERS, json=payload)
result  = resp.json().get("inventory_level", {})
print(f"Updated: variant {variant['id']} → {result.get('available')} units")
```

**If the product has multiple variants** (variable product), loop over all of them:
```python
for variant in product["variants"]:
    inventory_item_id = variant["inventory_item_id"]
    # repeat steps 2+3 for each variant
```

---

## 🔴 High Value — Order & Product Management

### 10. Cancel an Order

```python
resp  = requests.post(f"{BASE_URL}/orders/{order_id}/cancel.json",
                      headers=HEADERS, json={"reason": "other", "email": False})
order = resp.json().get("order", {})
print(f"Cancelled order {order.get('name')}")
```

If user gives order name (#1801) instead of ID, search first:
```python
resp     = requests.get(f"{BASE_URL}/orders.json", headers=HEADERS, params={"name": "#1801", "status": "any"})
order_id = resp.json()["orders"][0]["id"]
```

---

### 11. Delete a Test Order

```python
resp = requests.delete(f"{BASE_URL}/orders/{order_id}.json", headers=HEADERS)
if resp.status_code == 200:
    print(f"Deleted order {order_id}")
else:
    print(f"Cannot delete: {resp.status_code} — try cancelling first")
```

---

### 12. Update Order Shipping Address

```python
payload = {
    "order": {
        "shipping_address": {
            "first_name": "Jane", "last_name": "Doe",
            "address1": "Brigade Road", "city": "Bengaluru",
            "province": "Karnataka", "province_code": "KA",
            "zip": "560025", "country": "India", "country_code": "IN"
        }
    }
}
resp  = requests.put(f"{BASE_URL}/orders/{order_id}.json", headers=HEADERS, json=payload)
order = resp.json().get("order", {})
print(f"Updated shipping address on order {order.get('name')}")
```

---

### 13. Bulk Cancel / Delete Orders by Tag

Tag test orders as `qa-test` during creation, then bulk-clean them:

```python
resp   = requests.get(f"{BASE_URL}/orders.json", headers=HEADERS,
                      params={"tag": "qa-test", "status": "any", "limit": 250})
orders = resp.json().get("orders", [])
print(f"Found {len(orders)} orders tagged 'qa-test'")

for o in orders:
    oid = o["id"]
    if o.get("financial_status") not in ("refunded", "voided") and not o.get("cancelled_at"):
        requests.post(f"{BASE_URL}/orders/{oid}/cancel.json", headers=HEADERS, json={"email": False})
    requests.delete(f"{BASE_URL}/orders/{oid}.json", headers=HEADERS)
    print(f"  Cleaned up order {o['name']} (ID {oid})")
```

**Add `qa-test` tag when creating orders** so cleanup is easy:
```python
payload["order"]["tags"] = "qa-test"
```

---

### 14. Add / Update Tags on Orders or Products

```python
# Add tags to an order
resp = requests.put(f"{BASE_URL}/orders/{order_id}.json", headers=HEADERS,
                    json={"order": {"tags": "qa-test, mcsl-label-tested, sprint-42"}})

# Add tags to a product
resp = requests.put(f"{BASE_URL}/products/{product_id}.json", headers=HEADERS,
                    json={"product": {"tags": "qa-product, dangerous-goods"}})
```

---

### 15. Update Product — Any Field

Every writable product field via REST:

```python
payload = {
    "product": {
        # Identity
        "title":        "New Product Title",
        "vendor":       "PluginHive",
        "product_type": "Shipping Label Test",
        "body_html":    "<p>Updated description</p>",

        # Status
        "status":          "active",    # active | draft | archived
        "published_scope": "global",

        # Discoverability
        "tags": "qa-product, mcsl, dangerous-goods",

        # SEO
        "metafields_global_title_tag":       "SEO Title Here",
        "metafields_global_description_tag": "SEO description here",
    }
}
resp    = requests.put(f"{BASE_URL}/products/{product_id}.json", headers=HEADERS, json=payload)
product = resp.json().get("product", {})
print(f"Updated product: {product['title']} | status: {product['status']}")
```

Only send the fields you want to change — omitted fields are not touched.

**User intent → field mapping:**
| User says | Field |
|---|---|
| "rename product to X" | `title` |
| "change vendor to X" | `vendor` |
| "update description" | `body_html` |
| "add tags X, Y" | `tags` (replace entire tag string) |
| "archive / draft / activate" | `status` |
| "update SEO title" | `metafields_global_title_tag` |

---

### 15b. Update Product Variant — Any Field (single variant, REST)

Every writable variant field via REST PUT `/variants/{id}`:

```python
payload = {
    "variant": {
        # Pricing
        "price":            "250.00",
        "compare_at_price": "300.00",   # strikethrough/original price (null to remove)

        # Identity
        "sku":     "NEW-SKU-001",
        "barcode": "012345678901",

        # Shipping / MCSL
        "weight":           2.5,
        "weight_unit":      "kg",       # g | kg | oz | lb
        "grams":            2500,
        "requires_shipping": True,

        # Tax
        "taxable": True,

        # Inventory behaviour
        "inventory_management": "shopify",   # "shopify" | null (untracked)
        "inventory_policy":     "deny",      # "deny" (stop at 0) | "continue" (allow backorders)
    }
}
resp    = requests.put(f"{BASE_URL}/variants/{variant_id}.json", headers=HEADERS, json=payload)
variant = resp.json().get("variant", {})
print(f"Updated variant {variant_id}")
```

**User intent → field mapping:**
| User says | Field |
|---|---|
| "change SKU to X" | `sku` |
| "set price to X" | `price` |
| "set compare at price to X" | `compare_at_price` |
| "change weight to X kg/lb" | `weight` + `weight_unit` + `grams` |
| "allow backorders / overselling" | `inventory_policy: "continue"` |
| "stop selling when out of stock" | `inventory_policy: "deny"` |
| "mark as digital / no shipping" | `requires_shipping: False` |
| "stop tracking inventory" | `inventory_management: null` |

---

### 15c. Bulk Update Multiple Variants at Once (GraphQL)

Update any field on many variants in a **single API call** — no looping needed:

```python
BULK_UPDATE_QUERY = """
mutation productVariantsBulkUpdate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
  productVariantsBulkUpdate(productId: $productId, variants: $variants) {
    userErrors { field message }
    productVariants {
      id title price sku barcode weight weightUnit inventoryPolicy taxable requiresShipping
    }
  }
}
"""

resp     = requests.get(f"{BASE_URL}/products/{product_id}/variants.json", headers=HEADERS)
existing = resp.json()["variants"]

variants_input = []
for v in existing:
    variants_input.append({
        "id": f"gid://shopify/ProductVariant/{v['id']}",
        # Only include fields you want to change
        "price":            "199.00",
        "sku":              f"NEW-{v['sku']}",
        "inventoryPolicy":  "CONTINUE",   # GraphQL uses UPPERCASE: DENY | CONTINUE
        "taxable":          True,
        "requiresShipping": True,
    })

result  = gql(BULK_UPDATE_QUERY, {
    "productId": f"gid://shopify/Product/{product_id}",
    "variants":  variants_input,
})
updated = result["productVariantsBulkUpdate"]["productVariants"]
print(f"Updated {len(updated)} variants")
for v in updated:
    print(f"  {v['title']} → sku={v['sku']}, price={v['price']}, policy={v['inventoryPolicy']}")
```

**All updatable variant fields in GraphQL `ProductVariantsBulkInput`:**

| Field | Type | Notes |
|---|---|---|
| `id` | ID! | Required to identify which variant to update |
| `price` | String | e.g. `"199.00"` |
| `compareAtPrice` | String | Strikethrough price, null to remove |
| `sku` | String | Stock keeping unit |
| `barcode` | String | UPC / EAN / ISBN |
| `weight` | Float | Numeric weight value |
| `weightUnit` | WeightUnit | `GRAMS` \| `KILOGRAMS` \| `OUNCES` \| `POUNDS` |
| `requiresShipping` | Boolean | |
| `taxable` | Boolean | |
| `inventoryPolicy` | `DENY` \| `CONTINUE` | Backorder behaviour |
| `inventoryManagement` | `SHOPIFY` \| `NOT_MANAGED` | Whether Shopify tracks stock |
| `position` | Int | Sort order |
| `metafields` | Array | Add or update custom metadata |

---

### 16. Archive / Draft / Activate a Product

```python
# Archive
resp = requests.put(f"{BASE_URL}/products/{product_id}.json", headers=HEADERS,
                    json={"product": {"status": "archived"}})
# Draft
resp = requests.put(f"{BASE_URL}/products/{product_id}.json", headers=HEADERS,
                    json={"product": {"status": "draft"}})
# Active
resp = requests.put(f"{BASE_URL}/products/{product_id}.json", headers=HEADERS,
                    json={"product": {"status": "active"}})

print(f"Product status → {resp.json()['product']['status']}")
```

---

## 🟡 Setup & Validation

### 17. List Carrier Services

Confirms the PluginHive MCSL Multi-Carrier Shipping Label app is registered as a carrier on the store, and shows which carriers it advertises:

```python
resp     = requests.get(f"{BASE_URL}/carrier_services.json", headers=HEADERS)
carriers = resp.json().get("carrier_services", [])
for c in carriers:
    print(f"  - {c['name']} | active: {c['active']} | callback: {c['callback_url']}")
```

Expected: a PluginHive / MCSL entry with an active callback URL (typically pointing at `*.pluginhive.com` or `*.storepep.io`).

If no MCSL carrier appears, the app is not installed on this store → use **action 17b** below to install it.

---

### 17b. Create Dev Store & Install the MCSL QA App (Shopify Partner OAuth flow)

> **Why this can't be done over Admin API**: Shopify requires browser-based OAuth consent to install an app. We drive it via Playwright on the Shopify Partner dashboard (Partner ID `129786666`, app `QA-MultiCarrier Shipping Label`, `app_card_6038317`, Partner-side slug `mcsl-qa-4`, merchant-side slug `mcsl-qa`). The Python helper wraps a Node/Playwright script that reuses the automation repo's `auth-chrome.json` session.

**Use the project pipeline helper — it owns the locators, account-card handling, and plan/approval flow:**

```python
import sys
# self-locate: works from any clone
sys.path.insert(0, str(Path.home() / "Documents" / "MCSLDomainExpert"))  # or: $MCSL_REPO env var
from pipeline.new_carrier_onboarding import create_store_and_install_app

result = create_store_and_install_app(
    store_name="qa-validation-store-001",   # final store will be: <name>.myshopify.com
    plan_name="Advanced",                    # Advanced | Basic | etc.
    # Optional overrides — defaults already point at the right partner / app:
    # partner_stores_url="https://dev.shopify.com/dashboard/129786666/stores",
    # partner_apps_url  ="https://dev.shopify.com/dashboard/129786666/apps",
    # app_search_name   ="QA-MultiCarrier Shipping Label",
    # app_card_id       ="app_card_6038317",
    # app_slug          ="mcsl-qa",   # merchant-side URL slug (Partner-side is mcsl-qa-4)
    # timeout_seconds   =900,
)

print(f"Store created : {result.store_created}")
print(f"App installed : {result.app_installed}")
print(f"Store URL     : {result.shopify_url}")    # https://admin.shopify.com/store/<name>
print(f"App URL       : {result.app_url}")        # https://admin.shopify.com/store/<name>/apps/mcsl-qa
print(f"Duration      : {result.duration_seconds:.1f}s")
```

**What the helper does end-to-end (matches the automation TS in `tests/onboardingFlow/createStoreAndInstallApp.spec.ts`):**

1. Opens Shopify Partner dashboard with saved auth (`auth-chrome.json`).
2. Clicks **Add dev store** → fills the store name → picks the Shopify plan → creates store.
3. Resolves the **Choose an account** card using `USER_EMAIL` / `SHOPIFY_EMAIL` env vars.
4. Navigates to **Apps** → searches `QA-MultiCarrier Shipping Label` → opens `#app_card_6038317`.
5. Clicks **Install app**, then in the popup: searches the just-created store, selects it, clicks `#proceed_cta`.
6. Inside the `app-iframe`: clicks **Select Plan** → **Approve charges** (`#approve-charges-button`).
7. Fills the onboarding form (email + phone + privacy checkbox) → **Submit**.
8. Asserts the **Start** button appears and clicks it.
9. Confirms the **Best Shipping Options for…** heading is visible → app is fully onboarded.

**Required env vars** (already in the automation repo's `.env` / project `.env`):

| Var | Purpose |
|---|---|
| `MCSL_AUTOMATION_REPO_PATH` | Path to `mcsl-test-automation` repo (where `auth-chrome.json` lives) |
| `USER_EMAIL` / `SHOPIFY_EMAIL` | The Partner account email used in the **Choose an account** card |
| `MCSL_CHROME_AUTH_PATH` | _(optional)_ override for the storage state path (defaults to `<repo>/auth-chrome.json`) |

**Alternative — run the existing Playwright test directly** when you just want to repro the canonical flow:

```bash
cd $MCSL_AUTOMATION_REPO_PATH
npx playwright test tests/onboardingFlow/createStoreAndInstallApp.spec.ts --headed
```

This uses a `${Date.now()}DummyTestStore` name and the Advanced plan, then installs MCSL on the new store.

**Result structure** (`NewCarrierOnboardingResult` — see [pipeline/new_carrier_onboarding.py:22](pipeline/new_carrier_onboarding.py:22)):
```
store_name, store_created, app_installed, shopify_url, app_url,
stdout, stderr, returncode, started_at, finished_at, duration_seconds
```

**After install — what to say to the user:**
```
Created dev store: qa-validation-store-001.myshopify.com  ✓
Installed MCSL QA app                                     ✓
Plan approved, onboarding submitted, Start clicked
App URL: https://admin.shopify.com/store/qa-validation-store-001/apps/mcsl-qa
Next steps:
  - Run create_dev_app_and_reveal_token() to mint an Admin API token (17b.1)
  - Register the carrier(s) you want to validate inside the MCSL app (manual — Shopify cannot do this via API)
  - Then run pipeline.shopify_product_seed.create_seed_products(carrier_code=...) to populate the carrier-env product JSONs
```

**Important caveats:**
- The auth session in `auth-chrome.json` must be fresh — if it has expired, the helper will fail at the **Choose an account** card. Re-login the partner account via the automation repo's login flow first.
- App installation is **non-idempotent in the popup**: if the app is already installed on the store, the install link won't appear — handle by checking action 17 (List Carrier Services) for an existing MCSL carrier service before invoking the install flow.
- Plan approval triggers a real (test) charge in the Partner dev-store sandbox — fine for development stores, never run this on a live merchant store.

---

### 17b.1. Create Custom Dev App on the Same Store & Auto-Reveal the Admin Token

> **Why this exists separately from 17b**: the OAuth install in 17b hands the access token to PluginHive's MCSL backend, not to us. We can't pull that token back out. Instead we create a **second** app — a custom dev app — inside the merchant's admin (`Settings → Apps → Develop apps`), tick our scopes, install it (no OAuth redirect needed because it's merchant-internal), then scrape the one-shot `shpat_*` token from the API credentials tab. Two apps coexist on the store: the **QA app** (`QA-MultiCarrier Shipping Label`, installed in 17b) handles the carrier-service callback and UI, and the **dev-app token vehicle** (installed in 17b.1) provides the `shpat_*` token for the Admin API.

**Run it:**

```python
import sys
# self-locate: works from any clone
sys.path.insert(0, str(Path.home() / "Documents" / "MCSLDomainExpert"))  # or: $MCSL_REPO env var
from pipeline.new_carrier_onboarding import (
    create_dev_app_and_reveal_token,
    DEFAULT_ADMIN_SCOPES,        # the 26-scope MCSL set, see 17c
    DEFAULT_DEV_APP_NAME,        # "MCSL-Automation-Token"
)

result = create_dev_app_and_reveal_token(
    store_name="new-carrier-validation-001",
    app_name="MCSL-Automation-Token",         # any string; helps you find it later
    admin_scopes=DEFAULT_ADMIN_SCOPES,        # tuple of scope handles — see 17c "minimum viable"
    storefront_scopes=(),                     # pass () to skip Storefront entirely
    timeout_seconds=900,
)

print(f"app_created   : {result.app_created}")
print(f"app_installed : {result.app_installed}")
print(f"token_revealed: {result.token_revealed}")
print(f"app_id        : {result.app_id}")
print(f"admin_token   : {result.admin_token[:12]}…")
print(f"granted       : {len(result.granted_admin_scopes)} / requested {len(result.requested_admin_scopes)}")
print(f"missing       : {result.missing_admin_scopes}")
```

**What the Playwright script does end-to-end** (driven from [pipeline/new_carrier_onboarding.py](pipeline/new_carrier_onboarding.py:1)):

1. Opens `https://admin.shopify.com/store/<slug>/settings/apps/development` with saved auth (`auth-chrome.json`).
2. Handles the first-time "Allow custom app development" gate if it appears.
3. Clicks **Create an app** → fills the name → **Create app**.
4. Extracts the app id from the URL (`/apps/development/<id>/overview`).
5. Clicks **Configure Admin API scopes**, ticks each requested scope (tries multiple selectors per scope to survive admin redesigns), clicks **Save**.
6. _(Optional)_ Same for Storefront API scopes if any were requested.
7. Returns to overview → clicks **Install app** → confirms.
8. Navigates to the API credentials tab → clicks **Reveal token once** → scrapes the first `shpat_*` match from the DOM (falls back to a full-page regex if the targeted locator misses).
9. Returns a structured `DevAppTokenResult` with `admin_token`, `storefront_token`, `granted_admin_scopes`, `missing_admin_scopes`, `app_id`, timing, and raw stdout/stderr.

**Hand-off to the carrier-env writer:**

```python
from pipeline.new_carrier_validation import build_new_carrier_run, write_carrier_env_file, ShopifyProductRef

run = build_new_carrier_run(
    carrier_code="blue-dart",
    store_name=result.store_name,
    product_groups={"simple": [], "variable": [], "digital": [], "dangerous": []},  # fill from seeding
    shopify_access_token=result.admin_token,
    shopify_api_version="2026-04",
    shopify_url=f"https://admin.shopify.com/store/{result.store_name}",
    app_url=f"https://admin.shopify.com/store/{result.store_name}/apps/mcsl-qa",
)
env_path = write_carrier_env_file(run)
print(f"✓ Token persisted to {env_path}")
```

**One-shot token caveat — IMPORTANT:**
- The "Reveal token once" button shows the token exactly once per app install. If `result.token_revealed` is `True` but `result.admin_token` is empty (DOM scrape missed), **do not retry the same app** — the reveal is already burned. Either:
  1. Inspect `result.stdout` for the JSON payload (the token is there even if scraping failed in mid-flight), or
  2. Re-run `create_dev_app_and_reveal_token` with a **different** `app_name` to mint a fresh app.

**Scope-mismatch handling:**
- If `result.missing_admin_scopes` is non-empty, the script ticked some scopes but not others (likely because Shopify renamed a scope's DOM hook). The token has been issued for whatever subset was checked. You can either:
  1. Manually open `https://admin.shopify.com/store/<slug>/settings/apps/development/<app_id>/configuration`, finish ticking, save, **uninstall + reinstall** to get a fresh token with the full scope set; or
  2. Update the scope locator list in `_build_dev_app_script()` for the renamed handles and re-run.

**When not to use 17b.1:**
- The merchant has a corporate policy that forbids dev apps inside their store. In that case, fall back to the manual reveal in 17c.
- You only need read-only data from one or two endpoints — easier to use an existing Storefront public token.
- You're testing the QA app's own backend behaviour, not the Shopify Admin API — the QA app's token belongs to PluginHive and is not exposed via either flow.

---

### 17c. Configure Admin & Storefront API Scopes (Custom / Dev App)

> **When this applies**: Settings → Apps and sales channels → **Develop apps** → pick the app → **Configuration** → "Configure Admin API scopes" / "Configure Storefront API scopes". This is for **custom apps** the merchant creates inside their store (token format `shpat_*`), not the QA app (QA-MultiCarrier Shipping Label) installed via Partner OAuth (17b). Both flows ultimately yield an access token; the scopes you pick here determine which actions in this skill will succeed.

#### Quick rules
- **Scopes are evaluated at install time.** Changing scopes later requires the merchant to re-approve in admin. The token itself is **not rotatable** — to invalidate a leaked token, delete the app and create a new one.
- **Token formats**: Admin API → `shpat_*`. Storefront API (public) → `shpat_*` (different scope set) or Storefront public access token. Customer Account API → separate flow.
- **`granted_scopes` vs `requested_scopes`**: a token may receive fewer scopes than requested if the merchant denies some. Inspect via `GET /admin/oauth/access_scopes.json` after install.

---

#### Recommended Admin API scopes for the MCSL QA workflow

Map each scope to the actions in this skill that need it. Pick by which flows the app/QA run will exercise.

| Scope | Required for | Skill actions |
|---|---|---|
| `read_products`, `write_products` | Product CRUD, variant creation, variable products | 1, 2, 6, 7, 15, 15b, 15c, G3 |
| `read_orders`, `write_orders` | Order list/create/cancel/delete/update, tags, refunds | 3, 4, 8, 10, 11, 12, 13, 14, 28, G1, G2 |
| `read_all_orders` | Read orders **older than 60 days** (useful for regression cleanup) | 13, 20 |
| `read_draft_orders`, `write_draft_orders` | Draft-order → complete flow | 19 |
| `read_inventory`, `write_inventory` | Inventory set/adjust, BYPASS_STOCK reasoning, bulk updates | 9, 25, G4 |
| `read_locations` | Resolve `location_id` for inventory and fulfillment | 9, 18, 26, G2, G4 |
| `write_locations` | Only if QA changes location config (rare) | — |
| `read_fulfillments`, `write_fulfillments` | List fulfillments, create fulfillment service entries | 18, G2 |
| `read_assigned_fulfillment_orders`, `write_assigned_fulfillment_orders` | When MCSL is the fulfillment service for the order | (multi-package label flows) |
| `read_merchant_managed_fulfillment_orders`, `write_merchant_managed_fulfillment_orders` | When the merchant fulfills (default for MCSL test orders) | 18, G2 |
| `read_third_party_fulfillment_orders`, `write_third_party_fulfillment_orders` | When testing carrier services that own their own fulfillment | — |
| `read_shipping`, `write_shipping` | **Register the MCSL carrier service callback** | 17 (and the install flow itself) |
| `read_customers`, `write_customers` | `customer.toUpsert`, list/search, address updates | 8, 12, 23, 24, G1 |
| `read_files`, `write_files` | Storing/retrieving generated label PDFs | (automation pipeline) |
| `read_metaobjects`, `write_metaobjects` | MCSL stores carrier config + per-order shipping options here | 22 (extended) |
| `read_metaobject_definitions`, `write_metaobject_definitions` | First-time setup of MCSL metaobject schema | (carrier registration) |
| `read_returns`, `write_returns` | Return flows (often paired with refunds) | 28 |
| `read_discounts`, `read_price_rules` | When testing rate-at-checkout interaction with discounts | — |
| `read_locales`, `read_translations` | Multi-locale label / address validation | — |

**The "minimum viable" MCSL QA scope set** (covers everything in this skill except niche flows):
```
read_products, write_products,
read_orders, write_orders, read_all_orders,
read_draft_orders, write_draft_orders,
read_inventory, write_inventory,
read_locations,
read_fulfillments, write_fulfillments,
read_merchant_managed_fulfillment_orders, write_merchant_managed_fulfillment_orders,
read_assigned_fulfillment_orders, write_assigned_fulfillment_orders,
read_shipping, write_shipping,
read_customers, write_customers,
read_files, write_files,
read_metaobjects, write_metaobjects,
read_returns, write_returns
```

Verify scopes after install:
```python
resp = requests.get(f"https://{STORE}.myshopify.com/admin/oauth/access_scopes.json", headers=HEADERS)
granted = [s["handle"] for s in resp.json().get("access_scopes", [])]
print("Granted scopes:", granted)

# Fail fast if a required scope is missing
required = {"read_products", "write_orders", "write_shipping", "read_locations"}
missing  = required - set(granted)
if missing:
    print(f"❌ Missing required scopes: {missing}")
    print(f"   Reconfigure in: https://{STORE}.myshopify.com/admin/settings/apps/development")
```

---

#### Storefront API scopes — when and what

The Storefront API is **only needed if the QA app talks to the storefront the way a buyer would** (rate-at-checkout from the cart, headless integration testing, in-store-pickup widget validation). For pure Admin-API QA flows (this skill), you can skip the Storefront API entirely.

If you do enable Storefront access, here's what each scope unlocks for MCSL:

| Scope | What it unlocks |
|---|---|
| `unauthenticated_read_product_listings` | Read products & collections as a buyer (validate the same products that admin sees) |
| `unauthenticated_read_product_inventory` | Variant qty + product availability — for "shipping not offered when OOS" tests |
| `unauthenticated_read_product_pickup_locations` | `Location` + `StoreAvailability` — required for **in-store pickup** carrier flows |
| `unauthenticated_read_checkouts`, `unauthenticated_write_checkouts` | Drive cart → checkout → rates programmatically (headless rate-shopping tests) |
| `unauthenticated_read_selling_plans` | Subscription / prepaid plan products — test recurring-shipment carriers |
| `unauthenticated_read_customers`, `unauthenticated_write_customers` | Logged-in buyer carts (rarely needed for label QA) |
| `unauthenticated_read_metaobjects` | Read MCSL public metaobject config from the storefront side |
| `unauthenticated_read_content` | Articles/blogs — not relevant to shipping |

**Default Storefront set for MCSL rate-at-checkout testing:**
```
unauthenticated_read_product_listings,
unauthenticated_read_product_inventory,
unauthenticated_read_product_pickup_locations,
unauthenticated_read_checkouts, unauthenticated_write_checkouts,
unauthenticated_read_selling_plans
```

Storefront tokens come in two forms:
- **Public storefront access token** (created via Admin API or app config) — safe to embed in browser/mobile clients, rate-limited.
- **Private storefront access token** — server-side only, higher complexity limit.

Read with:
```python
resp = requests.post(
    f"https://{STORE}.myshopify.com/api/{API_VERSION}/graphql.json",
    headers={
        "X-Shopify-Storefront-Access-Token": STOREFRONT_TOKEN,
        "Content-Type": "application/json",
    },
    json={"query": "{ shop { name primaryDomain { url } } }"},
)
```

---

#### Customer Account API — usually not needed for MCSL

Only relevant if testing the **logged-in buyer's "My orders" view** of shipping/tracking. The scopes (`customer_read_orders`, `customer_read_customers`, etc.) live behind a separate auth flow and are not required for any action in this skill.

---

#### Token capture pattern after configuring scopes

**Preferred path (automated)** — use [17b.1](#17b1-create-custom-dev-app-on-the-same-store--auto-reveal-the-admin-token) which drives all five steps below in one Playwright run and returns the token in a structured `DevAppTokenResult`. Skip the manual steps unless 17b.1's locators have drifted from the current admin UI.

**Manual fallback** — for a dev app (the screen in the screenshot — `admin/settings/apps/development/.../overview`):
1. Click **Configure Admin API scopes** → tick everything from the "minimum viable" list above → Save.
2. (Optional) **Configure Storefront API scopes** → tick the rate-at-checkout set → Save.
3. Click **Install app** (top right) → grants the scopes.
4. Open **API credentials** tab → **Reveal token once** → copy `shpat_xxxxxxxx`.
5. Drop it into the right env file so this skill picks it up automatically:

```bash
# $MCSL_AUTOMATION_REPO_PATH/.env   (root, default store)
SHOPIFY_STORE_NAME=<store-slug>
SHOPIFY_ACCESS_TOKEN=shpat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SHOPIFY_API_VERSION=2026-04

# or, for a carrier-specific override:
# $MCSL_AUTOMATION_REPO_PATH/carrier-envs/<carrier>.env
SHOPIFY_STORE_NAME=<store-slug>
SHOPIFY_ACCESS_TOKEN=shpat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

After that, `resolve_store()` at the top of this skill picks it up with **zero prompts to the user**.

**Token can't be rotated** — if it leaks, the merchant must delete the dev app and create a fresh one (new client_id, new token). Plan for this in any QA pipeline that stores the token in CI secrets: build a rotation runbook, not a "just refresh it" assumption.

---

### 17d. End-to-End: Install → Token → Carrier-Env → Seed → Ready for Automation

The full new-carrier onboarding pipeline ties together helpers that already exist in this repo. **Shopify cannot register a carrier service inside the MCSL app via API** — that step stays manual. Everything around it is automatable.

#### The pipeline at a glance

```
1. create_store_and_install_app(store_name, ...)        ← QA app via Partner OAuth  [17b]
2. create_dev_app_and_reveal_token(store_name, ...)     ← dev-app token vehicle + shpat_*  [17b.1]
3. (manual)  register carrier inside MCSL app UI        ← cannot be done via API
4. create_seed_products(carrier_code, ...)              ← pipeline.shopify_product_seed
5. write_carrier_env_file(run)                          ← pipeline.new_carrier_validation
6. ready: run_order_creator / playwright suites
```

Step 1 installs the **QA app** (`QA-MultiCarrier Shipping Label`) so the carrier-service callback exists at checkout. Step 2 creates a **separate** custom dev app on the same store purely as a token vehicle — Shopify's OAuth install of the QA app returns the access token to PluginHive's backend (not to us), so we mint our own token via the dev app. Step 3 is the only manual step: the user opens the QA app's UI and enters the carrier's API credentials (Shopify has no API for this). Everything else is automated.

#### Reference implementation

```python
import sys
# self-locate: works from any clone
sys.path.insert(0, str(Path.home() / "Documents" / "MCSLDomainExpert"))  # or: $MCSL_REPO env var
import config
from pipeline.new_carrier_onboarding import create_store_and_install_app
from pipeline.shopify_product_seed   import create_seed_products
from pipeline.new_carrier_validation import (
    build_new_carrier_run, write_carrier_env_file, save_new_carrier_run,
    ShopifyProductRef,
)
from pipeline.order_creator import create_order, get_carrier_env_for_code

# ─── Step 1: install the MCSL QA app on a fresh dev store ────────────────────
onboarding = create_store_and_install_app(
    store_name="new-carrier-validation-001",
    plan_name="Advanced",
)
assert onboarding.store_created and onboarding.app_installed
print(f"Store ready: {onboarding.shopify_url}")
print(f"App ready  : {onboarding.app_url}")

# ─── Step 2: create a dev app on the same store and auto-reveal the token ────
# This drives the admin UI to create a custom dev app (token vehicle), tick the 26
# default scopes from 17c, install it, click "Reveal token once", and scrape
# the shpat_* value — all unattended. The token is one-shot: if anything
# fails after the reveal, you must create a fresh dev app, not retry.
from pipeline.new_carrier_onboarding import (
    create_dev_app_and_reveal_token, DEFAULT_ADMIN_SCOPES,
)

dev_app = create_dev_app_and_reveal_token(
    store_name=onboarding.store_name,
    app_name=f"MCSL-Automation-{onboarding.store_name}",
    admin_scopes=DEFAULT_ADMIN_SCOPES,         # the 26-scope MCSL set
    # storefront_scopes=(...)                  # optional, see 17c
)
assert dev_app.app_installed and dev_app.token_revealed, (
    "Dev-app install or token reveal failed — check dev_app.stderr"
)
if dev_app.missing_admin_scopes:
    raise RuntimeError(
        f"❌ Some scopes failed to tick: {dev_app.missing_admin_scopes}\n"
        f"   Open {onboarding.shopify_url}/admin/settings/apps/development/{dev_app.app_id} "
        f"→ Configure Admin API scopes → tick the missing ones → Save → reinstall."
    )
shopify_access_token = dev_app.admin_token
storefront_token     = dev_app.storefront_token   # "" if not configured
store_slug           = onboarding.store_name
print(f"✓ Token captured: {shopify_access_token[:12]}…  ({len(dev_app.granted_admin_scopes)} scopes)")

# ─── Step 3: STOP — user must register the carrier inside the MCSL app ───────
# Shopify has no API for "register carrier X in MCSL's settings page".
# The user opens the app URL, picks the carrier (e.g. "Blue Dart"), enters
# carrier API credentials (account number, license key, etc.), saves.
print(
    "🛑 Open the MCSL app and register the carrier you want to validate:\n"
    f"   {onboarding.app_url}\n"
    "   When done, type the carrier code (e.g. 'blue-dart', 'fedex-Rest', 'indiapost')."
)
carrier_code = input("Carrier code: ").strip()

# ─── Step 4: seed deterministic products for this carrier ────────────────────
# create_seed_products picks the right SIMPLE/VARIABLE/DIGITAL/DANGEROUS
# templates for the carrier (e.g. dangerous-goods only for carriers that support DG).
seeded = create_seed_products(
    carrier_code=carrier_code,
    store_name=store_slug,
    shopify_access_token=shopify_access_token,
    shopify_api_version="2026-04",
)
print(f"✓ Seeded {len(seeded.products)} products on {store_slug}")

# Group the seeded products by template type into ShopifyProductRef lists
product_groups = {
    "simple":    [ShopifyProductRef(product_id=p.product_id, variant_id=p.variant_id)
                  for p in seeded.products if p.group == "simple"],
    "variable":  [ShopifyProductRef(product_id=p.product_id, variant_id=p.variant_id)
                  for p in seeded.products if p.group == "variable"],
    "digital":   [ShopifyProductRef(product_id=p.product_id, variant_id=p.variant_id)
                  for p in seeded.products if p.group == "digital"],
    "dangerous": [ShopifyProductRef(product_id=p.product_id, variant_id=p.variant_id)
                  for p in seeded.products if p.group == "dangerous"],
}

# ─── Step 5: write the carrier-env file the automation reads ─────────────────
run = build_new_carrier_run(
    carrier_code=carrier_code,
    store_name=store_slug,
    product_groups=product_groups,
    store_created=onboarding.store_created,
    app_installed=onboarding.app_installed,
    shopify_url=onboarding.shopify_url,
    app_url=onboarding.app_url,
    user_email=config.USER_EMAIL if hasattr(config, "USER_EMAIL") else "",
    shopify_access_token=shopify_access_token,
    shopify_api_version="2026-04",
    registration_done=True,    # set by step 3
)
env_path = write_carrier_env_file(run)
save_new_carrier_run(run)
print(f"✓ Carrier env written: {env_path}")
# → $MCSL_AUTOMATION_REPO_PATH/carrier-envs/<carrier-slug>.env

# ─── Step 6: smoke-test by creating one order through the new env ────────────
order_name = create_order(carrier_env_path=env_path)
print(f"✓ Smoke test order: {order_name}  ← MCSL should now generate a label")
```

#### What ends up in the carrier-env file

`write_carrier_env_file` produces exactly the format the automation expects ([see existing carrier-envs/*.env]($MCSL_AUTOMATION_REPO_PATH/carrier-envs)):

```ini
CARRIER=blue-dart
SLACK_WEBHOOK_URL=
PARTNER_URL=
SHOPIFYURL=https://admin.shopify.com/store/new-carrier-validation-001
APPURL=https://admin.shopify.com/store/new-carrier-validation-001/apps/mcsl-qa
USER_EMAIL=madan@pluginhive.com
USER_PASSWORD=
STORE_PASSWORD=
SHOPIFY_API_VERSION=2026-04
SHOPIFY_STORE_NAME=new-carrier-validation-001
SHOPIFY_ACCESS_TOKEN=shpat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SIMPLE_PRODUCTS_JSON='[{"product_id":...,"variant_id":...}, ...]'
VARIABLE_PRODUCTS_JSON='[...]'
DIGITAL_PRODUCTS_JSON='[...]'
DANGEROUS_PRODUCTS_JSON='[...]'
```

After this file lands in `carrier-envs/<carrier>.env`, every action in this skill that takes `carrier_hint="<carrier name>"` will automatically resolve to **this** store + token + seeded products — no further prompts.

#### Natural-language → which helper to call

When the user talks to Claude (not the dashboard), pick the smallest subset of helpers that satisfies the request. The full 6-step pipeline is the **default for "onboard a new carrier"**, not a mandatory sequence.

| What the user says | Call only | Notes |
|---|---|---|
| "create a dev store called `foo`" | `create_store_and_install_app(store_name="foo")` | Installs the QA app too — it's part of the same Playwright run. If you really want store-only, skip this helper and use the Partner dashboard manually. |
| "store `foo` already exists, just create the dev app and give me the access token" | `create_dev_app_and_reveal_token(store_name="foo", admin_scopes=DEFAULT_ADMIN_SCOPES)` | No store creation, no MCSL install, no seeding, no env file. Returns the `shpat_*` token inline. |
| "give me a token with only `read_products` and `read_orders` on store `foo`" | `create_dev_app_and_reveal_token(store_name="foo", admin_scopes=("read_products", "read_orders"))` | Tighter scope set. `result.granted_admin_scopes` tells you what actually stuck. |
| "build the carrier-env contents for me but **don't write any file**" | `pipeline.new_carrier_validation.build_carrier_env_content(run)` | Returns the env file as a **string**. Print it to chat, never touches disk. Use this when the user wants to inspect/edit before persisting, or wants to paste it somewhere else (e.g. CI secret manager). |
| "now write that env to disk under `carrier-envs/blue-dart.env`" | `write_carrier_env_file(run)` | Persists to `<automation>/carrier-envs/<carrier-slug>.env`. Pass `overwrite=False` to refuse to clobber. |
| "rotate the token on store `foo`" | `create_dev_app_and_reveal_token(store_name="foo", app_name="MCSL-Automation-<date>")` then `write_carrier_env_file(run)` | Different `app_name` → new dev app → new token. Old app keeps working until you uninstall it. |
| "seed products for blue-dart on store `foo`" | `pipeline.shopify_product_seed.create_seed_products(carrier_code="blue-dart", store_name="foo", shopify_access_token=...)` | Standalone — no store/app/env handling. |
| "create one test order on the india-post carrier-env" | `pipeline.order_creator.create_order(carrier_env_path=get_carrier_env_for_code("indiapost"))` | Uses the env that's already on disk. |
| "show me the env you would write but don't save" | `print(build_carrier_env_content(run))` | Same as the third row — the "give me env here" pattern. |

**Two principles for routing:**
1. **Each helper is independent.** Calling step 4 doesn't require steps 1–3 to have happened in this session — only that their outputs (store slug + token + product IDs) exist.
2. **Treat the disk-write as opt-in.** If the user's wording leaves it ambiguous ("set up env for me" vs. "give me the env"), prefer `build_carrier_env_content` and ask before writing. The function names are intentionally split for this reason.

#### When parts of the pipeline get skipped

| Situation | Skip which step | Why |
|---|---|---|
| Reusing an existing dev store | 1 | Pass `store_name` of an existing store to step 2 onward |
| App already installed on that store | 1 (install half) | Check `List Carrier Services` (action 17) for MCSL entry first |
| Carrier already registered | 3 | Look at `data/new_carrier_runs/*.json` — `registration_done: true` |
| Products already seeded for this carrier | 4 | Load `data/new_carrier_runs/*.json` and reuse `product_groups` |
| Token rotation | 2 only | Run `write_carrier_env_file` with the new token; everything else unchanged |

#### Failure modes & what to do

| Failure | Likely cause | Fix |
|---|---|---|
| `create_store_and_install_app` times out at "Choose an account" | `auth-chrome.json` expired | Re-login the Partner account in `mcsl-test-automation`, regenerate `auth-chrome.json` |
| 401 on first Admin API call | Token missing scopes | Re-check granted scopes (step 2); reconfigure dev app, reinstall, get new token |
| `create_seed_products` 422 on dangerous-goods variant | Carrier doesn't support DG | `_seed_specs(carrier_code)` returns no DG entries; `DANGEROUS_PRODUCTS_JSON` stays `[]` — fine |
| Smoke order created but no label appears in MCSL | Carrier not registered in app, or registration is for the wrong account | Step 3 — open `app_url`, complete carrier registration UI |
| `write_carrier_env_file` overwrites an env you wanted to keep | Default `overwrite=True` | Pass `overwrite=False`; raises `FileExistsError` if the file is already there |

---

### 17e. Configure a Dev Store for Localised QA (Location · Zones · Markets)

> **When to use**: after `17b` + `17b.1` you have a working store and token, but the store inherits the Partner's country (usually US). Use this section to point the store at a different country — verified end-to-end for India on 2026-06-08. See [docs/MCSL_SHOPIFY_API_RATE_SHOPPING.md](docs/MCSL_SHOPIFY_API_RATE_SHOPPING.md:1) for the full deep-dive.

**API-doable from this skill:**
1. `locationEdit` GraphQL — change primary location to the target country (REST `/locations/{id}.json` PUT returns 406 on 2026-04, deprecated).
2. `deliveryProfileUpdate` GraphQL — change which countries the Domestic zone covers (REST `/shipping_zones/{id}.json` PUT also 406).
3. `marketCreate` GraphQL — add a Market so presentment currency follows the destination.

**Admin-UI-only (Shopify intentionally doesn't expose these):**
- `Shop.currency` (store default — but **Markets override this for buyer-facing pricing**, so you don't usually need to change it)
- `Shop.weight_unit`
- `Shop.country`
- Online Store sales channel activation

#### Working code — switch test store to India

```python
import requests

STORE, V, TOKEN = "<slug>", "2026-04", "shpat_..."
GQL = f"https://{STORE}.myshopify.com/admin/api/{V}/graphql.json"
HDR = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

def gql(q, v=None):
    return requests.post(GQL, headers=HDR, json={"query": q, "variables": v or {}}).json()

# 1) Find primary location id
locs = gql("{ locations(first:5) { nodes { id name } } }")
loc_id = locs["data"]["locations"]["nodes"][0]["id"]

# 2) Update primary location address (no `province` field on LocationEditAddressInput!)
gql("""
mutation locEdit($id: ID!, $input: LocationEditInput!) {
  locationEdit(id: $id, input: $input) {
    location { id address { city zip countryCode } }
    userErrors { field message }
  }
}
""", {"id": loc_id, "input": {
    "name": "Bengaluru Warehouse",
    "address": {
        "address1": "MG Road", "city": "Bengaluru",
        "countryCode": "IN", "zip": "560001", "phone": "+919876543210",
    },
}})

# 3) Find the default delivery profile + Domestic zone IDs
profile_data = gql("""
{
  deliveryProfiles(first: 3) {
    nodes {
      id default
      profileLocationGroups {
        locationGroup { id }
        locationGroupZones(first: 10) {
          nodes { zone { id name countries { code { countryCode } } } }
        }
      }
    }
  }
}
""")
prof  = next(p for p in profile_data["data"]["deliveryProfiles"]["nodes"] if p["default"])
plg   = prof["profileLocationGroups"][0]
zone  = next(z["zone"] for z in plg["locationGroupZones"]["nodes"] if z["zone"]["name"] == "Domestic")

# 4) Update Domestic zone → countries = [IN]
gql("""
mutation profUpdate($id: ID!, $profile: DeliveryProfileInput!) {
  deliveryProfileUpdate(id: $id, profile: $profile) {
    profile { id name }
    userErrors { field message }   # NOTE: no `code` field on UserError here
  }
}
""", {
    "id": prof["id"],
    "profile": {
        "locationGroupsToUpdate": [{
            "id": plg["locationGroup"]["id"],
            "zonesToUpdate": [{
                "id": zone["id"],
                "name": "Domestic",
                "countries": [{"code": "IN", "includeAllProvinces": True}],
            }],
        }],
    },
})

# 5) Add an India Market — makes presentment currency INR for India-destined carts
gql("""
mutation marketCreate($input: MarketCreateInput!) {
  marketCreate(input: $input) {
    market { id name handle regions(first: 3) { nodes { ... on MarketRegionCountry { code } } } }
    userErrors { field message }
  }
}
""", {"input": {"name": "India", "regions": [{"countryCode": "IN"}], "enabled": True}})
```

**Schema gotchas (these will save you 20 minutes of debugging):**
- `LocationEditAddressInput` has NO `province` field. Pass `address1`/`city`/`countryCode`/`zip`/`phone` only.
- `deliveryProfileUpdate.userErrors` is the BASE `UserError` type — no `code` field. Including it returns `undefinedField`. The more-specific subtypes do have `code`, but they're not what's returned here.
- `carrier_shipping_rate_providers` on the zone is **preserved** across `deliveryProfileUpdate` — MCSL stays attached when you change the country list.

---

### 17f. Trigger MCSL Rate-Shopping via Admin API `draftOrderCalculate`

> **Why this matters**: this is the fastest way to verify MCSL's carrier-service callback is responding correctly. No buyer flow, no checkout, no Online Store channel required. One mutation, one network round-trip, real rates from MCSL.

#### Working code — verified on test1121, IN→IN, 2026-06-08

```python
import requests, json
STORE, V, TOKEN = "<slug>", "2026-04", "shpat_..."
GQL = f"https://{STORE}.myshopify.com/admin/api/{V}/graphql.json"
HDR = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

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
      subtotalPriceSet      { presentmentMoney { amount currencyCode } }
      totalShippingPriceSet { presentmentMoney { amount currencyCode } }
      totalPriceSet         { presentmentMoney { amount currencyCode } }
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
            "lineItems": [{"variantId": "gid://shopify/ProductVariant/<ID>", "quantity": 1}],
            "shippingAddress": ADDR,
            "billingAddress":  ADDR,
            "email": "qa.test@pluginhive.com",
            "tags":  ["qa-test", "rate-check-in-in"],
        }
    },
})
data = r.json()["data"]["draftOrderCalculate"]["calculatedDraftOrder"]
for rt in data["availableShippingRates"]:
    p = rt["price"]
    print(f"  • {rt['title']:30s}  {p['amount']} {p['currencyCode']}")
```

**Expected output** (IN→IN, 500g, ₹500 product, MCSL with India Post configured):

```
subtotal       : 500.0 INR
total shipping : 0.0 INR        (rates available, none selected yet)
total          : 590.0 INR      (includes tax estimate)

availableShippingRates:
  • Business Parcel              41.0 INR
  • Speed Post                   96.0 INR
```

#### What each rate's `handle` actually contains

The `handle` field is a JWT. The base64 payload decodes to MCSL's per-rate response:

```json
{
  "title": "Business Parcel",
  "code": "BUSINESS_PARCEL",
  "source": "Multi Carrier Shipping Label",
  "price": "41.0",
  "currency": "INR",
  "price_presentment": "41.0",
  "currency_presentment": "INR",
  "estimated_delivery_time_range": null,
  "group_id": null
}
```

Pass this handle as `shippingLine.handle` on `draftOrderUpdate` (or `orderCreate`) to lock in that specific rate before completing the order.

#### Schema gotchas

- `Money` is a **scalar** (just a string). Do NOT select `{ amount currencyCode }` on `shippingLine.price` — that returns `selectionMismatch`. Use `MoneyV2` or `MoneyBag.presentmentMoney`/`MoneyBag.shopMoney` for the nested form (which is what `MoneyV2` typed fields like `availableShippingRates.price` return).
- `MoneyBag.presentmentMoney.currencyCode` reflects the **Market's currency**, not `Shop.currency`. So after adding an India Market (17e step 5), an India-destined draft order returns INR even though the store default is USD.

#### Verifying MCSL is attached to the destination zone

If `availableShippingRates` is empty or contains only static rates:

```graphql
{
  deliveryProfiles(first: 3) {
    nodes {
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

Look for `carrierService.name == "Multi Carrier Shipping Label"` on the destination's zone. MCSL auto-registers on install; if it's not there, reinstall (17b).

---

### 17g. Storefront API Rate-Shopping (Buyer-Flow Mirror)

> **When to use this instead of 17f**: when you specifically want to test the buyer-side path — same code path the storefront uses at checkout. Useful for verifying that storefront-side rate behaviour matches what `draftOrderCalculate` returns from admin.

**Prerequisites** (both admin-UI-only on fresh dev stores):
1. **Online Store sales channel activated** — without it, `cartCreate` and `storefront_access_tokens.json` both return `Online Store channel is locked`.
2. **Storefront API public token** — once Online Store is active, mint via:
   ```python
   r = requests.post(
       f"https://{STORE}.myshopify.com/admin/api/{V}/storefront_access_tokens.json",
       headers={"X-Shopify-Access-Token": ADMIN_TOKEN, "Content-Type": "application/json"},
       json={"storefront_access_token": {"title": "MCSL-QA-Rate-Check"}},
   )
   SF_TOKEN = r.json()["storefront_access_token"]["access_token"]
   ```

#### Working pattern

```python
SF_GQL = f"https://{STORE}.myshopify.com/api/{V}/graphql.json"
SF_HDR = {"X-Shopify-Storefront-Access-Token": SF_TOKEN, "Content-Type": "application/json"}

# 1) Create a cart with line item + India buyer identity
cart = requests.post(SF_GQL, headers=SF_HDR, json={"query": """
mutation cartCreate($input: CartInput!) {
  cartCreate(input: $input) {
    cart { id checkoutUrl }
    userErrors { field message }
  }
}
""", "variables": {"input": {
    "lines": [{"merchandiseId": "gid://shopify/ProductVariant/<ID>", "quantity": 1}],
    "buyerIdentity": {
        "email": "qa.test@pluginhive.com",
        "countryCode": "IN",
        "deliveryAddressPreferences": [{"deliveryAddress": {
            "firstName": "QA", "lastName": "Test",
            "address1": "MG Road", "city": "Bengaluru",
            "province": "Karnataka", "country": "India",
            "zip": "560001", "phone": "+919876543210"
        }}]
    }
}}}).json()
cart_id = cart["data"]["cartCreate"]["cart"]["id"]

# 2) Query deliveryGroups WITH carrier rates — this fires MCSL's callback
# @defer is MANDATORY when using withCarrierRates: true. Response is multipart.
resp = requests.post(
    SF_GQL,
    headers={**SF_HDR, "Accept": "multipart/mixed; deferSpec=20220824"},
    json={"query": """
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
""", "variables": {"id": cart_id}},
    stream=True,
)
# Parse multipart response — each chunk is one JSON object
```

#### Trigger requirements (all three must be true)

1. `withCarrierRates: true` argument on `deliveryGroups` — without it, only static rates.
2. `@defer` directive on the surrounding selection — Shopify hard-rejects `withCarrierRates: true` without it.
3. `buyerIdentity` with a shipping address set on the cart — otherwise Shopify has no destination.

#### Required Storefront API scopes (set on the dev app, 17c)

- `unauthenticated_read_checkouts` — cart reads + `deliveryGroups`
- `unauthenticated_write_checkouts` — `cartCreate`, `cartBuyerIdentityUpdate`, line adds
- `unauthenticated_read_product_listings` — fetch the variant ID in the first place

#### When 17g vs 17f

| Situation | Use |
|---|---|
| Verifying MCSL responds with correct rates per region/weight | **17f** (`draftOrderCalculate`) — simpler, no channel activation |
| Reproducing a buyer-reported "wrong rate at checkout" issue | **17g** — exact buyer-side code path |
| Headless storefront integration testing | **17g** — that's the API your headless client uses |
| QA on a fresh dev store where Online Store isn't active | **17f** (can't use 17g) |

---

### 17h. Convert a Rate Quote into a Real Order — `draftOrder*` Chain

> **Why this matters**: `draftOrderCalculate` (17f) is preview-only — nothing is persisted. To turn the rate quote into an order that hits the admin Orders list (and gets picked up by MCSL for label generation), chain three mutations. The resulting order keeps the **exact** MCSL rate response as its shipping line.

#### The chain

```
1. draftOrderCalculate  → returns availableShippingRates with JWT handles
                          (this is where MCSL gets called)
2. draftOrderCreate     → persists a Draft with shippingLine.shippingRateHandle
                          set to the handle of the rate you want
3. draftOrderComplete   → converts the Draft into a real Order
```

#### Working code — verified on test1121 producing order `#1001`, 2026-06-08

```python
import requests
STORE, V, TOKEN = "<slug>", "2026-04", "shpat_..."
GQL = f"https://{STORE}.myshopify.com/admin/api/{V}/graphql.json"
HDR = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

ADDR = {
    "firstName":"QA","lastName":"Tester","address1":"Bandra West, Hill Road",
    "city":"Mumbai","province":"Maharashtra","provinceCode":"MH",
    "country":"India","countryCode":"IN","zip":"400050","phone":"+919876543210",
}
DRAFT_INPUT = {
    "lineItems":       [{"variantId": "gid://shopify/ProductVariant/<ID>", "quantity": 1}],
    "shippingAddress": ADDR,
    "billingAddress":  ADDR,
    "email":           "qa.test@pluginhive.com",
    "tags":            ["qa-test", "speed-post"],
}

def gql(q, v=None):
    return requests.post(GQL, headers=HDR, json={"query": q, "variables": v or {}}).json()

# 1) Get rates from MCSL — no persistence
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
rates  = calc["data"]["draftOrderCalculate"]["calculatedDraftOrder"]["availableShippingRates"]
chosen = next(r for r in rates if r["title"] == "Speed Post")  # ← pick by title/code/price

# 2) Persist the draft with that rate locked in
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

# 3) Complete the draft → real Order
completed = gql("""
mutation complete($id: ID!, $paymentPending: Boolean) {
  draftOrderComplete(id: $id, paymentPending: $paymentPending) {
    draftOrder {
      order {
        id name displayFinancialStatus displayFulfillmentStatus
        shippingLine { title originalPriceSet { presentmentMoney { amount currencyCode } } }
        totalPriceSet { presentmentMoney { amount currencyCode } }
      }
    }
    userErrors { field message }
  }
}
""", {"id": draft_id, "paymentPending": True})
order = completed["data"]["draftOrderComplete"]["draftOrder"]["order"]
print(f"{order['name']}: {order['shippingLine']['title']} "
      f"@ {order['shippingLine']['originalPriceSet']['presentmentMoney']}")
```

#### Verified output (test1121, IN→IN, Speed Post locked in)

```
rates from MCSL (step 1):
  • Business Parcel  ₹41.00 INR
  • Speed Post       ₹96.00 INR

draft (step 2):  #D1  status=OPEN
order (step 3):  #1001  PENDING / UNFULFILLED
                 shippingLine = Speed Post @ ₹96.00 INR  (MCSL rate preserved)
                 total        = ₹686.00 INR
```

#### Schema gotchas — every one of these tripped us up

| Mistake | Symptom | Fix |
|---|---|---|
| Selecting `availableShippingRates` on `draftOrderCreate` response | `undefinedField: Field 'availableShippingRates' doesn't exist on type 'DraftOrder'` | It only lives on `CalculatedDraftOrder` (returned by `draftOrderCalculate`). Call `draftOrderCalculate` first. |
| `shippingLine: { handle: "..." }` on `DraftOrderInput` | `INVALID_VARIABLE: Field is not defined on ShippingLineInput` | Field is `shippingRateHandle`, not `handle`. |
| `paymentPending: false` on a fresh dev store with no payment gateway | Order may not be created | Use `paymentPending: True` to create as PENDING (good enough for QA). |

#### Decoding the JWT rate handle (optional — helpful for picking by code)

Each `handle` is a JWT whose payload contains MCSL's full per-rate response:

```python
import base64, json
parts = chosen["handle"].split(".")
payload = json.loads(base64.urlsafe_b64decode(parts[1] + "==").decode())
# {'title': 'Speed Post', 'code': 'SPEED_POST', 'source': 'Multi Carrier Shipping Label',
#  'price': '96.0', 'currency': 'INR', 'estimated_delivery_time_range': None, ...}
```

So instead of matching on `title == "Speed Post"` you can match on the carrier-stable `code == "SPEED_POST"`.

#### When 17h vs the alternatives

| | `orderCreate` + `BYPASS_STOCK` (G1) | `draftOrder*` chain (17h) |
|---|---|---|
| Triggers MCSL rate callback | ❌ skipped | ✅ |
| Shipping line on order | You supply manually | MCSL's actual rate response |
| Inventory behavior | Bypassed | Decrements (set `inventoryBehaviour: BYPASS` to skip) |
| API calls | 1 | 3 |
| Use when | Label QA with known rate | Full pipeline: rate-shop → pick → order → label |

---

### 17i. Build a Carrier-Env with Products in UPS-Canonical Order

> **Why this matters**: the automation's packaging tests in [`tests/packagingTypes/*.spec.ts`]($MCSL_AUTOMATION_REPO_PATH/tests/packagingTypes) reference products **by index** into `SIMPLE_PRODUCTS_JSON` / `VARIABLE_PRODUCTS_JSON` / `DIGITAL_PRODUCTS_JSON`. For example, `{ productType: 'simple', productCount: 6, quantities: [2] }` resolves to `SIMPLE_PRODUCTS[5]` (see [`createOrderAPI.ts:454-464`]($MCSL_AUTOMATION_REPO_PATH/support/pages/shopifyAPI/createOrderAPI.ts:454) — when `quantities.length === 1`, the resolver picks ONLY `productList[count-1]`). So for a new store's env to work identically against existing tests, the product sequence in each array **must match the team's canonical ordering** in `packaging-ups.env`. Building the env in JSON-file order (or worse, alphabetical) silently breaks index-based tests.

#### How to know which test uses which array index

For any product, find its UPS-env index in SIMPLE / VARIABLE / DIGITAL, then grep tests:

```bash
cd $MCSL_AUTOMATION_REPO_PATH
# Tests that pick SIMPLE_PRODUCTS[5] specifically:
grep -rn "productType:\s*['\"]simple['\"].*productCount:\s*6.*quantities:\s*\[[^,]*\]" \
  tests/packagingTypes/
```

(CASE 1 in the resolver: `quantities` length = 1 → picks index `count-1`. CASE 2/3: longer `quantities` array → slice from 0..count-1, so any index < count is hit.)

#### Building the env via the repo script

[scripts/build_carrier_env_ups_ordered.py](scripts/build_carrier_env_ups_ordered.py:1) handles the cross-store mapping:

```bash
python3 scripts/build_carrier_env_ups_ordered.py \
    --target-store dhl-express-automation \
    --target-token shpat_xxxxxxxxxxxxxxxx \
    --carrier dhl-express-rest \
    --output $MCSL_AUTOMATION_REPO_PATH/carrier-envs/dhl-express-automation-rest.env
```

What it does internally:

1. **Parse `carrier-envs/packaging-ups.env`** — gives the canonical `[{product_id, variant_id}, …]` arrays in sequence.
2. **Resolve each entry on the SOURCE store** (packaging-mcsl-automation) via `GET /products/{pid}.json` — looks up the title + `(option1, option2, option3)` triplet for that specific variant.
3. **Fetch all products on the TARGET store** and build a `title → product` lookup.
4. **For each canonical entry**: find the same title on the target store, pick the variant whose option triplet matches. Emit `{product_id, variant_id}` for the target store.
5. **Write the env file** with metadata (Slack webhook, USER_PASSWORD, etc.) inherited from the source env unless overridden.

CLI flags (all optional except the four above):

| Flag | Default | When to set |
|---|---|---|
| `--source-env` | `carrier-envs/packaging-ups.env` | Use a different canonical reference (e.g. `packaging-fedexrest.env`) |
| `--source-store` / `--source-token` / `--source-api-version` | Parsed from `--source-env` | Override if the env's credentials are stale |
| `--target-api-version` | `2026-04` | Older Shopify if needed |
| `--user-email`, `--user-password`, `--store-password`, `--slack-webhook` | Inherited from source env | Override per target store |
| `--partner-url` | PluginHive Partner stores URL | Different Partner account |

Exit codes: `0` on full match, `3` if the env was written but some canonical entries had no match on the target store (printed at the end — you'll see exactly which titles + signatures failed).

#### Key gotchas (each cost us debugging time)

1. **`Default Title` variants** — single-variant products in Shopify expose `option1 = "Default Title"`. The script treats these as the sentinel `("__default__",)` so they match any single-variant product on the target without needing exact option-triplet alignment.
2. **Deleted source variants** — UPS env can reference `variant_id`s that have since been deleted on the source store (product still exists, variant gone). The fallback: if the source product is currently single-variant, treat the entry as `("__default__",)`; otherwise emit the entry as unresolved with a warning. We hit this for `20 lb Prepacked Product` on UPS.
3. **Copy-paste typos in the canonical env** — a `{product_id, variant_id}` pair where the IDs don't actually belong together (variant orphaned to the wrong product). Symptom: the script reports a title that doesn't match anything on the target. Fix the canonical env (a one-line edit), then re-run.
4. **Cross-classification** (product appears in DIGITAL on canonical but is a simple shipping product elsewhere) — the script faithfully reproduces canonical's classification. If your target store's product has `requires_shipping: true` but UPS classified it as DIGITAL, it still goes in `DIGITAL_PRODUCTS_JSON` because that's what the team-blessed ordering says. Tests are written against that classification.
5. **Multi-element `quantities` arrays** trigger CASE 2 (slice 0..count-1). So `productCount: 6, quantities: [1, 2, 1, 1, 1, 1]` picks indexes 0–5, NOT just index 5. Watch the difference vs CASE 1 when reasoning about which array index a test exercises.

#### Verification after writing

Run a smoke test that mirrors what `weightAndVolume.spec.ts` does:

```python
import json
env = open("carrier-envs/dhl-express-automation-rest.env").read()
import re
simple = json.loads(re.search(r"SIMPLE_PRODUCTS_JSON='(\[.*?\])'", env).group(1))
print(f"SIMPLE_PRODUCTS[5] (used by Test 2/5/8 in weightAndVolume.spec.ts):")
print(f"  product_id  = {simple[5]['product_id']}")
print(f"  variant_id  = {simple[5]['variant_id']}")
# Cross-check the title via Admin API to confirm it's the right product
```

If `SIMPLE_PRODUCTS[5]` resolves to the same product title across all carrier-envs, you've kept index-test parity.

---

### 17j. The Complete "create XXX carrier store and give me full env" Pipeline

> **When this applies**: any time the user says *"create <X> carrier store and give me full env"* (or paraphrases — "set up YYY", "give me env for ZZZ"). Run AUTO phases end-to-end, then STOP and hand off for the carrier-registration step. Do NOT auto-add product dimensions before carrier is registered.

#### AUTO phases — run end-to-end without mid-way confirmation

| # | Step | Helper | Notes |
|---|---|---|---|
| 1 | Create dev store + install QA app via Partner OAuth | `create_store_and_install_app(store_name=...)` from `pipeline.new_carrier_onboarding` | Picks Dev tile (6 selector fallbacks), fills name + plan, submits |
| 2 | Plan **QA-Plan-3** + Approve charges | (inside step 1) | Card matched by text "QA-Plan-3" (NOT `nth(N)`); waits for RecurringApplicationCharge URL; clicks `#approve-charges-button` |
| 3 | Capture realized slug from post-install URL | (inside step 1) | Shopify appends suffix to typed name (e.g. `EmailTest` → `emailtest-andyfh5i`) |
| 4 | Dev app + Admin scopes (143) + **Storefront scopes (12)** + install + reveal `shpat_*` | `create_dev_app_and_reveal_token(...)` | Direct URL navigation to `/configuration/{admin,storefront}_api_integration` (the CTA-on-overview is flaky) |
| 4.5 | **Default Markets**: ensure `United States` primary + add `International` (all 234 non-US ISO codes) | `marketCreate` GraphQL | Only deviate if user names a different domestic country |

After 4.5, write a **minimal env** to `mcsl-test-automation/carrier-envs/<slug>.env` with all metadata but empty `SIMPLE_PRODUCTS_JSON='[]'` / `VARIABLE='[]'` / `DIGITAL='[]'`. Then STOP.

#### MANUAL HANDOFF — exact message back to the user

> "Store + app + dev-app + token are ready. Initial env written to `carrier-envs/<slug>.env`.
>
> **Next step is yours, in this order**:
> 1. Open `<app_url>`. The QA app shows an **onboarding form first** (Email / Phone / "I agree" checkbox / Submit) — fill it and click Submit, then click Start.
> 2. Once you're past onboarding, **register the carrier** inside the MCSL app (enter the carrier's account credentials, license keys, etc.). Shopify has no API for this.
>
> When you tell me the carrier is registered, I'll add packaging products with dimensions and rebuild the env in UPS-canonical sequence."

Do NOT proceed past this point. Wait for explicit "done" / "carrier added" / "now add products".

#### POST-HANDOFF phases — run on confirmation

By the time the user confirms carrier registration, the onboarding form is already submitted by them (it gates access to the carrier-registration screen). Skip `maybeFillOnboarding`; the seed script goes straight to the Menu.

| # | Step | Helper |
|---|---|---|
| 5 | Seed 22 packaging products + L×W×H dimensions via MCSL app UI | `mcsl-test-automation/scripts/seed-packaging-store.ts` — uses `SHOPIFY_STORE_NAME`, `SHOPIFY_ACCESS_TOKEN`, `APPURL` env vars |
| 6 | Rebuild env in UPS-canonical sequence (+ `SHIPPING_ADDRESS_JSON` + `AI_ENABLED=false`) | `scripts/build_carrier_env_ups_ordered.py --target-store <slug> --target-token <token> --carrier <code> --output <path> --country <ISO>` |
| 7 | Place one test order + capture `accountUUID` + substitute into toggle template + DM Ashok on Slack | `scripts/notify_qa_store_toggles_to_ashok.py --store-slug <slug> --carrier-env-path <env-path>` |
| 8 | (Auto on Madan's "Ashok confirmed" / "done") Swap carrier-env into `.env`, run `@smoke`, then `@sanity`, restore `.env` | `scripts/run_smoke_sanity_for_carrier.sh <env-path>` |

#### Phase 6 — the two extra env fields

The env file shape includes two fields beyond the products + token bundle:

- **`SHIPPING_ADDRESS_JSON`** — country-aware ship-to address. Built by `pipeline.new_carrier_validation.default_shipping_address(country_code)`. Built-in presets for `US`, `IN`, `AU`, `CA`, `GB`, `NZ`; unknown codes fall back to US. Pass `--country <ISO>` on `build_carrier_env_ups_ordered.py` (defaults to `US`). Shape matches existing envs: an array of single-key dicts `[{"street":...},{"city":...},{"state":...},{"countryCode":...},{"zip":...}]` — tests parse it positionally.
- **`AI_ENABLED=false`** — always emitted, every observed carrier-env uses `false`.

Country defaults to `US` for new stores (no auto-localisation unless explicitly requested). For an India store: `--country IN` → ship-to becomes `[Baker Street, Mumbai, Maharashtra, IN, 400001]`.

#### Phase 7 — toggle enablement request (the final auto step)

The MCSL app exposes ~41 feature toggles that must be enabled per-store before QA can run the full suite. These toggles are keyed by the store's **accountUUID**, which is only available after at least one order exists on the store (it's returned in the MCSL `/orders` API response).

What phase 7 does:
1. **Places one test order** via `pipeline.order_creator.create_order(carrier_env_path=...)` — picks the first product from `SIMPLE_PRODUCTS_JSON`, ships to a default address.
2. **Captures the `accountUUID`** by opening the MCSL app via Playwright (`pipeline.toggle_state.capture_store_and_toggle_state`), intercepting the `/orders` response.
3. **Substitutes** `__ACCOUNT_UUID__` in [templates/qa_store_toggles.json](templates/qa_store_toggles.json:1) with the captured UUID. Template contains 41 toggle keys (booleans, ints, strings, arrays).
4. **DMs Ashok on Slack** with the substituted JSON block in a code fence and the message *"Hi Ashok, please enable these toggles for my new QA store <slug>. Account UUID: ..."*.

CLI:
```bash
PYTHONPATH=. .venv/bin/python scripts/notify_qa_store_toggles_to_ashok.py \
    --store-slug madanindianpost \
    --carrier-env-path $MCSL_AUTOMATION_REPO_PATH/carrier-envs/madanindianpost.env
```

Flags: `--skip-order-create` if the store already has orders, `--dry-run` to print the substituted block without sending Slack, `--template <path>` to override the toggle template.

**Failure modes** (each exits with a non-zero code):
- `2` — `accountUUID` not in the captured `/orders` response. Usually means no orders exist yet (the auto-place step failed) OR `auth-chrome.json` is stale OR the app's onboarding form wasn't completed.
- `4` — Ashok not found in Slack search results.
- `6-7` — Slack API errors (token invalid, channel can't be opened, etc.).

Prerequisites: `SLACK_BOT_TOKEN` env var, `auth-chrome.json` fresh, MCSL app's onboarding form already completed (it should be, since QA cleared it during the handoff before registering the carrier).

#### After phase 7

Phase 7 handoff message:

> "Env written, products + dimensions confirmed, test order placed, account UUID captured, Slack DM sent to Ashok. **Tell me when Ashok replies `done` in Slack** and I'll auto-run smoke + sanity (phase 8)."

#### Phase 8 — auto-run smoke + sanity on user's "Ashok confirmed"

When the user replies *"done"* / *"Ashok confirmed"* / *"toggles enabled"* / similar after phase 7, immediately invoke:

```bash
bash scripts/run_smoke_sanity_for_carrier.sh \
    $MCSL_AUTOMATION_REPO_PATH/carrier-envs/<slug>.env
```

What it does:
1. Backs up `mcsl-test-automation/.env` → `.env.smoke-sanity-backup.$$`
2. Copies the carrier-env file to `mcsl-test-automation/.env` (the automation reads from `.env` via `dotenv.config({quiet: true})` in `playwright.config.ts`).
3. `npx playwright test --grep @smoke --reporter=list` → log to `/tmp/smoke_<carrier>.log`
4. `npx playwright test --grep @sanity --reporter=list` → log to `/tmp/sanity_<carrier>.log`
5. **Always restores** original `.env` via bash `trap EXIT INT TERM`, even on test failure.
6. Prints PASS/FAIL summary with exit codes.

Time: smoke ~5-10 min, sanity ~10-15 min. Run in background.

Final handoff (after phase 8):

> "Smoke + sanity complete for `<slug>`. Smoke: PASS/FAIL. Sanity: PASS/FAIL. Logs: `/tmp/smoke_<carrier>.log`, `/tmp/sanity_<carrier>.log`. Review failures and decide if regression is needed."

#### Override behaviour

If the user explicitly names a domestic country (e.g. *"create FedEx India store, domestic India"*), modify phase 4.5:
- Create `<Country>` market with that single country code instead of US/International
- Use `locationEdit` (GraphQL) to point the primary location at that country (no `province` field on `LocationEditAddressInput`)
- Use `deliveryProfileUpdate` to change Domestic zone countries
- `Shop.currency`, `Shop.weight_unit`, `Shop.country` stay default — Markets handles presentment currency

See section 17e for the working India-localisation code as a reference.

#### Onboarding form selectors (when the helper does handle it)

The QA app's onboarding form uses **`<input type="text">`** (NOT `type="email"`/`type="tel"`!). Correct locators:
- Email: `input[name="email"]` or `input[placeholder="john@gmail.com"]`
- Phone: `input[name="phoneNumber"]` or `input[placeholder="7567812342"]`
- Checkbox: `input[type="checkbox"]` (inside a Material-UI `<label class="jss3">`)
- Submit button starts `disabled` — poll `submit.isDisabled()` until false before clicking
- After Submit, wait for `Start` button → click → wait for `Menu` to confirm onboarding complete

The helper's `maybeFillOnboarding` does this correctly as of 2026-06-08.

#### Default values

- Email used by helper: `qa.test@pluginhive.com`
- Phone: `1234567890`
- `Shop.currency`/`weight_unit`/`country` are **never auto-changed** — leave US/USD defaults unless user explicitly localises (see memory: `mcsl-store-defaults-no-auto-localisation.md`)
- Filename default: `<store-slug>.env` in `mcsl-test-automation/carrier-envs/`. Ask only if carrier code differs from slug.

---

### 18. List Fulfillments for an Order

```python
resp         = requests.get(f"{BASE_URL}/orders/{order_id}/fulfillments.json", headers=HEADERS)
fulfillments = resp.json().get("fulfillments", [])

for f in fulfillments:
    print(f"  Fulfillment ID: {f['id']}")
    print(f"  Status:         {f['status']}")
    print(f"  Tracking:       {f.get('tracking_number')} via {f.get('tracking_company')}")
    print(f"  Service:        {f.get('service')}")
    for item in f.get("line_items", []):
        print(f"    - {item['title']} × {item['quantity']}")
```

---

### 19. Create Draft Order → Complete It

```python
# Step 1 — create draft
payload = {
    "draft_order": {
        "line_items": [{"variant_id": variant_id, "quantity": 1}],
        "customer": {"first_name": "QA", "last_name": "Test", "email": "qa.draft@pluginhive.com"},
        "shipping_address": {
            "first_name": "QA", "last_name": "Test",
            "address1": "MG Road", "city": "Bengaluru",
            "province": "Karnataka", "province_code": "KA",
            "zip": "560001", "country": "India", "country_code": "IN"
        },
        "tags": "qa-draft",
    }
}
resp     = requests.post(f"{BASE_URL}/draft_orders.json", headers=HEADERS, json=payload)
draft    = resp.json().get("draft_order", {})
draft_id = draft["id"]
print(f"Draft order created: #{draft['name']} (ID {draft_id})")

# Step 2 — complete it (becomes a real order, marked as paid)
resp  = requests.put(f"{BASE_URL}/draft_orders/{draft_id}/complete.json",
                     headers=HEADERS, params={"payment_pending": False})
order = resp.json().get("draft_order", {})
print(f"Completed → real order ID: {order.get('order_id')}")
```

---

### 20. Get Order Count

```python
for status in ["open", "closed", "cancelled", "any"]:
    resp = requests.get(f"{BASE_URL}/orders/count.json", headers=HEADERS, params={"status": status})
    print(f"  {status}: {resp.json().get('count', 0)} orders")
```

---

### 21. List Webhooks

```python
resp     = requests.get(f"{BASE_URL}/webhooks.json", headers=HEADERS)
webhooks = resp.json().get("webhooks", [])
print(f"Found {len(webhooks)} webhooks:")
for w in webhooks:
    print(f"  - [{w['id']}] {w['topic']:40s} → {w['address']}")
```

---

### 22. Get Metafields on a Product or Order

```python
# Metafields on a product
resp = requests.get(f"{BASE_URL}/products/{product_id}/metafields.json", headers=HEADERS)
mf   = resp.json().get("metafields", [])

# Metafields on an order
resp = requests.get(f"{BASE_URL}/orders/{order_id}/metafields.json", headers=HEADERS)
mf   = resp.json().get("metafields", [])

for m in mf:
    print(f"  {m['namespace']}.{m['key']} ({m['type']}): {m['value']}")
```

---

## 🟢 Nice to Have

### 23. Create Customer

```python
payload = {
    "customer": {
        "first_name": "QA", "last_name": "Tester",
        "email": "qa.tester@pluginhive.com",
        "phone": "+919876543210",
        "verified_email": True,
        "addresses": [{
            "address1": "MG Road", "city": "Bengaluru",
            "province": "Karnataka", "province_code": "KA",
            "zip": "560001", "country": "India", "country_code": "IN",
            "default": True
        }],
        "tags": "qa-customer"
    }
}
resp     = requests.post(f"{BASE_URL}/customers.json", headers=HEADERS, json=payload)
customer = resp.json().get("customer", {})
print(f"Created customer: {customer['first_name']} {customer['last_name']} (ID {customer['id']})")
```

---

### 24. Search Customer by Email or Name

```python
# By email (exact)
resp = requests.get(f"{BASE_URL}/customers/search.json", headers=HEADERS,
                    params={"query": "email:qa.tester@pluginhive.com"})

# By name (partial)
resp = requests.get(f"{BASE_URL}/customers/search.json", headers=HEADERS,
                    params={"query": "QA Tester"})

customers = resp.json().get("customers", [])
for c in customers:
    print(f"  ID {c['id']} | {c['first_name']} {c['last_name']} | {c['email']}")
```

---

### 25. Adjust Inventory (relative ±delta)

```python
delta   = +50  # positive = add stock, negative = remove stock
payload = {"location_id": location_id, "inventory_item_id": inventory_item_id, "available_adjustment": delta}
resp    = requests.post(f"{BASE_URL}/inventory_levels/adjust.json", headers=HEADERS, json=payload)
result  = resp.json().get("inventory_level", {})
print(f"Adjusted by {delta:+d} → now {result.get('available')} units")
```

Use `adjust` when user says "add 50 stock". Use `set` (action 9) when user says "set stock to 9999".

---

### 26. List Locations

```python
resp      = requests.get(f"{BASE_URL}/locations.json", headers=HEADERS)
locations = resp.json().get("locations", [])
print(f"Store has {len(locations)} location(s):")
for loc in locations:
    print(f"  ID {loc['id']} | {loc['name']} | active: {loc['active']}")
    print(f"    {loc.get('address1')}, {loc.get('city')}, {loc.get('country')}")
```

Default location is `locations[0]` — use its ID for all inventory operations unless the user specifies otherwise.

---

### 27. List Collections & Add Product to Collection

```python
# List all custom collections
resp        = requests.get(f"{BASE_URL}/custom_collections.json", headers=HEADERS)
collections = resp.json().get("custom_collections", [])
for c in collections:
    print(f"  ID {c['id']} | {c['title']}")

# Add product to a custom collection
payload = {"collect": {"product_id": product_id, "collection_id": collection_id}}
resp    = requests.post(f"{BASE_URL}/collects.json", headers=HEADERS, json=payload)
print(f"Added product {product_id} to collection {collection_id}")
```

---

### 28. Create Refund on an Order

```python
# Step 1 — calculate refund first (Shopify requires this)
resp = requests.post(f"{BASE_URL}/orders/{order_id}/refunds/calculate.json",
                     headers=HEADERS,
                     json={"refund": {"shipping": {"full_refund": True}, "refund_line_items": []}})
calc = resp.json().get("refund", {})

# Step 2 — apply the refund
payload = {
    "refund": {
        "notify": False, "note": "QA test refund",
        "shipping": {"full_refund": True},
        "refund_line_items": calc.get("refund_line_items", []),
        "transactions":      calc.get("transactions", [])
    }
}
resp   = requests.post(f"{BASE_URL}/orders/{order_id}/refunds.json", headers=HEADERS, json=payload)
refund = resp.json().get("refund", {})
print(f"Refund created: ID {refund.get('id')} on order {order_id}")
```

---

## Execution Pattern

Always run Python in the project virtualenv:

```bash
cd "$MCSL_REPO"  # path to your MCSLDomainExpert clone
PYTHONPATH=. .venv/bin/python -c "
# paste the action code here
"
```

Or write a temp script and run it:

```bash
PYTHONPATH=. .venv/bin/python /tmp/shopify_action.py
```

---

## Response Format

**For list:**
```
Found 8 products:
- ID 10322136203578 | "1. Simple Product"  | active | variant: 53565711483194 (₹50.00)
- ID 10322136301882 | "Test Variable"      | active | 125 variants
```

**For create:**
```
Created order #1894
- Order ID: 6226633621604
- Product: Test Variable / XS / Red / Kids (qty 1)
- Ship to: QA Tester, MG Road, Bengaluru KA 560001, IN
- Financial status: paid
```

**For variable product:**
```
Created variable product "Test Variable" (ID 10322136301882)
Options: Size × Color × Age Group  (5 × 5 × 5 = 125 variants)
  XS / Red / Kids   → variant ID 53565711745338 | ₹150.00
  XS / Red / Teen   → variant ID 53565711777906 | ₹150.00
  ... (125 total)
```

**For GraphQL order (BYPASS_STOCK):**
```
Using automation .env → store: indiapoststore2
Connected: IndiaPostStore2 (indiapoststore2.myshopify.com)
Created order #1895 (gid://shopify/Order/6226700000000)
  - Customer: QA Tester <qa.test@pluginhive.com> [upserted]
  - Ship to: MG Road, Bengaluru KA 560001, IN
  - Inventory: BYPASS_STOCK — no stock deducted ✓
  - Tags: qa-test
```

**For GraphQL large variant product:**
```
Created product "MCSL QA Multi-Variant Product" (gid://shopify/Product/8600000000001)
Options: Size (8) × Color (8) × Fabric (4)
Creating 256 variants...
  Batch 1: 100 variants created
  Batch 2: 100 variants created
  Batch 3: 56 variants created
Done — 256 variants total
```

**For GraphQL bulk inventory:**
```
Updated 125 variants to qty=9999:
  InventoryItem/111 @ Online Store → delta=+9999, now=9999
  ...
```

**For REST errors:**
```
API error 422: {"errors": {"line_items": ["is too short (minimum is 1 character)"]}}
```

**For GraphQL userErrors:**
```
GraphQL userErrors:
  - field: lineItems, message: Variant does not exist
```

---

## Important Notes

**Store & Auth**
- MCSL uses ONE primary automation store (root `.env` of the automation repo at `config.MCSL_AUTOMATION_REPO_PATH`).
- Optional carrier-specific overrides live under `carrier-envs/<carrier>.env`. Each may carry its own `SHOPIFY_STORE_NAME`, `SHOPIFY_ACCESS_TOKEN`, `SHOPIFY_API_VERSION`, and seeded product JSONs (`SIMPLE_PRODUCTS_JSON`, `VARIABLE_PRODUCTS_JSON`, `DIGITAL_PRODUCTS_JSON`, `DANGEROUS_PRODUCTS_JSON`).
- Routing: if the user mentions a carrier (`india post`, `blue dart`, `fedex`, `dhl`, `aramex`, etc.) → load `carrier-envs/<slug>.env`. Otherwise → root `.env`.
- Always print which env/store is active before running any action to prevent wrong-account mistakes.
- Cannot auto-install the MCSL app or generate a token via API — Shopify requires OAuth browser consent.

**Orders**
- Always use `BYPASS_STOCK` (GraphQL G1) for QA test orders — never deduct real inventory.
- Tag all test orders with `qa-test` at creation time so bulk cleanup (action 13) works.
- Orders appear in the real Shopify admin → Orders list immediately and are ready for MCSL label generation.
- Default ship-to address: **Bengaluru, KA 560001, India**.
- Carrier support varies (see [docs/MCSL_CARRIER_CAPABILITY_MATRIX.md](docs/MCSL_CARRIER_CAPABILITY_MATRIX.md:1)): India Post supports domestic + select international; FedEx / DHL / Aramex / Blue Dart support international; some carriers support dangerous goods, others don't.

**Products & Variants**
- REST: max 100 variants (hard limit in Shopify 2024-04+ REST).
- GraphQL `productVariantsBulkCreate`: up to **2048 variants** per product (official Shopify limit).
- For large variant counts use GraphQL G3 (create product first, then bulk add variants in chunks of 100).
- Use `productOptions` (not `options`) in GraphQL `ProductSetInput` — Shopify 2024-04+.
- Products created here are immediately usable for MCSL label generation in the app.
- For deterministic carrier-validation product provisioning, prefer `pipeline.shopify_product_seed.create_seed_products(carrier_code, ...)` so the seeded variant IDs flow into the carrier-env JSONs the automation expects.

**Inventory**
- Use REST action 9 (`/inventory_levels/set.json`) for single variant, single location updates.
- Use REST action 25 (`/inventory_levels/adjust.json`) for single variant relative delta.
- Use GraphQL G4 (`inventorySetQuantities`) for bulk absolute set across many variants/locations.
- Use GraphQL G4 (`inventoryAdjustQuantities`) for bulk relative delta across many variants/locations.
- 6 quantity types are writable: `available`, `on_hand`, `incoming`, `safety_stock`, `damaged`, `quality_control`.
- `committed` and `reserved` are read-only — calculated from open/draft orders, cannot be set.

**API choice**
- REST for simple CRUD (list, get, delete, single update).
- GraphQL for: BYPASS_STOCK orders, 100+ variant products, bulk inventory, order+fulfillment in one call.
- Both use the same `X-Shopify-Access-Token` header. Only the URL and payload format differ.

**Pagination**
- REST: max 250 per page, use `Link` header `page_info` cursor for full lists.
- GraphQL: use `first` + `after` cursor on connections for paginated queries.
