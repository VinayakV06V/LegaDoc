"""
OCR & Extraction Worker — see SYSTEM_DESIGN.md Container Diagram and Flow 2,
Track B. Consumes jobs from the queue; on completion, enqueues the AI-parse
job itself (OCR does not call the AI Parser directly — see System Connections
table, arrow #11).
"""

from celery import Celery

app = Celery(
    "ocr_worker",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/1",
)


@app.task(name="ocr_worker.extract_document", bind=True, max_retries=5)
def extract_document(self, document_id: str):
    """
    TODO:
      1. Fetch the raw file from Object Storage (arrow #10).
      2. Run PaddleOCR + regex field extraction. On a PaddleOCR failure
         (not just low confidence — an actual exception), fall back to
         Tesseract rather than failing the whole job outright; record which
         engine actually produced the result in Document.ocr_engine.
      3. Write the extracted text to Document.raw_text AND structured fields
         to the documents table (arrow #9) — the AI Parser has nothing to
         tag without raw_text.
      4. Enqueue ai_parser_worker.tag_document(document_id) (arrow #11).
    On repeated failure (both engines): dead-letter + flag via
    GET /documents?status=needs_review.
    Idempotency key = document_id + version — redelivery must not double-extract.
    """
    raise NotImplementedError("Fill in against SYSTEM_DESIGN.md Flow 2, Track B")
