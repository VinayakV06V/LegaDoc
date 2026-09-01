"""Documents — see SYSTEM_DESIGN.md Flow 2 (the core technical differentiator:
upload -> OCR -> AI Parser redaction -> blockchain hash-write, two parallel tracks)."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.security import require_role, get_current_claims

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("")
def upload_document(claims: dict = Depends(get_current_claims)):
    """POST /documents — Role permitted for that case/doc-type. Upload document
    or binary evidence. TODO: store raw file in Object Storage, create a
    Document row (status=processing), enqueue the hash-write job AND (for
    text-bearing docs) the OCR job — both in parallel, per Flow 2. Return 202.
    """
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")


@router.get("")
def list_documents(
    status_filter: Optional[str] = Query(default=None, alias="status"),
    claims: dict = Depends(require_role("admin", "io")),
):
    """GET /documents?status=needs_review — Admin / Investigating Officer.
    List documents where the AI Parser fell back to fully-redacted after
    repeated failure. Plain filtered query on the documents table. An IO
    should only see this for their own assigned cases — filter by
    CaseAssignment in the implementation, require_role alone isn't enough.
    """
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")


@router.get("/{document_id}")
def get_document(document_id: str, claims: dict = Depends(get_current_claims)):
    """GET /documents/:id — Role-filtered. Returns redacted or full view per
    auto-tagged sensitivity spans + role."""
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")


@router.get("/{document_id}/versions")
def get_document_versions(document_id: str, claims: dict = Depends(get_current_claims)):
    """GET /documents/:id/versions — Role-filtered. Version history.
    Append-only — originals never overwritten."""
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")


@router.get("/{document_id}/chain-status")
def get_chain_status(document_id: str, claims: dict = Depends(get_current_claims)):
    """GET /documents/:id/chain-status — Role-filtered. Poll blockchain
    confirmation. Short-poll target for Flow 2."""
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")


@router.post("/{document_id}/retry-chain-write")
def retry_chain_write(document_id: str, claims: dict = Depends(require_role("admin"))):
    """POST /documents/:id/retry-chain-write — Admin. Manually re-trigger a
    stuck chain-write. MUST reuse the original idempotency key from the failed
    attempt, never mint a new one — if Fabric actually confirmed the
    transaction before the crash, this guarantees no duplicate ledger entry.
    """
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")


@router.post("/{document_id}/redact-tag")
def correct_redaction_tag(document_id: str, claims: dict = Depends(require_role("io"))):
    """POST /documents/:id/redact-tag — Investigating Officer (the IO
    assigned to this document's case — check CaseAssignment, role alone
    isn't enough). Correct/override an AI Parser sensitivity tag. This is a
    correction path over the AI Parser's auto-tags, not the primary tagging
    mechanism."""
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")
