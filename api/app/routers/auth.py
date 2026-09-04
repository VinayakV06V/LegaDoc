"""Auth — see SYSTEM_DESIGN.md Interface Contracts, "Endpoint Table", and
the Security section's login-hardening rules."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas, security
from app.database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=schemas.TokenResponse)
def login(body: schemas.LoginRequest, db: Session = Depends(get_db)):
    """POST /auth/login — Public. Authenticates user by official email or Government Service ID.
    Issues short-lived access token + refresh token bound strictly to authoritative user role.
    """
    ident = body.email.strip()
    user = (
        db.query(models.User)
        .filter((models.User.email == ident) | (models.User.service_id == ident))
        .first()
    )

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


@router.get("/me", response_model=schemas.UserProfileResponse)
def get_current_user_profile(
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    """GET /auth/me — Authenticated. Returns authoritative user profile, department,
    government service ID, authoritative role, and assigned permissions list.
    """
    # Resolve permissions from user's role
    permissions = []
    if current_user.role_rel and current_user.role_rel.permissions:
        permissions = [p.code for p in current_user.role_rel.permissions]
    else:
        # Fallback to Role by code
        role_obj = db.query(models.Role).filter(models.Role.code == current_user.role).first()
        if role_obj and role_obj.permissions:
            permissions = [p.code for p in role_obj.permissions]

    org_name = current_user.organization.name if current_user.organization else None
    org_type = current_user.organization.org_type if current_user.organization else None

    return schemas.UserProfileResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        service_id=current_user.service_id,
        designation=current_user.designation,
        role=current_user.role,
        org_id=current_user.org_id,
        org_name=org_name,
        org_type=org_type,
        language_preference=current_user.language_preference or "en",
        permissions=permissions
    )


@router.post("/refresh", response_model=schemas.AccessTokenResponse)
def refresh_token(body: schemas.RefreshRequest):
    """POST /auth/refresh — Exchange a valid refresh token for a new access token."""
    claims = security.decode_token(body.refresh_token, expected_type="refresh")
    new_access = security.create_access_token(claims["sub"], claims["org_id"], claims["role"])
    return schemas.AccessTokenResponse(access_token=new_access)


@router.post("/logout")
def logout(claims: dict = Depends(security.get_current_claims)):
    """POST /auth/logout — Stateless session invalidation."""
    return {"status": "logged out"}

