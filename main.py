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

print("\nSelect the growth stage:")
print("1. Seedling")
print("2. Vegetative")
print("3. Flowering")
print("4. Maturity")

stage_choice = input("Enter your choice (1-4): ")

growth_stages = {
    "1": "Seedling",
    "2": "Vegetative",
    "3": "Flowering",
    "4": "Maturity"
}

if stage_choice in growth_stages:
    growth_stage = growth_stages[stage_choice]
    print(f"Growth stage entered: {growth_stage}")
else:
    print("Invalid choice. Please select a number from 1 to 4.")
    growth_stage = None

field_data[0]["growth_stage"] = growth_stage

stage_priority = {
    "Seedling": "Medium",
    "Vegetative": "Medium",
    "Flowering": "High",
    "Maturity": "Low"
}

field_data[0]["stage_priority"] = stage_priority[growth_stage]

print(f"Stage priority: {field_data[0]['stage_priority']}")

print("\nUpdated field data:")
print(json.dumps(field_data, indent=4))