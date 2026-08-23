import torch
import torch.nn as nn
from torchvision import models, transforms
from growth_stage import get_growth_stage
from PIL import Image
import json
import sys

# ---- Setup ----
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

wheat_class_names = ['Wheat Black Rust', 'Wheat Brown Rust', 'Wheat Healthy',
                      'Wheat Leaf Blight', 'Wheat Mildew', 'Wheat Septoria', 'Wheat Yellow Rust']

# Risk mapping - schema ke risk_type field ke liye
risk_type_map = {
    'Wheat Healthy': 'Healthy',
    'Wheat Black Rust': 'Fungal — Black Rust',
    'Wheat Brown Rust': 'Fungal — Leaf Rust',
    'Wheat Yellow Rust': 'Fungal — Yellow Rust',
    'Wheat Septoria': 'Fungal — Septoria',
    'Wheat Mildew': 'Fungal — Powdery Mildew',
    'Wheat Leaf Blight': 'Fungal — Leaf Blight'
}

recommended_action_map = {
    'Wheat Healthy': 'No action needed; continue routine monitoring',
    'Wheat Black Rust': 'Apply recommended fungicide within 48 hours; avoid overhead irrigation',
    'Wheat Brown Rust': 'Apply recommended fungicide within 48 hours; avoid overhead irrigation',
    'Wheat Yellow Rust': 'Apply recommended fungicide within 48 hours; avoid overhead irrigation',
    'Wheat Septoria': 'Apply fungicide; remove infected debris post-harvest',
    'Wheat Mildew': 'Apply sulfur-based fungicide; improve field ventilation',
    'Wheat Leaf Blight': 'Apply fungicide; ensure proper crop rotation'
}

CONFIDENCE_THRESHOLD = 0.5  # Iske neeche referral_flag True hoga

# ---- Load model ----
def load_model(model_path):
    model = models.mobilenet_v2(weights=None)
    model.classifier[1] = nn.Linear(model.last_channel, len(wheat_class_names))
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()
    return model

# ---- Predict single image ----
def predict_image(model, image_path, field_id="F001", crop="Wheat", sowing_date="2026-06-25"):
    growth_stage = get_growth_stage(sowing_date)
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    image = Image.open(image_path).convert("RGB")
    image_tensor = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = model(image_tensor)
        probs = torch.nn.functional.softmax(outputs, dim=1)
        confidence, predicted_idx = torch.max(probs, 1)

    predicted_class = wheat_class_names[predicted_idx.item()]
    confidence_score = round(confidence.item(), 2)

    is_healthy = predicted_class == 'Wheat Healthy'
    risk_score = 0.0 if is_healthy else confidence_score
    referral_flag = confidence_score < CONFIDENCE_THRESHOLD

    result = {
        "field_id": field_id,
        "crop": crop,
        "confidence_or_score": confidence_score,
        "growth_stage": growth_stage,
        "risk_type": risk_type_map[predicted_class],
        "risk_score": risk_score,
        "recommended_action": recommended_action_map[predicted_class],
        "safe_usage_note": "Use only approved fungicide at label dosage; observe pre-harvest interval" if not is_healthy else "N/A",
        "referral_flag": referral_flag
    }
    return result

# ---- Run ----
if __name__ == "__main__":
    model = load_model("person2_risk_detection/models/wheat_disease_model.pth")

    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        print("Usage: python predict.py <image_path>")
        sys.exit(1)

    result = predict_image(model, image_path)
    print(json.dumps(result, indent=2))