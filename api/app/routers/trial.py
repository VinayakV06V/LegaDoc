"""Trial / judgment — court disposition, see SYSTEM_DESIGN.md Flow 5.
Closes the investigation-track state diagram's final transition."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.security import require_role

router = APIRouter(prefix="/cases/{case_id}", tags=["trial"])


@router.post("/trial/hearing-notice")
def schedule_trial_hearing(case_id: str, claims: dict = Depends(require_role("court"))):
    """POST /cases/:id/trial/hearing-notice — Court. Moves investigation_status
    to Trial. Mirrors the bail hearing-notice pattern."""
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")


@router.post("/judgment")
def record_judgment(case_id: str, claims: dict = Depends(require_role("court"))):
    """POST /cases/:id/judgment — Court. Moves investigation_status to
    Judgment — the terminal state for the investigation track."""
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")
