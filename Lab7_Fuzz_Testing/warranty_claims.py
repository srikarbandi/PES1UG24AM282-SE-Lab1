import math


def to_finite_float(text):
    """Convert text to a float; return None if it is not a finite number."""
    try:
        value = float(text)
    except ValueError:
        return None
    return value if math.isfinite(value) else None


def parse_claim(text):
    """Parse "plan:months" into (Plan, months); return None if invalid."""
    if not isinstance(text, str):
        return None
    parts = text.split(':')
    if len(parts) != 2:
        return None
    plan = parts[0].strip()
    months = to_finite_float(parts[1])
    if not plan or months is None or months < 0:
        return None
    return plan.title(), months


def age_average(ages_csv):
    """Return the whole-number average of comma-separated ages, or None."""
    if not isinstance(ages_csv, str):
        return None
    try:
        values = [int(r) for r in ages_csv.split(',')]
    except ValueError:
        return None
    # split() always yields at least one item, so values is never empty
    if any(v < 0 for v in values):
        return None
    return sum(values) // len(values)


def payable_charge(text):
    """Return the charge after 18% tax and discount, or None if invalid."""
    if not isinstance(text, str):
        return None
    parts = text.split('|')
    if len(parts) != 2:
        return None
    charge = to_finite_float(parts[0])
    discount = to_finite_float(parts[1])
    if charge is None or discount is None or charge < 0 or discount < 0:
        return None
    total = charge * 1.18 - discount
    if not math.isfinite(total):
        return None
    return max(total, 0)


def main():
    print("==== Running parse_claim ====")
    user_input = input("Enter plan:age in months (e.g. standard:30): ")
    result = parse_claim(user_input)
    if result is None:
        print("Invalid input. Expected plan:months, e.g. standard:30")
    else:
        print("Plan and Age:", result)

    print("\n==== Running age_average ====")
    user_input = input("Enter product ages as CSV (e.g. 12,24,36): ")
    result = age_average(user_input)
    if result is None:
        print("Invalid input. Expected whole numbers separated by commas")
    else:
        print("Average Age:", result)

    print("\n==== Running payable_charge ====")
    user_input = input("Enter charge|discount (e.g. 1500|200): ")
    result = payable_charge(user_input)
    if result is None:
        print("Invalid input. Expected charge|discount, e.g. 1500|200")
    else:
        print("Payable Charge:", result)


if __name__ == "__main__":
    main()
