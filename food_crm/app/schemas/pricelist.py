from pydantic import BaseModel


class PriceListIn(BaseModel):
    name: str
    currency: str = "EUR"


class PriceListOut(PriceListIn):
    id: str
    tenant_id: str

    class Config:
        from_attributes = True


class PriceListLineIn(BaseModel):
    pricelist_id: str
    item_id: str
    price: float
    moq: float = 0


class PriceListLineOut(PriceListLineIn):
    id: str
    tenant_id: str

    class Config:
        from_attributes = True
