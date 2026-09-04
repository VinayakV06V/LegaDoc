import hashlib
import json
import os

INPUT_PATH = os.path.join("outputs", "semantic_data.json")

def generate_document_hash():

    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    text = json.dumps(data, sort_keys=True)

    return hashlib.sha256(text.encode()).hexdigest()