from paddleocr import PaddleOCR
import json
import os

# Initialize OCR model
ocr = PaddleOCR(use_angle_cls=True, lang="en")

# File paths
# Change this line

IMAGE_PATH = os.path.join("processed", "processed.jpg")
OUTPUT_PATH = os.path.join("outputs", "ocr_result.json")

# Run OCR
result = ocr.ocr(IMAGE_PATH, cls=True)

ocr_data = []

for line in result[0]:
    text = line[1][0]
    score = float(line[1][1])

    ocr_data.append({
        "text": text,
        "confidence": round(score, 2)
    })

# Create outputs folder if missing
os.makedirs("outputs", exist_ok=True)

# Save JSON
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(ocr_data, f, indent=4, ensure_ascii=False)

print("\n OCR completed successfully!")
print(f"Saved JSON : {OUTPUT_PATH}")