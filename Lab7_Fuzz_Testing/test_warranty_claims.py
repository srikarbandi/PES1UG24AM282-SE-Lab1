from hypothesis import given, strategies as st
from warranty_claims import parse_claim, age_average, payable_charge


@given(st.text() | st.none())
def test_parse_claim_no_crash(s):
    try:
        parse_claim(s)
    except Exception as e:
        assert False, f"parse_claim crashed with: {e!r}"


@given(st.text() | st.none())
def test_age_average_no_crash(s):
    try:
        age_average(s)
    except Exception as e:
        assert False, f"age_average crashed with: {e!r}"


@given(st.text() | st.none())
def test_payable_charge_no_crash(s):
    try:
        payable_charge(s)
    except Exception as e:
        assert False, f"payable_charge crashed with: {e!r}"


# ---------------------------------------------------------------------------
# Extra properties: well-formed input must still give correct answers, so the
# hardening cannot be "reject everything".
# ---------------------------------------------------------------------------

@given(
    st.text(min_size=1).filter(lambda p: ":" not in p and p.strip()),
    st.floats(min_value=0, max_value=1e9),
)
def test_parse_claim_valid_input(plan, months):
    assert parse_claim(f"{plan}:{months!r}") == (plan.strip().title(), months)


@given(st.lists(st.integers(min_value=0, max_value=10**6), min_size=1))
def test_age_average_valid_input(ages):
    result = age_average(",".join(str(age) for age in ages))
    assert min(ages) <= result <= max(ages)


@given(
    st.floats(min_value=0, max_value=1e9),
    st.floats(min_value=0, max_value=1e9),
)
def test_payable_charge_valid_input(charge, discount):
    result = payable_charge(f"{charge!r}|{discount!r}")
    assert result is not None and result >= 0
