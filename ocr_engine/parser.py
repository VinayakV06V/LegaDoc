import json
import os


# ---------------- HELPERS ----------------

def center_y(box):
    return (box[1] + box[3]) / 2


def same_row(a, b, threshold=12):
    return abs(center_y(a["box"]) - center_y(b["box"])) <= threshold


def nearest_right(label, words):
    candidates = []

    lx2 = label["box"][2]

    for w in words:
        if w is label:
            continue

        if same_row(label, w) and w["box"][0] > lx2:
            distance = w["box"][0] - lx2
            candidates.append((distance, w))

    if not candidates:
        return None

    candidates.sort(key=lambda x: x[0])
    return candidates[0][1]["text"]


def find_label(words, labels):
    for w in words:
        t = w["text"].lower()

        for l in labels:
            if l.lower() in t:
                return w

    return None


# ---------------- PARSER ----------------

def parse_fir(words):
    parsed = {
        "fir_number": None,
        "district": None,
        "police_station": None,
        "year": None,
        "registration_date": None,
        "registration_time": None,
        "ipc_sections": [],
        "type_of_information": None,
    }

    fields = {
        "district": ["District", "जिला"],
        "police_station": ["P.S.", "Police Station", "थाना"],
        "year": ["Year", "वर्ष"],
        "fir_number": ["FIR No", "FIR NO", "एफ.आई.आर"],
        "registration_date": ["Date", "दिनांक"],
        "registration_time": ["Time", "समय"],
        "type_of_information": ["Type of Information", "सूचना का प्रकार"],
    }

    for key, labels in fields.items():
        label = find_label(words, labels)
        if label:
            value = nearest_right(label, words)
            parsed[key] = value

    return parsed


# ---------------- MAIN ----------------

if __name__ == "__main__":

    INPUT = os.path.join("outputs", "ocr_result.json")
    OUTPUT = os.path.join("outputs", "parsed_fir.json")

    with open(INPUT, "r", encoding="utf-8") as f:
        words = json.load(f)

    parsed = parse_fir(words)

    os.makedirs("outputs", exist_ok=True)

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(parsed, f, indent=4, ensure_ascii=False)

    print("Saved:", OUTPUT)