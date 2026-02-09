from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDMixin, TimestampMixin


class Company(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "companies"
    tenant_id: Mapped[str] = mapped_column(
        ForeignKey("tenants.id"), index=True, nullable=False
    )

    name: Mapped[str] = mapped_column(String(250), index=True, nullable=False)
    vat: Mapped[str | None] = mapped_column(String(40), index=True)
    country: Mapped[str | None] = mapped_column(String(2))
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(50))
    address: Mapped[str | None] = mapped_column(String(400))

    is_customer: Mapped[bool] = mapped_column(Boolean, default=True)
    is_supplier: Mapped[bool] = mapped_column(Boolean, default=False)
