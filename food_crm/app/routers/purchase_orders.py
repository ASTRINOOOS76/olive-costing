from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.core.deps import get_ctx, get_db
from app.core.rbac import require_perm
from app.models.company import Company
from app.models.po import PurchaseOrder, PurchaseOrderLine
from app.schemas.po import POCreate, POOut
from app.services.pdf import render_doc_pdf

router = APIRouter(prefix="/purchase-orders", tags=["purchase-orders"])


@router.get("", response_model=list[POOut])
def list_pos(
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_ctx),
):
    require_perm(ctx["role"], "po:read")
    return (
        db.query(PurchaseOrder)
        .filter(PurchaseOrder.tenant_id == ctx["tenant_id"])
        .order_by(PurchaseOrder.created_at.desc())
        .all()
    )


@router.get("/{po_id}", response_model=POOut)
def get_po(
    po_id: str,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_ctx),
):
    require_perm(ctx["role"], "po:read")
    po = db.get(PurchaseOrder, po_id)
    if not po or po.tenant_id != ctx["tenant_id"]:
        raise HTTPException(404, "PO not found")
    return po


@router.post("", response_model=POOut)
def create_po(
    payload: POCreate,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_ctx),
):
    require_perm(ctx["role"], "po:create")
    supplier = db.get(Company, payload.supplier_id)
    if not supplier or supplier.tenant_id != ctx["tenant_id"]:
        raise HTTPException(404, "Supplier not found")

    po = PurchaseOrder(
        tenant_id=ctx["tenant_id"],
        supplier_id=payload.supplier_id,
        po_number=payload.po_number,
        po_date=payload.po_date,
        currency=payload.currency,
        notes=payload.notes,
    )
    for ln in payload.lines:
        po.lines.append(
            PurchaseOrderLine(
                tenant_id=ctx["tenant_id"],
                description=ln.description,
                qty=ln.qty,
                unit=ln.unit,
                unit_price=ln.unit_price,
            )
        )
    db.add(po)
    db.commit()
    db.refresh(po)
    return po


@router.get("/{po_id}/pdf")
def po_pdf(
    po_id: str,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_ctx),
):
    require_perm(ctx["role"], "po:read")
    po = db.get(PurchaseOrder, po_id)
    if not po or po.tenant_id != ctx["tenant_id"]:
        raise HTTPException(404, "PO not found")
    supplier = db.get(Company, po.supplier_id)
    pdf = render_doc_pdf(
        "Purchase Order",
        po.po_number,
        po.po_date,
        supplier.name if supplier else "Supplier",
        po.currency,
        po.notes,
        po.lines,
    )
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="PO_{po.po_number}.pdf"'
        },
    )
