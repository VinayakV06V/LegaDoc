"""
OCR & Extraction Worker — see SYSTEM_DESIGN.md Container Diagram and Flow 2,
Track B. Consumes jobs from the queue; on completion, enqueues the AI-parse
job itself (OCR does not call the AI Parser directly — see System Connections
table, arrow #11).

DB/storage access pattern matches workers/chain_worker/worker.py — reuse
api/app's models/database/storage/config directly rather than duplicating
the schema. Uncomment the imports below once you start filling this in.
"""
import os
import sys

# Reuse api/app instead of duplicating the schema — see this file's
# docstring and workers/chain_worker/worker.py for the same pattern.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "api"))

from celery import Celery

from app.config import settings
from app.preprocess import preprocess_image
from app.ocr import run_ocr
from app.parser import parse_fir
from app.semantic import semantic_parse

# Uncomment as you need them:
# from uuid import UUID
# from app import models
# from app.database import SessionLocal
# from app.storage import get_storage  # NOTE: get_storage() is a FastAPI
#     Depends()-style function that lazily builds a module-level singleton —
#     it works fine called directly here too, just isn't dependency-injected.

app = Celery(
    "ocr_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)


@app.task(name="ocr_worker.extract_document", bind=True, max_retries=5)
def extract_document(self, image_path: str):
    """
    OCR Worker for FIR document extraction
    """

    # Step 1: Preprocess
    processed_path = preprocess_image(image_path)

    # Step 2: OCR
    ocr_result = run_ocr(processed_path)

    # Step 3: Parse FIR
    parsed_data = parse_fir(ocr_result)

    # Step 4: Semantic output
    result = semantic_parse(parsed_data)

    return result
