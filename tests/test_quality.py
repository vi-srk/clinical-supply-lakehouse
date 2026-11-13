from datetime import date

from clinical_supply.quality import SHIPMENT_RULES, apply_rules, is_temperature_excursion


def good_shipment(**overrides):
    record = {
        "shipment_id": "SHP-0000001",
        "kit_quantity": 20,
        "shipped_date": date(2026, 1, 1),
        "delivered_date": date(2026, 1, 4),
        "min_temp_c": 3.0,
        "max_temp_c": 6.5,
    }
    return {**record, **overrides}


def test_good_record_passes():
    result = apply_rules([good_shipment()], SHIPMENT_RULES)
    assert len(result.valid) == 1
    assert result.pass_rate == 1.0


def test_bad_records_are_quarantined_with_reasons():
    records = [
        good_shipment(shipment_id=None),
        good_shipment(kit_quantity=-5),
        good_shipment(delivered_date=date(2025, 12, 30)),
        good_shipment(max_temp_c=None),
    ]
    result = apply_rules(records, SHIPMENT_RULES)
    assert result.valid == []
    reasons = [r["_failed_rules"] for r in result.quarantined]
    assert reasons == [
        ["shipment_id_present"],
        ["quantity_positive"],
        ["dates_in_order"],
        ["temperature_recorded"],
    ]


def test_undelivered_shipment_is_valid():
    result = apply_rules([good_shipment(delivered_date=None)], SHIPMENT_RULES)
    assert len(result.valid) == 1


def test_empty_input_has_full_pass_rate():
    assert apply_rules([], SHIPMENT_RULES).pass_rate == 1.0


def test_temperature_excursion():
    assert not is_temperature_excursion(good_shipment())
    assert is_temperature_excursion(good_shipment(max_temp_c=9.1))
    assert is_temperature_excursion(good_shipment(min_temp_c=1.2))
    assert not is_temperature_excursion(good_shipment(max_temp_c=None))
