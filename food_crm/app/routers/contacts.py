from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_ctx, get_db
from app.core.rbac import require_perm
from app.models.contact import Contact
from app.schemas.contact import ContactIn, ContactOut

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("", response_model=list[ContactOut])
def list_contacts(
    company_id: str | None = None,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_ctx),
):
    require_perm(ctx["role"], "contacts:read")
    q = db.query(Contact).filter(Contact.tenant_id == ctx["tenant_id"])
    if company_id:
        q = q.filter(Contact.company_id == company_id)
    return q.order_by(Contact.created_at.desc()).all()


@router.get("/{contact_id}", response_model=ContactOut)
def get_contact(
    contact_id: str,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_ctx),
):
    require_perm(ctx["role"], "contacts:read")
    c = db.get(Contact, contact_id)
    if not c or c.tenant_id != ctx["tenant_id"]:
        raise HTTPException(404, "Contact not found")
    return c


@router.post("", response_model=ContactOut)
def create_contact(
    payload: ContactIn,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_ctx),
):
    require_perm(ctx["role"], "contacts:create")
    c = Contact(tenant_id=ctx["tenant_id"], **payload.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@router.put("/{contact_id}", response_model=ContactOut)
def update_contact(
    contact_id: str,
    payload: ContactIn,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_ctx),
):
    require_perm(ctx["role"], "contacts:update")
    c = db.get(Contact, contact_id)
    if not c or c.tenant_id != ctx["tenant_id"]:
        raise HTTPException(404, "Contact not found")
    for k, v in payload.model_dump().items():
        setattr(c, k, v)
    db.commit()
    db.refresh(c)
    return c


@router.delete("/{contact_id}")
def delete_contact(
    contact_id: str,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_ctx),
):
    require_perm(ctx["role"], "contacts:delete")
    c = db.get(Contact, contact_id)
    if not c or c.tenant_id != ctx["tenant_id"]:
        raise HTTPException(404, "Contact not found")
    db.delete(c)
    db.commit()
    return {"ok": True}
