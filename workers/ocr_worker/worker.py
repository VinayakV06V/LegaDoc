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
    """
    TODO:
      1. db = SessionLocal(); document = db.get(models.Document, UUID(document_id))
      2. Fetch the raw file: get_storage().get(document.storage_path) (arrow #10).
      3. Run PaddleOCR + regex field extraction. On a PaddleOCR failure
         (not just low confidence — an actual exception), fall back to
         Tesseract rather than failing the whole job outright; record which
         engine actually produced the result in document.ocr_engine.
      4. Write the extracted text to document.raw_text, db.commit() (arrow #9)
         — the AI Parser has nothing to tag without raw_text.
      5. Enqueue ai_parser_worker.tag_document(document_id) via a QueueClient
         (arrow #11) — see api/app/queue.py's CeleryQueueClient for the
         pattern (send_task by name, don't import the AI Parser's task object).
    On repeated failure (both engines): dead-letter + flag via
    GET /documents?status=needs_review (that endpoint itself still needs
    implementing too — see api/app/routers/documents.py).
    Idempotency: use document_id + document.version as the key — redelivery
    must not double-extract.
    """
    raise NotImplementedError("Fill in against SYSTEM_DESIGN.md Flow 2, Track B")
