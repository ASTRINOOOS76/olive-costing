from datetime import date

from pydantic import BaseModel


class DealIn(BaseModel):
    company_id: str
    contact_id: str | None = None
    assigned_to: str | None = None
    title: str
    stage: str = "lead"
    value: float | None = None
    currency: str = "EUR"
    expected_close: date | None = None
    notes: str | None = None


class DealOut(DealIn):
    id: str
    tenant_id: str

    class Config:
        from_attributes = True


class DealStageUpdate(BaseModel):
    stage: str
