from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_ctx, get_db
from app.core.rbac import require_perm
from app.models.deal import Deal
from app.schemas.deal import DealIn, DealOut, DealStageUpdate

router = APIRouter(prefix="/deals", tags=["deals"])

VALID_STAGES = {"lead", "qualified", "proposal", "negotiation", "won", "lost"}


@router.get("", response_model=list[DealOut])
def list_deals(
    stage: str | None = None,
    company_id: str | None = None,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_ctx),
):
    require_perm(ctx["role"], "deals:read")
    q = db.query(Deal).filter(Deal.tenant_id == ctx["tenant_id"])
    if stage:
        q = q.filter(Deal.stage == stage)
    if company_id:
        q = q.filter(Deal.company_id == company_id)
    return q.order_by(Deal.created_at.desc()).all()


@router.get("/{deal_id}", response_model=DealOut)
def get_deal(
    deal_id: str,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_ctx),
):
    require_perm(ctx["role"], "deals:read")
    d = db.get(Deal, deal_id)
    if not d or d.tenant_id != ctx["tenant_id"]:
        raise HTTPException(404, "Deal not found")
    return d


@router.post("", response_model=DealOut)
def create_deal(
    payload: DealIn,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_ctx),
):
    require_perm(ctx["role"], "deals:create")
    if payload.stage not in VALID_STAGES:
        raise HTTPException(400, f"Invalid stage. Must be one of: {VALID_STAGES}")
    d = Deal(tenant_id=ctx["tenant_id"], **payload.model_dump())
    db.add(d)
    db.commit()
    db.refresh(d)
    return d


@router.put("/{deal_id}", response_model=DealOut)
def update_deal(
    deal_id: str,
    payload: DealIn,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_ctx),
):
    require_perm(ctx["role"], "deals:update")
    d = db.get(Deal, deal_id)
    if not d or d.tenant_id != ctx["tenant_id"]:
        raise HTTPException(404, "Deal not found")
    if payload.stage not in VALID_STAGES:
        raise HTTPException(400, f"Invalid stage. Must be one of: {VALID_STAGES}")
    for k, v in payload.model_dump().items():
        setattr(d, k, v)
    db.commit()
    db.refresh(d)
    return d


@router.patch("/{deal_id}/stage", response_model=DealOut)
def update_deal_stage(
    deal_id: str,
    payload: DealStageUpdate,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_ctx),
):
    require_perm(ctx["role"], "deals:update")
    d = db.get(Deal, deal_id)
    if not d or d.tenant_id != ctx["tenant_id"]:
        raise HTTPException(404, "Deal not found")
    if payload.stage not in VALID_STAGES:
        raise HTTPException(400, f"Invalid stage. Must be one of: {VALID_STAGES}")
    d.stage = payload.stage
    db.commit()
    db.refresh(d)
    return d


@router.delete("/{deal_id}")
def delete_deal(
    deal_id: str,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_ctx),
):
    require_perm(ctx["role"], "deals:delete")
    d = db.get(Deal, deal_id)
    if not d or d.tenant_id != ctx["tenant_id"]:
        raise HTTPException(404, "Deal not found")
    db.delete(d)
    db.commit()
    return {"ok": True}
