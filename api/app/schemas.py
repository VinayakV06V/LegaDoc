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
    email: str  # Official email or Government Service ID / Badge Number
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


# ---------- Documents ----------
class DocumentUploadResponse(BaseModel):
    id: UUID
    case_id: UUID
    doc_type: str
    version: int
    status: str
    chain_status: str
    doc_hash: Optional[str] = None


class DocumentView(BaseModel):
    id: UUID
    case_id: UUID
    doc_type: str
    version: int
    status: str
    chain_status: str
    text: Optional[str] = None  # None while status != "ready"; masked or full depending on role
    download_url: Optional[str] = None
    doc_hash: Optional[str] = None


class DocumentVersionSummary(BaseModel):
    id: UUID
    version: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChainStatusResponse(BaseModel):
    document_id: UUID
    chain_status: str


class RedactTagRequest(BaseModel):
    entity_type: str
    span_start: int
    span_end: int


# ---------- User Profile & Authoritative Identity ----------
class UserProfileResponse(BaseModel):
    id: UUID
    name: str
    email: str
    service_id: Optional[str] = None
    designation: Optional[str] = None
    role: str
    org_id: UUID
    org_name: Optional[str] = None
    org_type: Optional[str] = None
    language_preference: str = "en"
    permissions: list[str] = []

    model_config = ConfigDict(from_attributes=True)


# ---------- Dynamic Role & Permission Management ----------
class PermissionResponse(BaseModel):
    id: UUID
    code: str
    name: str
    category: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class RoleResponse(BaseModel):
    id: UUID
    code: str
    name: str
    description: Optional[str] = None
    is_system: bool
    permission_codes: list[str] = []
    user_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class RoleCreateRequest(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    permission_codes: list[str] = []


class RoleUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permission_codes: Optional[list[str]] = None


class AssignRoleRequest(BaseModel):
    role_code: str


class UserSummaryResponse(BaseModel):
    id: UUID
    name: str
    email: str
    service_id: Optional[str] = None
    designation: Optional[str] = None
    role: str
    org_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
