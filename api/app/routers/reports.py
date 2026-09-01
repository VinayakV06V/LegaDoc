"""Records/NCRB reporting — see SYSTEM_DESIGN.md Domain 7.

This endpoint MUST read from a dedicated de-identified DB view (e.g.
`case_metadata_deidentified`), never a filtered pass through the normal
/cases or /documents endpoints. That separation is the whole point — it makes
"someone forgot to apply the redaction filter here" structurally impossible
for this role, rather than just tested against.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.security import require_role

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/case-metadata")
def get_case_metadata(claims: dict = Depends(require_role("records_ncrb_analyst"))):
    """GET /reports/case-metadata — Records / NCRB Analyst. De-identified case
    metadata only (crime_type, status, dates, court_level — no identity or
    sensitive fields, even in redacted form)."""
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")
