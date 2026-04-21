# MCSL Carrier Request Registry

## Purpose

This KB snapshot gives AI QA a shared baseline for what to expect in carrier rate requests, label requests, and carrier responses across supported MCSL carriers.

Use it with the current test case. The carrier baseline gives the request family and common payload areas. The current scenario still decides the exact values and validations.

## Core Rule

- Use automation for navigation and locators.
- Use codebase, KB, wiki, and the current test case to decide what the current request and response should contain.
- If no carrier is named, start with generic MCSL behavior.
- If a carrier is named, use that carrier baseline before adding scenario-specific checks.

## Generic Baseline

- Rate request should reflect current origin, destination, shipment values, and selected service where relevant.
- Label request should reflect current shipment, package or line-item data, and customs/document data where applicable.
- Response should reflect the current order and carrier flow, not stale data from another order.

## Carrier Baselines

### FedEx
- Format: `json`
- Family: `fedex_rest`
- Common rate areas:
  - `requestedPackageLineItems`
  - `customsClearanceDetail`
  - `commodities`
- Common label areas:
  - `requestedShipment`
  - product-level customs or COO details
  - selected special-service nodes
- Special-service hints:
  - `specialServiceTypes`
  - `alcoholDetail`
  - `batteryDetails`
  - `dryIceWeight`
  - `holdAtLocationDetail`

### UPS
- Format: `json_or_xml_like_json`
- Family: `ups`
- Common rate areas:
  - `ShipmentRequest`
  - `Package`
  - service/account options
- Common label areas:
  - `ShipmentRequest`
  - `Package`
  - `LabelSpecification`
  - `ReasonForExport`
  - `ShipmentServiceOptions`
  - `DeliveryConfirmation`

### DHL
- Format: `json_or_xml`
- Family: `dhl_express`
- Common areas:
  - shipment pieces
  - shipper/recipient
  - customs/export declaration
  - paperless-trade or document data

### USPS
- Format: `json`
- Family: `usps`
- Common areas:
  - package dimensions
  - parcel values
  - service selection
  - customs where applicable

### USPS Stamps
- Format: `json`
- Family: `stamps`
- Common areas:
  - USPS service selection
  - package values
  - label format
  - current shipment data

### EasyPost
- Format: `json`
- Family: `easypost`
- Common areas:
  - address objects
  - parcel object
  - shipment object
  - selected carrier/service

### Canada Post
- Format: `json_or_xml`
- Family: `canada_post`
- Common areas:
  - parcel dimensions
  - weight
  - service options
  - sender/destination
  - label options

### Australia Post
- Format: `json`
- Family: `australia_post`
- Common areas:
  - parcel, service, shipment values
  - signature or extra-cover options when enabled

### TNT Australia
- Format: `json`
- Family: `tnt_australia`
- Common areas:
  - shipment pieces
  - service selection
  - label shipment identifiers

### Blue Dart
- Format: `json`
- Family: `blue_dart`
- Common areas:
  - address
  - package values
  - service data

### Amazon Shipping
- Format: `json`
- Family: `amazon_shipping`
- Common areas:
  - seller account context
  - package details
  - service availability

### MyPost
- Format: `json`
- Family: `mypost_business`
- Common areas:
  - parcel/service details
  - shipment/article data
  - label-generation data

### Purolator
- Format: `json_or_xml`
- Family: `purolator`
- Common areas:
  - Canadian shipment/service details
  - parcel/service label data

### PostNord
- Format: `json`
- Family: `postnord`
- Common areas:
  - shipment values
  - selected service
  - product-specific customs data
  - CN22/CN23 product-level data
- Negative check:
  - do not collapse different product-level COO/customs values into one shipment-level value

### TNT Express
- Format: `json_or_xml`
- Family: `tnt_express`
- Common areas:
  - shipment values
  - service selection
  - parcel/service label data

### Parcel Force
- Format: `json_or_xml`
- Family: `parcelforce`
- Common areas:
  - parcel
  - destination
  - service data

### EasyPost USPS
- Format: `json`
- Family: `easypost_usps`
- Common areas:
  - shipment address objects
  - parcel object
  - selected USPS service

### Post NL
- Format: `json`
- Family: `postnl`
- Common areas:
  - shipment values
  - service settings
  - customs data where applicable

### Aramex
- Format: `json`
- Family: `aramex`
- Common areas:
  - shipper
  - recipient
  - parcel/service data

### NZ Post
- Format: `json`
- Family: `nz_post`
- Common areas:
  - destination
  - parcel values
  - service selection

### Sendle
- Format: `json`
- Family: `sendle`
- Common areas:
  - sender
  - recipient
  - parcel
  - service data

### APC Postal Logistics
- Format: `json_or_xml`
- Family: `apc_postal_logistics`
- Common areas:
  - parcel
  - destination
  - service values

### Landmark Global
- Format: `json_or_xml`
- Family: `landmark_global`
- Common areas:
  - cross-border shipment values
  - parcel/service values
  - customs/document data where required

## AI QA Usage

1. Detect carrier from card or test case.
2. Apply carrier baseline from this registry.
3. Add current scenario-specific expectations.
4. Open current rate or label log.
5. Compare current evidence against:
   - carrier baseline
   - current scenario expectations
   - negative checks
