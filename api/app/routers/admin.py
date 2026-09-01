"""Admin & config — schema registry, AI Parser recognizer mapping, stage
requirements. See SYSTEM_DESIGN.md Domain 8 (Platform / Admin) — this role
concentrates nearly every dangerous capability in the system; don't loosen
require_role("admin") on any of these without re-reading that section."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.security import require_role

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/document-schemas")
def list_document_schemas(claims: dict = Depends(require_role("admin"))):
    """GET /admin/document-schemas — System Admin. Manage the tiered
    field-sensitivity schema registry."""
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")


@router.post("/document-schemas/{doc_type}/recognizers")
def set_recognizer_mapping(doc_type: str, claims: dict = Depends(require_role("admin"))):
    """POST /admin/document-schemas/:type/recognizers — System Admin. Map
    entity types (name, phone, medical condition, ID number, ...) to a
    DocumentSchema's sensitivity fields. One-time-per-type config that drives
    the AI Parser."""
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")


@router.get("/stage-requirements")
def list_stage_requirements(claims: dict = Depends(require_role("admin"))):
    """GET /admin/stage-requirements — System Admin. Manage mandatory-document/
    evidence config per crime type. Drives Flow 3's validation check."""
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")
