from datetime import date

from pydantic import BaseModel


class QuoteLineIn(BaseModel):
    description: str
    qty: float
    unit: str = "pcs"
    unit_price: float


class QuoteCreate(BaseModel):
    customer_id: str
    quote_number: str
    quote_date: date
    currency: str = "EUR"
    notes: str | None = None
    lines: list[QuoteLineIn]


class QuoteOut(BaseModel):
    id: str
    tenant_id: str
    customer_id: str
    quote_number: str
    quote_date: date
    currency: str
    status: str
    notes: str | None

    class Config:
        from_attributes = True
