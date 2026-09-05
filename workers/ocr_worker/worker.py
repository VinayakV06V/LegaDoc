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

sys.path.insert(
    0,
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "api")
)

from celery import Celery, current_app
from uuid import UUID

from app.config import settings
from app import models
from app.database import SessionLocal
from app.storage import get_storage

from ocr_engine.preprocess import preprocess_image
from ocr_engine.ocr import run_ocr
from ocr_engine.parser import parse_fir
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
def extract_document(self, document_id: str):

    db = SessionLocal()

    try:
        # 1. Get document from database
        document = db.get(models.Document, UUID(document_id))

        if document is None:
            raise Exception("Document not found")

        # 2. Load uploaded image
        storage = get_storage()
        image_path = storage.get(document.storage_path)

        # 3. Preprocess image
        processed_path = preprocess_image(image_path)

        # 4. Run PaddleOCR
        ocr_result = run_ocr(processed_path)

        # 5. Convert OCR result into plain text
        raw_text = "\n".join(item["text"] for item in ocr_result)

        # 6. Save raw OCR text
        document.raw_text = raw_text
        db.commit()

        # 7. Generic FIR extraction
        parsed_data = parse_fir(raw_text)

        # 8. Send document to AI Parser worker
        current_app.send_task(
            "ai_parser_worker.tag_document",
            args=[document_id],
        )

        # 9. Return OCR + parsed result
        return {
            "status": "success",
            "document_id": document_id,
            "raw_text": raw_text,
            "parsed_data": parsed_data,
        }

    finally:
        db.close()