"""TC-driven request/response expectation builder for AI QA."""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any

import config
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

from pipeline.carrier_request_registry import resolve_carrier_request_profile

logger = logging.getLogger(__name__)


@dataclass
class RequestExpectation:
    carrier: str = ""
    scenario: str = ""
    order_kind: str = ""
    request_family: str = ""
    request_format: str = ""
    request_types: list[str] = field(default_factory=list)
    rate_request_fields: list[str] = field(default_factory=list)
    label_request_fields: list[str] = field(default_factory=list)
    response_signals: list[str] = field(default_factory=list)
    negative_assertions: list[str] = field(default_factory=list)
    special_service_fields: list[str] = field(default_factory=list)
    reasoning: str = ""

    def to_text(self) -> str:
        lines = [
            "=== TC-DRIVEN REQUEST/RESPONSE EXPECTATIONS ===",
            f"Carrier: {self.carrier or '(generic)'}",
            f"Order kind: {self.order_kind or '(unspecified)'}",
            f"Request family: {self.request_family or '(generic)'}",
            f"Request format: {self.request_format or '(unknown)'}",
            f"Request types: {', '.join(self.request_types) if self.request_types else '(none)'}",
        ]
        if self.rate_request_fields:
            lines.append("Rate request should include:")
            lines.extend(f"- {item}" for item in self.rate_request_fields[:12])
        if self.label_request_fields:
            lines.append("Label request should include:")
            lines.extend(f"- {item}" for item in self.label_request_fields[:12])
        if self.response_signals:
            lines.append("Response / UI should show:")
            lines.extend(f"- {item}" for item in self.response_signals[:12])
        if self.negative_assertions:
            lines.append("Must NOT happen:")
            lines.extend(f"- {item}" for item in self.negative_assertions[:10])
        if self.special_service_fields:
            lines.append("Carrier special-service fields to watch:")
            lines.extend(f"- {item}" for item in self.special_service_fields[:12])
        if self.reasoning:
            lines.append(f"Reasoning: {self.reasoning}")
        return "\n".join(lines)


@dataclass
class ExpectationComparison:
    matched: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    observed_sources: list[str] = field(default_factory=list)
    observed_signals: list[str] = field(default_factory=list)
    observed_values: list[str] = field(default_factory=list)
    expected_values: list[str] = field(default_factory=list)

    def to_text(self) -> str:
        lines = ["=== EXPECTATION COMPARISON ==="]
        if self.observed_sources:
            lines.append("Observed evidence sources:")
            lines.extend(f"- {item}" for item in self.observed_sources[:8])
        if self.observed_signals:
            lines.append("Observed carrier/log signals:")
            lines.extend(f"- {item}" for item in self.observed_signals[:12])
        if self.observed_values:
            lines.append("Observed extracted values:")
            lines.extend(f"- {item}" for item in self.observed_values[:12])
        if self.expected_values:
            lines.append("Expected extracted values:")
            lines.extend(f"- {item}" for item in self.expected_values[:12])
        if self.matched:
            lines.append("Matched expectations:")
            lines.extend(f"- {item}" for item in self.matched[:12])
        if self.missing:
            lines.append("Missing or unconfirmed expectations:")
            lines.extend(f"- {item}" for item in self.missing[:12])
        return "\n".join(lines)


_EXPECTATION_PROMPT = """\
You are an MCSL shipping-domain expert helping an AI QA agent validate the CURRENT test case's rate/label logs.

SCENARIO:
{scenario}

CARRIER:
{carrier}

CARRIER REGISTRY:
{carrier_registry}

EXPERT INSIGHT:
{expert_insight}

DOMAIN KNOWLEDGE:
{domain_context}

CODE KNOWLEDGE:
{code_context}

Return ONLY JSON:
{{
  "order_kind": "product_update | settings_update | automation_rule | carrier_setup | checkout | label_generation | generic",
  "request_family": "carrier request family if known",
  "request_format": "json | xml | json_or_xml | carrier-specific variant if known",
  "request_types": ["rate", "label", "response"],
  "rate_request_fields": ["specific request field/value expectation for this scenario"],
  "label_request_fields": ["specific request field/value expectation for this scenario"],
  "response_signals": ["response or UI evidence expected for this scenario"],
  "negative_assertions": ["things that must not appear or regress"],
  "special_service_fields": ["carrier field names or service nodes worth checking in the current log"],
  "reasoning": "one short sentence"
}}
"""


def _parse_json(raw: str) -> dict[str, Any]:
    clean = re.sub(r"```(?:json)?\n?", "", (raw or "").strip()).strip().rstrip("`").strip()
    try:
        data = json.loads(clean)
        return data if isinstance(data, dict) else {}
    except Exception:
        pass
    match = re.search(r"\{[\s\S]*\}", raw or "")
    if match:
        try:
            data = json.loads(match.group(0))
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}
    return {}


def _dedupe(items: list[str]) -> list[str]:
    return [item for item in dict.fromkeys(item.strip() for item in items if item and item.strip())]


def _merge_expectations(base: RequestExpectation, extra: RequestExpectation) -> RequestExpectation:
    order_kind = extra.order_kind or base.order_kind
    return RequestExpectation(
        carrier=extra.carrier or base.carrier,
        scenario=extra.scenario or base.scenario,
        order_kind=order_kind,
        request_family=extra.request_family or base.request_family,
        request_format=extra.request_format or base.request_format,
        request_types=_dedupe(list(base.request_types) + list(extra.request_types)),
        rate_request_fields=_dedupe(list(base.rate_request_fields) + list(extra.rate_request_fields)),
        label_request_fields=_dedupe(list(base.label_request_fields) + list(extra.label_request_fields)),
        response_signals=_dedupe(list(base.response_signals) + list(extra.response_signals)),
        negative_assertions=_dedupe(list(base.negative_assertions) + list(extra.negative_assertions)),
        special_service_fields=_dedupe(list(base.special_service_fields) + list(extra.special_service_fields)),
        reasoning=_dedupe([base.reasoning, extra.reasoning])[0] if _dedupe([base.reasoning, extra.reasoning]) else "",
    )


def _registry_expectations(carrier: str) -> RequestExpectation:
    profile = resolve_carrier_request_profile(carrier)
    request_types = ["response"]
    if profile.rate_request_fields:
        request_types.append("rate")
    if profile.label_request_fields:
        request_types.append("label")
    return RequestExpectation(
        carrier=profile.canonical_name if profile.canonical_name != "Generic MCSL Carrier" else carrier,
        order_kind="generic",
        request_family=profile.request_family,
        request_format=profile.request_format,
        request_types=_dedupe(request_types),
        rate_request_fields=list(profile.rate_request_fields),
        label_request_fields=list(profile.label_request_fields),
        response_signals=list(profile.response_signals),
        negative_assertions=list(profile.negative_assertions),
        special_service_fields=list(profile.special_service_fields),
        reasoning=f"Carrier registry baseline used for {profile.canonical_name}.",
    )


def _heuristic_expectations(scenario: str, carrier: str) -> RequestExpectation:
    lower = (scenario or "").lower()
    exp = _registry_expectations(carrier)
    exp.scenario = scenario
    exp.reasoning = f"{exp.reasoning} Scenario-specific heuristics were added."
    if any(token in lower for token in ("rate req", "rate request", "checkout", "shipping method")):
        exp.request_types = _dedupe(list(exp.request_types) + ["rate"])
    if any(token in lower for token in ("label req", "label request", "generate label", "label created", "cn22", "commercial invoice")):
        exp.request_types = _dedupe(list(exp.request_types) + ["label"])
    if "customs value" in lower:
        exp.rate_request_fields.append("Customs value for the ordered product is present and trimmed to the expected precision.")
        exp.label_request_fields.append("Customs value is present in the customs/commodity section for the product.")
    if "country of origin" in lower or "coo" in lower:
        exp.label_request_fields.append("Country of origin is sent at product/line-item level, not only shipment level.")
        exp.negative_assertions.append("A single shipment-level COO must not overwrite all products when COO differs per product.")
    if "hs code" in lower:
        exp.label_request_fields.append("HS code is present for the product/commodity in the outbound payload.")
    if "weight" in lower or "dimensions" in lower:
        exp.rate_request_fields.append("Weight and package dimensions reflect the configured product/packaging values.")
    if "automation rule" in lower or "rate rule" in lower or "label rule" in lower:
        exp.order_kind = "automation_rule"
        exp.response_signals.append("The selected service/rule outcome matches the active automation rule.")
    if "carrier setup" in lower or "add carrier" in lower:
        exp.order_kind = "carrier_setup"
        exp.response_signals.append("Carrier is visible and usable after save.")
    if "checkout" in lower:
        exp.order_kind = "checkout"
        exp.rate_request_fields.append("Rate request reflects the checkout address and cart values from the current storefront order.")
    if "generate label" in lower or "label created" in lower:
        exp.order_kind = "label_generation"
        exp.response_signals.append("Order reaches LABEL CREATED and label summary/logs are available.")
    exp.request_types = _dedupe(exp.request_types)
    exp.rate_request_fields = _dedupe(exp.rate_request_fields)
    exp.label_request_fields = _dedupe(exp.label_request_fields)
    exp.response_signals = _dedupe(exp.response_signals)
    exp.negative_assertions = _dedupe(exp.negative_assertions)
    return exp


def _sig_tokens(text: str) -> set[str]:
    tokens = set(re.findall(r"[a-z0-9]{3,}", (text or "").lower()))
    return {t for t in tokens if t not in {"the", "and", "for", "with", "rate", "label", "request", "response"}}


_FAMILY_SIGNALS: dict[str, tuple[str, ...]] = {
    "fedex_rest": (
        "requestedshipment",
        "requestedpackagelineitems",
        "customsclearancedetail",
        "commodities",
        "specialservicetypes",
        "countryofmanufacture",
    ),
    "ups": (
        "shipmentrequest",
        "labelspecification",
        "shipmentserviceoptions",
        "deliveryconfirmation",
        "reasonforexport",
        "commodity",
    ),
    "dhl_express": (
        "exportdeclaration",
        "customerdetails",
        "packages",
        "specialservices",
        "paperlesstrade",
    ),
    "usps": (
        "service",
        "parcel",
        "customs",
        "shipto",
        "shipfrom",
    ),
    "stamps": (
        "stamps",
        "label",
        "package",
        "service",
    ),
    "easypost": (
        "shipment",
        "parcel",
        "to_address",
        "from_address",
    ),
    "canada_post": (
        "parcel",
        "servicecode",
        "mailing-scenario",
        "destination",
    ),
    "mypost_business": (
        "article",
        "shipment",
        "service",
        "mypost",
    ),
    "postnord": (
        "cn22",
        "cn23",
        "countryoforigin",
        "customs",
    ),
}


_FIELD_ALIASES: dict[str, tuple[str, ...]] = {
    "countryofmanufacture": ("countryoforigin", "country_of_origin", "origincountry", "coo"),
    "countryoforigin": ("countryofmanufacture", "country_of_origin", "origincountry", "coo"),
    "customsclearancedetail": ("customs", "commodity", "commodities", "customsdetail"),
    "requestedpackagelineitems": ("packagelineitems", "lineitems", "package", "packages"),
    "shipmentrequest": ("shipment", "shipment request"),
    "labelspecification": ("imagetype", "code", "label specification"),
    "shipmentserviceoptions": ("serviceoptions", "specialservices", "deliveryconfirmation"),
    "reasonforexport": ("repair", "gift", "sample", "reason for export"),
    "deliveryconfirmation": ("signature", "adultsignature", "adult signature"),
    "exportdeclaration": ("customs", "declaration", "paperlesstrade"),
    "to_address": ("destination", "shipto", "recipient"),
    "from_address": ("origin", "shipfrom", "shipper"),
}


def _normalize_observed_text(text: str) -> str:
    lowered = (text or "").lower()
    lowered = lowered.replace('"', " ").replace("'", " ")
    lowered = re.sub(r"[^a-z0-9]+", " ", lowered)
    compact = lowered.replace(" ", "")
    return f"{lowered}\n{compact}"


def _extract_observed_signals(expectation: RequestExpectation, observed_text: str) -> list[str]:
    normalized = _normalize_observed_text(observed_text)
    signals: list[str] = []
    if expectation.request_family:
        family_tokens = _FAMILY_SIGNALS.get(expectation.request_family, ())
        hits = [token for token in family_tokens if token in normalized]
        if hits:
            signals.append(f"{expectation.request_family}: " + ", ".join(hits[:6]))
    for field_name in expectation.special_service_fields[:8]:
        token = re.sub(r"[^a-z0-9]+", "", field_name.lower())
        aliases = _FIELD_ALIASES.get(token, ())
        if token and (token in normalized or any(alias in normalized for alias in aliases)):
            signals.append(f"special-service: {field_name}")
    if expectation.request_format and "xml" in expectation.request_format and "<" in (observed_text or ""):
        signals.append("xml-like payload detected")
    if expectation.request_format and "json" in expectation.request_format and "{" in (observed_text or ""):
        signals.append("json-like payload detected")
    return _dedupe(signals)


def _matches_expectation_item(item: str, normalized_observed: str) -> bool:
    tokens = _sig_tokens(item)
    if not tokens:
        return False
    alias_hits = 0
    direct_hits = 0
    for token in tokens:
        aliases = _FIELD_ALIASES.get(token, ())
        if token in normalized_observed:
            direct_hits += 1
            continue
        if any(alias in normalized_observed for alias in aliases):
            alias_hits += 1
    hit_count = direct_hits + alias_hits
    threshold = 1 if len(tokens) <= 2 else 2
    return hit_count >= threshold


_VALUE_PATTERNS: dict[str, tuple[re.Pattern[str], ...]] = {
    "reason_for_export": (
        re.compile(r"reason\s*for\s*export[^a-z0-9]{0,20}([A-Z_ -]{3,30})", re.I),
        re.compile(r'"ReasonForExport"\s*:\s*"([^"]+)"', re.I),
    ),
    "image_type": (
        re.compile(r'"Code"\s*:\s*"([A-Z]{2,5})"', re.I),
        re.compile(r"image\s*type[^a-z0-9]{0,20}([A-Z]{2,5})", re.I),
    ),
    "country_of_origin": (
        re.compile(r"country\s*of\s*origin[^a-z0-9]{0,20}([A-Z]{2}|[A-Za-z][A-Za-z ]{2,30})", re.I),
        re.compile(r"countryof(origin|manufacture)[^a-z0-9]{0,20}([A-Z]{2}|[A-Za-z][A-Za-z ]{2,30})", re.I),
        re.compile(r'"(countryOfOrigin|countryOfManufacture)"\s*:\s*"([^"]+)"', re.I),
    ),
    "customs_value": (
        re.compile(r"customs\s*value[^0-9]{0,20}([0-9]+(?:\.[0-9]{1,4})?)", re.I),
        re.compile(r"declared\s*value[^0-9]{0,20}([0-9]+(?:\.[0-9]{1,4})?)", re.I),
        re.compile(r'"(customsValue|declaredValue|custom_value)"\s*:\s*"?([0-9]+(?:\.[0-9]{1,4})?)', re.I),
    ),
    "hs_code": (
        re.compile(r"hs\s*code[^a-z0-9]{0,20}([A-Z0-9.\-]{4,20})", re.I),
        re.compile(r'"(hsCode|harmonizedCode|hs_code)"\s*:\s*"([^"]+)"', re.I),
    ),
    "item_identity": (
        re.compile(r'"sku"\s*:\s*"([^"]+)"', re.I),
        re.compile(r'"(productName|itemName|name|title|description|commodityDescription)"\s*:\s*"([^"]+)"', re.I),
        re.compile(r'\bsku\b[^a-z0-9]{0,20}([A-Za-z0-9._\-]{2,40})', re.I),
        re.compile(r'\b(description|commodity description|product name|item name)\b[^a-z0-9]{0,20}([A-Za-z0-9 _.\-]{3,60})', re.I),
    ),
}


def _extract_value_matches(observed_text: str, scenario: str) -> list[str]:
    found: list[str] = []
    scenario_lower = (scenario or "").lower()
    active_keys: list[str] = []
    if "reason for export" in scenario_lower or "repair" in scenario_lower or "gift" in scenario_lower:
        active_keys.append("reason_for_export")
    if "image type" in scenario_lower or "zpl" in scenario_lower or "png" in scenario_lower:
        active_keys.append("image_type")
    if "country of origin" in scenario_lower or "coo" in scenario_lower:
        active_keys.append("country_of_origin")
    if "customs value" in scenario_lower or "declared value" in scenario_lower:
        active_keys.append("customs_value")
    if "hs code" in scenario_lower:
        active_keys.append("hs_code")
    if (
        "multiple products" in scenario_lower
        or "each product" in scenario_lower
        or "individual product" in scenario_lower
        or "product level" in scenario_lower
        or "sku" in scenario_lower
        or "product" in scenario_lower
    ):
        active_keys.append("item_identity")

    for key in active_keys:
        patterns = _VALUE_PATTERNS.get(key, ())
        seen_for_key: list[str] = []
        for pattern in patterns:
            matches = pattern.findall(observed_text or "")
            if not matches:
                continue
            normalized_matches = matches if isinstance(matches, list) else [matches]
            for raw_match in normalized_matches:
                if isinstance(raw_match, tuple):
                    values = [group for group in raw_match if group]
                else:
                    values = [str(raw_match)]
                if not values:
                    continue
                value = values[-1].strip()
                if not value:
                    continue
                if len(value) > 40:
                    value = value[:40].rstrip()
                if value not in seen_for_key:
                    seen_for_key.append(value)
                    found.append(f"{key}: {value}")
                if len(seen_for_key) >= 4:
                    break
            if len(seen_for_key) >= 4:
                break

    if "signature" in scenario_lower or "delivery confirmation" in scenario_lower:
        if re.search(r"deliveryconfirmation|adultsignature|signature", observed_text or "", re.I):
            found.append("delivery_confirmation: signature-related value detected")
    if (
        "multiple products" in scenario_lower
        or "each product" in scenario_lower
        or "product level" in scenario_lower
        or "individual product" in scenario_lower
    ):
        for key in ("country_of_origin", "customs_value", "hs_code"):
            count = sum(1 for entry in found if entry.startswith(f"{key}:"))
            if count:
                found.append(f"{key}_count: {count}")
        item_count = sum(1 for entry in found if entry.startswith("item_identity:"))
        if item_count:
            found.append(f"item_identity_count: {item_count}")
    return _dedupe(found)


def _extract_expected_values_from_scenario(scenario: str) -> list[str]:
    scenario_text = scenario or ""
    lower = scenario_text.lower()
    expected: list[str] = []

    if "reason for export" in lower or "repair" in lower or "gift" in lower:
        for candidate in ("REPAIR", "GIFT", "SAMPLE", "SALE", "RETURN"):
            if candidate.lower() in lower:
                expected.append(f"reason_for_export: {candidate}")
                break

    if "image type" in lower or "zpl" in lower or "png" in lower or "pdf" in lower:
        for candidate in ("ZPL", "PNG", "PDF", "GIF"):
            if candidate.lower() in lower:
                expected.append(f"image_type: {candidate}")
                break

    if "country of origin" in lower or "coo" in lower:
        for pattern in (
            re.compile(r'country\s*of\s*origin[^a-z0-9]{0,20}"?([A-Z]{2}|[A-Za-z][A-Za-z ]{2,30})"?', re.I),
            re.compile(r'\bcoo\b[^a-z0-9]{0,20}"?([A-Z]{2}|[A-Za-z][A-Za-z ]{2,30})"?', re.I),
        ):
            match = pattern.search(scenario_text)
            if match:
                expected.append(f"country_of_origin: {match.group(1).strip()}")
                break

    if "hs code" in lower:
        match = re.search(r'hs\s*code[^a-z0-9]{0,20}"?([A-Z0-9.\-]{4,20})"?', scenario_text, re.I)
        if match:
            expected.append(f"hs_code: {match.group(1).strip()}")

    if "customs value" in lower or "declared value" in lower:
        match = re.search(r'(customs\s*value|declared\s*value)[^0-9]{0,20}([0-9]+(?:\.[0-9]{1,4})?)', scenario_text, re.I)
        if match:
            raw_value = match.group(2).strip()
            expected.append(f"customs_value: {raw_value}")
            if "." in raw_value:
                try:
                    expected.append(f"customs_value_trimmed_2dp: {float(raw_value):.2f}")
                except Exception:
                    pass
        elif "trim to 2" in lower or "2 decimal" in lower or "2 places" in lower:
            expected.append("customs_value_trimmed_2dp: expected")

    if "signature" in lower or "delivery confirmation" in lower or "adult signature" in lower:
        expected.append("delivery_confirmation: expected")

    multi_product_markers = (
        "multiple products",
        "each product",
        "individual product",
        "product level",
        "different coo values",
        "different country of origin",
    )
    if any(marker in lower for marker in multi_product_markers):
        if "country of origin" in lower or "coo" in lower:
            expected.append("country_of_origin_count_min: 2")
        if "customs value" in lower or "declared value" in lower:
            expected.append("customs_value_count_min: 2")
        if "hs code" in lower:
            expected.append("hs_code_count_min: 2")

    return _dedupe(expected)


def _expected_values_from_setup_inputs(setup_values: list[str] | None) -> list[str]:
    expected: list[str] = []
    key_counts: dict[str, int] = {}
    for raw in setup_values or []:
        if ":" not in raw:
            continue
        label, value = raw.split(":", 1)
        label_lower = label.strip().lower()
        normalized_value = value.strip()
        if not normalized_value:
            continue
        if label_lower in {"country of origin", "coo", "origin country"}:
            expected.append(f"country_of_origin: {normalized_value}")
            key_counts["country_of_origin"] = key_counts.get("country_of_origin", 0) + 1
        elif label_lower in {"customs value", "declared value"}:
            expected.append(f"customs_value: {normalized_value}")
            key_counts["customs_value"] = key_counts.get("customs_value", 0) + 1
            try:
                expected.append(f"customs_value_trimmed_2dp: {float(normalized_value):.2f}")
            except Exception:
                pass
        elif label_lower in {"hs code", "harmonized code"}:
            expected.append(f"hs_code: {normalized_value}")
            key_counts["hs_code"] = key_counts.get("hs_code", 0) + 1
        elif label_lower == "image type":
            expected.append(f"image_type: {normalized_value}")
        elif label_lower in {"reason for export"}:
            expected.append(f"reason_for_export: {normalized_value}")
        elif label_lower in {"delivery confirmation", "signature", "adult signature"}:
            expected.append("delivery_confirmation: expected")
    if key_counts.get("country_of_origin", 0) >= 2:
        expected.append(f"country_of_origin_count_min: {key_counts['country_of_origin']}")
    if key_counts.get("customs_value", 0) >= 2:
        expected.append(f"customs_value_count_min: {key_counts['customs_value']}")
    if key_counts.get("hs_code", 0) >= 2:
        expected.append(f"hs_code_count_min: {key_counts['hs_code']}")
    return _dedupe(expected)


def _expected_values_from_setup_item_inputs(setup_item_values: list[str] | None) -> list[str]:
    expected: list[str] = []
    distinct_records: dict[str, set[str]] = {
        "country_of_origin": set(),
        "customs_value": set(),
        "hs_code": set(),
        "item_identity": set(),
    }
    for raw in setup_item_values or []:
        if ":" not in raw or "." not in raw:
            continue
        scoped_label, value = raw.split(":", 1)
        record_name, label = scoped_label.split(".", 1)
        record_name = record_name.strip()
        label_lower = label.strip().lower()
        normalized_value = value.strip()
        if not normalized_value:
            continue
        if label_lower in {"country of origin", "coo", "origin country"}:
            expected.append(f"{record_name}.country_of_origin: {normalized_value}")
            distinct_records["country_of_origin"].add(record_name)
        elif label_lower in {"customs value", "declared value"}:
            expected.append(f"{record_name}.customs_value: {normalized_value}")
            distinct_records["customs_value"].add(record_name)
            try:
                expected.append(f"{record_name}.customs_value_trimmed_2dp: {float(normalized_value):.2f}")
            except Exception:
                pass
        elif label_lower in {"hs code", "harmonized code"}:
            expected.append(f"{record_name}.hs_code: {normalized_value}")
            distinct_records["hs_code"].add(record_name)
        elif label_lower == "item_identity":
            expected.append(f"{record_name}.item_identity: {normalized_value}")
            distinct_records["item_identity"].add(record_name)

    for key, records in distinct_records.items():
        if len(records) >= 2:
            expected.append(f"{key}_count_min: {len(records)}")
    return _dedupe(expected)


def _normalize_value(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (value or "").lower())


def _parse_value_entries(entries: list[str]) -> dict[str, list[str]]:
    parsed: dict[str, list[str]] = {}
    for entry in entries:
        if ":" not in entry:
            continue
        key, raw_value = entry.split(":", 1)
        parsed.setdefault(key.strip(), []).append(raw_value.strip())
    return parsed


def _match_record_scoped_values(expected_values: list[str], observed_values: list[str], base_key: str) -> bool:
    expected_map = _parse_value_entries(expected_values)
    observed_map = _parse_value_entries(observed_values)
    observed_candidates = observed_map.get(base_key, [])
    if not observed_candidates:
        return False
    normalized_observed = [_normalize_value(value) for value in observed_candidates]
    scoped_keys = [key for key in expected_map if key.endswith(f".{base_key}")]
    if not scoped_keys:
        return False
    observed_item_identities = [_normalize_value(value) for value in observed_map.get("item_identity", [])]
    for scoped_key in scoped_keys:
        record_prefix = scoped_key[: -(len(base_key) + 1)]
        scoped_identity_key = f"{record_prefix}.item_identity"
        expected_identities = [_normalize_value(value) for value in expected_map.get(scoped_identity_key, [])]
        if expected_identities and observed_item_identities:
            if not any(
                exp_id and any(exp_id in obs_id or obs_id in exp_id for obs_id in observed_item_identities if obs_id)
                for exp_id in expected_identities
            ):
                continue
        for exp in expected_map.get(scoped_key, []):
            exp_norm = _normalize_value(exp)
            if exp_norm and any(exp_norm in obs or obs in exp_norm for obs in normalized_observed if obs):
                return True
    return False


def _match_value_expectations(item: str, observed_values: list[str], expected_values: list[str]) -> bool:
    item_lower = (item or "").lower()
    value_text = "\n".join(observed_values).lower()
    if not value_text:
        return False
    observed_map = _parse_value_entries(observed_values)
    expected_map = _parse_value_entries(expected_values)

    def _match_expected_key(key: str) -> bool:
        observed = observed_map.get(key, [])
        expected = expected_map.get(key, [])
        if not observed:
            return False
        if not expected:
            return True
        norm_observed = [_normalize_value(value) for value in observed]
        for exp in expected:
            if exp.lower() == "expected":
                return True
            exp_norm = _normalize_value(exp)
            if exp_norm and any(exp_norm in obs or obs in exp_norm for obs in norm_observed if obs):
                return True
        return False

    def _match_count_key(count_key: str, value_key: str) -> bool:
        expected = expected_map.get(count_key, [])
        observed_counts = observed_map.get(f"{value_key}_count", [])
        if not expected:
            return False
        actual_count = 0
        for raw in observed_counts:
            try:
                actual_count = max(actual_count, int(raw))
            except Exception:
                continue
        if not actual_count:
            actual_count = len(observed_map.get(value_key, []))
        for exp in expected:
            try:
                if actual_count >= int(exp):
                    return True
            except Exception:
                continue
        return False

    if "country of origin" in item_lower or "countryoforigin" in item_lower or "countryofmanufacture" in item_lower or "coo" in item_lower:
        return (
            _match_count_key("country_of_origin_count_min", "country_of_origin")
            or _match_record_scoped_values(expected_values, observed_values, "country_of_origin")
            or _match_expected_key("country_of_origin")
        )
    if "customs value" in item_lower or "declared value" in item_lower:
        return (
            _match_count_key("customs_value_count_min", "customs_value")
            or _match_record_scoped_values(expected_values, observed_values, "customs_value_trimmed_2dp")
            or _match_record_scoped_values(expected_values, observed_values, "customs_value")
            or _match_expected_key("customs_value_trimmed_2dp")
            or _match_expected_key("customs_value")
        )
    if "hs code" in item_lower or "harmonized" in item_lower:
        return (
            _match_count_key("hs_code_count_min", "hs_code")
            or _match_record_scoped_values(expected_values, observed_values, "hs_code")
            or _match_expected_key("hs_code")
        )
    if "product" in item_lower or "item" in item_lower or "sku" in item_lower or "commodity" in item_lower:
        return (
            _match_count_key("item_identity_count_min", "item_identity")
            or _match_record_scoped_values(expected_values, observed_values, "item_identity")
            or _match_expected_key("item_identity")
        )
    if "reasonforexport" in item_lower or "reason for export" in item_lower:
        return _match_expected_key("reason_for_export")
    if "imagetype" in item_lower or "image type" in item_lower or "labelspecification" in item_lower:
        return _match_expected_key("image_type")
    if "deliveryconfirmation" in item_lower or "adult signature" in item_lower or "signature" in item_lower:
        return _match_expected_key("delivery_confirmation")
    return False


def compare_expectations(
    expectation: RequestExpectation,
    observed_text: str,
    *,
    observed_sources: list[str] | None = None,
    setup_values: list[str] | None = None,
    setup_item_values: list[str] | None = None,
) -> ExpectationComparison:
    expected_values = _dedupe(
        _expected_values_from_setup_item_inputs(setup_item_values)
        + _expected_values_from_setup_inputs(setup_values)
        + _extract_expected_values_from_scenario(expectation.scenario)
    )
    observed_values = _extract_value_matches(observed_text, expectation.scenario)
    normalized_observed = _normalize_observed_text(observed_text)
    comparison = ExpectationComparison(
        observed_sources=observed_sources or [],
        observed_signals=_extract_observed_signals(expectation, observed_text),
        observed_values=observed_values,
        expected_values=expected_values,
    )
    items = (
        list(expectation.rate_request_fields)
        + list(expectation.label_request_fields)
        + list(expectation.response_signals)
        + [f"NOT: {item}" for item in expectation.negative_assertions]
    )
    for item in items:
        matched = _matches_expectation_item(item, normalized_observed) or _match_value_expectations(item, observed_values, expected_values)
        if item.startswith("NOT: "):
            if matched:
                comparison.missing.append(item)
            else:
                comparison.matched.append(item)
        elif matched:
            comparison.matched.append(item)
        else:
            comparison.missing.append(item)
    return comparison


def build_request_expectations(
    *,
    scenario: str,
    carrier: str,
    expert_insight: str = "",
    domain_context: str = "",
    code_context: str = "",
    model: str | None = None,
) -> RequestExpectation:
    fallback = _heuristic_expectations(scenario, carrier)
    carrier_registry = resolve_carrier_request_profile(carrier).to_text()
    if not getattr(config, "ANTHROPIC_API_KEY", ""):
        return fallback

    try:
        llm = ChatAnthropic(
            model=model or config.CLAUDE_SONNET_MODEL,
            api_key=config.ANTHROPIC_API_KEY,
            max_tokens=1200,
            temperature=0,
        )
        prompt = _EXPECTATION_PROMPT.format(
            scenario=scenario,
            carrier=carrier or "(generic)",
            carrier_registry=(carrier_registry or "(none)")[:1800],
            expert_insight=(expert_insight or "(none)")[:900],
            domain_context=(domain_context or "(none)")[:1400],
            code_context=(code_context or "(none)")[:1800],
        )
        resp = llm.invoke([HumanMessage(content=prompt)])
        raw = resp.content
        if not isinstance(raw, str):
            raw = " ".join(
                block.get("text", "") if isinstance(block, dict) else str(block)
                for block in raw
            )
        data = _parse_json(raw)
        if not data:
            return fallback
        llm_expectation = RequestExpectation(
            carrier=carrier,
            scenario=scenario,
            order_kind=str(data.get("order_kind", fallback.order_kind) or fallback.order_kind),
            request_family=str(data.get("request_family", fallback.request_family) or fallback.request_family),
            request_format=str(data.get("request_format", fallback.request_format) or fallback.request_format),
            request_types=[str(v) for v in (data.get("request_types") or fallback.request_types)],
            rate_request_fields=[str(v) for v in (data.get("rate_request_fields") or fallback.rate_request_fields)],
            label_request_fields=[str(v) for v in (data.get("label_request_fields") or fallback.label_request_fields)],
            response_signals=[str(v) for v in (data.get("response_signals") or fallback.response_signals)],
            negative_assertions=[str(v) for v in (data.get("negative_assertions") or fallback.negative_assertions)],
            special_service_fields=[str(v) for v in (data.get("special_service_fields") or fallback.special_service_fields)],
            reasoning=str(data.get("reasoning", fallback.reasoning) or fallback.reasoning),
        )
        return _merge_expectations(fallback, llm_expectation)
    except Exception as exc:
        logger.debug("build_request_expectations failed: %s", exc)
        return fallback
