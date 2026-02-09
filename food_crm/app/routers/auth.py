from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.tenant import Tenant
from app.models.user import User
from app.schemas.auth import (
    LoginIn,
    RegisterOut,
    RegisterTenantIn,
    TokenOut,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    u = (
        db.query(User)
        .filter(User.tenant_id == payload.tenant_id, User.email == payload.email)
        .first()
    )
    if not u or not u.is_active or not verify_password(payload.password, u.password_hash):
        raise HTTPException(status_code=401, detail="Bad credentials")
    token = create_access_token(sub=u.id, tenant_id=u.tenant_id, role=u.role)
    return {"access_token": token}


@router.post("/register", response_model=RegisterOut)
def register_tenant(payload: RegisterTenantIn, db: Session = Depends(get_db)):
    """Self-service tenant registration (creates tenant + owner user)."""
    tenant = Tenant(name=payload.tenant_name)
    db.add(tenant)
    db.flush()

    user = User(
        tenant_id=tenant.id,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role="owner",
    )
    db.add(user)
    db.commit()
    db.refresh(tenant)
    db.refresh(user)

    token = create_access_token(sub=user.id, tenant_id=tenant.id, role=user.role)
    return {
        "tenant_id": tenant.id,
        "user_id": user.id,
        "access_token": token,
    }
