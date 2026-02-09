from datetime import date

from pydantic import BaseModel


class POLineIn(BaseModel):
    description: str
    qty: float
    unit: str = "pcs"
    unit_price: float


class POCreate(BaseModel):
    supplier_id: str
    po_number: str
    po_date: date
    currency: str = "EUR"
    notes: str | None = None
    lines: list[POLineIn]


class POOut(BaseModel):
    id: str
    tenant_id: str
    supplier_id: str
    po_number: str
    po_date: date
    currency: str
    status: str
    notes: str | None

    class Config:
        from_attributes = True
