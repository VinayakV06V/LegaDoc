"""
Applies already-computed DocumentSensitivityTag spans to raw text. This is
deliberately NOT the AI Parser — it doesn't detect anything, it just masks
whatever spans already exist in the DB. Real tag generation needs Presidio +
spaCy (ai_parser_worker), which isn't wired up in this environment. This
function is what the redaction filter actually runs at read time regardless
of whether a tag came from the AI Parser or an officer's manual correction —
same masking logic either way, see SYSTEM_DESIGN.md's Access Model.
"""

from app import models


def apply_redaction(raw_text: str, tags: list) -> str:
    """tags: DocumentSensitivityTag rows for this document. Overlapping tags
    are resolved by first-span-wins (sorted by span_start) — a real
    implementation would want tag validation to prevent overlaps from ever
    being written in the first place; not enforced at this baseline."""
    if not raw_text:
        return raw_text
    sorted_tags = sorted(tags, key=lambda t: t.span_start)
    out = []
    cursor = 0
    for tag in sorted_tags:
        if tag.span_start < cursor:
            continue  # overlaps an already-masked span — skip rather than corrupt output
        if tag.span_start > len(raw_text) or tag.span_end > len(raw_text):
            continue  # a stale tag from a shorter previous version of the text — don't crash
        out.append(raw_text[cursor:tag.span_start])
        out.append(f"[REDACTED:{tag.entity_type}]")
        cursor = tag.span_end
    out.append(raw_text[cursor:])
    return "".join(out)


def get_document_view(document: "models.Document", tags: list, role: str, full_access_roles: set) -> dict:
    """The single function every read path for a document's content should
    call — never build a "redacted vs full" branch ad hoc per endpoint."""
    if document.status != "ready":
        return {"status": document.status, "text": None}
    if role in full_access_roles:
        return {"status": document.status, "text": document.raw_text}
    return {"status": document.status, "text": apply_redaction(document.raw_text, tags)}
