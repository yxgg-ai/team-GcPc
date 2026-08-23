# pipeline.py
import functools

# ---- SAFE DEFAULTS — used only if a real module function fails ----
SAFE_DEFAULT_CROP = {"crop": "Unknown", "confidence_or_score": 0.0}
SAFE_DEFAULT_RISK = {"growth_stage": "Unknown", "risk_type": "Unable to assess", "risk_score": 0.0}
SAFE_DEFAULT_ADVISORY = {
    "recommended_action": "Manual inspection recommended — automated assessment unavailable",
    "safe_usage_note": "No automated recommendation available; consult local agricultural extension officer",
    "referral_flag": True,
}

def safe_call(default_value):
    """Decorator: if the wrapped function raises or returns something broken,
    fall back to a safe default instead of crashing the API."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                if not isinstance(result, dict):
                    raise ValueError("module returned non-dict result")
                return result
            except Exception as e:
                print(f"[FALLBACK TRIGGERED] {func.__name__} failed: {e}")
                return dict(default_value)
        return wrapper
    return decorator

# ---- SAMPLE FIELD LOCATIONS (used by all modules + map) ----
FIELD_LOCATIONS = {
    "F001": {"lat": 28.6139, "lon": 77.2090},
    "F002": {"lat": 28.7041, "lon": 77.1025},
    "F003": {"lat": 28.5355, "lon": 77.3910},
}

# ---- MODULE 1: Person 1's crop classification ----
@safe_call(SAFE_DEFAULT_CROP)
def classify_crop(field_id):
    dummy = {
        "F001": {"crop": "Wheat", "confidence_or_score": 0.85},
        "F002": {"crop": "Wheat", "confidence_or_score": 0.91},
        "F003": {"crop": "Rice", "confidence_or_score": 0.58},
    }
    return dummy.get(field_id, dict(SAFE_DEFAULT_CROP))

# ---- MODULE 2: Person 2's risk detection ----
@safe_call(SAFE_DEFAULT_RISK)
def detect_risk(field_id):
    dummy = {
        "F001": {"growth_stage": "Flowering", "risk_type": "Fungal — Leaf Rust", "risk_score": 0.78},
        "F002": {"growth_stage": "Vegetative", "risk_type": "None detected", "risk_score": 0.15},
        "F003": {"growth_stage": "Sowing", "risk_type": "Pest — possible aphid activity", "risk_score": 0.52},
    }
    return dummy.get(field_id, dict(SAFE_DEFAULT_RISK))

# ---- MODULE 3: Person 3's advisory engine ----
@safe_call(SAFE_DEFAULT_ADVISORY)
def generate_advisory(field_id, risk_score, confidence_or_score):
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
    return dummy.get(field_id, dict(SAFE_DEFAULT_ADVISORY))

# ---- ASSEMBLES THE FULL RECORD — this is what app.py calls ----
def get_field_data(field_id):
    if field_id not in FIELD_LOCATIONS:
        return {"error": "field_id not found"}

    crop_data = classify_crop(field_id)
    risk_data = detect_risk(field_id)
    advisory_data = generate_advisory(field_id, risk_data["risk_score"], crop_data["confidence_or_score"])

    return {
        "field_id": field_id,
        **crop_data,
        **risk_data,
        **advisory_data,
    }

def get_all_field_ids():
    return list(FIELD_LOCATIONS.keys())

def get_field_locations():
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