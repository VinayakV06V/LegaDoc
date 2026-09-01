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


@app.task(name="ai_parser_worker.tag_document", bind=True, max_retries=5)
def tag_document(self, document_id: str):
    """
    TODO:
      1. Read extracted text for this document_id.
      2. Run Presidio/spaCy against the recognizer config for this DocumentSchema
         (Tier 1/2 types use their specific mapping; Tier 3 uses the generic
         default profile).
      3. Write DocumentSensitivityTag rows — entity_type, span, confidence.
         NEVER write the raw matched text itself into the tag or into AuditLog.
      4. Write an AuditLog row for this auto-tag event (source="ai_parser"),
         computing row_hash = hash(prev_row_hash + content).
      5. Mark the document status="ready".

    FAIL-CLOSED RULE (do not weaken this): on repeated failure, do NOT mark
    the document ready. Instead set status="needs_review" — the redaction
    filter's default for "no confirmed tags yet" must be full redaction, not
    full exposure.
    """
    raise NotImplementedError("Fill in against SYSTEM_DESIGN.md Flow 2 Track B / Flow 6")


@app.task(name="ai_parser_worker.tag_case_diary_entry", bind=True, max_retries=5)
def tag_case_diary_entry(self, case_diary_entry_id: str):
    """Same pipeline as tag_document, minus the OCR step — the diary text is
    already plain text. Same fail-closed rule: on failure, the entry stays
    visible only to the assigned IO/SHO, not marked "ready" for wider roles.
    """
    raise NotImplementedError("Fill in against SYSTEM_DESIGN.md, Case Diary redaction fix")
