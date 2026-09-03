"""Admin & config — schema registry, AI Parser recognizer mapping, stage
requirements, org onboarding. See SYSTEM_DESIGN.md Domain 8 (Platform / Admin).

Config Admin vs. Security Auditor (see models.py, User.role): a single
super-admin holding both schema-editing power and audit-inspection power is
one compromised account away from total control. Config Admin owns
everything in this file. Security Auditor owns audit.py's ai-parser endpoint
instead — never both from the same role.

Schema and recognizer-mapping changes (and Chain Worker manual recovery in
documents.py) are exactly the actions SYSTEM_DESIGN.md flags as needing
second-person confirmation before they take effect in a real deployment —
not enforced in this baseline, but don't build single-click execution here
and call it done.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.security import require_role

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/document-schemas")
def list_document_schemas(claims: dict = Depends(require_role("config_admin"))):
    """GET /admin/document-schemas — Config Admin. Manage the tiered
    field-sensitivity schema registry."""
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")


@router.post("/document-schemas/{doc_type}/recognizers")
def set_recognizer_mapping(doc_type: str, claims: dict = Depends(require_role("config_admin"))):
    """POST /admin/document-schemas/:type/recognizers — Config Admin. Map
    entity types (name, phone, medical condition, ID number, ...) to a
    DocumentSchema's sensitivity fields. One-time-per-type config that drives
    the AI Parser. TODO: write an audit_log entry with the old vs new
    recognizer mapping diff — a silently-weakened recognizer is how someone
    quietly un-redacts a field, and that must be traceable.
    """
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")


@router.get("/stage-requirements")
def list_stage_requirements(claims: dict = Depends(require_role("config_admin"))):
    """GET /admin/stage-requirements — Config Admin. Manage mandatory-document/
    evidence config per crime type. Drives Flow 3's validation check."""
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")
