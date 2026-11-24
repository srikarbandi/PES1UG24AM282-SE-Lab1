import pytest
from warranty_claims import out_of_warranty_charge, claim_allowed, sla_status

# Example test cases:
def test_within_warranty():
    assert out_of_warranty_charge("standard", 20, "defect", False) == 0

def test_claim_allowed():
    assert claim_allowed(60, 1, False) is True

# Write the rest of the test cases so that the code is 90-100% covered.
