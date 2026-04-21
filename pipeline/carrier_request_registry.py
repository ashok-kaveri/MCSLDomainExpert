"""Shared carrier request/response expectation registry for AI QA."""
from __future__ import annotations

from dataclasses import dataclass, field

from pipeline.carrier_knowledge import CARRIER_PROFILES, detect_carrier_scope


@dataclass(frozen=True)
class CarrierRequestProfile:
    canonical_name: str
    request_format: str = "json"
    request_family: str = "generic"
    rate_request_fields: tuple[str, ...] = ()
    label_request_fields: tuple[str, ...] = ()
    response_signals: tuple[str, ...] = ()
    negative_assertions: tuple[str, ...] = ()
    special_service_fields: tuple[str, ...] = ()

    def to_text(self) -> str:
        lines = [
            f"Carrier registry: {self.canonical_name}",
            f"Request format: {self.request_format}",
            f"Request family: {self.request_family}",
        ]
        if self.rate_request_fields:
            lines.append("Carrier baseline rate fields:")
            lines.extend(f"- {item}" for item in self.rate_request_fields[:12])
        if self.label_request_fields:
            lines.append("Carrier baseline label fields:")
            lines.extend(f"- {item}" for item in self.label_request_fields[:12])
        if self.response_signals:
            lines.append("Carrier baseline response signals:")
            lines.extend(f"- {item}" for item in self.response_signals[:10])
        if self.negative_assertions:
            lines.append("Carrier baseline negative checks:")
            lines.extend(f"- {item}" for item in self.negative_assertions[:8])
        if self.special_service_fields:
            lines.append("Carrier special-service fields:")
            lines.extend(f"- {item}" for item in self.special_service_fields[:10])
        return "\n".join(lines)


_BASE_RATE_FIELDS = (
    "Ship from / origin address is correct for the active store and carrier account.",
    "Ship to / destination address matches the current order under test.",
    "Product or package weight is reflected in the outbound payload.",
    "Selected service or carrier code is reflected in the rating request when applicable.",
)

_BASE_LABEL_FIELDS = (
    "Label request references the current order/shipment and selected carrier service.",
    "Package or line-item data reflects the current shipment being generated.",
)

_BASE_RESPONSE_SIGNALS = (
    "The current order shows the expected shipping service, rate, and status transition for this carrier flow.",
    "Tracking or label artifacts are available after successful label generation.",
)

_BASE_NEGATIVE_ASSERTIONS = (
    "The request must not reuse stale data from a previous order or different carrier.",
)


def _profile(
    canonical_name: str,
    *,
    request_format: str = "json",
    request_family: str = "generic",
    rate_fields: tuple[str, ...] = (),
    label_fields: tuple[str, ...] = (),
    response_signals: tuple[str, ...] = (),
    negative_assertions: tuple[str, ...] = (),
    special_service_fields: tuple[str, ...] = (),
) -> CarrierRequestProfile:
    return CarrierRequestProfile(
        canonical_name=canonical_name,
        request_format=request_format,
        request_family=request_family,
        rate_request_fields=_BASE_RATE_FIELDS + tuple(rate_fields),
        label_request_fields=_BASE_LABEL_FIELDS + tuple(label_fields),
        response_signals=_BASE_RESPONSE_SIGNALS + tuple(response_signals),
        negative_assertions=_BASE_NEGATIVE_ASSERTIONS + tuple(negative_assertions),
        special_service_fields=tuple(special_service_fields),
    )


_REGISTRY: dict[str, CarrierRequestProfile] = {
    "FedEx": _profile(
        "FedEx",
        request_format="json",
        request_family="fedex_rest",
        rate_fields=(
            "FedEx REST rate payload should include requestedPackageLineItems for the active shipment.",
            "FedEx customs/rating payload should include customsClearanceDetail and commodities for international/customs scenarios.",
            "FedEx line-item customs values, weights, and commodity details should be product-specific when the scenario changes product data.",
        ),
        label_fields=(
            "FedEx label payload should include requestedShipment and requestedPackageLineItems for the generated shipment.",
            "FedEx customs/document payload should carry commodity-level countryOfManufacture or country-of-origin details where required.",
            "FedEx special service nodes should match the selected options for the current order.",
        ),
        response_signals=(
            "FedEx response should return the selected service or a valid carrier-specific alternative rather than a different carrier response.",
            "FedEx shipment response should expose tracking details or label/document output for the current order.",
        ),
        negative_assertions=(
            "Shipment-level customs values or COO must not overwrite distinct product-level values when products differ.",
        ),
        special_service_fields=(
            "specialServiceTypes",
            "alcoholDetail",
            "batteryDetails",
            "dryIceWeight",
            "holdAtLocationDetail",
            "shipmentSpecialServices",
        ),
    ),
    "UPS": _profile(
        "UPS",
        request_format="json_or_xml_like_json",
        request_family="ups",
        rate_fields=(
            "UPS rating payload should include ShipmentRequest and Package-level shipment details.",
            "UPS payload should reflect negotiated/service selection and account-specific options when configured.",
            "UPS international/customs payload should include commodity-level details for customs scenarios.",
        ),
        label_fields=(
            "UPS label payload should include ShipmentRequest, Package, and LabelSpecification or image-type details when applicable.",
            "UPS export scenarios should include ReasonForExport or equivalent international shipment details when configured.",
            "UPS DeliveryConfirmation or pickup/service options should match current carrier settings when relevant.",
        ),
        response_signals=(
            "UPS response should align with the selected UPS service and label format for the order under test.",
        ),
        special_service_fields=(
            "ShipmentRequest",
            "Package",
            "Commodity",
            "ReasonForExport",
            "ShipmentServiceOptions",
            "DeliveryConfirmation",
            "LabelSpecification",
        ),
    ),
    "DHL": _profile(
        "DHL",
        request_format="json_or_xml",
        request_family="dhl_express",
        rate_fields=(
            "DHL rate payload should include shipment pieces, weight, and shipper/recipient details for the active order.",
            "DHL customs/export data should be present for international/customs scenarios.",
        ),
        label_fields=(
            "DHL label payload should include shipment content, customs/export declaration details, and label generation parameters where applicable.",
            "DHL document or paperless-trade related fields should align with the scenario when documents are expected.",
        ),
        response_signals=(
            "DHL response should show the active DHL product/service and generated shipment/label output for the same order.",
        ),
        special_service_fields=(
            "exportDeclaration",
            "customerDetails",
            "content",
            "packages",
            "specialServices",
        ),
    ),
    "USPS": _profile(
        "USPS",
        request_format="json",
        request_family="usps",
        rate_fields=(
            "USPS rate payload should reflect domestic/international service selection, package dimensions, and parcel values.",
            "USPS customs data should appear for international scenarios that require forms or declarations.",
        ),
        label_fields=(
            "USPS label payload should include package, service, and shipper/recipient data for the current order.",
            "USPS customs/document data should align with the ordered product data when customs forms are required.",
        ),
        response_signals=(
            "USPS response should return an eligible USPS service and current-order tracking/label data.",
        ),
    ),
    "USPS Stamps": _profile(
        "USPS Stamps",
        request_format="json",
        request_family="stamps",
        rate_fields=(
            "Stamps.com/USPS payload should reflect the selected USPS service and package values for the active order.",
        ),
        label_fields=(
            "Stamps.com label payload should include label format/service details and current-order parcel information.",
        ),
        response_signals=(
            "Stamps response should return label output or service details for the same order under test.",
        ),
    ),
    "EasyPost": _profile(
        "EasyPost",
        request_format="json",
        request_family="easypost",
        rate_fields=(
            "EasyPost rate payload should include shipment to/from address objects and parcel details for the current order.",
        ),
        label_fields=(
            "EasyPost label payload should include parcel, shipment, and selected carrier/service details for the order under test.",
        ),
        response_signals=(
            "EasyPost response should return a shipment or label object bound to the current order, not stale shipment data.",
        ),
    ),
    "Canada Post": _profile(
        "Canada Post",
        request_format="json_or_xml",
        request_family="canada_post",
        rate_fields=(
            "Canada Post rate payload should include parcel dimensions, weights, and Canadian service options for the current order.",
        ),
        label_fields=(
            "Canada Post label payload should include parcel, sender, destination, and label-option data for the order under test.",
        ),
        response_signals=(
            "Canada Post response should expose the selected service or valid carrier alternative with current-order label/tracking output.",
        ),
    ),
    "Australia Post": _profile(
        "Australia Post",
        request_format="json",
        request_family="australia_post",
        rate_fields=(
            "Australia Post payload should reflect parcel, service, and shipment values for the active order.",
        ),
        label_fields=(
            "Australia Post label payload should include shipment/parcel details and any signature or extra-cover options when enabled.",
        ),
    ),
    "TNT Australia": _profile(
        "TNT Australia",
        request_format="json",
        request_family="tnt_australia",
        rate_fields=("TNT Australia payload should reflect current shipment pieces and service selection.",),
        label_fields=("TNT Australia label payload should include shipment identifiers and parcel/service data.",),
    ),
    "Blue Dart": _profile(
        "Blue Dart",
        request_format="json",
        request_family="blue_dart",
        rate_fields=("Blue Dart rate payload should reflect current order address, package, and service data.",),
        label_fields=("Blue Dart label payload should reflect current parcel, service, and shipper/recipient data.",),
    ),
    "Amazon Shipping": _profile(
        "Amazon Shipping",
        request_format="json",
        request_family="amazon_shipping",
        rate_fields=("Amazon Shipping payload should reflect seller account, package, and service availability for the active order.",),
        label_fields=("Amazon Shipping label payload should include seller, order, and package data for the current shipment.",),
        response_signals=("Amazon Shipping response should align with available seller/carrier service options for the active store.",),
    ),
    "MyPost": _profile(
        "MyPost",
        request_format="json",
        request_family="mypost_business",
        rate_fields=(
            "MyPost payload should include parcel/service details and Australia Post style shipment data for the active order.",
        ),
        label_fields=(
            "MyPost label payload should include shipment, article, and label-generation data for the current order.",
        ),
        response_signals=(
            "MyPost response should return service or label data tied to the current order and store account.",
        ),
    ),
    "Purolator": _profile(
        "Purolator",
        request_format="json_or_xml",
        request_family="purolator",
        rate_fields=("Purolator payload should include active shipment/service details for the current Canadian shipment.",),
        label_fields=("Purolator label payload should include parcel and service data for the current order.",),
    ),
    "PostNord": _profile(
        "PostNord",
        request_format="json",
        request_family="postnord",
        rate_fields=(
            "PostNord rate payload should reflect the current shipment values, selected service, and product-specific customs data when relevant.",
        ),
        label_fields=(
            "PostNord label/document payload should include product-level customs or CN22/CN23 data for the current order where required.",
        ),
        negative_assertions=(
            "PostNord CN22/CN23 output must not collapse distinct product-level COO or customs values into one shipment-level value.",
        ),
    ),
    "TNT Express": _profile(
        "TNT Express",
        request_format="json_or_xml",
        request_family="tnt_express",
        rate_fields=("TNT Express payload should reflect current shipment and service-selection values.",),
        label_fields=("TNT Express label payload should include shipment, parcel, and service data for the current order.",),
    ),
    "Parcel Force": _profile(
        "Parcel Force",
        request_format="json_or_xml",
        request_family="parcelforce",
        rate_fields=("Parcel Force payload should reflect current parcel, destination, and service data.",),
        label_fields=("Parcel Force label payload should include current order parcel and service values.",),
    ),
    "EasyPost USPS": _profile(
        "EasyPost USPS",
        request_format="json",
        request_family="easypost_usps",
        rate_fields=("EasyPost USPS rate payload should include shipment address and parcel objects for the current order.",),
        label_fields=("EasyPost USPS label payload should include selected USPS service and parcel data for the active shipment.",),
    ),
    "Post NL": _profile(
        "Post NL",
        request_format="json",
        request_family="postnl",
        rate_fields=("PostNL payload should reflect current shipment, destination, and service settings.",),
        label_fields=("PostNL label payload should include current-order parcel and service data, including customs when required.",),
    ),
    "Aramex": _profile(
        "Aramex",
        request_format="json",
        request_family="aramex",
        rate_fields=("Aramex payload should include current shipper/recipient and parcel/service details.",),
        label_fields=("Aramex label payload should include current shipment and parcel details for the order under test.",),
    ),
    "NZ Post": _profile(
        "NZ Post",
        request_format="json",
        request_family="nz_post",
        rate_fields=("NZ Post payload should reflect current order destination, parcel values, and service selection.",),
        label_fields=("NZ Post label payload should include current-order parcel and service data.",),
    ),
    "Sendle": _profile(
        "Sendle",
        request_format="json",
        request_family="sendle",
        rate_fields=("Sendle payload should include sender, recipient, parcel, and service information for the active order.",),
        label_fields=("Sendle label payload should include the current order shipment and parcel details.",),
    ),
    "APC Postal Logistics": _profile(
        "APC Postal Logistics",
        request_format="json_or_xml",
        request_family="apc_postal_logistics",
        rate_fields=("APC Postal Logistics payload should reflect parcel, destination, and service values for the active order.",),
        label_fields=("APC Postal Logistics label payload should include current-order parcel and service data.",),
    ),
    "Landmark Global": _profile(
        "Landmark Global",
        request_format="json_or_xml",
        request_family="landmark_global",
        rate_fields=("Landmark Global payload should reflect cross-border shipment, parcel, and service values for the active order.",),
        label_fields=("Landmark Global label/document payload should include current parcel and customs/document details when relevant.",),
    ),
}


def _fallback_profile(carrier_name: str) -> CarrierRequestProfile:
    return _profile(
        carrier_name or "Generic MCSL Carrier",
        request_format="json_or_xml",
        request_family="generic",
        rate_fields=("Carrier-specific rate payload should reflect the active shipment and selected service for this order.",),
        label_fields=("Carrier-specific label payload should reflect the active shipment, parcel, and customs data when required.",),
    )


def resolve_carrier_request_profile(carrier: str) -> CarrierRequestProfile:
    scope = detect_carrier_scope(carrier or "")
    if scope.primary and scope.primary.canonical_name in _REGISTRY:
        return _REGISTRY[scope.primary.canonical_name]
    lower = (carrier or "").strip().lower()
    if not lower:
        return _fallback_profile("")
    for profile in CARRIER_PROFILES:
        if lower == profile.canonical_name.lower() or lower in profile.aliases:
            return _REGISTRY.get(profile.canonical_name, _fallback_profile(profile.canonical_name))
    return _fallback_profile(carrier)


def all_carrier_request_profiles() -> list[CarrierRequestProfile]:
    seen: list[CarrierRequestProfile] = []
    for carrier in CARRIER_PROFILES:
        seen.append(_REGISTRY.get(carrier.canonical_name, _fallback_profile(carrier.canonical_name)))
    return seen
