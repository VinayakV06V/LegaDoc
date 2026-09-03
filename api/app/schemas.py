"""
Pydantic request/response models. Kept in one file at this baseline size —
split by resource group (matching routers/) once this gets big enough that
one file is actually hard to navigate, not before.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


# ---------- Auth ----------
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Cases ----------
class RegisterFIRRequest(BaseModel):
    crime_type: str
    complaint_text: str


class CaseResponse(BaseModel):
    id: UUID
    case_number: str
    crime_type: str
    court_level: Optional[str] = None
    investigation_status: str
    bail_status: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AssignIORequest(BaseModel):
    io_user_id: UUID
