# MCSL Carrier Support Registry

Searchable carrier support reference for MCSL Domain Expert.

## Core rule

- named carrier => carrier-specific
- no named carrier => generic MCSL platform behavior first

## Shared MCSL areas

- `ORDERS`
- `LABELS`
- `PICKUP`
- hamburger `Products`
- hamburger `Carriers`
- packaging / automation / request-log areas

## Carrier notes

### FedEx
- local code: `C2`
- local automation env: yes
- check HAL, signature, dry ice, alcohol, insurance, customs/commercial invoice
- verify request payloads, label payloads, and customs docs

### UPS
- local code: `C3`
- local automation env: yes
- check SurePost, negotiated rates, COD, insurance, international behavior
- verify service selection, rate rules, and label creation

### DHL Express
- local code: `C1`
- local automation env: yes
- check duty/tax handling, paperless trade, and international documents

### USPS / USPS Stamps
- local automation env: yes
- check pricing, service mapping, label output, and customs handling where relevant

### Canada Post
- local code: `C4`
- local automation env: yes
- check service-point, proof-of-age, and label output behavior

### Amazon Shipping
- local automation env: yes
- check seller/account setup constraints and service availability

### Purolator / PostNord / TNT Express / Parcel Force
- local automation env: yes
- treat as carrier-specific when named

### EasyPost USPS / Post NL / Aramex / NZ Post / Sendle / APC Postal Logistics / Landmark Global
- local automation env: yes
- use shared MCSL navigation plus carrier-specific setup and request/label validation

### Australia Post / MyPost / Blue Dart / TNT Australia
- local automation env: yes
- use shared MCSL navigation with carrier-specific setup/service checks

## Common verification areas

- carrier credentials
- product and packaging prerequisites
- rate request / label request logs
- generated labels and customs documents
- Shopify fulfillment and tracking sync
- automation rules
