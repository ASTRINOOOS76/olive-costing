from __future__ import annotations

from datetime import date as date_type

from sqlalchemy import Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin, TimestampMixin


class PurchaseOrder(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "purchase_orders"
    tenant_id: Mapped[str] = mapped_column(
        ForeignKey("tenants.id"), index=True, nullable=False
    )
    supplier_id: Mapped[str] = mapped_column(
        ForeignKey("companies.id"), index=True, nullable=False
    )

    po_number: Mapped[str] = mapped_column(
        String(50), index=True, nullable=False
    )
    po_date: Mapped[date_type] = mapped_column(Date, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    status: Mapped[str] = mapped_column(String(30), default="draft")
    notes: Mapped[str | None] = mapped_column(String(2000))
    lines = relationship(
        "PurchaseOrderLine", back_populates="po", cascade="all, delete-orphan"
    )


class PurchaseOrderLine(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "purchase_order_lines"
    tenant_id: Mapped[str] = mapped_column(
        ForeignKey("tenants.id"), index=True, nullable=False
    )
    po_id: Mapped[str] = mapped_column(
        ForeignKey("purchase_orders.id"), index=True, nullable=False
    )

    description: Mapped[str] = mapped_column(String(500), nullable=False)
    qty: Mapped[float] = mapped_column(Numeric(12, 3), nullable=False)
    unit: Mapped[str] = mapped_column(String(30), default="pcs")
    unit_price: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)

    po = relationship("PurchaseOrder", back_populates="lines")
