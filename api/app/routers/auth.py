"""Auth — see SYSTEM_DESIGN.md Interface Contracts, "Endpoint Table", and
the Security section's login-hardening rules."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas, security
from app.database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=schemas.TokenResponse)
def login(body: schemas.LoginRequest, db: Session = Depends(get_db)):
    """POST /auth/login — Public. Issue an access token (15 min) + refresh
    token (7 days).

    Constant-time on purpose: an unknown email still runs a bcrypt check
    (against a placeholder hash, see security.DUMMY_HASH) so response timing
    can't be used to enumerate which emails belong to real officer accounts.
    Same generic error either way — never reveal which of email/password
    was wrong.

    NOTE: real IP-based rate limiting (settings.LOGIN_RATE_LIMIT, 10/min)
    belongs at the ASGI middleware layer, not in this handler — not wired
    into this baseline yet.
    """
    user = db.query(models.User).filter(models.User.email == body.email).first()

    if user is None:
        security.dummy_password_check(body.password)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    if not security.verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    org_id = str(user.org_id)
    return schemas.TokenResponse(
        access_token=security.create_access_token(str(user.id), org_id, user.role),
        refresh_token=security.create_refresh_token(str(user.id), org_id, user.role),
    )


@router.post("/refresh", response_model=schemas.AccessTokenResponse)
def refresh_token(body: schemas.RefreshRequest):
    """POST /auth/refresh — Exchange a valid refresh token for a new access
    token. Not in the original endpoint table — added because a 15-minute
    access-token TTL is unusable without this."""
    claims = security.decode_token(body.refresh_token, expected_type="refresh")
    new_access = security.create_access_token(claims["sub"], claims["org_id"], claims["role"])
    return schemas.AccessTokenResponse(access_token=new_access)


@router.post("/logout")
def logout(claims: dict = Depends(security.get_current_claims)):
    """POST /auth/logout — Not in the original endpoint table.

    Baseline behavior: stateless. The 15-minute access-token TTL bounds the
    exposure window on its own. LATER (see SYSTEM_DESIGN.md): write the
    token's JTI to a Redis revocation set with a TTL matching its remaining
    lifetime, so a shared-device logout invalidates the session immediately
    instead of waiting out the TTL — not built here since this baseline has
    no live Redis to check against.
    """
    return {"status": "logged out"}
