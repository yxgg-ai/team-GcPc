import os
import json
from predict import load_model, predict_image

def batch_predict(model, image_folder, sowing_date="2026-06-25"):
    results = []
    field_counter = 1

    for filename in os.listdir(image_folder):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            image_path = os.path.join(image_folder, filename)
            field_id = f"F{field_counter:03d}"

            result = predict_image(model, image_path, field_id=field_id, sowing_date=sowing_date)
            results.append(result)
            field_counter += 1

    return results

if __name__ == "__main__":
    model = load_model("person2_risk_detection/models/wheat_disease_model.pth")

    folder = "person2_risk_detection/data/test_batch"
    results = batch_predict(model, folder)

    output_path = "person2_risk_detection/outputs/batch_risk_output.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Processed {len(results)} images")
    print(f"Saved to {output_path}")