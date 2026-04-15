"""
Scrape MCSL-specific KB articles from PluginHive.
Extracts article body content only — no navigation, no WooCommerce/Magento noise.
Saves clean markdown files to docs/kb_snapshots/.
"""

import os
import re
import time
import requests
import html2text
from bs4 import BeautifulSoup
from pathlib import Path

# All MCSL-specific KB URLs (provided by user)
# Note: seq_no variants are the same article — deduplicated below
URLS = [
    "https://www.pluginhive.com/knowledge-base/shopify-order-fulfilment-with-touchless-label-printing/",
    "https://www.pluginhive.com/knowledge-base/setting-up-shopify-multi-carrier-shipping-label-app/",
    "https://www.pluginhive.com/knowledge-base/set-up-shopify-purolator-shipping-with-the-multi-carrier-shipping-label-app/",
    "https://www.pluginhive.com/knowledge-base/shopify-carrier-calculated-shipping-rates/",
    "https://www.pluginhive.com/knowledge-base/open-a-free-ups-account-in-europe/",
    "https://www.pluginhive.com/knowledge-base/shopify-ups-shipping/",
    "https://www.pluginhive.com/knowledge-base/shopify-usps-shipping/",
    "https://www.pluginhive.com/knowledge-base/fedex-hold-at-location-at-shopify-checkout/",
    "https://www.pluginhive.com/knowledge-base/shopify-stamps-usps-shipping/",
    "https://www.pluginhive.com/knowledge-base/integrate-usps-easypost-on-shopify/",
    "https://www.pluginhive.com/knowledge-base/create-usps-account-for-shopify/",
    "https://www.pluginhive.com/knowledge-base/amazon-shipping-guide-for-shopify/",
    "https://www.pluginhive.com/knowledge-base/troubleshooting-shopify-multi-carrier-shipping-label-app/",
    "https://www.pluginhive.com/knowledge-base/configure-carrier-account-in-shopify-multi-carrier-shipping-label-app/",
    "https://www.pluginhive.com/knowledge-base/packing-methods-shopify-multi-carrier-shipping-label-app/",
    "https://www.pluginhive.com/knowledge-base/shipping-costs-based-on-shopify-shipping-zones/",
    "https://www.pluginhive.com/knowledge-base/customs-amount-on-commercial-invoice/",
    "https://www.pluginhive.com/knowledge-base/product-descriptions-on-commercial-invoice/",
    "https://www.pluginhive.com/knowledge-base/shipping-labels-for-shopify-flat-rate-shipping/",
    "https://www.pluginhive.com/knowledge-base/shopify-postnord-service-point/",
    "https://www.pluginhive.com/knowledge-base/shopify-alcohol-shipping-with-adult-signature/",
    "https://www.pluginhive.com/knowledge-base/how-to-split-and-partially-fulfil-shopify-orders/",
    "https://www.pluginhive.com/knowledge-base/create-and-ship-custom-items-in-shopify/",
    "https://www.pluginhive.com/knowledge-base/shopify-multi-carrier-shipping-label-app-faqs/",
    "https://www.pluginhive.com/knowledge-base/shopify-india-ups-international-shipping/",
    "https://www.pluginhive.com/knowledge-base/shopify-eu-shipping-print-tax-identification-numbers-on-labels/",
]

OUTPUT_DIR = Path(__file__).parent.parent / "docs" / "kb_snapshots"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# Article body CSS selectors to try in order
ARTICLE_SELECTORS = [
    "#eckb-article-content",
    ".eckb-article-content",
    ".epkb-article__content",
    ".epkb-article-content",
    ".entry-content",
    "article .content",
    "article",
    ".post-content",
    "main article",
]

# Noise selectors to remove before extraction
NOISE_SELECTORS = [
    "nav", "header", "footer",
    ".eckb-article-navigation", ".epkb-navigation",
    ".eckb-sidebar", ".epkb-sidebar",
    ".eckb-breadcrumb", ".epkb-breadcrumb",
    ".eckb-search", ".epkb-search",
    ".eckb-categories", ".epkb-categories",
    ".eckb-article-list", ".epkb-article-list",
    ".widget", ".sidebar",
    "#comments", ".comments",
    ".related-posts", ".wp-block-related-posts",
    "script", "style", "noscript",
    ".cookie-notice", ".gdpr",
]

h = html2text.HTML2Text()
h.ignore_links = False
h.ignore_images = True
h.ignore_emphasis = False
h.body_width = 0
h.protect_links = False


def url_to_filename(url: str) -> str:
    """Convert URL to a clean snake_case filename."""
    slug = url.rstrip("/").split("/")[-1]
    slug = re.sub(r"[^a-z0-9-]", "-", slug.lower())
    slug = re.sub(r"-+", "-", slug).strip("-")
    return f"{slug}.md"


def extract_article_content(soup: BeautifulSoup, url: str) -> str:
    """Extract article body only. Remove all navigation/noise."""
    # Remove noise elements first
    for sel in NOISE_SELECTORS:
        for el in soup.select(sel):
            el.decompose()

    # Try each article selector
    for sel in ARTICLE_SELECTORS:
        article = soup.select_one(sel)
        if article and len(article.get_text(strip=True)) > 200:
            return str(article)

    # Fallback: get main tag or body
    main = soup.find("main") or soup.find("body")
    return str(main) if main else ""


def scrape_url(url: str) -> tuple[str, str]:
    """Return (title, markdown_content) for a URL."""
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # Get page title
    title_tag = soup.find("h1") or soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else url.split("/")[-2]

    # Extract article content
    article_html = extract_article_content(soup, url)

    # Convert to markdown
    markdown = h.handle(article_html)

    # Clean up: remove excessive blank lines
    markdown = re.sub(r"\n{3,}", "\n\n", markdown).strip()

    return title, markdown


def build_file_content(url: str, title: str, markdown: str) -> str:
    """Wrap markdown with source metadata header."""
    return f"""# {title}

**Source:** {url}
**App:** Shopify Multi Carrier Shipping Label App (MCSL)
**Note:** Some screenshots may show older app UI — all text content is current.

---

{markdown}
"""


def main():
    seen_slugs = set()
    results = []

    for url in URLS:
        slug = url_to_filename(url)

        # Skip duplicate slugs (e.g. same page with ?seq_no=)
        base_slug = slug.split("?")[0]
        if base_slug in seen_slugs:
            print(f"  SKIP (duplicate): {url}")
            continue
        seen_slugs.add(base_slug)

        print(f"  Fetching: {url}")
        try:
            title, markdown = scrape_url(url)

            if len(markdown.strip()) < 100:
                print(f"    WARNING: Very short content ({len(markdown)} chars) — may be JS-rendered")
                results.append((slug, url, title, markdown, "short"))
            else:
                results.append((slug, url, title, markdown, "ok"))

            time.sleep(0.8)  # polite delay

        except Exception as e:
            print(f"    ERROR: {e}")
            results.append((slug, url, url.split("/")[-2], f"Error fetching: {e}", "error"))

    # Write files
    print(f"\nWriting {len(results)} files to {OUTPUT_DIR}...\n")
    for slug, url, title, markdown, status in results:
        out_path = OUTPUT_DIR / slug
        content = build_file_content(url, title, markdown)
        out_path.write_text(content, encoding="utf-8")
        chars = len(markdown)
        print(f"  {'✓' if status == 'ok' else '⚠'} {slug} ({chars:,} chars)")

    print(f"\nDone. {sum(1 for *_, s in results if s == 'ok')} ok, "
          f"{sum(1 for *_, s in results if s == 'short')} short, "
          f"{sum(1 for *_, s in results if s == 'error')} errors.")


if __name__ == "__main__":
    main()
