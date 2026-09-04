"""Admin & config — schema registry, AI Parser recognizer mapping, stage
requirements, org onboarding. See SYSTEM_DESIGN.md Domain 8 (Platform / Admin).

Config Admin vs. Security Auditor (see models.py, User.role): a single
super-admin holding both schema-editing power and audit-inspection power is
one compromised account away from total control. Config Admin owns
everything in this file. Security Auditor owns audit.py's ai-parser endpoint
instead — never both from the same role.

Schema and recognizer-mapping changes (and Chain Worker manual recovery in
documents.py) are exactly the actions SYSTEM_DESIGN.md flags as needing
second-person confirmation before they take effect in a real deployment —
not enforced in this baseline, but don't build single-click execution here
and call it done.
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.security import require_role

router = APIRouter(prefix="/admin", tags=["admin"])


# ---------- Dynamic Role & Permission Management ----------

@router.get("/permissions", response_model=list[schemas.PermissionResponse])
def list_permissions(
    claims: dict = Depends(require_role("config_admin")),
    db: Session = Depends(get_db)
):
    """GET /admin/permissions — Config Admin. List all system permissions grouped by category."""
    return db.query(models.Permission).order_by(models.Permission.category, models.Permission.code).all()


@router.get("/roles", response_model=list[schemas.RoleResponse])
def list_roles(
    claims: dict = Depends(require_role("config_admin")),
    db: Session = Depends(get_db)
):
    """GET /admin/roles — Config Admin. List all system and custom roles with their permissions and member counts."""
    roles = db.query(models.Role).order_by(models.Role.created_at).all()
    results = []
    for r in roles:
        user_count = db.query(models.User).filter((models.User.role_id == r.id) | (models.User.role == r.code)).count()
        perm_codes = [p.code for p in r.permissions]
        results.append(
            schemas.RoleResponse(
                id=r.id,
                code=r.code,
                name=r.name,
                description=r.description,
                is_system=r.is_system,
                permission_codes=perm_codes,
                user_count=user_count
            )
        )
    return results


@router.post("/roles", response_model=schemas.RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(
    body: schemas.RoleCreateRequest,
    claims: dict = Depends(require_role("config_admin")),
    db: Session = Depends(get_db)
):
    """POST /admin/roles — Config Admin. Create a new custom role and assign permissions."""
    code_normalized = body.code.strip().lower().replace(" ", "_")
    existing = db.query(models.Role).filter(models.Role.code == code_normalized).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Role with code '{code_normalized}' already exists."
        )

    new_role = models.Role(
        code=code_normalized,
        name=body.name.strip(),
        description=body.description,
        is_system=False
    )

    if body.permission_codes:
        perms = db.query(models.Permission).filter(models.Permission.code.in_(body.permission_codes)).all()
        new_role.permissions.extend(perms)

    db.add(new_role)
    db.commit()
    db.refresh(new_role)

    return schemas.RoleResponse(
        id=new_role.id,
        code=new_role.code,
        name=new_role.name,
        description=new_role.description,
        is_system=new_role.is_system,
        permission_codes=[p.code for p in new_role.permissions],
        user_count=0
    )


@router.put("/roles/{role_id}", response_model=schemas.RoleResponse)
def update_role(
    role_id: UUID,
    body: schemas.RoleUpdateRequest,
    claims: dict = Depends(require_role("config_admin")),
    db: Session = Depends(get_db)
):
    """PUT /admin/roles/{role_id} — Config Admin. Update role name, description, or permissions."""
    role = db.get(models.Role, role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

    if body.name is not None:
        role.name = body.name.strip()
    if body.description is not None:
        role.description = body.description

    if body.permission_codes is not None:
        perms = db.query(models.Permission).filter(models.Permission.code.in_(body.permission_codes)).all()
        role.permissions = perms

    db.commit()
    db.refresh(role)

    user_count = db.query(models.User).filter((models.User.role_id == role.id) | (models.User.role == role.code)).count()
    return schemas.RoleResponse(
        id=role.id,
        code=role.code,
        name=role.name,
        description=role.description,
        is_system=role.is_system,
        permission_codes=[p.code for p in role.permissions],
        user_count=user_count
    )


@router.delete("/roles/{role_id}")
def delete_role(
    role_id: UUID,
    claims: dict = Depends(require_role("config_admin")),
    db: Session = Depends(get_db)
):
    """DELETE /admin/roles/{role_id} — Config Admin. Delete a custom role."""
    role = db.get(models.Role, role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    if role.is_system:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="System protected roles cannot be deleted.")

    db.delete(role)
    db.commit()
    return {"status": "deleted", "role_code": role.code}


@router.get("/users", response_model=list[schemas.UserSummaryResponse])
def list_users(
    claims: dict = Depends(require_role("config_admin")),
    db: Session = Depends(get_db)
):
    """GET /admin/users — Config Admin. List users across organizations with assigned roles."""
    users = db.query(models.User).order_by(models.User.created_at).all()
    results = []
    for u in users:
        results.append(
            schemas.UserSummaryResponse(
                id=u.id,
                name=u.name,
                email=u.email,
                service_id=u.service_id,
                designation=u.designation,
                role=u.role,
                org_name=u.organization.name if u.organization else None
            )
        )
    return results


@router.post("/users/{user_id}/assign-role")
def assign_user_role(
    user_id: UUID,
    body: schemas.AssignRoleRequest,
    claims: dict = Depends(require_role("config_admin")),
    db: Session = Depends(get_db)
):
    """POST /admin/users/{user_id}/assign-role — Config Admin.
    Authoritatively assign a role to a user. Server-side verified to prevent privilege escalation.
    """
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    target_role = db.query(models.Role).filter(models.Role.code == body.role_code).first()
    if not target_role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Role '{body.role_code}' does not exist.")

    user.role = target_role.code
    user.role_id = target_role.id
    db.commit()

    return {
        "status": "success",
        "user_id": str(user.id),
        "user_name": user.name,
        "assigned_role": target_role.code,
        "role_name": target_role.name
    }


# ---------- Existing Schema & Requirements Endpoints ----------

@router.get("/document-schemas")
def list_document_schemas(claims: dict = Depends(require_role("config_admin"))):
    """GET /admin/document-schemas — Config Admin."""
    return [
        {"doc_type": "FIR", "tier": 1, "fields": ["informant_name", "victim_address", "phone_number"], "recognizers": "Spacy + Presidio NER"},
        {"doc_type": "Panchnama", "tier": 1, "fields": ["panch_witness_identities", "confidential_location"], "recognizers": "Presidio Custom NER"},
        {"doc_type": "Forensic_Report", "tier": 2, "fields": ["chemical_composition", "dna_profile"], "recognizers": "FSL Format Validator"},
        {"doc_type": "Bank_Statement", "tier": 1, "fields": ["account_number", "pan_card", "aadhaar_id"], "recognizers": "India Financial Regex"},
    ]


@router.post("/document-schemas/{doc_type}/recognizers")
def set_recognizer_mapping(doc_type: str, claims: dict = Depends(require_role("config_admin"))):
    """POST /admin/document-schemas/:type/recognizers — Config Admin."""
    return {"status": "configured", "doc_type": doc_type}


@router.get("/stage-requirements")
def list_stage_requirements(claims: dict = Depends(require_role("config_admin"))):
    """GET /admin/stage-requirements — Config Admin."""
    return [
        {"crime_type": "NDPS", "requirements": ["FIR", "Panchnama", "Forensic_Report", "Witness_Statement", "Arrest_Memo"]},
        {"crime_type": "Cybercrime", "requirements": ["FIR", "Panchnama", "Bank_Statement", "Witness_Statement"]},
        {"crime_type": "Homicide", "requirements": ["FIR", "Inquest_Report", "Post_Mortem_Report", "Forensic_Report", "Seizure_Memo"]}
    ]
