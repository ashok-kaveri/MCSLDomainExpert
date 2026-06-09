import os
#!/usr/bin/env python3
"""Copy all products (name, weight, dimensions, variants) from
packaging-mcsl-automation -> indiapoststore2."""
import json, os, sys, time, urllib.error, urllib.request

SRC = ("packaging-mcsl-automation", os.environ.get("SRC_TOKEN", ""))  # set SRC_TOKEN env var
DST = ("indiapoststore2",           os.environ.get("DST_TOKEN", ""))  # set DST_TOKEN env var
API = "2023-01"

DIM_KEYS = {"length", "width", "height", "depth", "size", "dimensions"}


def call(shop, token, method, path, body=None):
    url = f"https://{shop}.myshopify.com/admin/api/{API}{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("X-Shopify-Access-Token", token)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        print(f"  HTTP {e.code} {method} {path}: {e.read().decode()[:400]}", file=sys.stderr)
        raise


def fetch_all_products(shop, token):
    products, page_info = [], None
    path = f"/products.json?limit=250"
    while True:
        url = f"https://{shop}.myshopify.com/admin/api/{API}{path}"
        req = urllib.request.Request(url)
        req.add_header("X-Shopify-Access-Token", token)
        with urllib.request.urlopen(req) as r:
            data = json.loads(r.read().decode())
            products.extend(data["products"])
            link = r.headers.get("Link", "")
        # parse next cursor
        nxt = None
        for part in link.split(","):
            if 'rel="next"' in part:
                nxt = part[part.find("<")+1:part.find(">")]
        if not nxt:
            break
        path = nxt.split("/admin/api/" + API)[1]
    return products


def get_metafields(shop, token, owner_kind, owner_id):
    """owner_kind: 'products' or 'variants'"""
    return call(shop, token, "GET", f"/{owner_kind}/{owner_id}/metafields.json")["metafields"]


def main():
    src_shop, src_tok = SRC
    dst_shop, dst_tok = DST
    print(f"Source:  {src_shop}")
    print(f"Target:  {dst_shop}")

    print("\nFetching source products…")
    src_products = fetch_all_products(src_shop, src_tok)
    print(f"  got {len(src_products)} products")

    # destination location for inventory
    dst_locs = call(dst_shop, dst_tok, "GET", "/locations.json")["locations"]
    dst_loc = next((l for l in dst_locs if l.get("active")), dst_locs[0])
    print(f"  destination location: {dst_loc['id']} ({dst_loc['name']})")

    results = []
    for i, sp in enumerate(src_products, 1):
        title = sp["title"]
        print(f"\n[{i:02d}/{len(src_products)}] {title}")

        # product metafields (dimensions live here typically)
        p_mfs = get_metafields(src_shop, src_tok, "products", sp["id"])
        dim_mfs = [m for m in p_mfs if m["key"].lower() in DIM_KEYS or "dimension" in m["key"].lower()]
        if dim_mfs:
            print(f"  dimension metafields: {[(m['namespace'],m['key'],m['value']) for m in dim_mfs]}")

        # Build variants payload
        variants_payload = []
        variant_mf_map = []  # list of (idx, metafields)
        for vi, v in enumerate(sp["variants"]):
            vp = {
                "option1": v.get("option1"),
                "option2": v.get("option2"),
                "option3": v.get("option3"),
                "price": v.get("price"),
                "sku": v.get("sku"),
                "weight": v.get("weight"),
                "weight_unit": v.get("weight_unit"),
                "inventory_management": "shopify",
                "inventory_policy": v.get("inventory_policy", "deny"),
                "requires_shipping": v.get("requires_shipping", True),
                "taxable": v.get("taxable", True),
                "barcode": v.get("barcode"),
            }
            variants_payload.append({k: val for k, val in vp.items() if val is not None})
            v_mfs = get_metafields(src_shop, src_tok, "variants", v["id"])
            if v_mfs:
                variant_mf_map.append((vi, v_mfs))

        product_payload = {
            "product": {
                "title": title,
                "body_html": sp.get("body_html") or "",
                "vendor": sp.get("vendor") or "",
                "product_type": sp.get("product_type") or "",
                "tags": sp.get("tags") or "",
                "status": "active",
                "options": [
                    {"name": o["name"], "values": o.get("values", [])}
                    for o in sp.get("options", [])
                ] or None,
                "variants": variants_payload,
            }
        }
        # remove None
        product_payload["product"] = {k: v for k, v in product_payload["product"].items() if v is not None}

        try:
            created = call(dst_shop, dst_tok, "POST", "/products.json", product_payload)["product"]
        except Exception as e:
            print(f"  !! create failed: {e}")
            results.append({"title": title, "error": str(e)})
            continue

        new_id = created["id"]
        print(f"  -> created {new_id}")

        # reapply product metafields (only the dimension-ish ones — preserve everything actually)
        for m in p_mfs:
            try:
                call(dst_shop, dst_tok, "POST", f"/products/{new_id}/metafields.json", {
                    "metafield": {
                        "namespace": m["namespace"],
                        "key": m["key"],
                        "value": m["value"],
                        "type": m.get("type", "single_line_text_field"),
                    }
                })
            except Exception as e:
                print(f"     mf {m['namespace']}.{m['key']} failed: {e}")

        # reapply variant metafields + set inventory to 9999 on each variant
        for vi, new_v in enumerate(created["variants"]):
            # find any source mfs for this variant index
            for idx, mfs in variant_mf_map:
                if idx == vi:
                    for m in mfs:
                        try:
                            call(dst_shop, dst_tok, "POST", f"/variants/{new_v['id']}/metafields.json", {
                                "metafield": {
                                    "namespace": m["namespace"],
                                    "key": m["key"],
                                    "value": m["value"],
                                    "type": m.get("type", "single_line_text_field"),
                                }
                            })
                        except Exception as e:
                            print(f"     vmf {m['namespace']}.{m['key']} failed: {e}")

            # connect + set inventory
            try:
                call(dst_shop, dst_tok, "POST", "/inventory_levels/connect.json", {
                    "location_id": dst_loc["id"],
                    "inventory_item_id": new_v["inventory_item_id"],
                })
                call(dst_shop, dst_tok, "POST", "/inventory_levels/set.json", {
                    "location_id": dst_loc["id"],
                    "inventory_item_id": new_v["inventory_item_id"],
                    "available": 9999,
                })
            except Exception as e:
                print(f"     inventory set failed: {e}")

        results.append({
            "title": title,
            "src_id": sp["id"],
            "dst_id": new_id,
            "variants": [{"src": s["id"], "dst": d["id"], "weight": d["weight"], "unit": d["weight_unit"]}
                         for s, d in zip(sp["variants"], created["variants"])],
        })
        time.sleep(0.6)

    out = os.path.join(os.path.dirname(__file__), "migrate_packaging_to_indiapost_result.json")
    with open(out, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nDone. Wrote {out}")
    ok = sum(1 for r in results if "dst_id" in r)
    print(f"Created {ok}/{len(results)} products")


if __name__ == "__main__":
    main()
