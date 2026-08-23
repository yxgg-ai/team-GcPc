from datasets import load_from_disk

wheat_ds = load_from_disk("person2_risk_detection/data/wheat_dataset")
sample = wheat_ds[0]
sample["image"].save("person2_risk_detection/data/test_image.jpg")
print("Saved test image, label:", sample["label"])