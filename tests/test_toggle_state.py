from pipeline.toggle_state import _extract_toggle_map, compute_toggle_status


def test_extract_toggle_map_from_dict_and_list_payloads():
    dict_payload = {
        "toggles": {
            "minimum_customs_value_floor": True,
            "label_rollout": {"enabled": False},
        }
    }
    list_payload = {
        "toggles": [
            {"name": "checkout carrier restrictions", "active": True},
            {"key": "smart_label_rules", "status": False},
        ]
    }

    dict_map = _extract_toggle_map(dict_payload)
    list_map = _extract_toggle_map(list_payload)

    assert dict_map["minimumcustomsvaluefloor"] is True
    assert dict_map["labelrollout"] is False
    assert list_map["checkoutcarrierrestrictions"] is True
    assert list_map["smartlabelrules"] is False


def test_compute_toggle_status_matches_normalized_names():
    toggle_map = {
        "minimumcustomsvaluefloor": True,
        "checkoutcarrierrestrictions": False,
    }

    status = compute_toggle_status(
        ["Minimum customs value floor", "checkout carrier restrictions", "unknown toggle"],
        toggle_map,
    )

    assert "Minimum customs value floor" in status["enabled"]
    assert "checkout carrier restrictions" in status["missing"]
    assert "unknown toggle" in status["unknown"]
