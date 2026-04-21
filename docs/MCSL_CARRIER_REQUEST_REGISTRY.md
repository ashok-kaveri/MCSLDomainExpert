# MCSL Carrier Request Registry

## Purpose

This document gives AI QA a shared baseline for what to expect in carrier rate requests, label requests, and carrier responses.

Use this with the current test case. The registry is not meant to replace scenario reasoning. It gives the baseline carrier shape, and the current test case adds the exact field expectations.

## Rules

- Use automation for navigation, stable locators, and repeated UI flows.
- Use codebase, wiki, KB, and the current test case for deciding what the current request and response should contain.
- If a card does not name a carrier, treat it as generic MCSL platform behavior first.
- If a card names a carrier, use that carrier baseline before adding scenario-specific expectations.

## Generic Baseline

- Rate request should reflect:
  - current store origin
  - current order destination
  - current shipment weight / dimensions / product data
  - selected carrier or service where relevant
- Label request should reflect:
  - current shipment / order
  - current package or line-item data
  - current customs or document data when applicable
- Response should reflect:
  - current carrier flow
  - current order status transition
  - current tracking / label / document output
- Negative baseline:
  - request must not reuse stale data from another order or another carrier

## Carrier Registry

### FedEx
- Request format:
  - `json`
- Request family:
  - `fedex_rest`
- Rate request baseline:
  - `requestedPackageLineItems`
  - `customsClearanceDetail`
  - `commodities`
  - product-level customs data when the scenario changes product values
- Label request baseline:
  - `requestedShipment`
  - `requestedPackageLineItems`
  - commodity-level COO / country-of-manufacture when applicable
  - selected special-service payload when enabled
- Special-service hints:
  - `specialServiceTypes`
  - `alcoholDetail`
  - `batteryDetails`
  - `dryIceWeight`
  - `holdAtLocationDetail`
  - `shipmentSpecialServices`
- Negative checks:
  - shipment-level customs values or COO must not overwrite different product-level values

### UPS
- Request format:
  - `json_or_xml_like_json`
- Request family:
  - `ups`
- Rate request baseline:
  - `ShipmentRequest`
  - `Package`
  - service/account options
  - customs commodity details for international flows
- Label request baseline:
  - `ShipmentRequest`
  - `Package`
  - `LabelSpecification`
  - `ReasonForExport`
  - `ShipmentServiceOptions`
  - `DeliveryConfirmation`
- Special-service hints:
  - image type
  - pickup service
  - delivery confirmation
  - export reason

### DHL
- Request format:
  - `json_or_xml`
- Request family:
  - `dhl_express`
- Rate request baseline:
  - shipment pieces
  - shipment weight
  - shipper and recipient details
  - customs/export data for international scenarios
- Label request baseline:
  - shipment content
  - customs/export declaration data
  - paperless-trade or document-related data where applicable

### USPS
- Request format:
  - `json`
- Request family:
  - `usps`
- Rate request baseline:
  - package dimensions
  - parcel values
  - domestic/international service selection
- Label request baseline:
  - service
  - parcel
  - shipper/recipient
  - customs where required

### USPS Stamps
- Request format:
  - `json`
- Request family:
  - `stamps`
- Rate request baseline:
  - USPS service selection
  - package values
- Label request baseline:
  - label format
  - parcel values
  - current order shipment data

### EasyPost
- Request format:
  - `json`
- Request family:
  - `easypost`
- Rate request baseline:
  - address objects
  - parcel object
- Label request baseline:
  - shipment object
  - parcel object
  - selected carrier/service

### Canada Post
- Request format:
  - `json_or_xml`
- Request family:
  - `canada_post`
- Rate request baseline:
  - parcel dimensions
  - weight
  - service options
- Label request baseline:
  - sender
  - destination
  - parcel
  - label options

### Australia Post
- Request format:
  - `json`
- Request family:
  - `australia_post`
- Baseline:
  - parcel, service, and shipment values
  - label payload should include signature or extra-cover options when enabled

### TNT Australia
- Request format:
  - `json`
- Request family:
  - `tnt_australia`
- Baseline:
  - shipment pieces
  - service selection
  - label shipment identifiers

### Blue Dart
- Request format:
  - `json`
- Request family:
  - `blue_dart`
- Baseline:
  - order address
  - package values
  - service data

### Amazon Shipping
- Request format:
  - `json`
- Request family:
  - `amazon_shipping`
- Baseline:
  - seller account context
  - package details
  - service availability for the active store

### MyPost
- Request format:
  - `json`
- Request family:
  - `mypost_business`
- Baseline:
  - parcel/service details
  - shipment/article data
  - label-generation data

### Purolator
- Request format:
  - `json_or_xml`
- Request family:
  - `purolator`
- Baseline:
  - Canadian shipment/service details
  - parcel/service data in label flow

### PostNord
- Request format:
  - `json`
- Request family:
  - `postnord`
- Baseline:
  - current shipment values
  - selected service
  - product-specific customs data where relevant
  - CN22/CN23 product-level data where required
- Negative checks:
  - CN22/CN23 output must not collapse different product-level COO or customs values into one shipment-level value

### TNT Express
- Request format:
  - `json_or_xml`
- Request family:
  - `tnt_express`
- Baseline:
  - shipment values
  - service selection
  - parcel/service label data

### Parcel Force
- Request format:
  - `json_or_xml`
- Request family:
  - `parcelforce`
- Baseline:
  - parcel
  - destination
  - service data

### EasyPost USPS
- Request format:
  - `json`
- Request family:
  - `easypost_usps`
- Baseline:
  - shipment address objects
  - parcel object
  - selected USPS service

### Post NL
- Request format:
  - `json`
- Request family:
  - `postnl`
- Baseline:
  - shipment values
  - service settings
  - customs data when applicable

### Aramex
- Request format:
  - `json`
- Request family:
  - `aramex`
- Baseline:
  - shipper
  - recipient
  - parcel/service data

### NZ Post
- Request format:
  - `json`
- Request family:
  - `nz_post`
- Baseline:
  - destination
  - parcel values
  - service selection

### Sendle
- Request format:
  - `json`
- Request family:
  - `sendle`
- Baseline:
  - sender
  - recipient
  - parcel
  - service data

### APC Postal Logistics
- Request format:
  - `json_or_xml`
- Request family:
  - `apc_postal_logistics`
- Baseline:
  - parcel
  - destination
  - service values

### Landmark Global
- Request format:
  - `json_or_xml`
- Request family:
  - `landmark_global`
- Baseline:
  - cross-border shipment values
  - parcel/service values
  - customs/document data where required

## How AI QA Should Use This

1. Detect the carrier from the card or current test case.
2. Load the carrier baseline from this registry.
3. Add current scenario expectations from the test case.
4. Open the current run’s rate log or label log.
5. Compare the current run’s evidence against:
   - carrier baseline
   - current scenario expectations
   - negative checks

## Important Limitation

This registry is a baseline. It should not replace:
- current card context
- current product/setup changes
- current automation-rule changes
- current carrier-setting changes
- current request/log evidence
