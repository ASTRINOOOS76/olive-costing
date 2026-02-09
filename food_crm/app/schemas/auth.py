from pydantic import BaseModel, EmailStr


class LoginIn(BaseModel):
    tenant_id: str
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegisterTenantIn(BaseModel):
    tenant_name: str
    email: EmailStr
    password: str


class RegisterOut(BaseModel):
    tenant_id: str
    user_id: str
    access_token: str
