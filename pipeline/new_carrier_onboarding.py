"""Shopify Partner onboarding runner for new-carrier validation."""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
import textwrap
import time
from dataclasses import dataclass
from pathlib import Path

import config

DEFAULT_PARTNER_STORES_URL = "https://dev.shopify.com/dashboard/129786666/stores"
DEFAULT_PARTNER_APPS_URL = "https://dev.shopify.com/dashboard/129786666/apps"
DEFAULT_APP_CARD_ID = "app_card_6038317"
# Merchant-side app slug, used to build the store admin URL where the QA app
# lives (e.g. https://admin.shopify.com/store/<slug>/apps/mcsl-qa).
# NOTE: The Partner-side slug shown on dev.shopify.com (currently "mcsl-qa-4")
# is different — it's the Partner dashboard's app identifier, not the URL the
# merchant uses to reach the installed app. Existing carrier-envs/*.env all
# use "mcsl-qa" so we match that.
DEFAULT_APP_SLUG = "mcsl-qa"

DEFAULT_DEV_APP_NAME = "MCSL-Automation-Token"
DEFAULT_ADMIN_SCOPES: tuple[str, ...] = (
    "read_products", "write_products",
    "read_orders", "write_orders", "read_all_orders",
    "read_draft_orders", "write_draft_orders",
    "read_inventory", "write_inventory",
    "read_locations",
    "read_fulfillments", "write_fulfillments",
    "read_merchant_managed_fulfillment_orders", "write_merchant_managed_fulfillment_orders",
    "read_assigned_fulfillment_orders", "write_assigned_fulfillment_orders",
    "read_shipping", "write_shipping",
    "read_customers", "write_customers",
    "read_files", "write_files",
    "read_metaobjects", "write_metaobjects",
    "read_returns", "write_returns",
)
DEFAULT_STOREFRONT_SCOPES: tuple[str, ...] = ()


@dataclass(frozen=True)
class NewCarrierOnboardingResult:
    store_name: str
    store_created: bool
    app_installed: bool
    shopify_url: str
    app_url: str
    stdout: str
    stderr: str
    returncode: int
    started_at: float
    finished_at: float

    @property
    def duration_seconds(self) -> float:
        return max(0.0, self.finished_at - self.started_at)


def _automation_repo() -> Path:
    repo = Path(config.MCSL_AUTOMATION_REPO_PATH).expanduser().resolve()
    if not repo.exists():
        raise FileNotFoundError(f"Automation repo not found: {repo}")
    return repo


def _build_onboarding_script() -> str:
    return textwrap.dedent(
        """
        import { chromium } from 'playwright';
        import fs from 'node:fs';

        const storeName = process.env.NEW_CARRIER_STORE_NAME;
        const partnerStoresUrl = process.env.NEW_CARRIER_PARTNER_STORES_URL;
        const partnerAppsUrl = process.env.NEW_CARRIER_PARTNER_APPS_URL;
        const userEmail = process.env.USER_EMAIL || '';
        const shopifyUserEmail = process.env.SHOPIFY_EMAIL || userEmail;
        const appCardId = process.env.NEW_CARRIER_APP_CARD_ID || 'app_card_6038317';
        const appSearchName = process.env.NEW_CARRIER_APP_SEARCH || 'QA-MultiCarrier Shipping Label';
        const appSlug = process.env.NEW_CARRIER_APP_SLUG || 'mcsl-qa';
        const storagePath = process.env.NEW_CARRIER_STORAGE_PATH || './auth-chrome.json';
        const planName = process.env.NEW_CARRIER_SHOPIFY_PLAN || 'Advanced';

        if (!storeName) {
          throw new Error('NEW_CARRIER_STORE_NAME is required');
        }

        async function waitBestEffort(page, ms) {
          try {
            await page.waitForTimeout(ms);
          } catch {}
        }

        async function clickAccountCard(page) {
          await page.waitForLoadState('domcontentloaded').catch(() => {});
          const headings = page.getByRole('heading', { name: 'Choose an account' });
          const chooseVisible = await headings.first().isVisible().catch(() => false);
          if (!chooseVisible) return;
          const emailToUse = shopifyUserEmail || userEmail;
          let accountCard = page.locator('a.choose-account-card').filter({ hasText: emailToUse });
          if (await accountCard.count() === 0) {
            accountCard = page.locator('a.choose-account-card').first();
          }
          if (await accountCard.count() > 0) {
            await accountCard.first().click();
            await page.waitForLoadState('domcontentloaded').catch(() => {});
          }
        }

        async function maybeFillOnboarding(page) {
          // The QA app's onboarding form renders inside iframe[name="app-iframe"]
          // AFTER the recurring-charge approval. It can take 5–30s to appear.
          // Fixed-wait + early-return (the old logic) silently missed the form
          // when it rendered later than expected. Wait explicitly.
          const frame = page.frameLocator('iframe[name="app-iframe"]');

          // Wait for either Submit button OR the Start button OR the main app
          // shell (Menu) — whichever appears first. If Menu, onboarding was
          // already completed by an earlier session and we have nothing to do.
          const submit  = frame.getByRole('button', { name: 'Submit' }).first();
          const startBtn= frame.getByRole('button', { name: 'Start' }).first();
          const menuBtn = frame.getByRole('button', { name: 'Menu' }).first();

          let saw = '';
          for (let waited = 0; waited < 45000; waited += 1500) {
            if (await submit.count())   { saw = 'submit'; break; }
            if (await startBtn.count()) { saw = 'start';  break; }
            if (await menuBtn.count())  { saw = 'menu';   break; }
            await page.waitForTimeout(1500);
          }
          if (!saw) {
            console.log('[onboarding] never saw Submit / Start / Menu within 45s — leaving as-is');
            return;
          }
          if (saw === 'menu') {
            console.log('[onboarding] already onboarded (Menu visible) — skipping');
            return;
          }

          if (saw === 'submit') {
            // The actual DOM uses input[type="text"] (NOT email/tel) with
            // semantic name attributes. Locator must match by name=, not type=.
            const emailBox = frame.locator(
              'input[name="email"], input[placeholder="john@gmail.com"]'
            ).first();
            const phoneBox = frame.locator(
              'input[name="phoneNumber"], input[placeholder="7567812342"]'
            ).first();
            const checkbox = frame.locator('input[type="checkbox"]').first();
            // Wait briefly for inputs to render
            await emailBox.waitFor({ state: 'visible', timeout: 10000 }).catch(() => {});
            if (await emailBox.count()) await emailBox.fill('qa.test@pluginhive.com').catch(() => {});
            if (await phoneBox.count()) await phoneBox.fill('1234567890').catch(() => {});
            if (await checkbox.count()) await checkbox.check({ force: true }).catch(() => {});
            // The Submit button starts `disabled`; wait for it to become enabled
            // after the form gates validate (email + phone + checkbox).
            try {
              await submit.waitFor({ state: 'visible', timeout: 5000 });
              for (let waited = 0; waited < 15000; waited += 500) {
                const isDisabled = await submit.isDisabled().catch(() => true);
                if (!isDisabled) break;
                await page.waitForTimeout(500);
              }
            } catch {}
            await submit.click({ timeout: 10000 }).catch(() => {});
            console.log('[onboarding] form submitted');
          }

          // Wait up to 30s for Start button to appear after Submit
          for (let waited = 0; waited < 30000; waited += 1500) {
            if (await startBtn.count()) {
              await startBtn.click({ timeout: 10000 }).catch(() => {});
              console.log('[onboarding] Start clicked');
              break;
            }
            if (await menuBtn.count()) {
              console.log('[onboarding] Menu appeared — onboarding fully complete');
              break;
            }
            await page.waitForTimeout(1500);
          }
        }

        const browser = await chromium.launch({
          channel: 'chrome',
          headless: false,
          args: ['--disable-blink-features=AutomationControlled', '--window-size=1400,1000'],
        });

        const contextOptions = {};
        if (fs.existsSync(storagePath)) {
          contextOptions.storageState = storagePath;
        }
        const context = await browser.newContext(contextOptions);
        const page = await context.newPage();

        let created = false;
        let installed = false;

        try {
          await page.goto(partnerStoresUrl, { waitUntil: 'domcontentloaded', timeout: 120000 });
          await clickAccountCard(page);

          // Shopify renamed this CTA: 'Add dev store' (legacy) → 'Create store'
          // (current Partner dashboard). It's also rendered as a button now,
          // not a link, in the new shell. Try the new name first across both
          // roles, then fall back to the legacy name.
          async function findCreateStoreCta() {
            const candidates = [
              page.getByRole('button', { name: 'Create store', exact: true }),
              page.getByRole('link',   { name: 'Create store', exact: true }),
              page.getByRole('button', { name: 'Add dev store' }),
              page.getByRole('link',   { name: 'Add dev store' }),
            ];
            for (const c of candidates) {
              if (await c.first().count()) {
                await c.first().waitFor({ state: 'visible', timeout: 30000 }).catch(() => {});
                return c.first();
              }
            }
            return null;
          }
          const addStoreLink = await findCreateStoreCta();
          if (!addStoreLink) {
            throw new Error('Could not find Create store / Add dev store CTA on ' + page.url());
          }
          const popupPromise = page.waitForEvent('popup');
          await addStoreLink.click();
          const storePopup = await popupPromise;
          await storePopup.waitForLoadState('domcontentloaded', { timeout: 60000 }).catch(() => {});

          // Shopify added a "store type" chooser as the first step inside the
          // store-create page: Dev (testing/staging) vs Client transfer.
          // Clicking the Dev tile expands the name+plan form INLINE on the
          // same page — there is no intermediate submit. The bottom-right
          // "Create store" button stays greyed out until name+plan are filled.
          //
          // The tile is rendered as a clickable card containing both a "Dev"
          // heading and the description "Testing, dev, or staging environments".
          // Match by the unique description text since "Dev" alone is ambiguous
          // (it appears as the partner-account chip and the tile heading).
          await waitBestEffort(storePopup, 2500);
          const devDescription = /Testing,?\\s+dev,?\\s+or\\s+staging\\s+environments/i;
          let devClicked = false;
          const devCandidates = [
            // 1. Whole card by role + description as accessible name
            storePopup.getByRole('button', { name: devDescription }).first(),
            storePopup.getByRole('radio',  { name: devDescription }).first(),
            storePopup.getByRole('link',   { name: devDescription }).first(),
            // 2. Description text itself (will likely click a parent due to event bubbling)
            storePopup.getByText(devDescription).first(),
            // 3. Card with text content matching
            storePopup.locator('[role="button"], [role="radio"], a, label, button')
              .filter({ hasText: devDescription }).first(),
            // 4. Bare "Dev" heading as last resort
            storePopup.getByRole('heading', { name: /^Dev$/ }).first(),
          ];
          for (const sel of devCandidates) {
            if (await sel.count()) {
              try {
                await sel.scrollIntoViewIfNeeded({ timeout: 5000 }).catch(() => {});
                await sel.click({ timeout: 5000 });
                devClicked = true;
                break;
              } catch (e) { /* try next */ }
            }
          }
          if (!devClicked) {
            // Last-ditch DOM walker: click any element whose innerText contains
            // the unique description.
            const okJS = await storePopup.evaluate(() => {
              const all = document.querySelectorAll('*');
              for (const el of all) {
                const t = (el.textContent || '').trim();
                if (t && t.length < 200 &&
                    /Testing,?\\s+dev,?\\s+or\\s+staging\\s+environments/i.test(t)) {
                  let target = el;
                  // walk up until a clickable ancestor
                  for (let d = 0; d < 8 && target; d++) {
                    const role = target.getAttribute && target.getAttribute('role');
                    if (role === 'button' || role === 'radio' ||
                        target.tagName === 'BUTTON' || target.tagName === 'A' ||
                        target.tagName === 'LABEL') {
                      target.click();
                      return true;
                    }
                    target = target.parentElement;
                  }
                  el.click();
                  return true;
                }
              }
              return false;
            }).catch(() => false);
            devClicked = !!okJS;
          }
          await waitBestEffort(storePopup, 2000);

          // If we still couldn't click Dev, snapshot for diagnosis
          if (!devClicked) {
            try {
              const shot = '/tmp/mcsl_devtile_failed_' + Date.now() + '.png';
              await storePopup.screenshot({ path: shot, fullPage: true });
              console.error('Dev tile click failed — screenshot:', shot);
            } catch {}
            // Don't throw yet — the form may have been pre-populated; let the
            // nameField waitFor below decide whether we can proceed.
          }

          // Wait for the storeName input to appear (it's rendered after Dev tile
          // click). The new admin uses different attribute names than the old
          // legacy popup — try several locators.
          const nameField = storePopup.locator([
            'input[name="storeName"]',
            'input[name="name"]',
            'input[aria-label*="Store name" i]',
            'input[placeholder*="Store name" i]',
          ].join(', ')).first();
          await nameField.waitFor({ state: 'visible', timeout: 60000 });
          await nameField.fill(storeName);

          // Plan selector — try legacy <select>, then the new Polaris dropdown
          // (button labeled "Select a plan" → menu items by plan name).
          const planSelectLegacy = storePopup.locator('select[name="Shopify plan"], select[name="plan"]').first();
          if (await planSelectLegacy.count()) {
            await planSelectLegacy.selectOption(planName).catch(() => {});
          } else {
            // New Polaris dropdown
            const planBtn = storePopup.getByRole('button', { name: /Select a plan|Shopify plan/i }).first();
            if (await planBtn.count()) {
              await planBtn.click().catch(() => {});
              await waitBestEffort(storePopup, 1000);
              const planOption = storePopup.getByRole('option', { name: planName, exact: true }).first();
              if (await planOption.count()) {
                await planOption.click().catch(() => {});
              } else {
                // fallback: any clickable element with the plan text
                await storePopup.locator(`text="${planName}"`).first().click().catch(() => {});
              }
              await waitBestEffort(storePopup, 800);
            }
          }

          // Submit the form. Use a role+exact-name button locator because the
          // page now has BOTH a heading "Create store" and a button "Create
          // store" — plain getByText() returns a strict-mode violation.
          const submitBtn = storePopup.getByRole('button', { name: 'Create store', exact: true }).first();
          await submitBtn.waitFor({ state: 'visible', timeout: 30000 });
          await submitBtn.click();
          await clickAccountCard(storePopup);
          await waitBestEffort(storePopup, 12000);
          created = true;

          await page.goto(partnerAppsUrl, { waitUntil: 'domcontentloaded', timeout: 120000 });
          await clickAccountCard(page);

          const searchField = page.locator('#apps-search-input').first();
          await searchField.waitFor({ state: 'visible', timeout: 60000 });
          await searchField.fill(appSearchName);
          await waitBestEffort(page, 3000);

          const appCard = page.locator(`#${appCardId}`).first();
          await appCard.waitFor({ state: 'visible', timeout: 60000 });
          await appCard.click();

          const installLink = page.getByRole('link', { name: 'Install app' }).first();
          await installLink.waitFor({ state: 'visible', timeout: 60000 });
          const installPopupPromise = page.waitForEvent('popup');
          await installLink.click();
          const installPopup = await installPopupPromise;
          await installPopup.waitForLoadState('domcontentloaded', { timeout: 60000 }).catch(() => {});

          const storeSearch = installPopup.locator('#P0-0').first();
          await storeSearch.waitFor({ state: 'visible', timeout: 60000 });
          await storeSearch.fill(storeName);
          await waitBestEffort(installPopup, 8000);

          const filteredStore = installPopup.locator(`text="${storeName}"`).first();
          await filteredStore.waitFor({ state: 'visible', timeout: 60000 });
          await filteredStore.click();

          const proceed = installPopup.locator('#proceed_cta').first();
          await proceed.waitFor({ state: 'visible', timeout: 60000 });
          await proceed.click();
          await waitBestEffort(installPopup, 5000);

          // ── Three required steps after install ──────────────────────────
          //   a) Inside the app iframe: click "Select Plan" on the QA-Plan-3 card
          //      (MUST be picked by text, not nth(N) — the plan order changes
          //      as MCSL adds tiers).
          //   b) Wait for Shopify to redirect the popup to the recurring-charge
          //      confirmation page (leaves the iframe entirely).
          //   c) Click #approve-charges-button to approve the subscription.
          //   See memory: mcsl-qa-app-plan-approval.md
          // (renamed from `planName` to avoid TDZ collision with the Shopify
          //  plan `planName` declared at the top of this function scope.)
          const qaAppPlanName = process.env.NEW_CARRIER_PLAN_NAME || 'QA-Plan-3';
          const frame = installPopup.frameLocator('iframe[name="app-iframe"]');

          // Wait for the plan picker to render. The iframe lazily loads after
          // install — fixed waits cause races.
          await frame.locator(`text="${qaAppPlanName}"`).first()
            .waitFor({ state: 'visible', timeout: 45000 }).catch(() => {});

          // Click the "Select Plan" button INSIDE the card that contains the
          // qaAppPlanName text. Locator chaining: find a container with the
          // plan name, then locate the Select Plan button within it.
          let planClicked = false;
          try {
            const planCard = frame.locator(
              `:has-text("${qaAppPlanName}"):has(button:has-text("Select Plan"))`
            ).first();
            const selectBtn = planCard.getByRole('button', { name: 'Select Plan' }).first();
            if (await selectBtn.count()) {
              await selectBtn.click({ timeout: 10000 });
              planClicked = true;
            }
          } catch {}
          if (!planClicked) {
            // Fallback 1: enumerate Select Plan buttons and pick by sibling text
            const allPlanBtns = frame.getByRole('button', { name: 'Select Plan' });
            const count = await allPlanBtns.count();
            for (let i = 0; i < count; i++) {
              const btn = allPlanBtns.nth(i);
              // walk up to find a card-like ancestor and check text
              const cardText = await btn.evaluate((el) => {
                let p = el;
                for (let d = 0; d < 8 && p; d++) p = p.parentElement;
                return (p && p.textContent) || '';
              }).catch(() => '');
              if (cardText && cardText.includes(qaAppPlanName)) {
                await btn.click({ timeout: 10000 }).catch(() => {});
                planClicked = true;
                break;
              }
            }
          }
          if (!planClicked) {
            // Fallback 2: legacy behaviour (third card in default 4-plan layout)
            const fallback = frame.getByRole('button', { name: 'Select Plan' }).nth(2);
            if (await fallback.count()) {
              await fallback.click().catch(() => { planClicked = false; });
            }
          }

          // Wait for Shopify to navigate the popup to the recurring-charge
          // confirmation page (leaves the iframe). This is the readiness signal
          // for the Approve click.
          await installPopup.waitForURL(
            /\\/charges\\/.+\\/RecurringApplicationCharge\\/confirm_recurring_application_charge/,
            { timeout: 30000 }
          ).catch(() => {});
          await waitBestEffort(installPopup, 1500);

          // Approve the subscription — button id is stable across redesigns.
          const approve = installPopup.locator('#approve-charges-button').first();
          await approve.waitFor({ state: 'visible', timeout: 20000 }).catch(() => {});
          if (await approve.count()) {
            await approve.click({ timeout: 10000 }).catch(() => {});
          }

          // After approval, Shopify redirects back into the app. Give the iframe
          // a moment to load, then handle any post-approval onboarding form.
          await waitBestEffort(installPopup, 6000);
          await maybeFillOnboarding(installPopup);
          installed = true;

          // Capture the REALIZED slug — Shopify appends a random suffix to dev
          // store slugs (e.g. "EmailTest" → "emailtest-andyfh5i"). The install
          // popup has navigated to the merchant admin URL, which contains it.
          let realizedSlug = storeName;
          const candidateUrls = [
            installPopup.url(),
            storePopup.url(),
          ];
          for (const u of candidateUrls) {
            const m = u && u.match(/admin\\.shopify\\.com\\/store\\/([^\\/\\?#]+)/);
            if (m && m[1] && m[1] !== storeName) { realizedSlug = m[1]; break; }
          }

          const result = {
            store_name: realizedSlug,        // realized merchant slug
            input_name: storeName,           // what the user typed
            store_created: created,
            app_installed: installed,
            shopify_url: `https://admin.shopify.com/store/${realizedSlug}`,
            app_url: `https://admin.shopify.com/store/${realizedSlug}/apps/${appSlug}`,
          };
          console.log(JSON.stringify(result));
        } finally {
          await context.close().catch(() => {});
          await browser.close().catch(() => {});
        }
        """
    ).strip()


def create_store_and_install_app(
    *,
    store_name: str,
    partner_stores_url: str = DEFAULT_PARTNER_STORES_URL,
    partner_apps_url: str = DEFAULT_PARTNER_APPS_URL,
    app_search_name: str = "QA-MultiCarrier Shipping Label",
    app_card_id: str = DEFAULT_APP_CARD_ID,
    app_slug: str = DEFAULT_APP_SLUG,
    plan_name: str = "Advanced",
    timeout_seconds: int = 900,
) -> NewCarrierOnboardingResult:
    if not store_name.strip():
        raise ValueError("Store name is required")

    repo = _automation_repo()
    script = _build_onboarding_script()
    env = os.environ.copy()
    env.update(
        {
            "NEW_CARRIER_STORE_NAME": store_name.strip(),
            "NEW_CARRIER_PARTNER_STORES_URL": partner_stores_url.strip(),
            "NEW_CARRIER_PARTNER_APPS_URL": partner_apps_url.strip(),
            "NEW_CARRIER_APP_SEARCH": app_search_name,
            "NEW_CARRIER_APP_CARD_ID": app_card_id,
            "NEW_CARRIER_APP_SLUG": app_slug,
            "NEW_CARRIER_SHOPIFY_PLAN": plan_name,
            "NEW_CARRIER_STORAGE_PATH": getattr(
                config,
                "MCSL_CHROME_AUTH_PATH",
                str(repo / "auth-chrome.json"),
            ),
        }
    )

    started_at = time.time()
    with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False, dir=str(repo)) as handle:
        handle.write(script)
        temp_path = handle.name
    try:
        completed = subprocess.run(
            ["node", temp_path],
            cwd=str(repo),
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    finally:
        Path(temp_path).unlink(missing_ok=True)
    finished_at = time.time()

    stdout = completed.stdout or ""
    stderr = completed.stderr or ""
    if completed.returncode != 0:
        raise RuntimeError(stderr.strip() or stdout.strip() or "Store onboarding failed")

    lines = [line.strip() for line in stdout.splitlines() if line.strip()]
    payload = {}
    for line in reversed(lines):
        if line.startswith("{") and line.endswith("}"):
            payload = json.loads(line)
            break
    if not payload:
        raise RuntimeError("Store onboarding completed without structured result payload")

    return NewCarrierOnboardingResult(
        store_name=str(payload.get("store_name") or store_name),
        store_created=bool(payload.get("store_created")),
        app_installed=bool(payload.get("app_installed")),
        shopify_url=str(payload.get("shopify_url") or ""),
        app_url=str(payload.get("app_url") or ""),
        stdout=stdout,
        stderr=stderr,
        returncode=int(completed.returncode),
        started_at=started_at,
        finished_at=finished_at,
    )


@dataclass(frozen=True)
class DevAppTokenResult:
    store_name: str
    app_name: str
    app_id: str
    admin_token: str
    storefront_token: str
    granted_admin_scopes: tuple[str, ...]
    requested_admin_scopes: tuple[str, ...]
    missing_admin_scopes: tuple[str, ...]
    app_created: bool
    app_installed: bool
    token_revealed: bool
    stdout: str
    stderr: str
    returncode: int
    started_at: float
    finished_at: float

    @property
    def duration_seconds(self) -> float:
        return max(0.0, self.finished_at - self.started_at)


def _build_dev_app_script() -> str:
    return textwrap.dedent(
        """
        import { chromium } from 'playwright';
        import fs from 'node:fs';

        const storeName       = process.env.DEV_APP_STORE_NAME;
        const appName         = process.env.DEV_APP_NAME || 'MCSL-Automation-Token';
        const adminScopes     = (process.env.DEV_APP_ADMIN_SCOPES     || '').split(',').filter(Boolean);
        const storefrontScopes= (process.env.DEV_APP_STOREFRONT_SCOPES|| '').split(',').filter(Boolean);
        const storagePath     = process.env.DEV_APP_STORAGE_PATH || './auth-chrome.json';
        const tickAllScopes   = (process.env.DEV_APP_TICK_ALL_SCOPES || 'true') !== 'false';

        if (!storeName) throw new Error('DEV_APP_STORE_NAME is required');

        const devUrl = `https://admin.shopify.com/store/${storeName}/settings/apps/development`;

        async function wait(page, ms) { try { await page.waitForTimeout(ms); } catch {} }

        async function clickByText(page, text, opts) {
          // opts: { exact?: boolean, scope?: 'dialog' | 'page' }
          const exact = opts && opts.exact === true;
          const scopeDialog = opts && opts.scope === 'dialog';

          // Prefer a click inside an open dialog when scope='dialog' is requested
          // OR (default) when one is visible, since a modal usually owns the next action.
          const dialog = page.getByRole('dialog').first();
          const dialogVisible = await dialog.isVisible().catch(() => false);
          const searchRoots = [];
          if (dialogVisible || scopeDialog) searchRoots.push(dialog);
          searchRoots.push(page);

          for (const root of searchRoots) {
            for (const role of ['button', 'link']) {
              // Exact match first (so 'Install' won't pick up 'Install app')
              const exactEl = root.getByRole(role, { name: text, exact: true }).first();
              if (await exactEl.count()) {
                await exactEl.scrollIntoViewIfNeeded().catch(() => {});
                await exactEl.click().catch(() => {});
                return true;
              }
              if (!exact) {
                const looseEl = root.getByRole(role, { name: text, exact: false }).first();
                if (await looseEl.count()) {
                  await looseEl.scrollIntoViewIfNeeded().catch(() => {});
                  await looseEl.click().catch(() => {});
                  return true;
                }
              }
            }
          }
          // last resort: any element with that visible text
          const any = page.locator(`text=${JSON.stringify(text)}`).first();
          if (await any.count()) {
            await any.scrollIntoViewIfNeeded().catch(() => {});
            await any.click().catch(() => {});
            return true;
          }
          return false;
        }

        async function dumpDebug(page, label) {
          const url = page.url();
          const text = await page.locator('body').innerText().catch(() => '');
          return { label, url, page_text_snippet: (text || '').slice(0, 2000) };
        }

        async function tickAllCheckboxesOnPage(page) {
          // 'Select all' button if Shopify offers one
          for (const lbl of ['Select all', 'Select all permissions', 'Tick all']) {
            const btn = page.getByRole('button', { name: lbl, exact: false }).first();
            if (await btn.count()) {
              await btn.click().catch(() => {});
              await wait(page, 800);
              break;
            }
          }
          const boxes = page.locator('input[type="checkbox"]:not([disabled])');
          const total = await boxes.count();
          let tickedCount = 0;
          const tickedHandles = [];
          for (let i = 0; i < total; i++) {
            const box = boxes.nth(i);
            const checked = await box.isChecked().catch(() => false);
            if (!checked) {
              await box.check({ force: true }).catch(() => {});
              await wait(page, 30);
            }
            const nowChecked = await box.isChecked().catch(() => false);
            if (nowChecked) {
              tickedCount++;
              const handle = (await box.getAttribute('value').catch(() => null))
                          || (await box.getAttribute('name').catch(() => null))
                          || (await box.getAttribute('id').catch(() => null))
                          || '';
              if (handle) tickedHandles.push(handle);
            }
          }
          return { total, tickedCount, tickedHandles };
        }

        const browser = await chromium.launch({
          channel: 'chrome',
          headless: false,
          args: ['--disable-blink-features=AutomationControlled', '--window-size=1400,1000'],
        });

        const contextOptions = {};
        if (fs.existsSync(storagePath)) contextOptions.storageState = storagePath;
        const context = await browser.newContext(contextOptions);
        const page    = await context.newPage();

        let appCreated     = false;
        let appInstalled   = false;
        let tokenRevealed  = false;
        let appId          = '';
        let adminToken     = '';
        let storefrontToken= '';
        let grantedAdmin   = [];
        const debug        = [];

        try {
          await page.goto(devUrl, { waitUntil: 'domcontentloaded', timeout: 120000 });
          await wait(page, 4000);
          debug.push(await dumpDebug(page, 'after_goto_dev_url'));

          // ── Step 1: clear the legacy gate (Jan 1 2026 deprecation banner) ──
          // Two-stage gate on un-enabled stores:
          //   a) Click "Allow legacy custom app development" on /settings/apps/development
          //      → navigates to /settings/apps/development/enable
          //   b) Click "Allow custom app development" on the enable page
          //      → returns to /settings/apps/development with the gate open.
          // On already-enabled stores neither button is present; skip silently.
          if (await clickByText(page, 'Allow legacy custom app development')) {
            await page.waitForURL(/\\/apps\\/development\\/enable/, { timeout: 15000 }).catch(() => {});
            await wait(page, 1500);
            // confirm on /enable page (button label drops the "legacy" word)
            for (const lbl of ['Allow custom app development', 'Allow']) {
              if (await clickByText(page, lbl, { exact: true })) { break; }
            }
            await wait(page, 3000);
            await page.waitForURL(/\\/apps\\/development$/, { timeout: 15000 }).catch(() => {});
            await wait(page, 1500);
          }
          debug.push(await dumpDebug(page, 'after_gate'));

          // ── Step 2: open the Create-app form ──────────────────────────────
          // Three possible button labels depending on store state:
          //   - "Create a legacy custom app"  → first app on a freshly-enabled store
          //   - "Create an app"               → subsequent apps (apps list visible)
          //   - "Create app"                  → older admin versions
          for (const lbl of [
            'Create a legacy custom app',
            'Create an app',
            'Create app',
            'New app',
          ]) {
            if (await clickByText(page, lbl)) { await wait(page, 1500); break; }
          }
          debug.push(await dumpDebug(page, 'after_create_app_click'));

          const nameField = page.locator(
            'input[name="appName"], input[aria-label*="App name" i], input[placeholder*="App name" i]'
          ).first();
          await nameField.waitFor({ state: 'visible', timeout: 30000 });
          await nameField.fill(appName);
          // The submit button on this form is labeled "Create app" (no "an").
          // Match exactly so we don't fire the page's "Create an app" CTA.
          await clickByText(page, 'Create app', { exact: true });
          // Wait until the URL reflects the new app id, not just for DOMContentLoaded.
          await page.waitForURL(/\\/apps\\/development\\/\\d+/, { timeout: 30000 }).catch(() => {});
          await wait(page, 3000);
          appCreated = true;

          // Grab the app id from the URL → /apps/development/<APP_ID>/overview
          // Re-check up to 3 times in case the redirect chains.
          for (let attempt = 0; attempt < 3 && !appId; attempt++) {
            const m = page.url().match(/\\/apps\\/development\\/(\\d+)/);
            if (m) { appId = m[1]; break; }
            await wait(page, 1500);
          }
          if (!appId) {
            throw new Error('Failed to capture app_id after Create app — URL: ' + page.url());
          }
          debug.push(await dumpDebug(page, 'after_app_created'));

          // ── Step 3: Configure Admin API scopes — tick every checkbox ──────
          // Robust pattern: navigate explicitly, then waitFor the CTA to be
          // visible before clicking. Fixed waits cause races on the Polaris
          // admin where elements mount lazily.
          async function configureScopes(scopeKind /* 'Admin' | 'Storefront' */, debugLabel) {
            // The scope-config pages have STABLE direct URLs — way more
            // reliable than the "Configure ... API scopes" CTA on /overview
            // which only renders in certain admin states (and disappears
            // once the app is installed). Hit the URL directly.
            const slug = scopeKind === 'Admin' ? 'admin_api_integration' : 'storefront_api_integration';
            const directUrl = `${devUrl}/${appId}/configuration/${slug}`;
            await page.goto(directUrl, { waitUntil: 'networkidle', timeout: 60000 }).catch(() => {});

            // Wait for the scopes page to actually render at least one checkbox
            const anyCheckbox = page.locator('input[type="checkbox"]:not([disabled])').first();
            try {
              await anyCheckbox.waitFor({ state: 'visible', timeout: 25000 });
            } catch (e) {
              // Fallback: try the legacy CTA-on-overview path
              debug.push({ label: debugLabel + '_direct_url_failed', url: page.url() });
              await page.goto(`${devUrl}/${appId}/overview`, { waitUntil: 'networkidle' }).catch(() => {});
              const ctaName = `Configure ${scopeKind} API scopes`;
              const cta = page.getByRole('button', { name: ctaName, exact: true })
                .or(page.getByRole('link', { name: ctaName, exact: true }))
                .first();
              try {
                await cta.waitFor({ state: 'visible', timeout: 20000 });
                await cta.scrollIntoViewIfNeeded().catch(() => {});
                await cta.click();
                await anyCheckbox.waitFor({ state: 'visible', timeout: 20000 });
              } catch (e2) {
                debug.push({ label: debugLabel + '_cta_fallback_failed', url: page.url() });
                return { total: 0, tickedCount: 0, tickedHandles: [] };
              }
            }
            await wait(page, 1200);   // small settle for any lazy-loaded extras
            const ticks = await tickAllCheckboxesOnPage(page);
            const save = page.getByRole('button', { name: 'Save', exact: true }).first();
            await save.waitFor({ state: 'visible', timeout: 10000 }).catch(() => {});
            await save.click().catch(() => {});
            // wait for save to land — toast appears or URL stays put
            await wait(page, 3500);
            return ticks;
          }

          const adminTicks = await configureScopes('Admin', 'admin_scopes');
          grantedAdmin = adminTicks.tickedHandles;
          debug.push({
            label: 'admin_scopes_ticked',
            total_checkboxes: adminTicks.total,
            ticked: adminTicks.tickedCount,
          });

          // ── Step 4: (optional) Configure Storefront API scopes ────────────
          if (storefrontScopes.length || tickAllScopes) {
            const sfTicks = await configureScopes('Storefront', 'storefront_scopes');
            debug.push({
              label: 'storefront_scopes_ticked',
              total_checkboxes: sfTicks.total,
              ticked: sfTicks.tickedCount,
            });
          }

          // ── Step 5: Install app ───────────────────────────────────────────
          // Navigate explicitly and wait for the primary CTA to be visible.
          await page.goto(`${devUrl}/${appId}/overview`, { waitUntil: 'networkidle', timeout: 60000 }).catch(() => {});

          let installClicked = false;
          // Prefer the Polaris primary CTA in the body, then fall back to last
          // matching button, then any.
          const primaryInstall = page.locator(
            'button.Polaris-Button--variantPrimary, button.Polaris-Button--primary'
          ).filter({ hasText: /^Install app$/ }).first();
          const anyInstall = page.getByRole('button', { name: 'Install app', exact: true });

          // Wait for ANY install button to appear (whichever flavor)
          try {
            await Promise.race([
              primaryInstall.waitFor({ state: 'visible', timeout: 25000 }),
              anyInstall.first().waitFor({ state: 'visible', timeout: 25000 }),
            ]);
          } catch (e) {
            debug.push({ label: 'install_button_missing', url: page.url() });
          }

          if (await primaryInstall.count()) {
            await primaryInstall.scrollIntoViewIfNeeded().catch(() => {});
            await primaryInstall.click().catch(() => {});
            installClicked = true;
          } else {
            const count = await anyInstall.count();
            if (count > 0) {
              // last is usually the primary in DOM order
              await anyInstall.nth(count - 1).scrollIntoViewIfNeeded().catch(() => {});
              await anyInstall.nth(count - 1).click().catch(() => {});
              installClicked = true;
            }
          }

          // Wait for the consent dialog to render — explicit visibility wait
          // is the difference between a flaky click and a reliable one.
          const dialog = page.getByRole('dialog').first();
          let dialogVisible = false;
          try {
            await dialog.waitFor({ state: 'visible', timeout: 20000 });
            dialogVisible = true;
          } catch (e) {
            debug.push({ label: 'install_dialog_missing', url: page.url() });
          }

          let confirmed = false;
          if (dialogVisible) {
            for (const [lbl, exact] of [['Install', true], ['Install this app', true], ['Allow', true]]) {
              if (await clickByText(page, lbl, { exact, scope: 'dialog' })) { confirmed = true; break; }
            }
            // wait for dialog to dismiss as the install signal
            await dialog.waitFor({ state: 'hidden', timeout: 20000 }).catch(() => {});
          }
          await wait(page, 3000);

          // Verify install: the page should no longer show the install CTA
          const stillHasInstall = await page.getByRole('button', { name: /^Install app$/i }).first().count();
          appInstalled = installClicked && confirmed && stillHasInstall === 0;
          debug.push({
            label: 'after_install',
            url: page.url(),
            install_clicked: installClicked,
            dialog_appeared: dialogVisible,
            confirm_clicked: confirmed,
            install_still_present: stillHasInstall,
          });

          if (!appInstalled) {
            throw new Error('Install verification failed — see debug.after_install. The dev app exists ('
              + appId + ') but is NOT installed. Finish manually at '
              + devUrl + '/' + appId + '/overview');
          }

          // ── Step 6: API credentials → reveal token once ───────────────────
          await page.goto(`${devUrl}/${appId}/api_credentials`, { waitUntil: 'networkidle', timeout: 60000 }).catch(() => {});

          // Wait for the Reveal CTA to be visible (it's the readiness signal
          // that the API credentials panel has rendered).
          const revealCta = page.getByRole('button', { name: /^Reveal token once$/i })
            .or(page.getByRole('link', { name: /^Reveal token once$/i }))
            .first();
          try {
            await revealCta.waitFor({ state: 'visible', timeout: 20000 });
            await revealCta.click();
          } catch (e) {
            // some variants render as plain anchors with no role — fall through
            for (const lbl of ['Reveal token once', 'Reveal token', 'Reveal', 'Show token']) {
              if (await clickByText(page, lbl)) break;
            }
          }
          // After reveal click, wait for shpat_ to appear in the DOM
          try {
            await page.locator('text=/shpat_[A-Za-z0-9]{20,}/').first().waitFor({ state: 'visible', timeout: 10000 });
          } catch (e) {
            debug.push({ label: 'shpat_not_visible', url: page.url() });
          }
          const fullText = await page.content();
          const mm = fullText.match(/shpat_[A-Za-z0-9]{20,}/);
          if (mm) { adminToken = mm[0]; tokenRevealed = true; }

          if (storefrontScopes.length || tickAllScopes) {
            const sf = fullText.match(/[a-f0-9]{32}/);
            if (sf) storefrontToken = sf[0];
          }
          debug.push(await dumpDebug(page, 'after_reveal'));

          const result = {
            store_name: storeName,
            app_name: appName,
            app_id: appId,
            admin_token: adminToken,
            storefront_token: storefrontToken,
            granted_admin_scopes: grantedAdmin,
            app_created: appCreated,
            app_installed: appInstalled,
            token_revealed: tokenRevealed,
            debug,
          };
          console.log(JSON.stringify(result));
        } catch (err) {
          debug.push(await dumpDebug(page, 'on_error').catch(() => ({})));
          // Save a screenshot so we can see exactly what state the page was in.
          const shotPath = `/tmp/mcsl_devapp_error_${Date.now()}.png`;
          try {
            await page.screenshot({ path: shotPath, fullPage: true });
            debug.push({ label: 'screenshot_saved', path: shotPath });
          } catch (sx) {
            debug.push({ label: 'screenshot_failed', error: sx && sx.message ? sx.message : String(sx) });
          }
          console.log(JSON.stringify({
            store_name: storeName,
            app_name: appName,
            app_id: appId,
            admin_token: adminToken,
            storefront_token: storefrontToken,
            granted_admin_scopes: grantedAdmin,
            app_created: appCreated,
            app_installed: appInstalled,
            token_revealed: tokenRevealed,
            debug,
            error: err && err.message ? err.message : String(err),
          }));
        } finally {
          await context.close().catch(() => {});
          await browser.close().catch(() => {});
        }
        """
    ).strip()


def create_dev_app_and_reveal_token(
    *,
    store_name: str,
    app_name: str = DEFAULT_DEV_APP_NAME,
    admin_scopes: tuple[str, ...] | list[str] = DEFAULT_ADMIN_SCOPES,
    storefront_scopes: tuple[str, ...] | list[str] = DEFAULT_STOREFRONT_SCOPES,
    timeout_seconds: int = 900,
) -> DevAppTokenResult:
    """Create a custom dev app inside the merchant's store, tick the requested
    scopes, install it, and scrape the one-shot ``shpat_*`` Admin API token.

    The reveal happens **once** — re-running will create a new dev app rather
    than re-revealing the previous token. Use :func:`pipeline.new_carrier_validation.write_carrier_env_file`
    immediately after this returns to persist the token.

    Returns a :class:`DevAppTokenResult`. Raises on subprocess error.
    """
    if not store_name.strip():
        raise ValueError("store_name is required")
    requested_admin = tuple(admin_scopes)
    requested_store = tuple(storefront_scopes)

    repo   = _automation_repo()
    script = _build_dev_app_script()
    env    = os.environ.copy()
    env.update(
        {
            "DEV_APP_STORE_NAME":        store_name.strip(),
            "DEV_APP_NAME":              app_name,
            "DEV_APP_ADMIN_SCOPES":      ",".join(requested_admin),
            "DEV_APP_STOREFRONT_SCOPES": ",".join(requested_store),
            "DEV_APP_STORAGE_PATH": getattr(
                config,
                "MCSL_CHROME_AUTH_PATH",
                str(repo / "auth-chrome.json"),
            ),
        }
    )

    started_at = time.time()
    with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False, dir=str(repo)) as handle:
        handle.write(script)
        temp_path = handle.name
    try:
        completed = subprocess.run(
            ["node", temp_path],
            cwd=str(repo),
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    finally:
        Path(temp_path).unlink(missing_ok=True)
    finished_at = time.time()

    stdout = completed.stdout or ""
    stderr = completed.stderr or ""
    if completed.returncode != 0:
        raise RuntimeError(stderr.strip() or stdout.strip() or "Dev-app token reveal failed")

    payload: dict = {}
    for line in reversed([l.strip() for l in stdout.splitlines() if l.strip()]):
        if line.startswith("{") and line.endswith("}"):
            payload = json.loads(line)
            break
    if not payload:
        raise RuntimeError("Dev-app run completed without structured result payload")

    granted = tuple(payload.get("granted_admin_scopes") or [])
    missing = tuple(s for s in requested_admin if s not in granted)

    return DevAppTokenResult(
        store_name=str(payload.get("store_name") or store_name),
        app_name=str(payload.get("app_name") or app_name),
        app_id=str(payload.get("app_id") or ""),
        admin_token=str(payload.get("admin_token") or ""),
        storefront_token=str(payload.get("storefront_token") or ""),
        granted_admin_scopes=granted,
        requested_admin_scopes=requested_admin,
        missing_admin_scopes=missing,
        app_created=bool(payload.get("app_created")),
        app_installed=bool(payload.get("app_installed")),
        token_revealed=bool(payload.get("token_revealed")),
        stdout=stdout,
        stderr=stderr,
        returncode=int(completed.returncode),
        started_at=started_at,
        finished_at=finished_at,
    )
