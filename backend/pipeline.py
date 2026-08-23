# pipeline.py
# pipeline.py

# ---- SAMPLE FIELD LOCATIONS (used by all modules + map) ----
FIELD_LOCATIONS = {
    "F001": {"lat": 28.6139, "lon": 77.2090},  # Delhi region, placeholder
    "F002": {"lat": 28.7041, "lon": 77.1025},
    "F003": {"lat": 28.5355, "lon": 77.3910},
}

# ---- MODULE 1: Person 1's crop classification ----
def classify_crop(field_id):
    # DUMMY — replace with Person 1's real function when ready
    dummy = {
        "F001": {"crop": "Wheat", "confidence_or_score": 0.85},
        "F002": {"crop": "Wheat", "confidence_or_score": 0.91},
        "F003": {"crop": "Rice", "confidence_or_score": 0.58},
    }
    return dummy.get(field_id, {"crop": "Unknown", "confidence_or_score": 0.0})

# ---- MODULE 2: Person 2's risk detection ----
def detect_risk(field_id):
    # DUMMY — replace with Person 2's real function when ready
    dummy = {
        "F001": {"growth_stage": "Flowering", "risk_type": "Fungal — Leaf Rust", "risk_score": 0.78},
        "F002": {"growth_stage": "Vegetative", "risk_type": "None detected", "risk_score": 0.15},
        "F003": {"growth_stage": "Sowing", "risk_type": "Pest — possible aphid activity", "risk_score": 0.52},
    }
    return dummy.get(field_id, {"growth_stage": "Unknown", "risk_type": "Unknown", "risk_score": 0.0})

# ---- MODULE 3: Person 3's advisory engine ----
def generate_advisory(field_id, risk_score, confidence_or_score):
    # DUMMY — replace with Person 3's real function when ready
    dummy = {
        "F001": {"recommended_action": "Apply recommended fungicide within 48 hours; avoid overhead irrigation",
                  "safe_usage_note": "Use only approved fungicide at label dosage; observe pre-harvest interval",
                  "referral_flag": False},
        "F002": {"recommended_action": "Continue routine monitoring",
                  "safe_usage_note": "No pesticide action required at this time",
                  "referral_flag": False},
        "F003": {"recommended_action": "Monitor closely; consider neem-based biocontrol if spread continues",
                  "safe_usage_note": "Prefer biocontrol before chemical intervention at this stage",
                  "referral_flag": True},
    }
    return dummy.get(field_id, {"recommended_action": "N/A", "safe_usage_note": "N/A", "referral_flag": True})

# ---- ASSEMBLES THE FULL RECORD — this is what app.py calls ----
def get_field_data(field_id):
    crop_data = classify_crop(field_id)
    risk_data = detect_risk(field_id)
    advisory_data = generate_advisory(field_id, risk_data["risk_score"], crop_data["confidence_or_score"])

    if field_id not in FIELD_LOCATIONS:
        return {"error": "field_id not found"}

    return {
        "field_id": field_id,
        **crop_data,
        **risk_data,
        **advisory_data,
    }

def get_all_field_ids():
    return list(FIELD_LOCATIONS.keys())

def get_field_locations():
    # For Person 5's map view
    result = []
    for fid, loc in FIELD_LOCATIONS.items():
        data = get_field_data(fid)
        result.append({
            "field_id": fid,
            "lat": loc["lat"],
            "lon": loc["lon"],
            "risk_type": data["risk_type"],
            "risk_score": data["risk_score"],
        })
    return result