from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_ctx, get_db
from app.core.rbac import require_perm
from app.models.company import Company
from app.schemas.company import CompanyIn, CompanyOut

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("", response_model=list[CompanyOut])
def list_companies(
    is_customer: bool | None = None,
    is_supplier: bool | None = None,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_ctx),
):
    require_perm(ctx["role"], "companies:read")
    q = db.query(Company).filter(Company.tenant_id == ctx["tenant_id"])
    if is_customer is not None:
        q = q.filter(Company.is_customer == is_customer)
    if is_supplier is not None:
        q = q.filter(Company.is_supplier == is_supplier)
    return q.order_by(Company.created_at.desc()).all()


@router.get("/{company_id}", response_model=CompanyOut)
def get_company(
    company_id: str,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_ctx),
):
    require_perm(ctx["role"], "companies:read")
    c = db.get(Company, company_id)
    if not c or c.tenant_id != ctx["tenant_id"]:
        raise HTTPException(404, "Company not found")
    return c


@router.post("", response_model=CompanyOut)
def create_company(
    payload: CompanyIn,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_ctx),
):
    require_perm(ctx["role"], "companies:create")
    c = Company(tenant_id=ctx["tenant_id"], **payload.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@router.put("/{company_id}", response_model=CompanyOut)
def update_company(
    company_id: str,
    payload: CompanyIn,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_ctx),
):
    require_perm(ctx["role"], "companies:update")
    c = db.get(Company, company_id)
    if not c or c.tenant_id != ctx["tenant_id"]:
        raise HTTPException(404, "Company not found")
    for k, v in payload.model_dump().items():
        setattr(c, k, v)
    db.commit()
    db.refresh(c)
    return c


@router.delete("/{company_id}")
def delete_company(
    company_id: str,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_ctx),
):
    require_perm(ctx["role"], "companies:delete")
    c = db.get(Company, company_id)
    if not c or c.tenant_id != ctx["tenant_id"]:
        raise HTTPException(404, "Company not found")
    db.delete(c)
    db.commit()
    return {"ok": True}
