import pytest
from amusement_park_ride_access import process_ride_admissions, inspect_safety_restraints


def test_invalid_groups_type():
    with pytest.raises(ValueError):
        process_ride_admissions({}, 5)


def test_negative_express_fee():
    with pytest.raises(ValueError):
        process_ride_admissions([], -0.01)


def test_closed_group_and_open_group():
    result = process_ride_admissions([
        {"is_open": False, "ride_type": "family", "patrons": [{"height_cm": 150}]},
        {"is_open": True, "ride_type": "family", "patrons": [{"height_cm": 150}]},
    ], 5)
    assert result == {"total_revenue": 10.0, "status": "COMPLETED"}


def test_all_ride_types_and_unknown_type():
    groups = [
        {"is_open": True, "ride_type": "roller_coaster", "patrons": [{"height_cm": 150}]},
        {"is_open": True, "ride_type": "water_ride", "patrons": [{"height_cm": 150}]},
        {"is_open": True, "ride_type": "family", "patrons": [{"height_cm": 150}]},
        {"is_open": True, "ride_type": "unknown", "patrons": [{"height_cm": 150}]},
    ]
    result = process_ride_admissions(groups, 5)
    assert result == {"total_revenue": 53.0, "status": "COMPLETED"}


def test_patron_height_and_child_decisions():
    groups = [{"is_open": True, "ride_type": "family", "patrons": [
        {"height_cm": 0},                 # invalid height
        {"height_cm": 119},               # below minimum
        {"height_cm": 120, "is_child": True},
        {"height_cm": 160, "is_child": False},
    ]}]
    result = process_ride_admissions(groups, 5)
    assert result == {"total_revenue": 16.0, "status": "COMPLETED"}


def test_health_warning_non_coaster_and_coaster():
    non_coaster = process_ride_admissions([{"is_open": True, "ride_type": "family", "patrons": [
        {"height_cm": 150, "health_warning": True}, {"height_cm": 150}
    ]}], 5)
    assert non_coaster["total_revenue"] == 10.0

    coaster = process_ride_admissions([{"is_open": True, "ride_type": "roller_coaster", "patrons": [
        {"height_cm": 150}, {"height_cm": 150, "health_warning": True}, {"height_cm": 150}
    ]}], 5)
    assert coaster == {"total_revenue": 0.0, "status": "ZERO_ADMISSIONS"}


def test_fast_lane_enabled_and_disabled():
    result = process_ride_admissions([
        {"is_open": True, "ride_type": "family", "has_fast_lane": True, "patrons": [{"height_cm": 150}]},
        {"is_open": True, "ride_type": "family", "has_fast_lane": False, "patrons": [{"height_cm": 150}]},
    ], 7)
    assert result["total_revenue"] == 27.0


def test_safety_audit_and_zero_admissions_and_completed():
    audit = process_ride_admissions([{"is_open": True, "patrons": [{"height_cm": 0} for _ in range(5)]}], 5)
    zero = process_ride_admissions([{"is_open": True, "patrons": [{"height_cm": 0}]}], 5)
    completed = process_ride_admissions([{"is_open": True, "patrons": [{"height_cm": 150}]}], 5)
    assert audit["status"] == "SAFETY_AUDIT"
    assert zero["status"] == "ZERO_ADMISSIONS"
    assert completed["status"] == "COMPLETED"


def test_restraint_empty_stream():
    assert inspect_safety_restraints([]) == "NO_DATA"


def test_restraint_zero_streak_reset_and_emergency():
    assert inspect_safety_restraints([[0, 1, 0, 1]]) == "SAFE"
    assert inspect_safety_restraints([[1, 0, 0]]) == "EMERGENCY_LOCK"
