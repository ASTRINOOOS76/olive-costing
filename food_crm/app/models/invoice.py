from __future__ import annotations

from datetime import date as date_type

from sqlalchemy import Date, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin, TimestampMixin


class Invoice(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "invoices"
    tenant_id: Mapped[str] = mapped_column(
        ForeignKey("tenants.id"), index=True, nullable=False
    )
    customer_id: Mapped[str] = mapped_column(
        ForeignKey("companies.id"), index=True, nullable=False
    )
    invoice_number: Mapped[str] = mapped_column(
        String(50), index=True, nullable=False
    )
    invoice_date: Mapped[date_type] = mapped_column(Date, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    total: Mapped[float] = mapped_column(Numeric(14, 4), default=0)
    status: Mapped[str] = mapped_column(
        String(30), default="draft"
    )  # draft / submitted / accepted / rejected
    mydata_mark: Mapped[str | None] = mapped_column(String(80))
    notes: Mapped[str | None] = mapped_column(String(2000))

    lines = relationship(
        "InvoiceLine", back_populates="invoice", cascade="all, delete-orphan"
    )


class InvoiceLine(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "invoice_lines"
    tenant_id: Mapped[str] = mapped_column(
        ForeignKey("tenants.id"), index=True, nullable=False
    )
    invoice_id: Mapped[str] = mapped_column(
        ForeignKey("invoices.id"), index=True, nullable=False
    )

    description: Mapped[str] = mapped_column(String(500), nullable=False)
    qty: Mapped[float] = mapped_column(Numeric(12, 3), nullable=False)
    unit: Mapped[str] = mapped_column(String(30), default="pcs")
    unit_price: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)
    vat_rate: Mapped[float] = mapped_column(Numeric(6, 3), default=0)

    invoice = relationship("Invoice", back_populates="lines")


class MyDataSubmission(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "mydata_submissions"
    tenant_id: Mapped[str] = mapped_column(
        ForeignKey("tenants.id"), index=True, nullable=False
    )
    invoice_id: Mapped[str] = mapped_column(
        ForeignKey("invoices.id"), index=True, nullable=False
    )
    request_json: Mapped[str] = mapped_column(Text)
    response_json: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        String(30), default="queued"
    )  # queued / submitted / accepted / rejected / error
    error: Mapped[str | None] = mapped_column(Text)
