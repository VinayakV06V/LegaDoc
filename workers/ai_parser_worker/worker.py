"""
AI Parser Worker — self-hosted Presidio + spaCy NER, NOT a generative model.
See SYSTEM_DESIGN.md Flow 2 Track B, Flow 6 (audit trail), and the "Security"
section's fail-closed rule.

Handles both Document text (post-OCR) and Case Diary entries (see "Case Diary
now routes through the redaction pipeline") — same task, same rule either way.

DB access pattern matches workers/chain_worker/worker.py — reuse api/app's
models/database/audit/config directly rather than duplicating the schema.
Uncomment the imports below once you start filling this in; app.audit's
write_audit_log() already handles the row_hash chain (including the
pg_advisory_xact_lock) correctly — call that, don't reimplement it here.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "api"))

from celery import Celery

from app.config import settings

from uuid import UUID

from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider

from app import models
from app.database import SessionLocal
from app.audit import write_audit_log

app = Celery(
    "ai_parser_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)


CONFIDENCE_REVIEW_THRESHOLD = 70  # 0-100; below this, auto-flag even on "success"
# spaCy + Presidio NLP engine
provider = NlpEngineProvider(
    nlp_configuration={
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
    }
)

nlp_engine = provider.create_engine()
analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["en"])

@app.task(name="ai_parser_worker.tag_document", bind=True, max_retries=5)
def tag_document(self, document_id: str):

    db = SessionLocal()

    try:
        # 1. Fetch document
        document = db.get(models.Document, UUID(document_id))

        if document is None:
            raise Exception("Document not found")

        if not document.raw_text:
            raise Exception("OCR text not available")

        # 2. Run Presidio + spaCy
        results = analyzer.analyze(
            text=document.raw_text,
            language="en",
        )

        tags = []

        # 3. Save sensitivity tags
        for entity in results:
            tag = models.DocumentSensitivityTag(
                document_id=document.id,
                entity_type=entity.entity_type,
                span_start=entity.start,
                span_end=entity.end,
                confidence=int(round(entity.score * 100)),
                source="presidio",
            )

            db.add(tag)
            tags.append(tag)

        # 4. Decide document status (Fail-Closed)
        low_confidence = any(
            tag.confidence < CONFIDENCE_REVIEW_THRESHOLD
            for tag in tags
        )

        if low_confidence:
            document.status = "needs_review"
        else:
            document.status = "ready"

        # 5. Audit log
        # 5. Audit log
        write_audit_log(
            db=db,
            action="auto_tag_completed",
            target_type="document",
            target_id=document.id,
            metadata={
                "tags_created": len(tags),
                "source": "ai_parser",
            },
        )

        db.commit()

        return {
            "status": document.status,
            "document_id": document_id,
            "tags_created": len(tags),
        }

    finally:
        db.close()


@app.task(name="ai_parser_worker.tag_case_diary_entry", bind=True, max_retries=5)
def tag_case_diary_entry(self, case_diary_entry_id: str):
    """Same pipeline as tag_document, minus the OCR step — the diary text is
    already plain text. Same fail-closed rule: on failure, the entry stays
    visible only to the assigned IO/SHO, not marked "ready" for wider roles.
    """
    raise NotImplementedError("Fill in against SYSTEM_DESIGN.md, Case Diary redaction fix")
