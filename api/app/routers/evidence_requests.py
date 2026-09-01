"""Evidence requests — see SYSTEM_DESIGN.md Flow 3 (parallel, AND-join)."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.security import require_role, get_current_claims

router = APIRouter(tags=["evidence-requests"])


@router.post("/cases/{case_id}/evidence-requests")
def create_evidence_request(case_id: str, claims: dict = Depends(require_role("io"))):
    """POST /cases/:id/evidence-requests — IO. Create request to external org.
    One row per request — supports parallel N requests."""
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")


@router.get("/cases/{case_id}/evidence-requests")
def list_evidence_requests(case_id: str, claims: dict = Depends(get_current_claims)):
    """GET /cases/:id/evidence-requests — IO / relevant Authority. List requests + status."""
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")


@router.post("/evidence-requests/{request_id}/submit")
def submit_evidence_request(request_id: str, claims: dict = Depends(get_current_claims)):
    """POST /evidence-requests/:id/submit — The specific requested Authority.
    Fulfill request, attach document. Triggers the document upload pipeline
    (see Flow 2) — this endpoint itself should call into the same upload path
    as POST /documents, not duplicate it.
    """
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")
