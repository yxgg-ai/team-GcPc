# pipeline.py

DUMMY_DATA = {
    "F001": {"field_id": "F001", "crop": "Wheat", "confidence_or_score": 0.85,
              "growth_stage": "Flowering", "risk_type": "Fungal — Leaf Rust", "risk_score": 0.78,
              "recommended_action": "Apply recommended fungicide within 48 hours; avoid overhead irrigation",
              "safe_usage_note": "Use only approved fungicide at label dosage; observe pre-harvest interval",
              "referral_flag": False},
    "F002": {"field_id": "F002", "crop": "Wheat", "confidence_or_score": 0.91,
              "growth_stage": "Vegetative", "risk_type": "None detected", "risk_score": 0.15,
              "recommended_action": "Continue routine monitoring",
              "safe_usage_note": "No pesticide action required at this time",
              "referral_flag": False},
    "F003": {"field_id": "F003", "crop": "Rice", "confidence_or_score": 0.58,
              "growth_stage": "Sowing", "risk_type": "Pest — possible aphid activity", "risk_score": 0.52,
              "recommended_action": "Monitor closely; consider neem-based biocontrol if spread continues",
              "safe_usage_note": "Prefer biocontrol before chemical intervention at this stage",
              "referral_flag": True},
}

def get_field_data(field_id):
    return DUMMY_DATA.get(field_id, {"error": "field_id not found"})

def get_all_field_ids():
    return list(DUMMY_DATA.keys())