"""Case lifecycle + charge sheet + Case Diary — see SYSTEM_DESIGN.md Interface
Contracts, "Endpoint Table", and Flow 1 / Flow 3.

GET /cases/:id uses verify_case_access — this is the fix for the CRITICAL
finding "any IO officer could browse any sensitive case across the state."
Role alone is never enough for a case-scoped read; CaseAssignment is checked
for every IO, every time.
"""

import random
import string
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.security import require_role, get_current_claims, verify_case_access

router = APIRouter(prefix="/cases", tags=["cases"])


def _generate_case_number(crime_type: str) -> str:
    """Not cryptographically meaningful — just a human-readable, collision-
    resistant-enough identifier for a demo. A real deployment would follow
    each state's actual FIR numbering convention instead."""
    year = datetime.now(timezone.utc).year
    prefix = "".join(ch for ch in crime_type.upper() if ch.isalpha())[:3] or "CAS"
    suffix = "".join(random.choices(string.digits, k=6))
    return f"{prefix}-{year}-{suffix}"


@router.post("", response_model=schemas.CaseResponse, status_code=status.HTTP_201_CREATED)
def register_fir(
    body: schemas.RegisterFIRRequest,
    claims: dict = Depends(require_role("duty_officer")),
    db: Session = Depends(get_db),
):
    """POST /cases — Duty Officer. Register FIR, create case. See Flow 1.

    Scope note: this baseline creates the Case row and assigns a
    case_number. It does NOT yet create the linked complaint Document row
    or enqueue the blockchain hash-write job (arrow #5 in System
    Connections) — those need Object Storage and a live queue, neither of
    which this environment has running. Wire them in once MinIO/Redis are
    actually available; the Case row itself is real and durable now.
    """
    case = models.Case(
        case_number=_generate_case_number(body.crime_type),
        crime_type=body.crime_type,
        investigation_status="FIR_Registered",
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    return case


@router.get("", response_model=list[schemas.CaseResponse])
def list_cases(claims: dict = Depends(get_current_claims), db: Session = Depends(get_db)):
    """GET /cases — Any authenticated role. List cases, filtered by role/org
    visibility. Paginated, filterable by crime_type/status.

    Baseline scoping: Config Admin/Security Auditor/Court/Prosecutor/Duty
    Officer/SHO see every case (matches the Access Model — these roles need
    cross-case visibility to do their job). An IO sees only cases they're
    assigned to, same rule as verify_case_access. Pagination and
    crime_type/status filtering are not implemented yet — this returns
    everything the role is allowed to see, unpaginated.
    """
    role = claims.get("role")
    if role == "io":
        user_id = UUID(claims["sub"])
        return (
            db.query(models.Case)
            .join(models.CaseAssignment, models.CaseAssignment.case_id == models.Case.id)
            .filter(models.CaseAssignment.io_user_id == user_id)
            .all()
        )
    return db.query(models.Case).all()


@router.get("/{case_id}", response_model=schemas.CaseResponse)
def get_case(case_id: str, claims: dict = Depends(verify_case_access), db: Session = Depends(get_db)):
    """GET /cases/:id — Role-filtered. Fetch case summary + linked resources.

    Only returns the case summary at this baseline — linked resources
    (documents, evidence requests, bail record) are each their own endpoint
    and aren't joined in here yet.
    """
    case = db.get(models.Case, UUID(case_id))
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return case


@router.post("/{case_id}/assign-io", status_code=status.HTTP_201_CREATED)
def assign_io(
    case_id: str,
    body: schemas.AssignIORequest,
    claims: dict = Depends(require_role("sho")),
    db: Session = Depends(get_db),
):
    """POST /cases/:id/assign-io — SHO. Assign investigating officer.
    Creates a CaseAssignment row — this is what verify_case_access checks,
    so an IO has no case access at all until this has run for them."""
    case_uuid = UUID(case_id)
    if db.get(models.Case, case_uuid) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    if db.get(models.User, body.io_user_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="IO user not found")

    assignment = models.CaseAssignment(case_id=case_uuid, io_user_id=body.io_user_id)
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return {"case_id": case_id, "io_user_id": str(body.io_user_id), "assigned_at": assignment.assigned_at}


@router.post("/{case_id}/reassign-io")
def reassign_io(case_id: str, claims: dict = Depends(require_role("sho", "config_admin"))):
    """POST /cases/:id/reassign-io — SHO / Config Admin. Reassign IO
    mid-case. Logged as its own audit event; EvidenceRequest ownership
    follows the Case, not the individual IO, so in-flight requests transfer
    transparently.

    Not implemented in this baseline — assign-io (above) is the fully
    working reference implementation to build this from; the only real
    difference is closing out the previous CaseAssignment row and writing
    an audit_log entry recording the change.
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
