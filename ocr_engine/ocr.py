from paddleocr import PaddleOCR
import json
import os

# English OCR
ocr_en = PaddleOCR(use_angle_cls=True, lang="en")

# Hindi OCR
ocr_hi = PaddleOCR(use_angle_cls=True, lang="hi")


def extract(engine, image_path):
    result = engine.ocr(image_path, cls=True)
    words = []

    if result and result[0]:
        for line in result[0]:
            box = line[0]
            text = line[1][0]
            score = float(line[1][1])

            x1 = int(min(p[0] for p in box))
            y1 = int(min(p[1] for p in box))
            x2 = int(max(p[0] for p in box))
            y2 = int(max(p[1] for p in box))

            words.append({
                "text": text,
                "confidence": score,
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
            round(w["x"] / 6),
            round(w["y"] / 6),
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