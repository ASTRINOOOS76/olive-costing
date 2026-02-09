from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDMixin, TimestampMixin


class Item(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "items"
    tenant_id: Mapped[str] = mapped_column(
        ForeignKey("tenants.id"), index=True, nullable=False
    )

    sku: Mapped[str | None] = mapped_column(String(60), index=True)
    name: Mapped[str] = mapped_column(String(250), index=True, nullable=False)
    unit: Mapped[str] = mapped_column(String(30), default="pcs")
    vat_rate: Mapped[float] = mapped_column(Numeric(6, 3), default=0)
    category: Mapped[str | None] = mapped_column(String(80))
