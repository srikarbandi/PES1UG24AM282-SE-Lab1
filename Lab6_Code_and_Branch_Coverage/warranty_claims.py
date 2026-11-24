COVERED_MONTHS = {"basic": 12, "standard": 24, "premium": 36}


def out_of_warranty_charge(plan, age_months, claim_type, is_registered):
    if plan not in COVERED_MONTHS:
        raise ValueError("unknown plan")
    if age_months < 0:
        raise ValueError("invalid age")
    covered = COVERED_MONTHS[plan]
    if is_registered and plan != "premium":
        covered += 6
    excess = age_months - covered
    if excess <= 0:
        return 0
    if claim_type == "accidental":
        rate = 200
    else:
        rate = 100
    if excess > 12:
        rate = rate + 50
        if claim_type == "accidental":
            rate += 25
    return excess * rate


def claim_allowed(days_since_last_claim, claims_filed, is_recall):
    if is_recall:
        return claims_filed <= 5
    if days_since_last_claim < 30:
        return False
    return claims_filed <= 2


def sla_status(hours_left, is_hardware, is_priority):
    if is_hardware:
        cutoff = 48
    else:
        cutoff = 24
    if is_priority:
        cutoff += 24
    if hours_left >= cutoff:
        return "on_track"
    elif hours_left >= cutoff - 12:
        return "at_risk"
    return "critical"
