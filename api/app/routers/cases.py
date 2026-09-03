"""Case lifecycle + charge sheet + Case Diary — see SYSTEM_DESIGN.md Interface
Contracts, "Endpoint Table", and Flow 1 / Flow 3."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.security import require_role, get_current_claims

router = APIRouter(prefix="/cases", tags=["cases"])


@router.post("")
def register_fir(claims: dict = Depends(require_role("duty_officer"))):
    """POST /cases — Duty Officer. Register FIR, create case.
    Action-shaped, not raw POST — validates crime-type config. See Flow 1.
    """
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")


@router.get("")
def list_cases(claims: dict = Depends(get_current_claims)):
    """GET /cases — Any authenticated role. List cases, filtered by role/org
    visibility. Paginated, filterable by crime_type/status."""
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")


@router.get("/{case_id}")
def get_case(case_id: str, claims: dict = Depends(get_current_claims)):
    """GET /cases/:id — Role-filtered. Fetch case summary + linked resources."""
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")


@router.post("/{case_id}/assign-io")
def assign_io(case_id: str, claims: dict = Depends(require_role("sho"))):
    """POST /cases/:id/assign-io — SHO. Assign investigating officer.
    Creates a CaseAssignment row."""
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")


@router.post("/{case_id}/reassign-io")
def reassign_io(case_id: str, claims: dict = Depends(require_role("sho", "config_admin"))):
    """POST /cases/:id/reassign-io — SHO / Admin. Reassign IO mid-case.
    Logged as its own audit event. EvidenceRequest ownership follows the
    Case, not the individual IO, so in-flight requests transfer transparently.
    """
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")


@router.post("/{case_id}/case-diary")
def add_case_diary_entry(case_id: str, claims: dict = Depends(require_role("io"))):
    """POST /cases/:id/case-diary — IO. Append a running case-diary entry.
    Append-only, not a Document upload. TODO: enqueue the entry's text as a
    lightweight AI-parse job (no OCR step needed) before marking it "ready" —
    see SYSTEM_DESIGN.md, "Case Diary now routes through the redaction pipeline".
    """
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")


@router.get("/{case_id}/case-diary")
def list_case_diary_entries(case_id: str, claims: dict = Depends(get_current_claims)):
    """GET /cases/:id/case-diary — Role-filtered. List case-diary entries.
    Same visibility rule as the rest of the case file."""
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")


@router.post("/{case_id}/file-charge-sheet")
def file_charge_sheet(case_id: str, claims: dict = Depends(require_role("prosecutor"))):
    """POST /cases/:id/file-charge-sheet — Prosecutor. Attempt charge sheet
    filing. Validated against Stage Requirements — 409 if incomplete. See Flow 3.
    """
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")
