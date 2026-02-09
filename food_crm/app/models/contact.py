from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDMixin, TimestampMixin


class Contact(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "contacts"
    tenant_id: Mapped[str] = mapped_column(
        ForeignKey("tenants.id"), index=True, nullable=False
    )
    company_id: Mapped[str] = mapped_column(
        ForeignKey("companies.id"), index=True, nullable=False
    )

    first_name: Mapped[str | None] = mapped_column(String(120))
    last_name: Mapped[str | None] = mapped_column(String(120))
    email: Mapped[str | None] = mapped_column(String(255), index=True)
    phone: Mapped[str | None] = mapped_column(String(50))
    position: Mapped[str | None] = mapped_column(String(120))
