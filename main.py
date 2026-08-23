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

growth_stage_factors = {
    "Seedling": 0.8,
    "Vegetative": 1.0,
    "Flowering": 1.2,
    "Maturity": 1.0
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

# STEP 4 - RISK SEVERITY

risk_score = field_data[0]["risk_score"]

stage_factor = growth_stage_factors[growth_stage]

adjusted_risk_score = min(risk_score * stage_factor, 1.0)

if adjusted_risk_score >= 0.70:
    risk_severity = "High"
elif adjusted_risk_score >= 0.40:
    risk_severity = "Moderate"
else:
    risk_severity = "Low"

field_data[0]["adjusted_risk_score"] = round(adjusted_risk_score, 2)

field_data[0]["risk_severity"] = risk_severity

# STEP 5 - RECOMMENDATION ENGINE

risk_type = field_data[0]["risk_type"]

if "Fungal" in risk_type and risk_severity == "High":
    recommended_action = (
        "Apply recommended fungicide within 48 hours; "
        "avoid overhead irrigation"
    )

elif "Fungal" in risk_type and risk_severity == "Moderate":
    recommended_action = (
        "Monitor fungal symptoms closely; "
        "consider approved fungicide if symptoms increase"
    )

elif risk_severity == "High":
    recommended_action = (
        "Take immediate control measures and seek expert advice"
    )

else:
    recommended_action = (
        "Continue monitoring the field for changes"
    )

field_data[0]["recommended_action"] = recommended_action

print(f"Recommended action: {recommended_action}")

print(f"Risk severity: {risk_severity}")

# STEP 6 - REFERRAL CHECK

confidence_score = field_data[0]["confidence_or_score"]

referral_threshold = 0.60

if confidence_score < referral_threshold:
    referral_flag = True
else:
    referral_flag = False

field_data[0]["referral_flag"] = referral_flag

print(f"Referral required: {referral_flag}")

print("\nUpdated field data:")
print(json.dumps(field_data, indent=2))


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

with open("crop_predictions.json", "r") as file:
    person1_data = json.load(file)

    person1_field = person1_data[0]

    # Load Person 2 risk detection output
with open("person2_risk_detection/outputs/dummy_risk_output.json", "r") as file:
    person2_data = json.load(file)

print("Person 2 risk data loaded successfully.")
print(f"Number of risk records from Person 2: {len(person2_data)}")

print("Person 1 data loaded successfully.")
print(f"Number of fields from Person 1: {len(person1_data)}")

# Combine Person 1 crop data with Person 2 risk data

field_data = []

for risk_record in person2_data:
    for crop_record in person1_data:
        if risk_record["field_id"] == crop_record["field_id"]:
            
            combined_record = crop_record.copy()
            combined_record.update(risk_record)
            
            field_data.append(combined_record)

print("Input data loaded successfully.")
print(f"Number of fields: {len(field_data)}")


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

growth_stage_factors = {
    "Seedling": 0.8,
    "Vegetative": 1.0,
    "Flowering": 1.2,
    "Maturity": 1.0
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

# STEP 4 - RISK SEVERITY

person2_risk = next(
    (risk for risk in person2_data if risk["field_id"] == field_data[0]["field_id"]),
    None
)

if person2_risk is None:
    print("No matching Person 2 risk data found.")
    exit()

risk_score = person2_risk["risk_score"]

stage_factor = growth_stage_factors[growth_stage]

adjusted_risk_score = min(risk_score * stage_factor, 1.0)

if adjusted_risk_score >= 0.70:
    risk_severity = "High"
elif adjusted_risk_score >= 0.40:
    risk_severity = "Moderate"
else:
    risk_severity = "Low"

field_data[0]["adjusted_risk_score"] = round(adjusted_risk_score, 2)

field_data[0]["risk_severity"] = risk_severity

# REFERRAL CHECK

referral_flag = person2_data[0].get("referral_flag", False)

field_data[0]["referral_flag"] = referral_flag

# STEP 5 - RECOMMENDATION ENGINE

risk_type = field_data[0]["risk_type"]

# FUNGAL RISK
if "Fungal" in risk_type and risk_severity == "High":
    recommended_action = (
        "Apply recommended fungicide within 48 hours; "
        "avoid overhead irrigation"
    )

elif "Fungal" in risk_type and risk_severity == "Moderate":
    recommended_action = (
        "Monitor fungal symptoms closely; "
        "consider approved fungicide if symptoms increase"
    )

elif "Fungal" in risk_type and risk_severity == "Low":
    recommended_action = (
        "Continue monitoring; "
        "maintain appropriate field conditions"
    )

# PEST RISK
elif "Pest" in risk_type and risk_severity == "High":
    recommended_action = (
        "Take immediate pest management action; "
        "follow integrated pest management guidelines"
    )

elif "Pest" in risk_type and risk_severity == "Moderate":
    recommended_action = (
        "Monitor pest activity closely; "
        "consider appropriate pest management"
    )

elif "Pest" in risk_type and risk_severity == "Low":
    recommended_action = (
        "Continue routine monitoring for pest activity"
    )

# UNCERTAIN / LOW CONFIDENCE
elif "Uncertain" in risk_type:
    recommended_action = (
        "Manual field inspection recommended"
    )

# HEALTHY
elif "Healthy" in risk_type:
    recommended_action = (
        "No action needed; continue routine monitoring"
    )

else:
    recommended_action = (
        "Continue monitoring and assess field conditions"
    )

field_data[0]["recommended_action"] = recommended_action

# STEP 6 - REFERRAL CHECK

confidence_score = field_data[0]["confidence_or_score"]

referral_threshold = 0.60

if confidence_score < referral_threshold:
    referral_flag = True
else:
    referral_flag = False

field_data[0]["referral_flag"] = referral_flag

print(f"Referral required: {referral_flag}")

print("\nUpdated field data:")
print(json.dumps(field_data, indent=4))

with open("person3_output.json", "w", encoding="utf-8") as file:
    json.dump(field_data, file, indent=4)

print("\nPerson 3 output saved successfully.")