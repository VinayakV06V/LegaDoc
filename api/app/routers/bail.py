"""Bail track — see SYSTEM_DESIGN.md Flow 4. Runs entirely independently of
investigation_status; never gate one on the other."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.security import require_role

router = APIRouter(prefix="/cases/{case_id}/bail", tags=["bail"])


@router.post("/arrest")
def record_arrest(case_id: str, claims: dict = Depends(require_role("io", "duty_officer"))):
    """POST /cases/:id/bail/arrest — Investigating Officer / Duty Officer.
    Record arrest. Starts the independent bail track (bail_status = Arrested)."""
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")


@router.post("/application")
def file_bail_application(case_id: str, claims: dict = Depends(require_role("defense"))):
    """POST /cases/:id/bail/application — Defense (submission-only)."""
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")


@router.post("/hearing-notice")
def schedule_bail_hearing(case_id: str, claims: dict = Depends(require_role("court"))):
    """POST /cases/:id/bail/hearing-notice — Court."""
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")


@router.post("/order")
def issue_bail_order(case_id: str, claims: dict = Depends(require_role("court"))):
    """POST /cases/:id/bail/order — Court. Same role as hearing-notice;
    differentiated by audit-log action, not a separate "Judge" role."""
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")


@router.post("/surety")
def register_surety(case_id: str, claims: dict = Depends(require_role("defense"))):
    """POST /cases/:id/bail/surety — Accused (submission-only)."""
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")
