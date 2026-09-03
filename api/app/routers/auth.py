"""Auth & Org — see SYSTEM_DESIGN.md Interface Contracts, "Endpoint Table"."""

from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login():
    """POST /auth/login — Public. Issue an access token (15 min TTL) + a
    refresh token (7 days).

    TODO, in order:
      1. Rate-limit this endpoint specifically — settings.LOGIN_RATE_LIMIT
         (10/minute per IP). This is the one truly public-facing surface in
         the system; it gets the strictest limit.
      2. Look up the user by email.
      3. Run bcrypt.checkpw against the stored hash — AND, if the email
         doesn't exist, run a dummy bcrypt check against a fixed hash anyway.
         Skipping the dummy check on an unknown email makes response timing
         distinguish "no such officer" from "wrong password," which lets an
         attacker enumerate valid police accounts one timing measurement at
         a time. Both paths must take the same time.
      4. On success, call security.create_access_token + a matching refresh
         token; on failure, a generic "invalid credentials" error — never
         reveal which of email/password was wrong.
    """
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")


@router.post("/refresh")
def refresh_token():
    """POST /auth/refresh — Exchange a valid refresh token for a new access
    token. Not in the original endpoint table — added because a 15-minute
    access-token TTL is unusable without this."""
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")


@router.post("/logout")
def logout():
    """POST /auth/logout — Not in the original endpoint table. TODO once
    token revocation exists: write the current access token's JTI to the
    Redis revocation set (settings.TOKEN_REVOCATION_REDIS_DB) with a TTL
    matching its remaining lifetime, so a shared-device logout actually
    invalidates the session instead of just discarding the client-side copy.
    """
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Not implemented yet")
