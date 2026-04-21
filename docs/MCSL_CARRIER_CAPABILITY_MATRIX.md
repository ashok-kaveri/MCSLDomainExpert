# MCSL Carrier Capability Matrix

## Purpose

This document is the MCSL carrier source-of-truth for AI planning, QA, and support handoff.

Use it to answer:

- Is the card carrier-specific or generic?
- Which carrier code and setup path are relevant?
- Is there local automation env support for that carrier?
- Which MCSL areas are usually involved?

## Core rule

- If a card explicitly mentions a carrier, treat it as `carrier-specific`.
- If a card does not mention a carrier, treat it as `generic`.
- Generic cards should use a stable default carrier path for execution planning unless retrieved context says the feature is carrier-neutral or must be verified across multiple carriers.

## Platform scale

- MCSL platform support from wiki:
  - 43 unique carriers
  - 46 carrier configurations
- Local automation-ready subset confirmed from `mcsl-test-automation/carrier-envs`:
  - FedEx
  - UPS
  - DHL
  - USPS
  - USPS Stamps
  - Australia Post
  - TNT Australia
  - Blue Dart
  - Amazon Shipping
  - MyPost
  - Purolator
  - PostNord
  - TNT Express
  - Canada Post
  - Parcel Force
  - EasyPost USPS
  - Post NL
  - Aramex
  - NZ Post
  - Sendle
  - APC Postal Logistics
  - Landmark Global

## Shared MCSL navigation model

Most carrier flows still reuse the same MCSL platform navigation:

- top tabs:
  - `ORDERS`
  - `LABELS`
  - `PICKUP`
  - also `MANIFEST`, `TRACKING`
- hamburger navigation:
  - `Products`
  - `Carriers`
  - `General Settings`
  - shipping / packaging / automation areas
- Shopify verification:
  - `Orders` for fulfillment / tracking verification
  - `Products` for product creation and product sync verification

## Carrier matrix

| Carrier | Code | Platform Supported | Automation Env Seen | Typical Notes |
|---|---|---:|---:|---|
| FedEx | `C2` | Yes | Yes | HAL, signature, dry ice, alcohol, insurance, customs, One Rate |
| FedEx REST | `C39` | Yes | Partial/local naming may vary | Modern FedEx API migration path |
| FedEx Same Day City | `C37` | Yes | No | Same-day city delivery |
| UPS | `C3` | Yes | Yes | SurePost, negotiated rates, COD, insurance, international |
| UPS OAuth | `C38` | Yes | No | Modern UPS OAuth migration path |
| DHL Express | `C1` | Yes | Yes | Duty/tax options, paperless trade, international |
| TNT Australia | `C?` | Yes | Yes | Australia-focused TNT automation store |
| DHL Packet | `C10` | Yes | No | Lightweight packet flows |
| USPS via Stamps | `C4` in wiki | Yes | Yes | Commercial pricing, registered mail, test/sample labels |
| USPS Direct | `C5` | Yes | No | Legacy USPS direct path |
| USPS REST / OAuth | `C45` / `C46` / `C48` | Yes | No | Modern USPS migration paths |
| Amazon Shipping | `C43` | Yes | Yes | Amazon-specific shipping/account integration |
| Canada Post | `C6` | Yes | Yes | FlexDelivery, proof of age, bilingual labels |
| Purolator | `C16` | Yes | Yes | Dangerous goods, chain of signature |
| Blue Dart | not mapped here | Yes | Yes | India-focused carrier support |
| Australia Post | not mapped here | Yes | Yes | AU carrier support |
| MyPost | not mapped here | Yes | Yes | AU-related carrier/account path |
| EasyPost / USPS via EasyPost | carrier family | Yes | Yes | Used for USPS-family REST workflows |
| PostNord | `C?` | Yes | Yes | Nordic automation store confirmed |
| TNT Express | `C?` | Yes | Yes | TNT express automation store confirmed |
| Parcel Force | `C?` | Yes | Yes | UK-focused automation store confirmed |
| Post NL | `C?` | Yes | Yes | PostNL automation store confirmed |
| Aramex | `C?` | Yes | Yes | Aramex automation store confirmed |
| NZ Post | `C?` | Yes | Yes | NZ-specific automation store confirmed |
| Sendle | `C?` | Yes | Yes | AU-focused automation store confirmed |
| APC Postal Logistics | `C?` | Yes | Yes | APC automation store confirmed |
| Landmark Global | `C?` | Yes | Yes | Cross-border automation store confirmed |

## Generic card guidance

Use `generic` handling when the card is about:

- order import or order grid behavior
- product settings
- packaging settings
- rate automation rules
- request-log / label-log visibility
- Shopify fulfillment sync
- tracking updates
- sign-off / handoff / QA workflow mechanics

These are usually platform behaviors first, and carrier details second.

## Carrier-specific card guidance

Use `carrier-specific` handling when the card mentions:

- carrier name
- carrier service names
- carrier credentials / onboarding
- special services like:
  - Hold at Location
  - COD
  - signature options
  - dry ice
  - alcohol
  - dangerous goods
  - duty/tax behavior
  - customs / invoice behavior

## QA planning guidance

- If carrier-specific:
  - use the named carrier first
  - use carrier request/response expectations from KB/wiki/code
  - use that carrier's automation env if available
- If generic:
  - use the shared MCSL flow first
  - default to a stable automation-ready carrier path such as UPS unless context suggests otherwise
  - verify whether the result should be identical across multiple carriers

## Verification areas to remember

- MCSL request / label / automation logs
- product settings and packaging prerequisites
- carrier setup / credentials / production key
- Shopify order fulfillment status
- tracking number sync back to Shopify
- rate automation / label automation rules

## Source anchors

- Wiki:
  - `modules/shipping/carrier-integrations.md`
  - `modules/shipping/carrier-configuration.md`
  - `modules/shipping/label-generation.md`
  - `modules/shipping/rate-shopping.md`
  - `modules/workflows/automation-rules.md`
- Automation:
  - `carrier-envs/*.env`
  - `tests/automationRules/*`
  - `tests/orderGrid/*`
  - `testData/Packaging Types/*`
- Local KB snapshots:
  - carrier setup
  - troubleshooting
  - packaging
  - customs
  - flat rate / checkout / label flows
