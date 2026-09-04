import sqlite3
import os

from retention.encrypt import decrypt_text

DB_PATH = os.path.join("retention", "documents.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
SELECT
document_type,
merchant,
customer,
receipt_number,
subtotal,
tax,
total,
confidence
FROM documents
ORDER BY id DESC
LIMIT 1
""")

row = cursor.fetchone()

conn.close()

print("\n===== RETRIEVED DOCUMENT =====\n")

print("Document Type :", row[0])
print("Merchant      :", row[1])
print("Customer      :", decrypt_text(row[2]))
print("Receipt No.   :", row[3])
print("Subtotal      :", row[4])
print("Tax           :", row[5])
print("Total         :", row[6])
print("Confidence    :", row[7])