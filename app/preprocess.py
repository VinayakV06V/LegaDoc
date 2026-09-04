import cv2
import numpy as np
import os

INPUT_PATH = os.path.join("uploads", "test.jpg")
OUTPUT_PATH = os.path.join("processed", "processed.jpg")

image = cv2.imread(INPUT_PATH)

if image is None:
    raise FileNotFoundError("Image not found")

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# ---------- Shadow Removal ----------
dilated = cv2.dilate(gray, np.ones((7,7), np.uint8))
bg = cv2.medianBlur(dilated, 21)
shadow_removed = 255 - cv2.absdiff(gray, bg)

# ---------- CLAHE ----------
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
contrast = clahe.apply(shadow_removed)

# ---------- Denoise ----------
blur = cv2.GaussianBlur(contrast, (5,5), 0)

# ---------- Threshold ----------
binary = cv2.adaptiveThreshold(
    blur,255,
    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    cv2.THRESH_BINARY,
    15,10
)

# ---------- Morphology ----------
kernel = np.ones((2,2), np.uint8)
clean = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
clean = cv2.morphologyEx(clean, cv2.MORPH_CLOSE, kernel)

# ---------- Quality Score ----------
lap = cv2.Laplacian(gray, cv2.CV_64F).var()

if lap > 150:
    quality = "Excellent"
elif lap > 80:
    quality = "Good"
elif lap > 40:
    quality = "Average"
else:
    quality = "Poor"

os.makedirs("processed", exist_ok=True)
cv2.imwrite(OUTPUT_PATH, clean)

print("\n========== PREPROCESS REPORT ==========")
print("Saved :", OUTPUT_PATH)
print(f"Sharpness Score : {lap:.2f}")
print("Quality :", quality)
print("======================================")