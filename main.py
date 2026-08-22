import json


# ============================================================
# PERSON 3 — CROP HEALTH & PEST RISK MODULE
# Problem Statement: SIH26131 / PSCMR094
# ============================================================

print("==============================================")
print("   CROP HEALTH & PEST RISK MONITORING SYSTEM")
print("==============================================")
print("Person 3 module started successfully.\n")

# ============================================================
# STEP 2 — SAMPLE INPUT DATA
# ============================================================

field_data = [
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
    }
]

print("Input data loaded successfully.")
print(f"Number of fields: {len(field_data)}")