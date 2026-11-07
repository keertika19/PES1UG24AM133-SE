import pytest
from amusement_park_ride_access import process_ride_admissions, inspect_safety_restraints


def test_adult_family_ride():
    result = process_ride_admissions([{"is_open": True, "ride_type": "family", "patrons": [{"height_cm": 150}]}], 5)
    assert result == {"total_revenue": 10.0, "status": "COMPLETED"}


def test_child_water_ride_with_fast_lane():
    result = process_ride_admissions([{"is_open": True, "ride_type": "water_ride", "has_fast_lane": True,
                                      "patrons": [{"height_cm": 130, "is_child": True}]}], 5)
    assert result == {"total_revenue": 15.8, "status": "COMPLETED"}


def test_roller_coaster_adult():
    result = process_ride_admissions([{"is_open": True, "ride_type": "roller_coaster",
                                      "patrons": [{"height_cm": 180}]}], 5)
    assert result["total_revenue"] == 25.0


def test_closed_ride_is_skipped():
    result = process_ride_admissions([{"is_open": False, "ride_type": "family"}], 5)
    assert result["status"] == "ZERO_ADMISSIONS"


def test_unknown_ride_type_is_rejected():
    result = process_ride_admissions([{"is_open": True, "ride_type": "virtual"}], 5)
    assert result["status"] == "ZERO_ADMISSIONS"


def test_invalid_height_is_rejected():
    result = process_ride_admissions([{"is_open": True, "patrons": [{"height_cm": 0}]}], 5)
    assert result["status"] == "ZERO_ADMISSIONS"


def test_health_warning_rejects_patron():
    result = process_ride_admissions([{"is_open": True, "ride_type": "family",
                                      "patrons": [{"height_cm": 160, "health_warning": True}]}], 5)
    assert result["status"] == "ZERO_ADMISSIONS"


def test_too_many_rejections_trigger_audit():
    patrons = [{"height_cm": 0} for _ in range(5)]
    result = process_ride_admissions([{"is_open": True, "patrons": patrons}], 5)
    assert result["status"] == "SAFETY_AUDIT"


def test_invalid_groups_and_negative_fee_raise_error():
    with pytest.raises(ValueError):
        process_ride_admissions("not a list", 5)
    with pytest.raises(ValueError):
        process_ride_admissions([], -1)


def test_restraint_no_data():
    assert inspect_safety_restraints([]) == "NO_DATA"


def test_restraint_safe_readings():
    assert inspect_safety_restraints([[0, 1, 0, 1], [1, 1, 0]]) == "SAFE"


def test_restraint_emergency_lock():
    assert inspect_safety_restraints([[1, 0, 0, 1]]) == "EMERGENCY_LOCK"
