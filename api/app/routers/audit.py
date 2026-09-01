"""Audit trail — see SYSTEM_DESIGN.md, "Security: ... Audit Integrity" and Flow 6.

Every read of /audit-log/ai-parser must itself write a row to AuditLog
(action="read_ai_parser_audit") — that's the meta-audit, and it's not a
separate table or endpoint, just another write to the same audit_log.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.security import require_role, get_current_claims

router = APIRouter(prefix="/cases/{case_id}/audit-log", tags=["audit"])


@router.get("")
def get_audit_log(case_id: str, claims: dict = Depends(get_current_claims)):
    """GET /cases/:id/audit-log — Role-filtered. Full for Admin/Court,
    summarized (aggregate lines only, e.g. "3 fields auto-tagged, 1 corrected")
    for every other role."""
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")


@router.get("/ai-parser")
def get_ai_parser_audit(case_id: str, claims: dict = Depends(require_role("admin"))):
    """GET /cases/:id/audit-log/ai-parser — System Admin only. Full entity-level
    detail of every AI Parser auto-tag decision and every human correction on
    this case's documents. No bulk/cross-case export — one case at a time.
    TODO: write the meta-audit row (this read is itself an audited event)
    before returning the response.
    """
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")
