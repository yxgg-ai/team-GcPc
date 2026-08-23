# Person 2 — Crop Health Risk Detection

AI/ML engine for detecting wheat disease/pest risk from leaf images, with growth-stage
context and confidence-based expert referral.

## Files

| File | Purpose |
|---|---|
| `src/download_data.py` | Downloads and filters wheat leaf disease dataset from HuggingFace |
| `src/growth_stage.py` | Computes crop growth stage from sowing date |
| `src/predict.py` | Loads trained model, runs prediction on a single image, outputs full schema |
| `src/batch_predict.py` | Runs prediction on a folder of images at once |
| `src/risk_detector.py` | Simplified `detect(image_path)` wrapper for teammate integration |
| `src/dummy_output.py` | Day 1 hardcoded sample output (schema placeholder) |
| `src/get_test_image.py`, `src/get_batch_images.py` | Utility scripts to pull sample images from the dataset for testing |

## Model

MobileNetV2 (transfer learning), trained on 1,401 wheat leaf images across 7 classes
(Healthy, Black Rust, Brown Rust, Yellow Rust, Septoria, Mildew, Leaf Blight).
83% train accuracy, 75% validation accuracy.

Model weights (`wheat_disease_model.pth`) are not committed to the repo (too large) —
download/train separately using `src/download_data.py` and the training notebook, then
place the `.pth` file in `models/`.

## Usage

```bash
pip install -r requirements.txt

# Single image
python src/predict.py path/to/leaf_image.jpg

# Batch (folder of images)
python src/batch_predict.py

# Simplified interface for integration
python -c "from src.risk_detector import detect; print(detect('path/to/image.jpg'))"
```

## Output schema

```json
{
  "field_id": "F001",
  "crop": "Wheat",
  "confidence_or_score": 0.82,
  "growth_stage": "Flowering",
  "risk_type": "Fungal — Leaf Rust",
  "risk_score": 0.71,
  "recommended_action": "Apply recommended fungicide within 48 hours; avoid overhead irrigation",
  "safe_usage_note": "Use only approved fungicide at label dosage; observe pre-harvest interval",
  "referral_flag": false
}
```