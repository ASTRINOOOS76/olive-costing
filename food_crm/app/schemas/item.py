from pydantic import BaseModel


class ItemIn(BaseModel):
    sku: str | None = None
    name: str
    unit: str = "pcs"
    vat_rate: float = 0
    category: str | None = None


class ItemOut(ItemIn):
    id: str
    tenant_id: str

    class Config:
        from_attributes = True
