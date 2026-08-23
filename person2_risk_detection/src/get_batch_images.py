from datasets import load_from_disk

wheat_ds = load_from_disk("person2_risk_detection/data/wheat_dataset")

# 4 alag alag samples nikalo (dataset ke different parts se, taaki variety mile)
indices = [0, 300, 700, 1200]

for i, idx in enumerate(indices):
    sample = wheat_ds[idx]
    sample["image"].save(f"person2_risk_detection/data/test_batch/sample_{i+1}.jpg")
    print(f"Saved sample_{i+1}.jpg, original label: {sample['label']}")

print("Done!")