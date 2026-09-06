import cv2
import os

def preprocess(input_path, output_path):
    img = cv2.imread(input_path)

    img = cv2.resize(img, None, fx=2, fy=2,
                     interpolation=cv2.INTER_CUBIC)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    gray = cv2.fastNlMeansDenoising(gray)

    th = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        15
    )

    os.makedirs("processed", exist_ok=True)
    cv2.imwrite(output_path, th)
    print("Saved:", output_path)

if __name__ == "__main__":
    preprocess("uploads/test.jpg", "processed/test.jpg")