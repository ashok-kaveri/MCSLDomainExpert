#!/usr/bin/env python3
"""Create freight test products in the qa-moody-store Shopify store."""
import json
import os
import sys
import time
import urllib.error
import urllib.request

SHOP = "qa-moody-store"
TOKEN = os.environ.get("SHOPIFY_ACCESS_TOKEN", "")  # set via .env / shell env
API_VERSION = "2023-01"
BASE = f"https://{SHOP}.myshopify.com/admin/api/{API_VERSION}"

# (price_usd, weight_lbs) — order taken from the screenshot
ITEMS = [
    (43.00, 0.20),   # 1  Yellowstone Iconic Sweep Coasters
    (1.00,  0.10),   # 2  Yellowstone Can Koozie
    (10.50, 0.20),   # 3  Exotico Music Clear Concert Bag
    (37.00, 1.10),   # 4  El Mayor Napkin Caddy
    (11.00, 0.10),   # 5  Yellowstone Julep Strainer
    (62.50, 0.30),   # 6  Yellowstone Harlow Pen
    (42.50, 0.50),   # 7  Penelope Paris Softy Rose Gold
    (25.00, 2.00),   # 8  Penelope Bar Mat
    (15.00, 1.00),   # 9  Penelope Iconic Rail Mat
    (4.50,  0.10),   # 10 Penelope Bar Key
    (37.00, 1.10),   # 11 Penelope Napkin Caddy
    (52.50, 20.00),  # 12 Penelope Barrel Head
    (50.00, 0.20),   # 13 Yellowstone Stickers
    (1.55,  0.10),   # 14 Yellowstone Lapel Pin
    (15.00, 0.20),   # 15 Penelope 2025 1oz Sampling Cups
    (31.00, 1.00),   # 16 Penelope Cigar Ceramic Ashtray
    (0.00,  1.00),   # 17 TQM Iconic Service Mat
    (0.00,  20.00),  # 18 Rossville Union Barrel Head
    (0.00,  1.00),   # 19 Yellowstone Bar Rail
    (0.00,  45.00),  # 20 Remus Authentic Barrel Head
    (0.00,  18.00),  # 21 El Mayor Authentic Barrel Head
    (0.00,  17.77),  # 22 Daviess County Barrel Head
]
QTY = 9999


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
        print(f"  HTTP {e.code}: {e.read().decode()[:300]}", file=sys.stderr)
        raise


def get_location_id() -> int:
    locs = api("GET", "/locations.json")["locations"]
    # prefer the first active location
    for loc in locs:
        if loc.get("active"):
            return loc["id"]
    return locs[0]["id"]


def create_product(name: str, price: float, weight_lbs: float):
    payload = {
        "product": {
            "title": name,
            "product_type": "Freight Test",
            "status": "active",
            "variants": [
                {
                    "price": f"{price:.2f}",
                    "weight": weight_lbs,
                    "weight_unit": "lb",
                    "inventory_management": "shopify",
                    "inventory_policy": "continue",
                    "requires_shipping": True,
                }
            ],
        }
    }
    return api("POST", "/products.json", payload)["product"]


def set_inventory(location_id: int, inventory_item_id: int, qty: int):
    # Make sure the inventory item is stocked at this location
    api(
        "POST",
        "/inventory_levels/connect.json",
        {"location_id": location_id, "inventory_item_id": inventory_item_id},
    )
    api(
        "POST",
        "/inventory_levels/set.json",
        {
            "location_id": location_id,
            "inventory_item_id": inventory_item_id,
            "available": qty,
        },
    )


def main():
    print(f"Store: {SHOP}.myshopify.com  API: {API_VERSION}")
    loc_id = get_location_id()
    print(f"Using location_id={loc_id}")
    results = []
    for i, (price, weight) in enumerate(ITEMS, start=1):
        name = f"freight {i}"
        print(f"[{i:02d}/{len(ITEMS)}] Creating '{name}'  price=${price:.2f}  weight={weight} lb")
        try:
            product = create_product(name, price, weight)
            variant = product["variants"][0]
            inv_id = variant["inventory_item_id"]
            set_inventory(loc_id, inv_id, QTY)
            results.append(
                {
                    "name": name,
                    "product_id": product["id"],
                    "variant_id": variant["id"],
                    "inventory_item_id": inv_id,
                    "price": price,
                    "weight": weight,
                }
            )
            print(f"   -> product_id={product['id']}  variant_id={variant['id']}  qty={QTY}")
        except Exception as e:
            print(f"   !! failed: {e}", file=sys.stderr)
            results.append({"name": name, "error": str(e)})
        # gentle rate-limit cushion (Shopify REST: ~2 req/s)
        time.sleep(0.6)

    out = os.path.join(os.path.dirname(__file__), "freight_products_result.json")
    with open(out, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nDone. Wrote {out}")


if __name__ == "__main__":
    main()
