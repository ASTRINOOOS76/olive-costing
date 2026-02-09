from pydantic import BaseModel


class CompanyIn(BaseModel):
    name: str
    vat: str | None = None
    country: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    is_customer: bool = True
    is_supplier: bool = False


class CompanyOut(CompanyIn):
    id: str
    tenant_id: str

    class Config:
        from_attributes = True
