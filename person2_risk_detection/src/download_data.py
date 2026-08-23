from datasets import load_dataset
from collections import Counter

print("Downloading dataset... ye 1-2 min le sakta hai")
ds = load_dataset("mithun932001/cropdata")

wheat_labels = ["Wheat Black Rust", "Wheat Brown Rust", "Wheat Healthy",
                 "Wheat Leaf Blight", "Wheat Mildew", "Wheat Septoria", "Wheat Yellow Rust"]

label_names = ds["train"].features["label"].names
wheat_label_ids = [i for i, name in enumerate(label_names) if name in wheat_labels]

wheat_ds = ds["train"].filter(lambda x: x["label"] in wheat_label_ids)

print("\nTotal wheat images:", len(wheat_ds))
print("\nLabel distribution:")
counts = Counter(wheat_ds["label"])
for label_id, count in counts.items():
    print(f"  {label_names[label_id]}: {count}")

wheat_ds.save_to_disk("person2_risk_detection/data/wheat_dataset")
print("\nSaved to person2_risk_detection/data/wheat_dataset")