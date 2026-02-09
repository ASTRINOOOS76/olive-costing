from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDMixin, TimestampMixin


class PriceList(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "pricelists"
    tenant_id: Mapped[str] = mapped_column(
        ForeignKey("tenants.id"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="EUR")


class PriceListLine(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "pricelist_lines"
    tenant_id: Mapped[str] = mapped_column(
        ForeignKey("tenants.id"), index=True, nullable=False
    )
    pricelist_id: Mapped[str] = mapped_column(
        ForeignKey("pricelists.id"), index=True, nullable=False
    )
    item_id: Mapped[str] = mapped_column(
        ForeignKey("items.id"), index=True, nullable=False
    )

    price: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)
    moq: Mapped[float] = mapped_column(Numeric(12, 3), default=0)
