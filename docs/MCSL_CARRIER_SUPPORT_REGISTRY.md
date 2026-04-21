# MCSL Carrier Support Registry

## Purpose

This document gives the MCSL Domain Expert a compact per-carrier support reference.

Use it for:
- carrier-specific card interpretation
- QA prerequisite planning
- request/label verification focus
- support-ticket diagnosis

## Generic Rule

- If a card names a carrier, treat it as carrier-specific.
- If a card does not name a carrier, treat it as generic MCSL platform behavior first.
- Generic cards should prefer shared MCSL flows:
  - `ORDERS`
  - `LABELS`
  - `PICKUP`
  - hamburger `Products`
  - hamburger `Carriers`
  - packaging / automation / request-log areas

## Carrier Registry

### FedEx
- Internal code used locally: `C2`
- Local automation env: yes
- Focus:
  - HAL
  - signature
  - dry ice
  - alcohol
  - insurance
  - customs / commercial invoice
- Typical checks:
  - product/carrier settings
  - rate request payload
  - label request payload
  - customs document output

### UPS
- Internal code used locally: `C3`
- Local automation env: yes
- Focus:
  - SurePost
  - negotiated rates
  - COD
  - insurance
  - international behavior
- Typical checks:
  - service selection
  - rate rules
  - rate response
  - label creation

### DHL Express
- Internal code used locally: `C1`
- Local automation env: yes
- Focus:
  - duty / tax handling
  - paperless trade
  - international documents
- Typical checks:
  - international account setup
  - customs values
  - document generation
  - label output

### USPS
- Internal code used locally: `C22`
- Local automation env: yes
- Focus:
  - service pricing
  - domestic/international label behavior
  - customs where applicable
- Typical checks:
  - service availability
  - commercial pricing
  - label output

### USPS Stamps
- Internal code used locally: `C22`
- Local automation env: yes
- Focus:
  - Stamps account path
  - commercial pricing
  - registered/certified-style services
- Typical checks:
  - service mapping
  - label generation

### Canada Post
- Internal code used locally: `C4`
- Local automation env: yes
- Focus:
  - service-point behavior
  - proof of age
  - localized label output
- Typical checks:
  - carrier setup
  - service options
  - tracking sync

### Amazon Shipping
- Local automation env: yes
- Focus:
  - seller/account setup constraints
  - carrier-specific service availability

### Purolator
- Local automation env: yes
- Focus:
  - carrier-specific service and Canadian shipment behavior

### PostNord
- Local automation env: yes
- Focus:
  - label/customs/document behavior on shared MCSL flows

### TNT Express
- Local automation env: yes
- Focus:
  - international/service workflow on shared MCSL flows

### Parcel Force
- Local automation env: yes
- Focus:
  - service/account and label verification

### EasyPost USPS
- Local automation env: yes
- Focus:
  - USPS-family REST workflow through EasyPost

### Post NL
- Local automation env: yes
- Focus:
  - service and label expectations on shared MCSL flows

### Aramex
- Local automation env: yes
- Focus:
  - account/setup and request/label validation

### NZ Post
- Local automation env: yes
- Focus:
  - rating/label/account rules in standard MCSL navigation

### Sendle
- Local automation env: yes
- Focus:
  - account/setup and request/response behavior

### APC Postal Logistics
- Local automation env: yes
- Focus:
  - carrier setup plus order/label flow verification

### Landmark Global
- Local automation env: yes
- Focus:
  - cross-border setup and document/label behavior

### Australia Post / MyPost / Blue Dart / TNT Australia
- Local automation env: yes
- Focus:
  - carrier-specific setup and service behavior using shared MCSL flows

## Common Verification Areas

- carrier credentials and onboarding
- product / packaging prerequisites
- rate request / label request logs
- generated labels and customs documents
- Shopify fulfillment and tracking sync
- automation rules / service-selection rules
