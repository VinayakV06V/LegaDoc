import sqlite3
import json
import os

from retention.hash import generate_document_hash
from retention.audit import write_log

DB_PATH = os.path.join("retention", "documents.db")
INPUT_PATH = os.path.join("outputs", "semantic_data.json")

# -----------------------------
# Create Database
# -----------------------------
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS fir_documents(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    document_hash TEXT UNIQUE,

    fir_number TEXT,
    district TEXT,
    police_station TEXT,

    registration_date TEXT,
    registration_time TEXT,

    year TEXT,

    ipc_sections TEXT,

    type_of_information TEXT,

    confidence REAL
)
""")

# -----------------------------
# Load FIR JSON
# -----------------------------
with open(INPUT_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

doc_hash = generate_document_hash()

# -----------------------------
# Duplicate Check
# -----------------------------
cursor.execute(
    "SELECT id FROM fir_documents WHERE document_hash=?",
    (doc_hash,)
)

if cursor.fetchone():
    write_log("STORE_FIR", "DUPLICATE", data["fir_number"])
    print("Duplicate FIR detected!")
    conn.close()
    exit()

# -----------------------------
# Insert
# -----------------------------
cursor.execute("""
INSERT INTO fir_documents(
document_hash,
fir_number,
district,
police_station,
registration_date,
registration_time,
year,
ipc_sections,
type_of_information,
confidence)

VALUES(?,?,?,?,?,?,?,?,?,?)
""", (

doc_hash,
data["fir_number"],
data["district"],
data["police_station"],
data["registration_date"],
data["registration_time"],
data["year"],
json.dumps(data["ipc_sections"]),
data["type_of_information"],
data["confidence"]

))

conn.commit()

write_log("STORE_FIR", "SUCCESS", data["fir_number"])

print("FIR stored successfully!")

conn.close()