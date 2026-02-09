from __future__ import annotations

from datetime import date

from sqlalchemy import Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDMixin, TimestampMixin


class Deal(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "deals"
    tenant_id: Mapped[str] = mapped_column(
        ForeignKey("tenants.id"), index=True, nullable=False
    )
    company_id: Mapped[str] = mapped_column(
        ForeignKey("companies.id"), index=True, nullable=False
    )
    contact_id: Mapped[str | None] = mapped_column(
        ForeignKey("contacts.id"), index=True
    )
    assigned_to: Mapped[str | None] = mapped_column(
        ForeignKey("users.id"), index=True
    )

    title: Mapped[str] = mapped_column(String(300), nullable=False)
    stage: Mapped[str] = mapped_column(String(60), default="lead")
    # lead -> qualified -> proposal -> negotiation -> won -> lost
    value: Mapped[float | None] = mapped_column(Numeric(14, 4))
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    expected_close: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(String(2000))
