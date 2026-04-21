# MCSL Carrier Capability Matrix

This document is a searchable carrier reference for the MCSL Domain Expert.

## Interpretation Rule

- If a card explicitly names a carrier, treat it as carrier-specific.
- If a card does not name a carrier, treat it as a generic MCSL platform feature or issue.
- Generic cards should use a stable automation-ready carrier path for QA planning unless retrieved context says the scenario must remain carrier-neutral or must cover multiple carriers.

## Platform Scale

- Wiki-confirmed platform support:
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

## Shared MCSL Navigation

Most carriers reuse the same MCSL navigation model:

- top tabs:
  - `ORDERS`
  - `LABELS`
  - `PICKUP`
  - `MANIFEST`
  - `TRACKING`
- hamburger menu:
  - `Products`
  - `Carriers`
  - `General Settings`
  - shipping / packaging / automation areas
- Shopify admin verification:
  - `Orders`
  - `Products`

## Carrier Notes

### FedEx
- Common code used in local planning: `C2`
- Local automation env present
- Often involves:
  - signature
  - HAL
  - dry ice
  - alcohol
  - insurance
  - customs / commercial invoice

### UPS
- Common code used in local planning: `C3`
- Local automation env present
- Often involves:
  - SurePost
  - negotiated rates
  - COD
  - insurance
  - international flows

### DHL
- Platform-supported in wiki
- Local automation env present
- Often involves:
  - duty / tax handling
  - paperless trade
  - international shipping

### USPS / USPS Stamps
- Platform-supported in multiple variants
- Local automation env present for USPS and USPS Stamps
- Often involves:
  - commercial pricing
  - registered / certified services
  - lightweight domestic and international flows

### Canada Post
- Platform-supported in wiki
- Local automation env present
- Often involves:
  - FlexDelivery / service points
  - proof of age
  - bilingual labels

### Purolator / PostNord / TNT Express / Parcel Force
- Platform-supported and now present in local automation envs
- Usually carrier-specific rather than generic
- Use named carrier flows first when the card mentions them

### EasyPost USPS / Post NL / Aramex / NZ Post / Sendle / APC Postal Logistics / Landmark Global
- Local automation env present
- Treat as carrier-specific when named in cards or support tickets
- Use shared MCSL navigation plus the named carrier context from wiki and automation

### Amazon Shipping
- Platform-supported
- Local automation env present
- Often involves Amazon account or seller-side setup constraints

### Australia Post / MyPost / Blue Dart
- Platform-supported or locally automated in the current repo
- Use carrier-specific docs and automation context when named in a card

## Generic Issue Categories

If no carrier is named, first consider:

- generic platform workflow
- packaging or product data
- Shopify sync
- rate automation or label automation rules
- request / label log behavior
- code defect

## QA Planning Rule

- Carrier-specific card:
  - use named carrier first
  - use that carrier's request / response expectations
  - use that automation env if locally available
- Generic card:
  - use shared MCSL flow first
  - default to a stable automation-ready path unless context says otherwise
  - validate whether the issue should reproduce across multiple carriers or just one execution path
