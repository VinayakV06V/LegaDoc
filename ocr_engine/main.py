import subprocess
import sys

steps = [
    ("Image Preprocessing", "ocr_engine/preprocess.py"),
    ("OCR Extraction", "ocr_engine/ocr.py"),
    ("FIR Parsing", "ocr_engine/parser.py"),
    ("Semantic Structuring", "ocr_engine/semantic.py"),
]

print("\n========== FIR OCR PIPELINE ==========\n")

for title, script in steps:
    print(f"\nRunning: {title}")

    result = subprocess.run([sys.executable, script])

    if result.returncode != 0:
        print(f"\n{title} failed!")
        exit(1)

print("\nPipeline completed successfully!")