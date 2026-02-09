from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_ctx, get_db
from app.core.rbac import require_perm
from app.models.item import Item
from app.schemas.item import ItemIn, ItemOut

router = APIRouter(prefix="/items", tags=["items"])


@router.get("", response_model=list[ItemOut])
def list_items(
    category: str | None = None,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_ctx),
):
    require_perm(ctx["role"], "items:read")
    q = db.query(Item).filter(Item.tenant_id == ctx["tenant_id"])
    if category:
        q = q.filter(Item.category == category)
    return q.order_by(Item.name).all()


@router.get("/{item_id}", response_model=ItemOut)
def get_item(
    item_id: str,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_ctx),
):
    require_perm(ctx["role"], "items:read")
    it = db.get(Item, item_id)
    if not it or it.tenant_id != ctx["tenant_id"]:
        raise HTTPException(404, "Item not found")
    return it


@router.post("", response_model=ItemOut)
def create_item(
    payload: ItemIn,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_ctx),
):
    require_perm(ctx["role"], "items:create")
    it = Item(tenant_id=ctx["tenant_id"], **payload.model_dump())
    db.add(it)
    db.commit()
    db.refresh(it)
    return it


@router.put("/{item_id}", response_model=ItemOut)
def update_item(
    item_id: str,
    payload: ItemIn,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_ctx),
):
    require_perm(ctx["role"], "items:update")
    it = db.get(Item, item_id)
    if not it or it.tenant_id != ctx["tenant_id"]:
        raise HTTPException(404, "Item not found")
    for k, v in payload.model_dump().items():
        setattr(it, k, v)
    db.commit()
    db.refresh(it)
    return it


@router.delete("/{item_id}")
def delete_item(
    item_id: str,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_ctx),
):
    require_perm(ctx["role"], "items:delete")
    it = db.get(Item, item_id)
    if not it or it.tenant_id != ctx["tenant_id"]:
        raise HTTPException(404, "Item not found")
    db.delete(it)
    db.commit()
    return {"ok": True}
