"""Audit trail — see SYSTEM_DESIGN.md, "Security: ... Audit Integrity" and Flow 6.

GET /ai-parser is Security Auditor, deliberately NOT Config Admin — see
Domain 8's role split. The account that edits redaction rules should not
also be the account that inspects whether redaction is working correctly;
that's the same person checking their own work.

Every read of /audit-log/ai-parser must itself write a row to AuditLog
(action="read_ai_parser_audit") — that's the meta-audit, and it's not a
separate table or endpoint, just another write to the same audit_log. This
endpoint also needs its own tighter rate limit — it's the single most
sensitive read path in the system, worth protecting from being spammed
even by a legitimate but compromised account.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.security import require_role, get_current_claims

router = APIRouter(prefix="/cases/{case_id}/audit-log", tags=["audit"])


@router.get("")
def get_audit_log(case_id: str, claims: dict = Depends(get_current_claims)):
    """GET /cases/:id/audit-log — Role-filtered. Full for Config Admin/
    Security Auditor/Court, summarized (aggregate lines only, e.g. "3 fields
    auto-tagged, 1 corrected") for every other role."""
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")


@router.get("/ai-parser")
def get_ai_parser_audit(case_id: str, claims: dict = Depends(require_role("security_auditor"))):
    """GET /cases/:id/audit-log/ai-parser — Security Auditor only (not
    Config Admin — see module docstring). Full entity-level detail of every
    AI Parser auto-tag decision and every human correction on this case's
    documents. No bulk/cross-case export — one case at a time. Apply a
    tighter per-endpoint rate limit here than the general API default.
    TODO: write the meta-audit row (this read is itself an audited event)
    before returning the response.
    """
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")
