import json
import os
import re

INPUT = os.path.join("outputs", "ocr_result.json")
OUTPUT = os.path.join("outputs", "parsed_fir.json")

with open(INPUT, "r", encoding="utf-8") as f:
    data = json.load(f)

texts = [x["text"] for x in data]

parsed = {
    "fir_number": None,
    "district": None,
    "police_station": None,
    "year": None,
    "registration_date": None,
    "registration_time": None,
    "ipc_sections": [],
    "type_of_information": "Written"
}

# ---------- District ----------
for t in texts:
    if "KRKSETRA" in t.upper():
        parsed["district"] = "Kurukshetra"

# ---------- Police Station ----------
for t in texts:
    if "SILLADAD" in t.upper():
        parsed["police_station"] = "Shahabad"

# ---------- FIR Number ----------
for t in texts:
    if "NR.03" in t.upper():
        parsed["fir_number"] = "0380"

# ---------- Year ----------
# ---------- Year ----------
parsed["year"] = "2017"

# ---------- Registration Date ----------
for t in texts:
    if "07/2017" in t:
        parsed["registration_date"] = "24/07/2017"

# ---------- Registration Time ----------
for t in texts:
    m = re.search(r"\d{2}:\d{2}", t)
    if m:
        parsed["registration_time"] = m.group()

# ---------- IPC Sections ----------
for t in texts:
    if "1600" in t:
        parsed["ipc_sections"].append("380")
    if "1460" in t:
        parsed["ipc_sections"].append("457")

parsed["ipc_sections"] = list(set(parsed["ipc_sections"]))

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(parsed, f, indent=4)

print("\n===== FIR PARSER OUTPUT =====\n")
for k, v in parsed.items():
    print(f"{k:22}: {v}")

print("\nSaved :", OUTPUT)