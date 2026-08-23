from datetime import date

def get_growth_stage(sowing_date_str, current_date_str=None):
    """
    sowing_date_str: "YYYY-MM-DD" format mein sowing ki date
    current_date_str: "YYYY-MM-DD" format mein aaj ki date (default: aaj)
    """
    sowing_date = date.fromisoformat(sowing_date_str)

    if current_date_str:
        current_date = date.fromisoformat(current_date_str)
    else:
        current_date = date.today()

    days_since_sowing = (current_date - sowing_date).days

    if days_since_sowing < 0:
        return "Not sown yet"
    elif days_since_sowing <= 20:
        return "Sowing"
    elif days_since_sowing <= 60:
        return "Vegetative"
    elif days_since_sowing <= 90:
        return "Flowering"
    else:
        return "Maturity"


if __name__ == "__main__":
    # Test cases
    print(get_growth_stage("2026-11-01", "2026-11-10"))   # Sowing
    print(get_growth_stage("2026-11-01", "2026-12-15"))   # Vegetative
    print(get_growth_stage("2026-11-01", "2027-01-10"))   # Flowering
    print(get_growth_stage("2026-11-01", "2027-02-15"))   # Maturity