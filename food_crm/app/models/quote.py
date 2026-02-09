from __future__ import annotations

from datetime import date as date_type

from sqlalchemy import Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin, TimestampMixin


class Quote(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "quotes"
    tenant_id: Mapped[str] = mapped_column(
        ForeignKey("tenants.id"), index=True, nullable=False
    )
    customer_id: Mapped[str] = mapped_column(
        ForeignKey("companies.id"), index=True, nullable=False
    )

    quote_number: Mapped[str] = mapped_column(
        String(50), index=True, nullable=False
    )
    quote_date: Mapped[date_type] = mapped_column(Date, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    status: Mapped[str] = mapped_column(String(30), default="draft")
    notes: Mapped[str | None] = mapped_column(String(2000))
    lines = relationship(
        "QuoteLine", back_populates="quote", cascade="all, delete-orphan"
    )


class QuoteLine(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "quote_lines"
    tenant_id: Mapped[str] = mapped_column(
        ForeignKey("tenants.id"), index=True, nullable=False
    )
    quote_id: Mapped[str] = mapped_column(
        ForeignKey("quotes.id"), index=True, nullable=False
    )

    description: Mapped[str] = mapped_column(String(500), nullable=False)
    qty: Mapped[float] = mapped_column(Numeric(12, 3), nullable=False)
    unit: Mapped[str] = mapped_column(String(30), default="pcs")
    unit_price: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)

    quote = relationship("Quote", back_populates="lines")
