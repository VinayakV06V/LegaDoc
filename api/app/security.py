"""
JWT issuance/verification and the RBAC dependency every protected route uses.
This is the ONE place role/org checks happen — per SYSTEM_DESIGN.md's B2B
multi-tenant overlay, don't reinvent this per-endpoint.

Stubbed for the baseline: encode/decode work, but there's no real password
hashing or login flow wired up yet — that's real work for whoever picks up
POST /auth/login.
"""

from datetime import datetime, timedelta
from typing import Iterable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def create_access_token(user_id: str, org_id: str, role: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {"sub": user_id, "org_id": org_id, "role": role, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")


def get_current_claims(token: str = Depends(oauth2_scheme)) -> dict:
    """Every protected endpoint depends on this (directly or via require_role)."""
    return decode_token(token)


def require_role(*allowed_roles: str):
    """FastAPI dependency factory: Depends(require_role("sho", "config_admin")).
    Org-scoping (does this claim's org_id match the resource being touched) is
    each router's own responsibility on top of this — role alone isn't enough
    for anything that reads/writes a specific case or org's data.
    """

    def _check(claims: dict = Depends(get_current_claims)) -> dict:
        if claims.get("role") not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role not permitted for this action")
        return claims

    return _check
