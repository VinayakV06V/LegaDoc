"""Org management — see SYSTEM_DESIGN.md Interface Contracts, "Endpoint Table"."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.security import require_role

router = APIRouter(tags=["orgs"])


@router.get("/orgs/{org_id}/users")
def list_org_users(org_id: str, claims: dict = Depends(require_role("admin"))):
    """GET /orgs/:orgId/users — Org Admin. List an org's users."""
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")


@router.post("/orgs")
def onboard_org(claims: dict = Depends(require_role("admin"))):
    """POST /orgs — System Admin. Onboard external authority org.
    MVP: admin pre-registration, not self-service.
    """
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")
