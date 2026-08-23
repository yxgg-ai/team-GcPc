from predict import load_model, predict_image

MODEL_PATH = "person2_risk_detection/models/wheat_disease_model.pth"
_model = None

def detect(image_path, sowing_date="2026-06-25"):
    global _model
    if _model is None:
        _model = load_model(MODEL_PATH)

    full_result = predict_image(_model, image_path, sowing_date=sowing_date)

    # Simplified output jaisa dost ne manga hai
    simplified = {
        "growth_stage": full_result["growth_stage"],
        "risk_type": full_result["risk_type"].replace("Fungal — ", ""),
        "risk_score": full_result["risk_score"]
    }
    return simplified


if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        image_path = "person2_risk_detection/data/test_image.jpg"

    result = detect(image_path)
    print(json.dumps(result, indent=2))