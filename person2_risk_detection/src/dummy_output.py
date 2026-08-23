import json

dummy_samples = [
    {
        "field_id": "F001",
        "crop": "Wheat",
        "confidence_or_score": 0.82,
        "growth_stage": "Flowering",
        "risk_type": "Fungal — Leaf Rust",
        "risk_score": 0.71,
        "recommended_action": "Apply recommended fungicide within 48 hours; avoid overhead irrigation",
        "safe_usage_note": "Use only approved fungicide at label dosage; observe pre-harvest interval",
        "referral_flag": False
    },
    {
        "field_id": "F002",
        "crop": "Wheat",
        "confidence_or_score": 0.55,
        "growth_stage": "Vegetative",
        "risk_type": "Healthy",
        "risk_score": 0.08,
        "recommended_action": "No action needed; continue routine monitoring",
        "safe_usage_note": "N/A",
        "referral_flag": False
    },
    {
        "field_id": "F003",
        "crop": "Wheat",
        "confidence_or_score": 0.39,
        "growth_stage": "Sowing",
        "risk_type": "Uncertain — low confidence",
        "risk_score": 0.40,
        "recommended_action": "Manual field inspection recommended",
        "safe_usage_note": "N/A",
        "referral_flag": True
    },
    {
        "field_id": "F004",
        "crop": "Wheat",
        "confidence_or_score": 0.90,
        "growth_stage": "Maturity",
        "risk_type": "Fungal — Powdery Mildew",
        "risk_score": 0.63,
        "recommended_action": "Apply sulfur-based fungicide; improve field ventilation",
        "safe_usage_note": "Use only approved fungicide at label dosage; observe pre-harvest interval",
        "referral_flag": False
    },
    {
        "field_id": "F005",
        "crop": "Wheat",
        "confidence_or_score": 0.77,
        "growth_stage": "Vegetative",
        "risk_type": "Pest — Aphid infestation",
        "risk_score": 0.58,
        "recommended_action": "Apply neem-based insecticide; monitor for 3-5 days",
        "safe_usage_note": "Follow integrated pest management guidelines",
        "referral_flag": False
    },
    {
        "field_id": "F006",
        "crop": "Wheat",
        "confidence_or_score": 0.85,
        "growth_stage": "Flowering",
        "risk_type": "Healthy",
        "risk_score": 0.05,
        "recommended_action": "No action needed; continue routine monitoring",
        "safe_usage_note": "N/A",
        "referral_flag": False
    }
]

with open("person2_risk_detection/outputs/dummy_risk_output.json", "w") as f:
    json.dump(dummy_samples, f, indent=2)

print("Done! Check outputs/dummy_risk_output.json")