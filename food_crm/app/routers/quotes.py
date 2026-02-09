from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.core.deps import get_ctx, get_db
from app.core.rbac import require_perm
from app.models.company import Company
from app.models.quote import Quote, QuoteLine
from app.schemas.quote import QuoteCreate, QuoteOut
from app.services.pdf import render_doc_pdf

router = APIRouter(prefix="/quotes", tags=["quotes"])


@router.get("", response_model=list[QuoteOut])
def list_quotes(
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_ctx),
):
    require_perm(ctx["role"], "quotes:read")
    return (
        db.query(Quote)
        .filter(Quote.tenant_id == ctx["tenant_id"])
        .order_by(Quote.created_at.desc())
        .all()
    )


@router.get("/{quote_id}", response_model=QuoteOut)
def get_quote(
    quote_id: str,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_ctx),
):
    require_perm(ctx["role"], "quotes:read")
    q = db.get(Quote, quote_id)
    if not q or q.tenant_id != ctx["tenant_id"]:
        raise HTTPException(404, "Quote not found")
    return q


@router.post("", response_model=QuoteOut)
def create_quote(
    payload: QuoteCreate,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_ctx),
):
    require_perm(ctx["role"], "quotes:create")
    customer = db.get(Company, payload.customer_id)
    if not customer or customer.tenant_id != ctx["tenant_id"]:
        raise HTTPException(404, "Customer not found")

    quote = Quote(
        tenant_id=ctx["tenant_id"],
        customer_id=payload.customer_id,
        quote_number=payload.quote_number,
        quote_date=payload.quote_date,
        currency=payload.currency,
        notes=payload.notes,
    )
    for ln in payload.lines:
        quote.lines.append(
            QuoteLine(
                tenant_id=ctx["tenant_id"],
                description=ln.description,
                qty=ln.qty,
                unit=ln.unit,
                unit_price=ln.unit_price,
            )
        )
    db.add(quote)
    db.commit()
    db.refresh(quote)
    return quote


@router.get("/{quote_id}/pdf")
def quote_pdf(
    quote_id: str,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_ctx),
):
    require_perm(ctx["role"], "quotes:read")
    quote = db.get(Quote, quote_id)
    if not quote or quote.tenant_id != ctx["tenant_id"]:
        raise HTTPException(404, "Quote not found")
    customer = db.get(Company, quote.customer_id)
    pdf = render_doc_pdf(
        "Quotation",
        quote.quote_number,
        quote.quote_date,
        customer.name if customer else "Customer",
        quote.currency,
        quote.notes,
        quote.lines,
    )
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="Quote_{quote.quote_number}.pdf"'
        },
    )
