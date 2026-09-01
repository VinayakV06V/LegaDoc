"""Auth & Org — see SYSTEM_DESIGN.md Interface Contracts, "Endpoint Table"."""

from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login():
    """POST /auth/login — Public. Issue session/JWT.
    TODO: verify credentials against app.models.User, call security.create_access_token.
    """
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")
