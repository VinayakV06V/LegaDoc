import json


def merge_rows(blocks, y_tol=12, x_gap=35):
    # Sort by page position
    blocks = sorted(blocks, key=lambda b: (b["y"], b["x"]))

    rows = []

    # Group into rows
    for b in blocks:
        placed = False

        for row in rows:
            if abs(row["y"] - b["y"]) <= y_tol:
                row["words"].append(b)
                placed = True
                break

        if not placed:
            rows.append({
                "y": b["y"],
                "words": [b]
            })

    merged = []

    for row in rows:
        words = sorted(row["words"], key=lambda w: w["x"])

        sentence = words[0]["text"]
        last_x = words[0]["box"][2]

        for w in words[1:]:
            # Small horizontal gap → same sentence
            if w["x"] - last_x <= x_gap:
                sentence += " " + w["text"]
            else:
                sentence += "    " + w["text"]

            last_x = w["box"][2]

        merged.append({
            "y": row["y"],
            "text": sentence
        })

    return merged


if __name__ == "__main__":

    with open("outputs/ocr_result.json", encoding="utf-8") as f:
        blocks = json.load(f)

    lines = merge_rows(blocks)

    print("\n===== MERGED OCR LINES =====\n")

    for i, line in enumerate(lines[:15], 1):
        print(f"{i:02d}. {line['text']}")