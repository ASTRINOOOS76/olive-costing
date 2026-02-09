from pydantic import BaseModel


class ContactIn(BaseModel):
    company_id: str
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None
    position: str | None = None


class ContactOut(ContactIn):
    id: str
    tenant_id: str

    class Config:
        from_attributes = True
