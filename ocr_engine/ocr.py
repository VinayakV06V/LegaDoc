from paddleocr import PaddleOCR
import json
import os

# English PP-OCRv5
ocr_en = PaddleOCR(
    text_detection_model_name="PP-OCRv5_server_det",
    text_recognition_model_name="PP-OCRv5_server_rec"
)

# Hindi PP-OCRv5
ocr_hi = PaddleOCR(
    text_detection_model_name="PP-OCRv5_server_det",
    text_recognition_model_name="PP-OCRv5_server_rec"
)


def extract(engine, image_path):
    results = engine.predict(image_path)
    words = []

    for page in results:
        texts = page["rec_texts"]
        scores = page["rec_scores"]
        boxes = page["rec_boxes"]

        for txt, score, box in zip(texts, scores, boxes):
            x1 = int(min(p[0] for p in box))
            y1 = int(min(p[1] for p in box))
            x2 = int(max(p[0] for p in box))
            y2 = int(max(p[1] for p in box))

            words.append({
                "text": txt,
                "confidence": float(score),
                "box": [x1, y1, x2, y2],
                "x": x1,
                "y": y1
            })

    return words



def remove_duplicates(words):
    final = []
    seen = set()

    for w in words:
        key = (
            round(w["x"] / 8),
            round(w["y"] / 8),
            w["text"].lower()
        )

        if key not in seen:
            seen.add(key)
            final.append(w)

    return final


def run_ocr(image_path):
    en = extract(ocr_en, image_path)
    hi = extract(ocr_hi, image_path)

    merged = remove_duplicates(en + hi)
    merged.sort(key=lambda k: (k["y"], k["x"]))

    return merged


if __name__ == "__main__":
    INPUT = os.path.join("processed", "test.jpg")
    OUTPUT = os.path.join("outputs", "ocr_result.json")

    data = run_ocr(INPUT)

    os.makedirs("outputs", exist_ok=True)

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print("Saved:", OUTPUT)
    