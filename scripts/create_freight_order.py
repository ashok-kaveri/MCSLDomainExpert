#!/usr/bin/env python3
"""Create a single Shopify order containing all 22 freight products."""
import json
import os
import sys
import urllib.error
import urllib.request

SHOP = "qa-moody-store"
TOKEN = os.environ.get("SHOPIFY_ACCESS_TOKEN", "")  # set via .env / shell env
API_VERSION = "2023-01"
BASE = f"https://{SHOP}.myshopify.com/admin/api/{API_VERSION}"

RESULT_FILE = os.path.join(os.path.dirname(__file__), "freight_products_result.json")

# Quantities from the screenshot, in the same order as ITEMS in create_freight_products.py
QUANTITIES = [1, 50, 5, 2, 4, 1, 1, 2, 5, 10, 4, 2, 1, 10, 4, 5, 5, 2, 10, 1, 2, 2]

US_ADDRESS = {
    "first_name": "Madan",
    "last_name": "QA",
    "address1": "1600 Amphitheatre Parkway",
    "city": "Mountain View",
    "province": "California",
    "province_code": "CA",
    "country": "United States",
    "country_code": "US",
    "zip": "94043",
    "phone": "+14155550123",
}


def api(method: str, path: str, body=None):
    url = f"{BASE}{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("X-Shopify-Access-Token", TOKEN)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode()[:600]}", file=sys.stderr)
        raise


def main():
    with open(RESULT_FILE) as f:
        products = json.load(f)

    assert len(products) == len(QUANTITIES), (
        f"Have {len(products)} products but {len(QUANTITIES)} quantities"
    )

    line_items = []
    for prod, qty in zip(products, QUANTITIES):
        if "variant_id" not in prod:
            print(f"Skipping {prod.get('name')} (no variant_id)", file=sys.stderr)
            continue
        line_items.append({"variant_id": prod["variant_id"], "quantity": qty})

    payload = {
        "order": {
            "line_items": line_items,
            "customer": {
                "first_name": US_ADDRESS["first_name"],
                "last_name": US_ADDRESS["last_name"],
                "email": "madan+freighttest@pluginhive.com",
            },
            "email": "madan+freighttest@pluginhive.com",
            "shipping_address": US_ADDRESS,
            "billing_address": US_ADDRESS,
            "financial_status": "pending",
            "send_receipt": False,
            "send_fulfillment_receipt": False,
            "inventory_behaviour": "decrement_obeying_policy",
            "tags": "freight-test",
            "note": "Freight test order — all 22 freight products, US address",
        }
    }

    print(f"Creating order with {len(line_items)} line items...")
    resp = api("POST", "/orders.json", payload)
    order = resp["order"]
    print(f"  Order ID:     {order['id']}")
    print(f"  Order name:   {order['name']}")
    print(f"  Total weight: {order.get('total_weight')} grams")
    print(f"  Total price:  {order.get('total_price')} {order.get('currency')}")
    print(f"  Admin URL:    https://admin.shopify.com/store/{SHOP}/orders/{order['id']}")

    out = os.path.join(os.path.dirname(__file__), "freight_order_result.json")
    with open(out, "w") as f:
        json.dump(order, f, indent=2)
    print(f"\nSaved order details to {out}")


if __name__ == "__main__":
    main()
