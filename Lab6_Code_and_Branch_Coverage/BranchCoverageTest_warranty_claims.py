"""Lab 6 - Branch coverage tests for warranty_claims.py

Every decision in the module is exercised both ways (True and False), with
boundary values on each side of the comparisons.

Run from inside the "Lab 6" folder:
    coverage run --branch -m pytest BranchCoverageTest_warranty_claims.py
    coverage report -m
"""
import pytest
from warranty_claims import out_of_warranty_charge, claim_allowed, sla_status


# ---------------------------------------------------------------------------
# out_of_warranty_charge - input validation
#   if plan not in COVERED_MONTHS      (True: raises / False: continues)
#   if age_months < 0                  (True: raises / False: continues)
# ---------------------------------------------------------------------------

def test_unknown_plan_raises():
    with pytest.raises(ValueError, match="unknown plan"):
        out_of_warranty_charge("gold", 10, "defect", False)


def test_negative_age_raises():
    with pytest.raises(ValueError, match="invalid age"):
        out_of_warranty_charge("basic", -1, "defect", False)


def test_age_zero_is_valid():
    # boundary: 0 is not negative, so no exception and well within warranty
    assert out_of_warranty_charge("basic", 0, "defect", False) == 0


# ---------------------------------------------------------------------------
# out_of_warranty_charge - registration bonus
#   if is_registered and plan != "premium"   (+6 months covered)
# ---------------------------------------------------------------------------

def test_registered_basic_gets_six_extra_months():
    # covered = 12 + 6 = 18
    assert out_of_warranty_charge("basic", 18, "defect", True) == 0
    assert out_of_warranty_charge("basic", 19, "defect", True) == 100


def test_registered_standard_gets_six_extra_months():
    # covered = 24 + 6 = 30
    assert out_of_warranty_charge("standard", 30, "defect", True) == 0
    assert out_of_warranty_charge("standard", 31, "defect", True) == 100


def test_registered_premium_gets_no_bonus():
    # registered but premium -> covered stays 36
    assert out_of_warranty_charge("premium", 36, "defect", True) == 0
    assert out_of_warranty_charge("premium", 37, "defect", True) == 100


def test_unregistered_gets_no_bonus():
    # covered stays 12
    assert out_of_warranty_charge("basic", 12, "defect", False) == 0
    assert out_of_warranty_charge("basic", 13, "defect", False) == 100


# ---------------------------------------------------------------------------
# out_of_warranty_charge - charge calculation
#   if excess <= 0                        (return 0)
#   if claim_type == "accidental"         (rate 200 / rate 100)
#   if excess > 12                        (+50 surcharge)
#       if claim_type == "accidental"     (+25 extra)
# ---------------------------------------------------------------------------

def test_within_warranty():
    # starter test
    assert out_of_warranty_charge("standard", 20, "defect", False) == 0


def test_accidental_short_excess_uses_higher_rate():
    # covered 12, excess 8 -> 8 * 200
    assert out_of_warranty_charge("basic", 20, "accidental", False) == 1600


def test_non_accidental_short_excess_uses_base_rate():
    # covered 12, excess 8 -> 8 * 100 (any claim type other than "accidental")
    assert out_of_warranty_charge("basic", 20, "defect", False) == 800
    assert out_of_warranty_charge("basic", 20, "cosmetic", False) == 800


def test_excess_of_exactly_12_has_no_surcharge():
    # boundary: excess > 12 is False when excess == 12
    assert out_of_warranty_charge("basic", 24, "defect", False) == 12 * 100
    assert out_of_warranty_charge("basic", 24, "accidental", False) == 12 * 200


def test_excess_of_13_defect_gets_surcharge():
    # boundary: excess 13 -> rate 100 + 50
    assert out_of_warranty_charge("basic", 25, "defect", False) == 13 * 150


def test_excess_of_13_accidental_gets_extra_surcharge():
    # boundary: excess 13 -> rate 200 + 50 + 25
    assert out_of_warranty_charge("basic", 25, "accidental", False) == 13 * 275


def test_registered_accidental_long_excess():
    # covered 12 + 6 = 18, excess 22 -> rate 275
    assert out_of_warranty_charge("basic", 40, "accidental", True) == 22 * 275


# ---------------------------------------------------------------------------
# claim_allowed
#   if is_recall                      (claims_filed <= 5)
#   if days_since_last_claim < 30     (False)
#   otherwise                         (claims_filed <= 2)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("claims_filed, expected", [
    (0, True),
    (5, True),    # boundary: limit for recalls is 5
    (6, False),   # boundary: one over the limit
])
def test_recall_claim_limit(claims_filed, expected):
    # days_since_last_claim = 0 on purpose: recalls ignore the waiting period
    assert claim_allowed(0, claims_filed, True) is expected


@pytest.mark.parametrize("days_since_last_claim, expected", [
    (0, False),
    (29, False),  # boundary: still inside the 30 day waiting period
    (30, True),   # boundary: waiting period over
])
def test_non_recall_waiting_period(days_since_last_claim, expected):
    assert claim_allowed(days_since_last_claim, 0, False) is expected


@pytest.mark.parametrize("claims_filed, expected", [
    (1, True),    # starter test case
    (2, True),    # boundary: limit for normal claims is 2
    (3, False),   # boundary: one over the limit
])
def test_non_recall_claim_limit(claims_filed, expected):
    assert claim_allowed(60, claims_filed, False) is expected


# ---------------------------------------------------------------------------
# sla_status
#   if is_hardware                   (cutoff 48 / 24)
#   if is_priority                   (cutoff + 24)
#   if hours_left >= cutoff          (on_track)
#   elif hours_left >= cutoff - 12   (at_risk)
#   else                             (critical)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("hours_left, is_hardware, is_priority, expected", [
    # software, normal priority -> cutoff 24
    (24, False, False, "on_track"),
    (23, False, False, "at_risk"),
    (12, False, False, "at_risk"),
    (11, False, False, "critical"),
    # hardware, normal priority -> cutoff 48
    (48, True, False, "on_track"),
    (47, True, False, "at_risk"),
    (36, True, False, "at_risk"),
    (35, True, False, "critical"),
    # software, priority -> cutoff 48
    (48, False, True, "on_track"),
    (36, False, True, "at_risk"),
    (35, False, True, "critical"),
    # hardware, priority -> cutoff 72
    (72, True, True, "on_track"),
    (60, True, True, "at_risk"),
    (59, True, True, "critical"),
])
def test_sla_status(hours_left, is_hardware, is_priority, expected):
    assert sla_status(hours_left, is_hardware, is_priority) == expected
