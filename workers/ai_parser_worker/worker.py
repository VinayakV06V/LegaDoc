"""
AI Parser Worker — self-hosted Presidio + spaCy NER, NOT a generative model.
See SYSTEM_DESIGN.md Flow 2 Track B, Flow 6 (audit trail), and the "Security"
section's fail-closed rule.

Handles both Document text (post-OCR) and Case Diary entries (see "Case Diary
now routes through the redaction pipeline") — same task, same rule either way.
"""

from celery import Celery

app = Celery(
    "ai_parser_worker",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/1",
)


CONFIDENCE_REVIEW_THRESHOLD = 70  # 0-100; below this, auto-flag even on "success"


@app.task(name="ai_parser_worker.tag_document", bind=True, max_retries=5)
def tag_document(self, document_id: str):
    """
    TODO:
      1. Read Document.raw_text for this document_id (set by the OCR worker
         — nothing to tag without it).
      2. Run Presidio/spaCy against the recognizer config for this DocumentSchema
         (Tier 1/2 types use their specific mapping; Tier 3 uses the generic
         default profile).
      3. Write DocumentSensitivityTag rows — entity_type, span, confidence
         as int(round(presidio_score * 100)), 0-100. NEVER write the raw
         matched text itself into the tag or into AuditLog.
      4. Write an AuditLog row for this auto-tag event (source="ai_parser"),
         computing row_hash = hash(prev_row_hash + content) under
         pg_advisory_xact_lock (see models.AuditLog's concurrency warning).
      5. If every tag on this document is >= CONFIDENCE_REVIEW_THRESHOLD,
         mark status="ready". If ANY tag is below it, mark
         status="needs_review" instead — a low-confidence tag that
         "succeeded" is not the same as a trustworthy one, and treating it
         as such is exactly the kind of quiet erosion of fail-closed
         behavior worth guarding against.

    FAIL-CLOSED RULE (do not weaken this): on repeated failure, do NOT mark
    the document ready. Set status="needs_review" — the redaction filter's
    default for "no confirmed tags yet" must be full redaction, not full
    exposure. Add a permanent automated test asserting this — it's the
    single most important safety property in the system, and the easiest one
    to accidentally break under deadline pressure without a test catching it.
    """
    raise NotImplementedError("Fill in against SYSTEM_DESIGN.md Flow 2 Track B / Flow 6")


@app.task(name="ai_parser_worker.tag_case_diary_entry", bind=True, max_retries=5)
def tag_case_diary_entry(self, case_diary_entry_id: str):
    """Same pipeline as tag_document, minus the OCR step — the diary text is
    already plain text. Same fail-closed rule: on failure, the entry stays
    visible only to the assigned IO/SHO, not marked "ready" for wider roles.
    """
    raise NotImplementedError("Fill in against SYSTEM_DESIGN.md, Case Diary redaction fix")
