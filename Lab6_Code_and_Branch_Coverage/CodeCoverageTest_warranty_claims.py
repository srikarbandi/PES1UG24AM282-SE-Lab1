"""Lab 6 - Code (line) coverage tests for warranty_claims.py

Run from inside the "Lab 6" folder:
    coverage run -m pytest CodeCoverageTest_warranty_claims.py
    coverage report -m
"""
import pytest
from warranty_claims import out_of_warranty_charge, claim_allowed, sla_status


# ---------------------------------------------------------------------------
# out_of_warranty_charge
# ---------------------------------------------------------------------------

def test_within_warranty():
    # starter test: standard covers 24 months, age 20 -> excess <= 0 -> returns 0
    assert out_of_warranty_charge("standard", 20, "defect", False) == 0


def test_unknown_plan_raises():
    with pytest.raises(ValueError, match="unknown plan"):
        out_of_warranty_charge("gold", 10, "defect", False)


def test_negative_age_raises():
    with pytest.raises(ValueError, match="invalid age"):
        out_of_warranty_charge("basic", -1, "defect", False)


def test_registered_accidental_long_excess():
    # basic 12 + 6 (registered) = 18 months covered, excess = 40 - 18 = 22
    # rate = 200 (accidental) + 50 (excess > 12) + 25 (accidental surcharge) = 275
    assert out_of_warranty_charge("basic", 40, "accidental", True) == 22 * 275


def test_defect_long_excess():
    # basic 12 months covered, excess = 40 - 12 = 28
    # rate = 100 (other claim types) + 50 (excess > 12) = 150
    assert out_of_warranty_charge("basic", 40, "defect", False) == 28 * 150


# ---------------------------------------------------------------------------
# claim_allowed
# ---------------------------------------------------------------------------

def test_claim_allowed():
    # starter test: not a recall, 60 days since last claim, 1 claim filed
    assert claim_allowed(60, 1, False) is True


def test_claim_too_soon_after_last_claim():
    assert claim_allowed(10, 0, False) is False


def test_recall_claim_allowed():
    assert claim_allowed(0, 3, True) is True


# ---------------------------------------------------------------------------
# sla_status
# ---------------------------------------------------------------------------

def test_sla_on_track_hardware_priority():
    # hardware (48) + priority (24) -> cutoff 72, 100 hours left
    assert sla_status(100, True, True) == "on_track"


def test_sla_at_risk_software():
    # software cutoff 24: 15 hours left is below 24 but not below 12
    assert sla_status(15, False, False) == "at_risk"


def test_sla_critical_software():
    assert sla_status(5, False, False) == "critical"
