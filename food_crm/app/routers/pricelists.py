from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_ctx, get_db
from app.core.rbac import require_perm
from app.models.pricelist import PriceList, PriceListLine
from app.schemas.pricelist import (
    PriceListIn,
    PriceListLineIn,
    PriceListLineOut,
    PriceListOut,
)

router = APIRouter(prefix="/pricelists", tags=["pricelists"])


# ── Price Lists ──────────────────────────────────────────────
@router.get("", response_model=list[PriceListOut])
def list_pricelists(
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_ctx),
):
    require_perm(ctx["role"], "pricelists:read")
    return (
        db.query(PriceList)
        .filter(PriceList.tenant_id == ctx["tenant_id"])
        .order_by(PriceList.name)
        .all()
    )


@router.post("", response_model=PriceListOut)
def create_pricelist(
    payload: PriceListIn,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_ctx),
):
    require_perm(ctx["role"], "pricelists:create")
    pl = PriceList(tenant_id=ctx["tenant_id"], **payload.model_dump())
    db.add(pl)
    db.commit()
    db.refresh(pl)
    return pl


@router.delete("/{pricelist_id}")
def delete_pricelist(
    pricelist_id: str,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_ctx),
):
    require_perm(ctx["role"], "pricelists:delete")
    pl = db.get(PriceList, pricelist_id)
    if not pl or pl.tenant_id != ctx["tenant_id"]:
        raise HTTPException(404, "Price list not found")
    db.delete(pl)
    db.commit()
    return {"ok": True}


# ── Price List Lines ─────────────────────────────────────────
@router.get("/{pricelist_id}/lines", response_model=list[PriceListLineOut])
def list_pricelist_lines(
    pricelist_id: str,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_ctx),
):
    require_perm(ctx["role"], "pricelists:read")
    return (
        db.query(PriceListLine)
        .filter(
            PriceListLine.tenant_id == ctx["tenant_id"],
            PriceListLine.pricelist_id == pricelist_id,
        )
        .all()
    )


@router.post("/{pricelist_id}/lines", response_model=PriceListLineOut)
def add_pricelist_line(
    pricelist_id: str,
    payload: PriceListLineIn,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_ctx),
):
    require_perm(ctx["role"], "pricelists:create")
    line = PriceListLine(
        tenant_id=ctx["tenant_id"],
        pricelist_id=pricelist_id,
        item_id=payload.item_id,
        price=payload.price,
        moq=payload.moq,
    )
    db.add(line)
    db.commit()
    db.refresh(line)
    return line


@router.delete("/{pricelist_id}/lines/{line_id}")
def delete_pricelist_line(
    pricelist_id: str,
    line_id: str,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_ctx),
):
    require_perm(ctx["role"], "pricelists:delete")
    line = db.get(PriceListLine, line_id)
    if not line or line.tenant_id != ctx["tenant_id"] or line.pricelist_id != pricelist_id:
        raise HTTPException(404, "Line not found")
    db.delete(line)
    db.commit()
    return {"ok": True}
