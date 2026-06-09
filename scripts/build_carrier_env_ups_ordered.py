"""Build a carrier-env file for a target store with products listed in the
EXACT SAME SEQUENCE as packaging-ups.env (the team's canonical ordering).

Why this matters: the automation's packaging tests in
`tests/packagingTypes/*.spec.ts` reference products by INDEX into
SIMPLE_PRODUCTS / VARIABLE_PRODUCTS / DIGITAL_PRODUCTS arrays (e.g.
`{ productType: 'simple', productCount: 6, quantities: [2] }` picks
SIMPLE_PRODUCTS[5]). For those tests to run identically against any
new store, the array sequence must match UPS's canonical ordering.

Algorithm:
  1. Parse the canonical env (default: carrier-envs/packaging-ups.env)
     for SIMPLE / VARIABLE / DIGITAL arrays.
  2. For each (product_id, variant_id) entry, hit the SOURCE store and
     resolve it to (product_title, variant_option_signature). That gives
     the canonical sequence.
  3. On the TARGET store, build a title → product lookup.
  4. Emit the env file: each canonical entry → target store's
     (product_id, variant_id), matched by title + option-triplet.

Usage:
  python3 scripts/build_carrier_env_ups_ordered.py \\
      --target-store dhl-express-automation \\
      --target-token shpat_xxxxxxxxxxxxxxxx \\
      --carrier dhl-express-rest \\
      --output /path/to/carrier-envs/dhl-express-automation-rest.env

Optional:
  --source-env  (default: mcsl-test-automation/carrier-envs/packaging-ups.env)
  --source-store / --source-token (default: parsed from --source-env)
  --source-api-version (default: parsed from --source-env, fallback 2023-01)
  --target-api-version (default: 2026-04)
  --user-email / --user-password / --store-password / --slack-webhook
        (defaults: parsed from --source-env)

Caveats — flagged at the end of the run:
  * Canonical entries whose underlying variant has been DELETED on the
    source store fall back to single-variant matching by title. Stop
    and re-check those rows manually if you see them flagged.
  * Multi-variant products where the option triplet doesn't match on
    the target store get skipped with a warning — the target needs
    matching option values.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
import time
from pathlib import Path

import requests


# ─── env-file parsing helpers ────────────────────────────────────────────────
def parse_env_file(path: Path) -> dict[str, str]:
    out = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        out[k.strip()] = v.strip().strip("'\"")
    return out


def parse_env_array(env_text: str, key: str) -> list[dict]:
    m = re.search(rf"^{key}='?(\[.*?\])'?$", env_text, re.M)
    return json.loads(m.group(1)) if m else []


# ─── Shopify helpers (with retry against TLS hiccups) ────────────────────────
def hdr(token: str) -> dict[str, str]:
    return {"X-Shopify-Access-Token": token, "Content-Type": "application/json"}


def fetch_product(store: str, version: str, token: str, pid: int, retries: int = 3):
    last_exc = None
    for attempt in range(retries):
        try:
            r = requests.get(
                f"https://{store}.myshopify.com/admin/api/{version}/products/{pid}.json",
                headers=hdr(token),
                timeout=20,
            )
            if r.status_code == 404:
                return None
            r.raise_for_status()
            return r.json().get("product")
        except Exception as exc:
            last_exc = exc
            time.sleep(1.5 * (attempt + 1))
    print(f"  ⚠️  fetch failed for {pid} on {store} after {retries} retries: {last_exc}",
          file=sys.stderr)
    return None


def all_products(store: str, version: str, token: str) -> list[dict]:
    out, url = [], f"https://{store}.myshopify.com/admin/api/{version}/products.json?limit=250"
    while url:
        r = requests.get(url, headers=hdr(token), timeout=30)
        r.raise_for_status()
        out.extend(r.json().get("products", []))
        link = r.headers.get("Link", "")
        nxt = next((p for p in link.split(",") if 'rel="next"' in p), None)
        url = nxt.split("<", 1)[1].split(">", 1)[0] if nxt else None
    return out


# ─── core resolution ─────────────────────────────────────────────────────────
SINGLE_SIG = ("__default__",)


def source_lookup(p: dict, vid: int) -> tuple[str, tuple | None]:
    """Return (title, variant_signature) for an entry on the source store."""
    if not p:
        return None, None
    title = p["title"]
    variants = p.get("variants", [])
    var = next((v for v in variants if int(v["id"]) == int(vid)), None)
    if not var:
        # variant deleted on source — fall back if product is currently single-variant
        if len(variants) == 1:
            return title, SINGLE_SIG
        return title, None
    sig = (var.get("option1"), var.get("option2"), var.get("option3"))
    if all(s in (None, "Default Title") for s in sig):
        sig = SINGLE_SIG
    return title, sig


def target_lookup(by_title: dict[str, dict], title: str, sig: tuple | None) -> dict | None:
    p = by_title.get(title)
    if not p:
        return None
    if sig == SINGLE_SIG or sig is None:
        variants = p.get("variants", [])
        if not variants:
            return None
        return {"product_id": int(p["id"]), "variant_id": int(variants[0]["id"])}
    for v in p.get("variants", []):
        v_sig = (v.get("option1"), v.get("option2"), v.get("option3"))
        if v_sig == sig:
            return {"product_id": int(p["id"]), "variant_id": int(v["id"])}
    return None


def jline(arr: list[dict]) -> str:
    return "'" + json.dumps(arr, separators=(",", ":")) + "'"


# ─── main ────────────────────────────────────────────────────────────────────
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("Usage:")[0])
    ap.add_argument("--target-store", required=True, help="Target Shopify store slug (e.g. dhl-express-automation)")
    ap.add_argument("--target-token", required=True, help="shpat_* Admin API token for the target store")
    ap.add_argument("--carrier",     required=True, help="CARRIER value to write into the env file")
    ap.add_argument("--output",      required=True, type=Path, help="Destination path for the env file")

    # Derive from config.MCSL_AUTOMATION_REPO_PATH (env-driven via .env so
    # this works on every team member's machine, not just one laptop).
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    import config  # noqa: E402
    default_source_env = Path(config.MCSL_AUTOMATION_REPO_PATH) / "carrier-envs" / "packaging-ups.env"
    ap.add_argument("--source-env", type=Path, default=default_source_env,
                    help="Canonical env file to copy ordering from (default: packaging-ups.env)")
    ap.add_argument("--source-store",        default=None)
    ap.add_argument("--source-token",        default=None)
    ap.add_argument("--source-api-version",  default=None)

    ap.add_argument("--target-api-version", default="2026-04")

    # Optional metadata overrides (otherwise inherited from source env)
    ap.add_argument("--user-email",     default=None)
    ap.add_argument("--user-password",  default=None)
    ap.add_argument("--store-password", default=None)
    ap.add_argument("--slack-webhook",  default=None)
    ap.add_argument("--partner-url",    default="https://dev.shopify.com/dashboard/129786666/stores")
    ap.add_argument("--country",        default="US",
                    help="ISO 2-letter country for SHIPPING_ADDRESS_JSON default (US, IN, AU, CA, GB, NZ). "
                         "Defaults to US.")
    ap.add_argument("--ai-enabled",     default="false", choices=["true", "false"],
                    help="Value for AI_ENABLED env field (always 'false' in all observed carrier-envs).")

    args = ap.parse_args()

    if not args.source_env.exists():
        print(f"ERROR: source env file not found: {args.source_env}", file=sys.stderr)
        return 2

    source_text = args.source_env.read_text()
    source_env  = parse_env_file(args.source_env)

    src_store = args.source_store        or source_env.get("SHOPIFY_STORE_NAME", "")
    src_token = args.source_token        or source_env.get("SHOPIFY_ACCESS_TOKEN", "")
    src_v     = args.source_api_version  or source_env.get("SHOPIFY_API_VERSION", "2023-01")
    if not (src_store and src_token):
        print("ERROR: could not derive source store/token. Pass --source-store/--source-token.",
              file=sys.stderr)
        return 2

    canonical = {
        "simple":   parse_env_array(source_text, "SIMPLE_PRODUCTS_JSON"),
        "variable": parse_env_array(source_text, "VARIABLE_PRODUCTS_JSON"),
        "digital":  parse_env_array(source_text, "DIGITAL_PRODUCTS_JSON"),
    }
    for cat, arr in canonical.items():
        print(f"canonical {cat:8s}: {len(arr)} entries from {args.source_env.name}")

    # Resolve each canonical entry → (title, sig) via source store
    print("\nResolving canonical entries against source store…")
    source_cache: dict[int, dict] = {}
    ordered: dict[str, list[tuple[str, tuple | None]]] = {"simple": [], "variable": [], "digital": []}
    unresolved = []
    for cat, arr in canonical.items():
        for entry in arr:
            pid, vid = int(entry["product_id"]), int(entry["variant_id"])
            if pid not in source_cache:
                source_cache[pid] = fetch_product(src_store, src_v, src_token, pid)
            title, sig = source_lookup(source_cache[pid], vid)
            if title is None:
                unresolved.append((cat, pid, vid))
                continue
            ordered[cat].append((title, sig))
    if unresolved:
        print(f"\n⚠️  {len(unresolved)} canonical entries unresolvable on source store:")
        for cat, pid, vid in unresolved:
            print(f"    [{cat}] product_id={pid} variant_id={vid}")

    # Build target store title → product lookup
    print(f"\nFetching all products on target store '{args.target_store}'…")
    target_products = all_products(args.target_store, args.target_api_version, args.target_token)
    by_title = {p["title"]: p for p in target_products}
    print(f"  target has {len(target_products)} products")

    # Map canonical sequence → target IDs
    result: dict[str, list[dict]] = {"simple": [], "variable": [], "digital": []}
    missing = []
    trace = []
    for cat, sigs in ordered.items():
        for i, (title, sig) in enumerate(sigs):
            m = target_lookup(by_title, title, sig)
            if m:
                result[cat].append(m)
                trace.append((cat, i, title, sig, m["product_id"], m["variant_id"], "ok"))
            else:
                missing.append((cat, title, sig))
                trace.append((cat, i, title, sig, None, None, "MISS"))

    print("\n=== mapping trace ===")
    for cat, i, title, sig, pid, vid, status in trace:
        sig_str = "single" if sig == SINGLE_SIG else "/".join(str(s) for s in (sig or ()) if s)
        if status == "ok":
            print(f"  [{cat[0].upper()}{i:02d}] {title[:38]:38s} ({sig_str:20s}) → p={pid} v={vid}")
        else:
            print(f"  [{cat[0].upper()}{i:02d}] {title[:38]:38s} ({sig_str:20s}) → ⚠️  no match on target")

    print(f"\nMatched: SIMPLE={len(result['simple'])}  VARIABLE={len(result['variable'])}  "
          f"DIGITAL={len(result['digital'])}")
    print(f"Canonical: SIMPLE={len(canonical['simple'])}  VARIABLE={len(canonical['variable'])}  "
          f"DIGITAL={len(canonical['digital'])}")
    if missing:
        print(f"\n{len(missing)} entries failed to match on target store — env will be SHORTER than canonical.")
        for cat, title, sig in missing:
            print(f"    [{cat}] '{title}' sig={sig}")

    # Compose the env
    user_email     = args.user_email     or source_env.get("USER_EMAIL", "")
    user_password  = args.user_password  or source_env.get("USER_PASSWORD", "")
    store_password = args.store_password or source_env.get("STORE_PASSWORD", "")
    slack_webhook  = args.slack_webhook  or source_env.get("SLACK_WEBHOOK_URL", "")

    # Country-aware SHIPPING_ADDRESS_JSON. Reuse the canonical map in
    # pipeline.new_carrier_validation so it stays consistent across builders.
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from pipeline.new_carrier_validation import default_shipping_address
    address = default_shipping_address(args.country)
    address_json = "'" + json.dumps(address, separators=(",", ":")) + "'"

    env = f"""CARRIER={args.carrier}
SLACK_WEBHOOK_URL={slack_webhook}
PARTNER_URL={args.partner_url}
SHOPIFYURL=https://admin.shopify.com/store/{args.target_store}
APPURL=https://admin.shopify.com/store/{args.target_store}/apps/mcsl-qa
USER_EMAIL={user_email}
USER_PASSWORD={user_password}
STORE_PASSWORD={store_password}
SHOPIFY_API_VERSION={args.target_api_version}
SHOPIFY_STORE_NAME={args.target_store}
SHOPIFY_ACCESS_TOKEN={args.target_token}
SIMPLE_PRODUCTS_JSON={jline(result['simple'])}
VARIABLE_PRODUCTS_JSON={jline(result['variable'])}
DIGITAL_PRODUCTS_JSON={jline(result['digital'])}
SHIPPING_ADDRESS_JSON={address_json}
AI_ENABLED={args.ai_enabled}
"""

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(env)
    print(f"\n✓ Wrote env to {args.output}")
    return 0 if not missing else 3   # exit 3 = wrote env but with gaps


if __name__ == "__main__":
    raise SystemExit(main())
